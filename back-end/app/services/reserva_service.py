from datetime import datetime, timezone
from typing import Any

from app.core.auth import CurrentUser
from app.core.exceptions import AppError
from app.database.supabase import gateway
from app.schemas.models import CancelamentoReserva, ReservaCreate
from app.services.profile_service import get_my_profile


async def create(payload: ReservaCreate, user: CurrentUser) -> dict[str, Any]:
    profile = await get_my_profile(user)
    if profile["tipo_perfil"] != "consumidor":
        raise AppError("Somente consumidores podem realizar reservas.", 403, "forbidden")
    result = await gateway.rpc(
        "criar_reserva_atomica",
        {"p_destinacao_id": payload.id_destinacao, "p_quantidade": str(payload.quantidade)},
        user.token,
    )
    return result[0] if isinstance(result, list) and result else result


async def list_mine(user: CurrentUser) -> list[dict[str, Any]]:
    profile = await get_my_profile(user)
    if profile["tipo_perfil"] != "consumidor":
        return []
    select = (
        "*,consumidor_destinacao!inner(id_consumidor,id_destinacao,"
        "destinacao(local,data_inicio,horario_inicio,status,"
        "classificacao(excedente(nome,unidade_medida))))"
    )
    return await gateway.select(
        "reserva", user.token, select=select,
        **{"consumidor_destinacao.id_consumidor": f"eq.{profile['dados']['id_consumidor']}"},
        order="data_reserva.desc"
    )


async def cancel(reservation_id: int, payload: CancelamentoReserva, user: CurrentUser) -> dict[str, Any]:
    rows = await gateway.select(
        "reserva", user.token, select="id_reserva,status", id_reserva=f"eq.{reservation_id}", limit="1"
    )
    if not rows:
        raise AppError("Reserva não encontrada.", 404, "not_found")
    if rows[0]["status"] not in ("ativa", "confirmada"):
        raise AppError("Esta reserva não pode mais ser cancelada.", 409, "invalid_transition")
    return await gateway.update(
        "reserva",
        {
            "status": "cancelada",
            "motivo_cancelamento": payload.motivo,
            "data_cancelamento": datetime.now(timezone.utc).isoformat(),
        },
        user.token,
        id_reserva=f"eq.{reservation_id}",
    )
