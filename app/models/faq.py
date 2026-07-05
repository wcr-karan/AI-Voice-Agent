"""
Pydantic models for FAQ lookup.
"""

from pydantic import BaseModel, Field


class FAQRequest(BaseModel):
    """
    Request payload from Retell Function Node to look up an FAQ answer.
    """
    args: dict = Field(..., description="Function arguments from Retell")
    call_id: str = Field(..., description="Retell call ID")

    @property
    def question(self) -> str:
        return self.args.get("question", "")


class FAQEntry(BaseModel):
    """Represents a single FAQ entry from Google Sheets."""
    id: int = Field(..., description="FAQ entry ID")
    category: str = Field(default="", description="FAQ category (pricing, services, etc.)")
    question: str = Field(..., description="FAQ question text")
    answer: str = Field(..., description="FAQ answer text")
    keywords: list[str] = Field(default_factory=list, description="Search keywords")


class FAQResponse(BaseModel):
    """Response returned to Retell after FAQ lookup."""
    found: bool = Field(..., description="Whether a matching FAQ was found")
    answer: str = Field(default="", description="The answer text")
    category: str = Field(default="", description="FAQ category")
    message: str = Field(default="", description="Human-readable message for the agent to speak")
