from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Dict, Any
import logging
from app.api.v1.dependencies import verify_api_key
from app.services.asc_parser import ASCParsingService
from app.api.v1.schemas.circuit import ASCConversionResponse, ASCParseResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/asc-to-json", tags=["ASC Parsing"])

@router.post("/convert", response_model=ASCParseResponse)
async def convert_asc_to_json(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Convert an LTspice ASC file to JSON format
    """
    logger.info("Received request to convert ASC file to JSON")
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_ASC_TYPES:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only ASC files are allowed."
        )
    
    # Check file size
    file_size = 0
    if file.size:
        file_size = file.size
    else:
        # If size is not available, we'll check after reading
        pass
    
    if file_size > settings.MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {settings.MAX_FILE_SIZE} bytes."
        )
    
    # Read file content
    try:
        file_content = await file.read()
        logger.debug(f"Read {len(file_content)} bytes from file")
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Check file size after reading if not already checked
    if not file.size and len(file_content) > settings.MAX_FILE_SIZE:
        logger.warning(f"File too large: {len(file_content)} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {settings.MAX_FILE_SIZE} bytes."
        )
    
    # Process file
    try:
        logger.info("Processing ASC file conversion")
        circuit_data = ASCParsingService.convert_to_json(file_content)
        logger.info("ASC file conversion completed successfully")
        return ASCParseResponse(**circuit_data)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@router.post("/parse", response_model=ASCParseResponse)
async def parse_asc_file(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Parse an ASC file and return structured data
    """
    logger.info("Received request to parse ASC file")
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_ASC_TYPES:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only ASC files are allowed."
        )
    
    # Check file size
    file_size = 0
    if file.size:
        file_size = file.size
    else:
        # If size is not available, we'll check after reading
        pass
    
    if file_size > settings.MAX_FILE_SIZE:
        logger.warning(f"File too large: {file_size} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {settings.MAX_FILE_SIZE} bytes."
        )
    
    # Read file content
    try:
        file_content = await file.read()
        logger.debug(f"Read {len(file_content)} bytes from file")
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Check file size after reading if not already checked
    if not file.size and len(file_content) > settings.MAX_FILE_SIZE:
        logger.warning(f"File too large: {len(file_content)} bytes")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds limit of {settings.MAX_FILE_SIZE} bytes."
        )
    
    # Process file
    try:
        logger.info("Processing ASC file parsing")
        circuit_data = ASCParsingService.parse_asc_file(file_content)
        logger.info("ASC file parsing completed successfully")
        return ASCParseResponse(**circuit_data)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )