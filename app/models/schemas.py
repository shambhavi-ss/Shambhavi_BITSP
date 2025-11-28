from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel, Field, validator


class DocumentRequest(BaseModel):
    """Incoming payload describing where to fetch the document from."""

    document: AnyHttpUrl = Field(..., description="Publicly accessible URL of the bill document")


class BillItem(BaseModel):
    item_name: str = Field(..., description="Name or description of the line item")
    item_amount: Decimal = Field(..., description="Extended amount for the line item")
    item_rate: Optional[Decimal] = Field(None, description="Unit rate if available")
    item_quantity: Optional[Decimal] = Field(None, description="Quantity if available")

    @validator("item_amount", "item_rate", "item_quantity", pre=True)
    def coerce_decimal(cls, value: Optional[float | str | Decimal]) -> Optional[Decimal]:
        if value is None or value == "":
            return None
        return Decimal(str(value))


class PageLineItems(BaseModel):
    page_no: str = Field(..., description="Page number (1-indexed)")
    page_type: Optional[str] = Field(
        None, description="Bill Detail | Final Bill | Pharmacy or other source label"
    )
    bill_items: List[BillItem] = Field(default_factory=list)


class ExtractionData(BaseModel):
    pagewise_line_items: List[PageLineItems] = Field(default_factory=list)
    total_item_count: int


class TokenUsage(BaseModel):
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class ExtractionResponse(BaseModel):
    is_success: bool
    token_usage: Optional[TokenUsage] = None
    data: Optional[ExtractionData] = None
    message: Optional[str] = None


class LLMExtractionRequest(BaseModel):
    page_number: int
    ocr_text: str


class LLMItemSchema(BaseModel):
    item_name: str
    item_amount: Optional[Decimal] = None
    item_rate: Optional[Decimal] = None
    item_quantity: Optional[Decimal] = None
    
    @validator("item_amount", "item_rate", "item_quantity", pre=True)
    def coerce_decimal(cls, value: Optional[float | str | Decimal]) -> Optional[Decimal]:
        if value is None or value == "":
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None


class LLMPageExtraction(BaseModel):
    page_no: int
    page_type: Optional[str] = None
    items: List[LLMItemSchema]



