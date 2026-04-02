from pydantic import BaseModel, field_validator
from typing import Optional


class ReviewRequest(BaseModel):
    code: str

    @field_validator("code")
    @classmethod
    def code_must_not_be_too_long(cls, v):
        if not v.strip():
            raise ValueError("Code cannot be empty.")
        if len(v) > 5000:
            raise ValueError("Code is too long. Max 5000 characters.")
        return v


class ReviewIssue(BaseModel):
    type: str
    severity: str
    description: str


class ReviewResponse(BaseModel):
    score: Optional[int] = None
    issues: list[ReviewIssue] = []
    suggestions: list[str] = []
    summary: Optional[str] = None
    error: Optional[str] = None

