import json
import asyncio
from typing import Optional, List, Any
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException

from app.config import BaseAPIConfig
from app.extraction.rag_knowledge import build_rag_system_prompt


class InvoiceItemSchema(BaseModel):
    description: str = Field(description="Description of the item or service.")
    quantity: float = Field(default=1.0, description="Quantity of items, default 1.")
    unit_price: float = Field(default=0.0, description="Price per unit.")
    total_price: float = Field(description="Total price for this line item.")


class InvoiceOutputSchema(BaseModel):
    """
    Schema for structured extraction of financial documents from email text.
    Supports 4 document types with full IVA breakdown in EUR.
    """
    # Classificação
    document_type: str = Field(
        default="non_financial",
        description="Document type: accounts_payable | paid_bill | payment_receipt | non_financial"
    )
    is_valid_invoice: bool = Field(
        description="True if the text is a valid financial document with monetary values."
    )

    # Entidade
    vendor_name: str = Field(default="", description="Name of the company that issued the invoice.")
    invoice_number: Optional[str] = Field(None, description="The unique invoice or receipt number.")

    # Datas
    issue_date: Optional[str] = Field(None, description="Issue date in YYYY-MM-DD format.")
    due_date: Optional[str] = Field(None, description="Payment due date in YYYY-MM-DD format.")

    # Valores financeiros (sempre EUR)
    currency: str = Field(default="EUR", description="Currency, always EUR by default.")
    net_amount: float = Field(default=0.0, description="Amount before IVA/VAT (valor líquido).")
    iva_rate: float = Field(default=0.23, description="IVA rate applied (e.g. 0.23 for 23%).")
    iva_amount: float = Field(default=0.0, description="IVA/VAT amount (valor do IVA).")
    total_amount: float = Field(default=0.0, description="Grand total including IVA.")

    # Dados bancários e reconciliação
    iban: Optional[str] = Field(None, description="Payer IBAN (conta que emite).")
    iban_beneficiary: Optional[str] = Field(None, description="Beneficiary IBAN (conta que recebe).")
    swift: Optional[str] = Field(None, description="Bank SWIFT/BIC code.")
    payment_reference: Optional[str] = Field(None, description="Multibanco reference, MB WAY, or transfer description.")
    linked_invoice_number: Optional[str] = Field(
        None,
        description="Invoice number this payment receipt is paying (only for payment_receipt type)."
    )

    # Line items
    items: List[InvoiceItemSchema] = Field(default_factory=list, description="List of items/services.")


class LLMExtractorClient:
    """
    Orchestrates LLM-based extraction of financial documents from raw email text.
    Uses Llama3 (via Ollama) with a structured RAG prompt for Portuguese/EU documents.
    """
    def __init__(self, model_name: str = "llama3:latest", temperature: float = 0.0):
        self.settings = BaseAPIConfig.get_settings()
        self.api_key = self.settings.openai_api_key
        self.ollama_base_url = self.settings.ollama_base_url

        if self.ollama_base_url:
            print(f"Initializing LLMExtractor with Local Llama3 via Ollama at {self.ollama_base_url}")
            self.llm = ChatOllama(
                model=model_name,
                temperature=temperature,
                base_url=self.ollama_base_url,
                timeout=180
            )
        else:
            print(f"Initializing LLMExtractor with OpenAI fallback")
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=temperature,
                api_key=self.api_key,
                max_retries=3
            )

        self.parser = PydanticOutputParser(pydantic_object=InvoiceOutputSchema)

    def build_prompt(self, tenant_iva_rate: float = 0.23, currency: str = "EUR") -> ChatPromptTemplate:
        """
        Builds the RAG-injected ChatPromptTemplate with tenant-specific IVA rate.
        """
        system_prompt = build_rag_system_prompt(tenant_iva_rate=tenant_iva_rate, currency=currency)
        human_template = "Email content to analyze:\n\n{ocr_text}"
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_template)
        ])

    async def invoke_llm_chain(
        self,
        raw_text: str,
        tenant_iva_rate: float = 0.23,
        currency: str = "EUR",
        custom_prompt: Optional[ChatPromptTemplate] = None
    ) -> Optional[InvoiceOutputSchema]:
        """
        Runs the LCEL pipeline: Prompt | LLM | Parser
        Returns structured InvoiceOutputSchema or None on failure.
        """
        prompt = custom_prompt if custom_prompt else self.build_prompt(
            tenant_iva_rate=tenant_iva_rate,
            currency=currency
        )
        chain = prompt | self.llm | self.parser

        try:
            print(f"Sending text to AI Agent ({self.llm.__class__.__name__}) — IVA: {tenant_iva_rate*100:.1f}%")
            result: InvoiceOutputSchema = await chain.ainvoke({
                "ocr_text": raw_text,
                "format_instructions": self.parser.get_format_instructions()
            })

            # Post-processing: ensure net_amount and iva_amount are consistent
            if result.total_amount > 0 and result.iva_amount == 0.0:
                result.iva_amount = round(
                    result.total_amount * tenant_iva_rate / (1 + tenant_iva_rate), 2
                )
                result.net_amount = round(result.total_amount - result.iva_amount, 2)

            if result.net_amount > 0 and result.total_amount == 0.0:
                result.total_amount = round(result.net_amount * (1 + result.iva_rate), 2)
                result.iva_amount = round(result.total_amount - result.net_amount, 2)

            result.currency = currency
            return result

        except OutputParserException as e:
            print(f"LLM output parse error: {e}")
            return None
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return None
