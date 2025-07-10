"""
Core interfaces for the payment system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ProviderCredentials:
    """Credentials for payment provider."""
    dealer_code: str
    username: str
    password: str
    customer_type_id: int


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    @abstractmethod
    async def create_payment_link(
        self,
        amount: float,
        # Credentials for per-request authentication
        credentials: Optional[ProviderCredentials] = None,
        other_trx_code: str = "1",
        full_name: str = "",
        gsm_number: str = "",
        email: str = "",
        currency: str = "TL",
        installment_number: int = 0,
        is_pool_payment: int = 0,
        is_pre_auth: int = 0,
        is_tokenized: int = 0,
        is_three_d: int = 1,
        redirect_url: str = "",
        description: str = "",
        customer_code: str = "",
        first_name: str = "",
        last_name: str = "",
        birth_date: str = "",
        customer_gsm_number: str = "",
        customer_email: str = "",
        address: str = "",
        set_installment_by: int = 1,
        commission_by_dealer: str = "0",
        is_commission_diff_by_dealer: int = 0,
        buyer_full_name: str = "",
        buyer_email: str = "",
        buyer_gsm_number: str = "",
        buyer_address: str = ""
    ) -> Dict[str, Any]:
        """Create a payment request."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the payment provider."""
        pass
