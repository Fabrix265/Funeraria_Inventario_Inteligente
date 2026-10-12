from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class EmailChangeRequest(SQLModel, table=True):
    __tablename__ = "email_change_request"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False, index=True)
    email_anterior: str = Field(nullable=False, max_length=255)
    email_nuevo: str = Field(nullable=False, max_length=255)
    codigo_hash: str = Field(nullable=False, index=True)
    expira_en: datetime = Field(nullable=False)
    intentos: int = Field(default=0)
    usado_en: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
