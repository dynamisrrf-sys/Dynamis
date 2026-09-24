from datetime import date
from typing import Any

from app.core.auth import CurrentUser
from app.core.exceptions import AppError
from app.database.supabase import gateway
from app.schemas.models import ExcedenteCreate
from app.services.profile_service import get_my_profile


async def list_mine(user: CurrentUser) -> list[dict[str, Any]]:
    profile = await get_my_profile(user)
    if profile["tipo_perfil"] != "estabelecimento":
        raise AppError("Apenas estabelecimentos possuem excedentes próprios.", 403, "forbidden")
    establishment_id = profile["dados"]["id_estabelecimento"]
    return await gateway.select(
        "excedente", user.token, select="*", id_estabelecimento=f"eq.{establishment_id}",
        order="data_publicacao.desc"
    )


async def create(payload: ExcedenteCreate, user: CurrentUser) -> dict[str, Any]:
    profile = await get_my_profile(user)
    if profile["tipo_perfil"] != "estabelecimento":
        raise AppError("Somente estabelecimentos podem cadastrar excedentes.", 403, "forbidden")
    if payload.validade < date.today():
        raise AppError("A validade não pode estar no passado.", 422, "invalid_expiration")
    data = payload.model_dump(mode="json", exclude_none=True)
    data.update({
        "id_estabelecimento": profile["dados"]["id_estabelecimento"],
        "status": "aguardando_classificacao",
    })
    return await gateway.insert("excedente", data, user.token)


async def list_available(user: CurrentUser) -> list[dict[str, Any]]:
    result = await gateway.rpc("listar_excedentes_disponiveis", {}, user.token)
    return result or []
