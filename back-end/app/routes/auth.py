from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.models import LoginRequest, SignupRequest
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Autenticação"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(payload: LoginRequest):
    return await auth_service.login(payload)


@router.post("/cadastro", status_code=201)
async def signup(payload: SignupRequest):
    return await auth_service.signup(payload)


@router.post("/refresh")
async def refresh(payload: RefreshRequest):
    return await auth_service.refresh(payload.refresh_token)
