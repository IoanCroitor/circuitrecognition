from fastapi import APIRouter, Depends
from typing import Dict
from app.api.v1.dependencies import verify_api_key

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", response_model=Dict[str, str])
async def health_check(api_key: str = Depends(verify_api_key)):
    """
    Check if the API is running
    """
    return {"status": "healthy"}