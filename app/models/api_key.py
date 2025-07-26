import hashlib
import os
from typing import Optional

# In a real application, this would be stored in a database
# For this implementation, we'll use a simple in-memory store
API_KEYS = {
    "test-key-123": {"user": "test-user", "permissions": ["read", "write"]},
    "admin-key-456": {"user": "admin", "permissions": ["read", "write", "admin"]}
}

def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for secure storage
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def validate_api_key(api_key: str) -> bool:
    """
    Validate an API key against the stored keys
    
    Args:
        api_key (str): The API key to validate
        
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    # In a real application, this would check against a database
    # For this implementation, we'll check against our in-memory store
    return api_key in API_KEYS

def get_api_key_info(api_key: str) -> Optional[dict]:
    """
    Get information about an API key
    
    Args:
        api_key (str): The API key to look up
        
    Returns:
        dict: Information about the API key, or None if not found
    """
    return API_KEYS.get(api_key)

def generate_api_key() -> str:
    """
    Generate a new API key
    
    Returns:
        str: A new API key
    """
    return os.urandom(32).hex()