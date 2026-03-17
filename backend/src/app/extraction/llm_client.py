import json
import asyncio
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
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
    items: List[InvoiceItemSchema] = Field(default_factory=list, description="List of items/services on the invoice.")
    is_valid_invoice: bool = Field(description="True if the text appears to be a valid invoice or receipt. False if it's spam/conversational text.")


class LLMExtractorClient:
    """
    Orchestrates extraction of highly unstructured text or LayoutLM outputs
    into structured Pydantic models using OpenAI's Function Calling (Instructor)
    or Langchain core tools.
    """
    def __init__(self, model_name: str = "gpt-4-turbo-preview", temperature: float = 0.0):
        self.settings = BaseAPIConfig.get_settings()
        self.api_key = self.settings.openai_api_key
        
        # Use Langchain wrapper
        if not self.api_key:
            print("Warning: OPENAI_API_KEY is not set.")
            
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=self.api_key,
            max_retries=3 # Rate limit handling built-in via Tenacity/Langchain
        )
        
        # Output parser bound to Pydantic
        self.parser = PydanticOutputParser(pydantic_object=InvoiceOutputSchema)

    def format_prompt(self) -> ChatPromptTemplate:
        """
        Creates the ChatPromptTemplate injecting the instructions and the strict JSON Schema
        for the LLM output.
        """
        system_template = """
        You are an elite financial data extraction AI. You will be provided with the raw OCR text of an email attachment (often an invoice, receipt, or bill).
        
        Your objective is to extract the billing information strictly adhering to the JSON schema below.
        If a field is not present in the text, use null (or 0.0 for currencies).
        If the document is just a random conversational email or spam, set 'is_valid_invoice' to false.
        
        Schema Format Instructions:
        {format_instructions}
        
        Only output the raw JSON requested, no markdown fences, no conversational text.
        """
        
        human_template = "Raw Document OCR Text:\n{ocr_text}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template)
        ])
        
        return prompt

    async def invoke_llm_chain(self, raw_ocr_text: str, custom_prompt: Optional[ChatPromptTemplate] = None) -> Optional[InvoiceOutputSchema]:
        """
        Triggers the LCEL (LangChain Expression Language) pipeline 
        to process the raw unstructured OCR text into a validated Pydantic DTO.
        """
        if not self.api_key:
            return None
            
        prompt = custom_prompt if custom_prompt else self.format_prompt()
        
        # Chain formulation: Prompt | LLM | Parser
        chain = prompt | self.llm | self.parser
        
        try:
            # We add manual exponential backoff handling for OpenAI API limits 
            # (though max_retries handles standard 429s automatically inside ChatOpenAI)
            print("Sending text to OpenAI via Langchain for semantic extraction...")
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
