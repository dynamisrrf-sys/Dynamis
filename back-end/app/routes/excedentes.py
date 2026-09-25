from fastapi import APIRouter

from app.core.auth import UserDependency
from app.schemas.models import ExcedenteCreate
from app.services import excedente_service


router = APIRouter(prefix="/excedentes", tags=["Excedentes"])


@router.get("/meus")
async def mine(user: UserDependency):
    return await excedente_service.list_mine(user)


@router.get("/disponiveis")
async def available(user: UserDependency):
    return await excedente_service.list_available(user)


@router.post("", status_code=201)
async def create(payload: ExcedenteCreate, user: UserDependency):
    return await excedente_service.create(payload, user)
