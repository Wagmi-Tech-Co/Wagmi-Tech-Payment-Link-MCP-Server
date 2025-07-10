"""
Moka United payment provider implementation.
"""
import os
import httpx
from typing import Dict, Any, Optional
from core.interfaces import PaymentProvider, ProviderCredentials
from providers.moka.constants import CREATE_USER_POS_PAYMENT
from utils.auth import generate_moka_key, get_dealer_customer_type_id
from utils.validation import validate_payment_request
from utils.logging import setup_logger
from errors.exceptions import PaymentProviderError, NetworkError, AuthenticationError


class MokaProvider(PaymentProvider):
    """Moka United payment provider implementation."""
    
    def __init__(self):
        self.logger = setup_logger(f"{__name__}.MokaProvider")
        self.logger.info("MokaProvider initialized")
    
    def get_provider_name(self) -> str:
        """Get the name of the payment provider."""
        return "moka"
    
    async def create_payment_link(
        self,
        amount: float,
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
        """Create a payment request with Moka United API."""
        
        try:
            # Validate input data
            payment_data = {
                'amount': amount,
                'email': email,
                'gsm_number': gsm_number,
                'customer_email': customer_email,
                'customer_gsm_number': customer_gsm_number
            }
            validate_payment_request(payment_data)
            
            # Generate authentication key
            auth_key = generate_moka_key(credentials)
            dealer_customer_type_id = get_dealer_customer_type_id(credentials)
            
            self.logger.info(f"Creating payment request for amount: {amount}")
            self.logger.debug(f"URL: {CREATE_USER_POS_PAYMENT}")
            self.logger.debug(f"Transaction code: {other_trx_code}")
            
            # Build request body
            body = self._build_request_body(
                auth_key=auth_key,
                dealer_customer_type_id=dealer_customer_type_id,
                credentials=credentials,
                amount=amount,
                other_trx_code=other_trx_code,
                full_name=full_name,
                gsm_number=gsm_number,
                email=email,
                currency=currency,
                installment_number=installment_number,
                is_pool_payment=is_pool_payment,
                is_pre_auth=is_pre_auth,
                is_tokenized=is_tokenized,
                is_three_d=is_three_d,
                redirect_url=redirect_url,
                description=description,
                customer_code=customer_code,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                customer_gsm_number=customer_gsm_number,
                customer_email=customer_email,
                address=address,
                set_installment_by=set_installment_by,
                commission_by_dealer=commission_by_dealer,
                is_commission_diff_by_dealer=is_commission_diff_by_dealer,
                buyer_full_name=buyer_full_name,
                buyer_email=buyer_email,
                buyer_gsm_number=buyer_gsm_number,
                buyer_address=buyer_address
            )
            
            # Make API request
            response = await self._make_request(body)
            
            self.logger.info("Payment request created successfully")
            return response
            
        except (AuthenticationError, NetworkError, PaymentProviderError) as e:
            self.logger.error(f"Payment creation failed: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in payment creation: {str(e)}")
            raise PaymentProviderError(f"Unexpected error: {str(e)}")
    
    def _build_request_body(self, auth_key: str, dealer_customer_type_id: int, credentials: Optional[ProviderCredentials] = None, **kwargs) -> Dict[str, Any]:
        """Build the request body for Moka United API."""
        
        if credentials:
            dealer_code = credentials.dealer_code
            username = credentials.username
            password = credentials.password
            dealer_customer_type_id = credentials.customer_type_id
        else:
            dealer_code = os.getenv("DEALER_CODE")
            username = os.getenv("USERNAME")
            password = os.getenv("PASSWORD")
        
        # Handle automatic field population from main fields
        full_name = kwargs.get('full_name', '')
        first_name = kwargs.get('first_name', '')
        last_name = kwargs.get('last_name', '')
        buyer_full_name = kwargs.get('buyer_full_name', '')
        
        gsm_number = kwargs.get('gsm_number', '')
        customer_gsm_number = kwargs.get('customer_gsm_number', '')
        buyer_gsm_number = kwargs.get('buyer_gsm_number', '')
        
        email = kwargs.get('email', '')
        customer_email = kwargs.get('customer_email', '')
        buyer_email = kwargs.get('buyer_email', '')
        
        # If FullName is provided but FirstName or LastName are empty, split FullName
        if full_name and (not first_name or not last_name):
            name_parts = full_name.strip().split(' ', 1)  # Split into max 2 parts
            if not first_name:
                first_name = name_parts[0] if name_parts else ''
                self.logger.debug(f"Auto-populated FirstName from FullName: '{first_name}'")
            if not last_name and len(name_parts) > 1:
                last_name = name_parts[1]
                self.logger.debug(f"Auto-populated LastName from FullName: '{last_name}'")
        
        # If FullName is provided but BuyerFullName is empty, use FullName
        if full_name and not buyer_full_name:
            buyer_full_name = full_name
            self.logger.debug(f"Auto-populated BuyerFullName from FullName: '{buyer_full_name}'")
        
        # If gsm_number is provided but customer_gsm_number or buyer_gsm_number are empty, use gsm_number
        if gsm_number:
            if not customer_gsm_number:
                customer_gsm_number = gsm_number
                self.logger.debug(f"Auto-populated CustomerGsmNumber from GsmNumber: '{customer_gsm_number}'")
            if not buyer_gsm_number:
                buyer_gsm_number = gsm_number
                self.logger.debug(f"Auto-populated BuyerGsmNumber from GsmNumber: '{buyer_gsm_number}'")
        
        # If email is provided but customer_email or buyer_email are empty, use email
        if email:
            if not customer_email:
                customer_email = email
                self.logger.debug(f"Auto-populated CustomerEmail from Email: '{customer_email}'")
            if not buyer_email:
                buyer_email = email
                self.logger.debug(f"Auto-populated BuyerEmail from Email: '{buyer_email}'")
        
        return {
            "DealerAuthentication": {
                "DealerCode": dealer_code,
                "Username": username,
                "Password": password,
                "CheckKey": auth_key
            },
            "PaymentUserPosRequest": {
                "OtherTrxCode": kwargs.get('other_trx_code', '1'),
                "DealerCustomerTypeId": str(dealer_customer_type_id),
                "FullName": full_name,
                "GsmNumber": gsm_number,
                "Email": email,
                "IsPreAuth": str(kwargs.get('is_pre_auth', 0)),
                "IsPoolPayment": str(kwargs.get('is_pool_payment', 0)),
                "IsTokenized": str(kwargs.get('is_tokenized', 0)),
                "DealerCustomerId": "",
                "CustomerCode": kwargs.get('customer_code', ''),
                "FirstName": first_name,
                "LastName": last_name,
                "Gender": "0",
                "BirthDate": kwargs.get('birth_date', ''),
                "CustomerGsmNumber": customer_gsm_number,
                "CustomerEmail": customer_email,
                "Address": kwargs.get('address', ''),
                "Amount": str(kwargs.get('amount')),
                "Currency": kwargs.get('currency', 'TL'),
                "InstallmentNumber": str(kwargs.get('installment_number', 0)),
                "SetInstallmentBy": str(kwargs.get('set_installment_by', 1)),
                "IsThreeD": str(kwargs.get('is_three_d', 1)),
                "Description": kwargs.get('description', ''),
                "RedirectUrl": kwargs.get('redirect_url', ''),
                "CommissionByDealer": kwargs.get('commission_by_dealer', '0'),
                "IsCommissionDiffByDealer": str(kwargs.get('is_commission_diff_by_dealer', 0)),
                "ReturnHash": 1,
                "BuyerInformation": {
                    "BuyerFullName": buyer_full_name,
                    "BuyerGsmNumber": buyer_gsm_number,
                    "BuyerEmail": buyer_email,
                    "BuyerAddress": kwargs.get('buyer_address', '')
                }
            }
        }
    
    async def _make_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to Moka United API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(CREATE_USER_POS_PAYMENT, json=body)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise PaymentProviderError(f"API error (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            raise PaymentProviderError(f"Request processing error: {str(e)}")
