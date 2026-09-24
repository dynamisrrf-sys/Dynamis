from typing import Any

from app.core.auth import CurrentUser
from app.core.exceptions import AppError
from app.database.supabase import gateway
from app.schemas.models import ClassificacaoCreate, DestinacaoCreate
from app.services.profile_service import get_my_profile


async def _require_establishment(user: CurrentUser) -> None:
    profile = await get_my_profile(user)
    if profile["tipo_perfil"] != "estabelecimento":
        raise AppError("Operação restrita a estabelecimentos.", 403, "forbidden")


async def create_classification(payload: ClassificacaoCreate, user: CurrentUser) -> dict[str, Any]:
    await _require_establishment(user)
    data = payload.model_dump(mode="json", exclude_none=True)
    data["status"] = "concluida"
    classification = await gateway.insert("classificacao", data, user.token)
    await gateway.update(
        "excedente", {"status": "classificado"}, user.token,
        id_excedente=f"eq.{payload.id_excedente}"
    )
    return classification


async def create_destination(payload: DestinacaoCreate, user: CurrentUser) -> dict[str, Any]:
    await _require_establishment(user)
    if payload.data_fim and payload.data_fim < payload.data_inicio:
        raise AppError("A data final não pode anteceder a inicial.", 422, "invalid_date_range")
    data = payload.model_dump(mode="json", exclude_none=True)
    data["status"] = "disponivel"
    destination = await gateway.insert("destinacao", data, user.token)
    classifications = await gateway.select(
        "classificacao", user.token, select="id_excedente",
        id_classificacao=f"eq.{payload.id_classificacao}", limit="1"
    )
    if classifications:
        await gateway.update(
            "excedente", {"status": "disponivel"}, user.token,
            id_excedente=f"eq.{classifications[0]['id_excedente']}"
        )
    return destination


async def list_destination_types(user: CurrentUser) -> list[dict[str, Any]]:
    return await gateway.select(
        "tipo_destinacao", user.token, select="*", status="eq.ativo", order="nome.asc"
    )
