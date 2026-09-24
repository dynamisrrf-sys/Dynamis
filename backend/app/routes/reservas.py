from fastapi import APIRouter

from app.core.auth import UserDependency
from app.schemas.models import CancelamentoReserva, ReservaCreate
from app.services import reserva_service


router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.get("")
async def mine(user: UserDependency):
    return await reserva_service.list_mine(user)


@router.post("", status_code=201)
async def create(payload: ReservaCreate, user: UserDependency):
    return await reserva_service.create(payload, user)


@router.patch("/{reservation_id}/cancelar")
async def cancel(reservation_id: int, payload: CancelamentoReserva, user: UserDependency):
    return await reserva_service.cancel(reservation_id, payload, user)
