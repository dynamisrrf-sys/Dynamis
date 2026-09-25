from fastapi import APIRouter

from app.core.auth import UserDependency
from app.services.profile_service import get_my_profile


router = APIRouter(prefix="/perfil", tags=["Perfil"])


@router.get("/me")
async def me(user: UserDependency):
    return await get_my_profile(user)
