from fastapi import APIRouter

from app.core.auth import UserDependency
from app.schemas.models import ClassificacaoCreate, DestinacaoCreate
from app.services import fluxo_service


router = APIRouter(tags=["Fluxo do excedente"])


@router.post("/classificacoes", status_code=201)
async def classify(payload: ClassificacaoCreate, user: UserDependency):
    return await fluxo_service.create_classification(payload, user)


@router.post("/destinacoes", status_code=201)
async def destination(payload: DestinacaoCreate, user: UserDependency):
    return await fluxo_service.create_destination(payload, user)


@router.get("/tipos-destinacao")
async def destination_types(user: UserDependency):
    return await fluxo_service.list_destination_types(user)
