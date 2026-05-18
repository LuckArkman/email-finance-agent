import json
import asyncio
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
import instructor

from app.config import BaseAPIConfig

class InvoiceItemSchema(BaseModel):
    description: str = Field(description="Description of the item or service.")
    quantity: float = Field(default=1.0, description="Quantity of items, default 1.")
    unit_price: float = Field(default=0.0, description="Price per unit.")
    total_price: float = Field(description="Total price for this line item.")

class InvoiceOutputSchema(BaseModel):
    """
    Schema for representing the final parsed structure of an Invoice/Receipt.
    This acts as the strict Output Parser constraint for the LLM.
    """
    vendor_name: str = Field(description="Name of the company that issued the invoice.")
    invoice_number: Optional[str] = Field(None, description="The unique invoice or receipt number.")
    issue_date: Optional[str] = Field(None, description="Date of the invoice/receipt in YYYY-MM-DD format if possible.")
    due_date: Optional[str] = Field(None, description="Due date of the invoice in YYYY-MM-DD format if applicable.")
    currency: str = Field(default="BRL", description="Currency of the transaction (e.g., BRL, USD, EUR).")
    subtotal: float = Field(default=0.0, description="Subtotal amount before taxes.")
    tax_amount: float = Field(default=0.0, description="Total tax amount.")
    total_amount: float = Field(description="The grand total amount to be paid.")
    
    iban: Optional[str] = Field(None, description="Bank account IBAN for payment.")
    swift: Optional[str] = Field(None, description="Bank SWIFT/BIC code.")
    
    items: List[InvoiceItemSchema] = Field(default_factory=list, description="List of items/services on the invoice.")
    is_valid_invoice: bool = Field(description="True if the text is a valid financial document (Invoice/Receipt).")


class LLMExtractorClient:
    """
    Orchestrates extraction of highly unstructured text or LayoutLM outputs
    into structured Pydantic models using OpenAI's Function Calling (Instructor)
    or Langchain core tools.
    """
    def __init__(self, model_name: str = "llama3:latest", temperature: float = 0.0):
        self.settings = BaseAPIConfig.get_settings()
        self.api_key = self.settings.openai_api_key
        self.ollama_base_url = self.settings.ollama_base_url
        
        # Prefer Ollama/Llama3 if configured
        if self.ollama_base_url:
            print(f"Initializing LLMExtractor with Local Llama3 via Ollama at {self.ollama_base_url}")
            self.llm = ChatOllama(
                model=model_name,
                temperature=temperature,
                base_url=self.ollama_base_url,
                timeout=180
            )
        else:
            print(f"Initializing LLMExtractor with OpenAI {model_name}")
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview", # Fallback model
                temperature=temperature,
                api_key=self.api_key,
                max_retries=3
            )
        
        # Output parser bound to Pydantic
        self.parser = PydanticOutputParser(pydantic_object=InvoiceOutputSchema)

    def format_prompt(self) -> ChatPromptTemplate:
        """
        Creates the ChatPromptTemplate using the centralized Brain Persona
        from the PromptManager.
        """
        from app.extraction.prompts import PromptManager
        return PromptManager.build_agent_brain_prompt()

    async def invoke_llm_chain(self, raw_ocr_text: str, custom_prompt: Optional[ChatPromptTemplate] = None) -> Optional[InvoiceOutputSchema]:
        """
        Triggers the LCEL (LangChain Expression Language) pipeline 
        to process the raw unstructured OCR text into a validated Pydantic DTO.
        """
        prompt = custom_prompt if custom_prompt else self.format_prompt()
        
        # Chain formulation: Prompt | LLM | Parser
        chain = prompt | self.llm | self.parser
        
        try:
            # Automatic retry logic is built-in Langchain for both OpenAI and Ollama
            print(f"Sending text to AI Agent ({self.llm.__class__.__name__}) for semantic extraction...")
            result: InvoiceOutputSchema = await chain.ainvoke(
                {"ocr_text": raw_ocr_text, "format_instructions": self.parser.get_format_instructions()}
            )
            return result
            
        except OutputParserException as e:
            print(f"Failed to parse LLM output cleanly: {e}")
            return None
        except Exception as e:
            print(f"Generic error in LLMExtractorClient: {e}")
            return None
