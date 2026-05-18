from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.deps.db_session import SessionDep
from src.services.auth_service import AuthService

auth_router = APIRouter()

@auth_router.post("/login")
def login(
    db: SessionDep, 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return AuthService.login(
        db, 
        username=form_data.username, 
        password_plain=form_data.password
    )