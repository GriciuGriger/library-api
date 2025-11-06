from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional

class BookCreate(BaseModel):
    """Schema for creating a new book"""
    serial: str = Field(...,min_length=6, max_length=6, description="6-digit serial number")
    title: str = Field(..., min_length=1, description="Book_title")
    author: str = Field(..., min_length=1, description="Book_author")

    @field_validator("serial")
    @classmethod
    def validate_serial(cls, v):
        if not v.isdigit():
            raise ValueError("Serial must be a number")
        return v

class BookResponse(BaseModel):
    """Schema for book response"""
    serial: str 
    title: str
    author: str
    is_borrowed: bool
    borrowed_by: Optional[str] = None
    borrowed_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Allows conversion from SQLAlchemy model to Pydantic model

class LoanRequest(BaseModel):
    """Schema for loan operations (borrow/return)"""
    action: str = Field(..., description="Action: borrow or return")
    card_number: Optional[str] = Field(None, min_length=6, max_length=6, description="6-digit card number")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ["borrow", "return"]:
            raise ValueError("Action must be 'borrow' or 'return'")
        return v

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.isdigit():
            raise ValueError("Card number must contain only digits")
        if v and len(v) != 6:
            raise ValueError("Card number must be 6 digits")
        return v

    @model_validator(mode='after')
    def validate_card_number_required(self):
        """Validate that card_number is required for borrow action"""
        if self.action == "borrow" and not self.card_number:
            raise ValueError("Card number is required for borrow action")
        if self.action == "return" and self.card_number:
            raise ValueError("Card number is not allowed for return action")
        return self