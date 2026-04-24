"""Configuration management for Mermaid MCP Server."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    openai_api_key: str = ""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 3000
    debug: bool = False
    
    # LLM Settings
    llm_model: str = "gpt-4.1-mini"
    llm_max_tokens: int = 4000
    llm_temperature: float = 0.7
    max_retries: int = 3
    
    # Rendering
    default_theme: str = "default"
    default_background: str = "white"
    default_width: int = 1920
    default_height: int = 1080
    output_format: str = "png"
    
    # Paths
    diagrams_dir: Path = Path("diagrams")
    cache_dir: Path = Path(".cache")
    
    # Mermaid
    mermaid_live_base: str = "https://mermaid.live/edit#"
    mermaid_ink_base: str = "https://mermaid.ink/img/"
    
    # Timeout
    render_timeout: int = 30
    llm_timeout: int = 60
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
