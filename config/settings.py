"""
Configuration management for the payment system.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from errors.exceptions import ConfigurationError


@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8050
    name: str = "Payment MCP"


@dataclass 
class MokaConfig:
    """Moka United API configuration."""
    dealer_code: str
    username: str
    password: str
    customer_type_id: int = 2
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not all([self.dealer_code, self.username, self.password]):
            raise ConfigurationError("Missing required Moka configuration")


class ConfigManager:
    """Central configuration manager."""
    
    def __init__(self):
        self._server_config: Optional[ServerConfig] = None
        self._moka_config: Optional[MokaConfig] = None
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        if self._server_config is None:
            self._server_config = ServerConfig()
        return self._server_config
    
    def get_moka_config(self) -> MokaConfig:
        """Get Moka configuration from environment variables."""
        if self._moka_config is None:
            try:
                self._moka_config = MokaConfig(
                    dealer_code=os.getenv('DEALER_CODE', ''),
                    username=os.getenv('USERNAME', ''),
                    password=os.getenv('PASSWORD', ''),
                    customer_type_id=int(os.getenv('CUSTOMER_TYPE_ID', '2'))
                )
            except ValueError as e:
                raise ConfigurationError(f"Invalid configuration value: {str(e)}")
        
        return self._moka_config
    
    def set_config_from_env(self, env_vars: Dict[str, str]) -> None:
        """Set configuration from environment variables."""
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # Reset cached configs to force reload
        self._moka_config = None
    
    def validate_config(self) -> None:
        """Validate all configurations."""
        try:
            self.get_moka_config()
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")


# Global config manager instance
config_manager = ConfigManager()
