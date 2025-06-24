"""
Authentication utilities for payment providers.
"""
import os
import hashlib
from typing import Optional
from errors.exceptions import AuthenticationError


def generate_moka_key() -> str:
    """
    Generate authentication key for Moka United API.
    
    Returns:
        SHA256 hash of the concatenated credentials
        
    Raises:
        AuthenticationError: If required environment variables are missing
    """
    try:
        dealer_code = os.getenv('DEALER_CODE')
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        
        if not all([dealer_code, username, password]):
            missing = []
            if not dealer_code:
                missing.append('DEALER_CODE')
            if not username:
                missing.append('USERNAME')
            if not password:
                missing.append('PASSWORD')
            
            raise AuthenticationError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        key = f"{dealer_code}MK{username}PD{password}"
        return hashlib.sha256(key.encode()).hexdigest()
        
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Error generating authentication key: {str(e)}")


def get_dealer_customer_type_id() -> int:
    """
    Get dealer customer type ID from environment variables.
    
    Returns:
        Customer type ID, defaults to 2 if not set
    """
    try:
        return int(os.getenv("CUSTOMER_TYPE_ID", 2))
    except ValueError:
        return 2
