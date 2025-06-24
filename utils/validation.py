"""
Validation utilities for payment data.
"""
from typing import Dict, Any
from errors.exceptions import ValidationError


def validate_amount(amount: float) -> None:
    """
    Validate payment amount.
    
    Args:
        amount: Payment amount to validate
        
    Raises:
        ValidationError: If amount is invalid
    """
    if amount <= 0:
        raise ValidationError("Payment amount must be greater than 0")



def validate_email(email: str) -> None:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Raises:
        ValidationError: If email format is invalid
    """
    if email and '@' not in email:
        raise ValidationError("Invalid email format")


def validate_gsm_number(gsm_number: str) -> None:
    """
    Validate GSM number format.
    
    Args:
        gsm_number: GSM number to validate
        
    Raises:
        ValidationError: If GSM number format is invalid
    """
    if gsm_number and not gsm_number.isdigit():
        raise ValidationError("GSM number must contain only digits")


def validate_payment_request(payment_data: Dict[str, Any]) -> None:
    """
    Validate complete payment request data.
    
    Args:
        payment_data: Payment request data to validate
        
    Raises:
        ValidationError: If any validation fails
    """
    # Validate required fields
    if 'amount' not in payment_data:
        raise ValidationError("Amount is required")
    
    validate_amount(payment_data['amount'])
    
    # Validate optional fields if present
    if payment_data.get('email'):
        validate_email(payment_data['email'])
    
    if payment_data.get('gsm_number'):
        validate_gsm_number(payment_data['gsm_number'])
    
    if payment_data.get('customer_email'):
        validate_email(payment_data['customer_email'])
    
    if payment_data.get('customer_gsm_number'):
        validate_gsm_number(payment_data['customer_gsm_number'])
