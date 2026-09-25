from typing import Any

from app.core.auth import CurrentUser
from app.database.supabase import gateway


PROFILE_TABLES = ("estabelecimento", "consumidor", "agente")


async def get_my_profile(user: CurrentUser) -> dict[str, Any]:
    for table in PROFILE_TABLES:
        rows = await gateway.select(
            table, user.token, select="*", auth_user_id=f"eq.{user.id}", limit="1"
        )
        if rows:
            return {"tipo_perfil": table, "dados": rows[0]}
    return {"tipo_perfil": None, "dados": None}
