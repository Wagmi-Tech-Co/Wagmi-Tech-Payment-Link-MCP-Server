"""
Moka United payment provider constants and configuration.
"""

BASE_URL = "https://service.mokaunited.com"
TEST_URL = "https://service.refmokaunited.com"
API_VERSION = "v1"

# Use test URL for now - can be made configurable
API_URL = BASE_URL
PAYMENT_USER_POS = f"{API_URL}/PaymentUserPos"
CREATE_USER_POS_PAYMENT = f"{PAYMENT_USER_POS}/CreateUserPosPayment"
