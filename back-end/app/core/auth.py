from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AppError
from app.database.supabase import gateway


bearer = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class CurrentUser:
    id: str
    email: str
    token: str


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError("Autenticação necessária.", 401, "authentication_required")
    user = await gateway.get_user(credentials.credentials)
    return CurrentUser(id=user["id"], email=user.get("email", ""), token=credentials.credentials)


UserDependency = Annotated[CurrentUser, Depends(get_current_user)]
