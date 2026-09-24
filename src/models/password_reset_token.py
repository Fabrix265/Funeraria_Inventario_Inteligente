from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class PasswordResetToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    token_hash: str = Field(nullable=False, unique=True, index=True)
    expira_en: datetime = Field(nullable=False)
    usado_en: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)