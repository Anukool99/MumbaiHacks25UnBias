from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArticleCreate(BaseModel):
    """Schema for creating a new article."""
    title: str = Field(..., min_length=1, max_length=255, description="Article title")
    content: str = Field(..., min_length=1, description="Article content")
    author: Optional[str] = Field(None, max_length=255, description="Article author")


class ArticleUpdate(BaseModel):
    """Schema for updating an article."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Article title")
    content: Optional[str] = Field(None, min_length=1, description="Article content")
    author: Optional[str] = Field(None, max_length=255, description="Article author")


class ArticleResponse(BaseModel):
    """Schema for article response."""
    id: UUID
    title: str
    content: str
    author: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

