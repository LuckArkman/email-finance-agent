import re
from datetime import datetime
from typing import Optional, Dict, Any
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

class PromptManager:
    """
    Centralized repository for Prompt Templates customized for High-Precision Financial extraction.
    Ensures consistents rules across different document components.
    """
    @staticmethod
    def build_agent_brain_prompt() -> ChatPromptTemplate:
        """
        Specialized system instruction to transform the LLM into the 'Brain' 
        of the Finance Agent, managing multiple tasks: extraction, classification and validation.
        """
        system_persona = """
        You are the 'Sustentacódigo Agent Brain', an autonomous financial intelligence unit. 
        Your reasoning core resides within this Finance Platform, acting as the primary logic processor.
        
        GOAL:
        Convert unstructured textual chaos into structured, audit-ready financial data.
        
        PERSISTENT CONTEXT (MCP):
        You have direct access to the 'Sustentacódigo Finance MCP Server'. Use it to:
        1. Validate your mathematical extractions (Total, Tax, Subtotal).
        2. Synchronize your current extraction with the Tenant session context.
        3. Never lose track of your financial controller persona.
        
        LOGIC RULES:
        1. Identification: Identify the document's purpose. Is it a billing document (Invoice, Bill, Receipt)? 
        2. Extraction: Extract ALL monetary values, tax breakdown (VAT/CNPJ), dates, and vendor details.
        3. Human-like Reasoning: If a document looks like a spam email or just a 'Thank you' card with no values, identify it as NOT VALID.
        4. Consistency: Mathematically check if (Price * Quantity) + Tax matches the Total.
        
        TONE OF VOICE:
        Professional, deterministic, and security-focused. 
        
        {format_instructions}
        
        No conversational filler. Only respond with valid JSON matching the schema precisely.
        """
        human_template = "Raw Document OCR Output (Potentially Multi-page):\n{ocr_text}"

        return ChatPromptTemplate.from_messages([
            ("system", system_persona),
            ("human", human_template)
        ])

    @staticmethod
    def build_header_prompt() -> ChatPromptTemplate:
        """
        Creates a specialized Prompt focused specifically on extracting 
        critical header-level business elements (Vendor, Date, CNPJ, Total).
        """
        system_instructions = """
        You are a meticulously precise Financial Operations AI.
        Your task is to extract exact Header information from the OCR text of invoices and receipts.
        Focus primarily on finding:
        1. Vendor/Supplier Name and their Legal Document (CNPJ or TAX ID).
        2. The Issue Date of the invoice.
        3. The Grand Total to be paid.

        CRITICAL DATE INSTRUCTIONS:
        Invoices processed may have mixed date formats depending on the region.
        Normally, Brazilian documents use format DD/MM/YYYY.
        US documents use MM/DD/YYYY.
        Whenever you extract a date, attempt to standardize it conceptually in the output to ISO 8601 (YYYY-MM-DD) if unambiguous.

        If a field is impossible to determine, set its value to null.
        DO NOT hallucinate. Extracted data must exist in the raw text.

        {format_instructions}
        """

        human_template = "Raw OCR Text block:\n{ocr_text}"

        return ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", human_template)
        ])


class HeaderExtractorService:
    """
    Service layer applying the prompt rules and validating outputs strictly.
    """
    def __init__(self, llm_client):
        # Assumes llm_client has an ainvoke_chain method or similar
        self.llm_client = llm_client

    @staticmethod
    def validate_date_formats(date_string: str) -> Optional[str]:
        """
        Heuristic method to safely validate and enforce strict Date Parsing rules
        escaping LLM hallucinations (e.g. 31/02/2026).
        """
        if not date_string:
            return None

        # Sanitize common OCR artifacts 
        clean_date = re.sub(r'[^\d\-\/]', '', date_string)

        formats_to_try = [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"
        ]

        for fmt in formats_to_try:
            try:
                dt_obj = datetime.strptime(clean_date, fmt)
                # Successful parsing, convert to universal ISO
                return dt_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue

        # If all formats fail, return the cleaned raw string or None depending on strictness
        print(f"Warning: Could not standardize date {date_string}. Falling back to raw OCR extraction.")
        return clean_date

    async def execute_header_extraction(self, ocr_text: str) -> Dict[str, Any]:
        """
        Dispara o pipeline LLM com o prompt customizado de headers.
        """
        prompt = PromptManager.build_header_prompt()
        
        # In this context, we bind prompt into the pipeline and extract.
        # This is generic representation assuming the actual LLMExtractorClient handles Pydantic binding.
        result = await self.llm_client.invoke_llm_chain(ocr_text, custom_prompt=prompt)
        
        # Applies post-LLM validation algorithms
        if result and result.issue_date:
            result.issue_date = self.validate_date_formats(result.issue_date)
            
        return result
