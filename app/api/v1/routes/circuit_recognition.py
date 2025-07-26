from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from typing import Dict, Any
import logging
import time
from app.api.v1.dependencies import verify_api_key
from app.services.circuit_recognizer import CircuitRecognitionService
from app.api.v1.schemas.circuit import CircuitData, CircuitRecognitionResponse, ASCConversionResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/recognize-circuit", tags=["Circuit Recognition"])

# Initialize service
circuit_service = CircuitRecognitionService()

@router.post("", response_model=Dict[str, Any])
async def recognize_circuit(
    file: UploadFile = File(...),
    output_format: str = Form("asc"),
    api_key: str = Depends(verify_api_key)
):
    """
    Process an image of a hand-drawn circuit and generate an ASC or JSON file
    """
    logger.info("Received request to recognize circuit from image")
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG and PNG images are allowed."
        )
    
    # Validate output format
    if output_format not in ["asc", "json"]:
        logger.warning(f"Invalid output format: {output_format}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid output format. Use 'asc' or 'json'."
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
        logger.info(f"Processing circuit image with output format: {output_format}")
        start_time = time.time()
        result = circuit_service.process_image(file_content, output_format)
        processing_time = time.time() - start_time
        logger.info(f"Circuit recognition completed in {processing_time:.2f} seconds")
        
        if output_format == "json":
            return result["data"]
        else:
            # Return ASC content as plain text
            return {"content": result["data"]}
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

@router.post("/parse", response_model=CircuitRecognitionResponse)
async def recognize_and_parse(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Process an image and return structured circuit data
    """
    logger.info("Received request to recognize and parse circuit from image")
    
    # Validate file type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        logger.warning(f"Invalid file type: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPG and PNG images are allowed."
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
        logger.info("Processing circuit image for structured data")
        start_time = time.time()
        result = circuit_service.process_image(file_content, "json")
        processing_time = time.time() - start_time
        logger.info(f"Circuit recognition and parsing completed in {processing_time:.2f} seconds")
        
        return CircuitRecognitionResponse(
            circuit=CircuitData(**result["data"]),
            processing_time=result["processing_time"]
        )
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )