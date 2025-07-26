from fastapi import Header, HTTPException, status
from app.core.config import settings
from app.models.api_key import validate_api_key

async def verify_api_key(x_api_key: str = Header(...)):
    """
    Dependency to verify API key in request headers
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "API Key"},
        )
    
    if not validate_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "API Key"},
        )
    
    return x_api_key