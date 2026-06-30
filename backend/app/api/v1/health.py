from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Check API health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

