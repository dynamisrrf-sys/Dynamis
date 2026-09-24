from typing import Any

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.database.supabase import gateway
from app.schemas.models import LoginRequest, SignupRequest


PROFILE_TABLES = {
    "consumidor": "consumidor",
    "estabelecimento": "estabelecimento",
    "agente": "agente",
}


async def login(payload: LoginRequest) -> dict[str, Any]:
    data = await gateway.request(
        "POST",
        "/auth/v1/token",
        params={"grant_type": "password"},
        payload={"email": str(payload.email), "password": payload.password},
    )
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data.get("expires_in", 3600),
        "user": {"id": data["user"]["id"], "email": data["user"].get("email")},
    }


async def signup(payload: SignupRequest) -> dict[str, Any]:
    auth_data = await gateway.request(
        "POST",
        "/auth/v1/signup",
        payload={
            "email": str(payload.email),
            "password": payload.password,
            "data": {"display_name": payload.nome},
        },
    )
    user = auth_data.get("user") or {}
    if not user.get("id"):
        raise AppError("Não foi possível criar o usuário.", 502, "signup_failed")

    session_token = auth_data.get("access_token")
    settings = get_settings()
    elevated = not session_token and bool(settings.supabase_secret_key)
    if not session_token and not elevated:
        return {
            "requires_email_confirmation": True,
            "message": "Confirme seu e-mail. O perfil será concluído no primeiro acesso.",
            "user": {"id": user["id"], "email": user.get("email")},
        }

    profile = {
        "nome": payload.nome,
        "tipo": payload.tipo,
        "email": str(payload.email),
        "telefone": payload.telefone,
        "cidade": payload.cidade,
        "status": "ativo",
        "auth_user_id": user["id"],
    }
    if payload.tipo_perfil == "consumidor":
        profile["cpf"] = payload.documento
    else:
        profile["cnpj"] = payload.documento
        profile["responsavel"] = payload.responsavel or payload.nome

    await gateway.insert(
        PROFILE_TABLES[payload.tipo_perfil],
        {key: value for key, value in profile.items() if value is not None},
        session_token,
        elevated=elevated,
    )

    return {
        "requires_email_confirmation": not bool(session_token),
        "access_token": session_token,
        "refresh_token": auth_data.get("refresh_token"),
        "user": {"id": user["id"], "email": user.get("email")},
    }


async def refresh(refresh_token: str) -> dict[str, Any]:
    data = await gateway.request(
        "POST", "/auth/v1/token", params={"grant_type": "refresh_token"},
        payload={"refresh_token": refresh_token}
    )
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data.get("expires_in", 3600),
    }
