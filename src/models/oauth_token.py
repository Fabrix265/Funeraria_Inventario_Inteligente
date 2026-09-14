from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class OAuthToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    proveedor: str = Field(default="google_drive")
    access_token: str
    refresh_token: str
    token_expiry: Optional[datetime] = None
    usuario_id: Optional[int] = Field(default=None, foreign_key="user.id")
