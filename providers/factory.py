"""
Provider factory for payment providers.
"""
from typing import Dict, Type, List
from core.interfaces import PaymentProvider
from errors.exceptions import ConfigurationError


class ProviderFactory:
    """Factory class for creating payment provider instances."""
    
    _providers: Dict[str, Type[PaymentProvider]] = {}
    
    @classmethod
    def _get_providers(cls) -> Dict[str, Type[PaymentProvider]]:
        """Lazy load providers to avoid circular imports."""
        if not cls._providers:
            # Import here to avoid circular imports
            from providers.moka.provider import MokaProvider
            cls._providers = {
                'moka': MokaProvider,
            }
        return cls._providers
    
    @classmethod
    def create_provider(cls, provider_name: str) -> PaymentProvider:
        """
        Create a payment provider instance.
        
        Args:
            provider_name: Name of the provider to create
            
        Returns:
            PaymentProvider instance
            
        Raises:
            ConfigurationError: If provider is not supported
        """
        provider_name = provider_name.lower()
        providers = cls._get_providers()
        
        if provider_name not in providers:
            available = ', '.join(providers.keys())
            raise ConfigurationError(
                f"Unsupported provider '{provider_name}'. Available providers: {available}"
            )
        
        provider_class = providers[provider_name]
        return provider_class()
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        providers = cls._get_providers()
        return list(providers.keys())
