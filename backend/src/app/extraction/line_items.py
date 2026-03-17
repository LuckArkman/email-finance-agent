from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

class LineItemSchema(BaseModel):
    """
    Schema for individual items extracted from invoice tables/grids.
    """
    id: int = Field(default=1, description="Sequential ID of the item.")
    description: str = Field(description="Detailed description or title of the product/service.")
    quantity: float = Field(default=1.0, description="Quantity of the item purchased.")
    unit_price: float = Field(default=0.0, description="Price per unit.")
    tax_rate: float = Field(default=0.0, description="Tax rate applied to this specific item (%) if any.")
    calculated_total: float = Field(default=0.0, description="The mathematical total line amount (quantity * unit_price).")

    @validator("calculated_total", pre=True, always=True)
    def validate_mathematical_sum(cls, v, values):
        """
        Garantia de fechamento de sum: Soma dos (ValorUnitário*Qtd) deve igualar ao total do item.
        This ensures LLMs don't hallucinate mathematical breakdowns.
        """
        qty = values.get('quantity', 1.0)
        u_price = values.get('unit_price', 0.0)
        
        # We auto-calculate if there's a discrepancy or missing value
        expected_total = round(qty * u_price, 2)
        
        # If the extracted total differs significantly from the math, we override it
        # to ensure financial integrity.
        if v == 0.0 or abs(v - expected_total) > 0.05:
            # We can log this internally here.
            return expected_total
            
        return v

class InvoiceTableSchema(BaseModel):
    items: List[LineItemSchema] = Field(description="The array of isolated line items purchased")

class LineItemExtractor:
    """
    Specialized service to isolate and extract tabular data (grids) from OCR texts
    using strict LangChain Prompts.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.parser = PydanticOutputParser(pydantic_object=InvoiceTableSchema)

    def build_table_prompt(self) -> ChatPromptTemplate:
        """
        Creates a specialized Prompt focusing on Parsing the Table layout para o LLM.
        """
        system_instructions = """
        You are an elite Table Parsing Financial AI.
        Your sole task is to extract the line items (the actual products or services sold) from the provided document OCR text.
        
        Rules:
        1. Find the table or grid describing the items.
        2. Extract EACH item as a separate JSON object in the array.
        3. Do NOT include shipping, global taxes, or headers in this list. ONLY the individual line items.
        
        {format_instructions}
        """

        human_template = "Invoice OCR Text:\n{ocr_text}"

        return ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", human_template)
        ])

    async def extract_line_items(self, ocr_text: str) -> List[LineItemSchema]:
        """
        Orchestrates the LLM extraction specifically targeting table layouts.
        """
        prompt = self.build_table_prompt()
        
        # Re-use the LLM core client
        llm = self.llm_client.llm
        
        chain = prompt | llm | self.parser
        
        try:
            print("Sending text for Table Grid extraction...")
            result: InvoiceTableSchema = await chain.ainvoke(
                {"ocr_text": ocr_text, "format_instructions": self.parser.get_format_instructions()}
            )
            return result.items
        except Exception as e:
            print(f"Failed to extract line items: {e}")
            return []
