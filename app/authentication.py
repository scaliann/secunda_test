from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

settings = get_settings()


api_key_header = APIKeyHeader(
    name="Authorization",
    description="Static API key for authentication",
    auto_error=False,
)


async def check_permission(
    api_key: str = Depends(api_key_header),
) -> bool:
    """Проверить наличие прав."""

    if not settings.api_key:
        return True

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return True
