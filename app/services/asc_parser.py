import os
import tempfile
import logging
from typing import Dict, Any
from asc_to_json_parser import ASCParser, convert_asc_to_json
from app.core.logging import get_logger

logger = get_logger(__name__)

class ASCParsingService:
    @staticmethod
    def parse_asc_file(file_content: bytes) -> Dict[str, Any]:
        """
        Parse ASC file content and return structured data
        
        Args:
            file_content (bytes): The ASC file content as bytes
            
        Returns:
            Dict[str, Any]: Parsed circuit data
            
        Raises:
            Exception: If there's an error processing the file
        """
        logger.info("Parsing ASC file")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".asc", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Parse the ASC file
            logger.debug(f"Parsing ASC file at {temp_file_path}")
            parser = ASCParser(temp_file_path)
            circuit_data = parser.parse()
            logger.info("ASC file parsed successfully")
            return circuit_data
        except Exception as e:
            logger.error(f"Error parsing ASC file: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Temporary file {temp_file_path} cleaned up")
    
    @staticmethod
    def convert_to_json(file_content: bytes) -> Dict[str, Any]:
        """
        Convert ASC file content to JSON format
        
        Args:
            file_content (bytes): The ASC file content as bytes
            
        Returns:
            Dict[str, Any]: Circuit data in JSON format
            
        Raises:
            Exception: If there's an error processing the file
        """
        logger.info("Converting ASC file to JSON")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".asc", delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Convert ASC to JSON
            logger.debug(f"Converting ASC file at {temp_file_path} to JSON")
            circuit_data = convert_asc_to_json(temp_file_path)
            logger.info("ASC file converted to JSON successfully")
            return circuit_data
        except Exception as e:
            logger.error(f"Error converting ASC file to JSON: {str(e)}")
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Temporary file {temp_file_path} cleaned up")