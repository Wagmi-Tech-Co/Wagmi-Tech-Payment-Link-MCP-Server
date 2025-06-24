"""
Custom exceptions for the payment system.
"""


class PaymentError(Exception):
    """Base exception for payment-related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class PaymentProviderError(PaymentError):
    """Exception raised when payment provider encounters an error."""
    pass


class AuthenticationError(PaymentError):
    """Exception raised when authentication fails."""
    pass


class ValidationError(PaymentError):
    """Exception raised when input validation fails."""
    pass


class ConfigurationError(PaymentError):
    """Exception raised when configuration is invalid."""
    pass


class NetworkError(PaymentError):
    """Exception raised when network requests fail."""
    pass
