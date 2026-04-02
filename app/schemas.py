from pydantic import BaseModel
from typing import Optional


class ReviewRequest(BaseModel):
    code: str


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
