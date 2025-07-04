"""
Authentication utilities for payment providers.
"""
import os
import hashlib
from typing import Optional
from errors.exceptions import AuthenticationError


def generate_moka_key(credentials: Optional['ProviderCredentials'] = None) -> str:
    """
    Generate authentication key for Moka United API.
    
    Args:
        credentials: Optional credentials to use instead of environment variables
    
    Returns:
        SHA256 hash of the concatenated credentials
        
    Raises:
        AuthenticationError: If required credentials are missing
    """
    try:
        if credentials:
            dealer_code = credentials.dealer_code
            username = credentials.username
            password = credentials.password
        else:
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
                f"Missing required credentials: {', '.join(missing)}"
            )
        
        key = f"{dealer_code}MK{username}PD{password}"
        return hashlib.sha256(key.encode()).hexdigest()
        
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError(f"Error generating authentication key: {str(e)}")


def get_dealer_customer_type_id(credentials: Optional['ProviderCredentials'] = None) -> int:
    """
    Get dealer customer type ID from credentials or environment variables.
    
    Args:
        credentials: Optional credentials to use instead of environment variables
    
    Returns:
        Customer type ID
        
    Raises:
        AuthenticationError: If customer type ID is missing or invalid
    """
    try:
        if credentials:
            if credentials.customer_type_id <= 0:
                raise AuthenticationError("Customer type ID must be provided and greater than 0")
            return credentials.customer_type_id
        
        env_value = os.getenv("CUSTOMER_TYPE_ID")
        if not env_value:
            raise AuthenticationError("CUSTOMER_TYPE_ID environment variable is required")
            
        customer_type_id = int(env_value)
        if customer_type_id <= 0:
            raise AuthenticationError("Customer type ID must be greater than 0")
            
        return customer_type_id
    except ValueError:
        raise AuthenticationError("Customer type ID must be a valid integer")
