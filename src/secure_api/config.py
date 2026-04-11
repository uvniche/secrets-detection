from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load secrets from environment — never hardcode API keys in source."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Secure API Demo"
    # Example: set API_KEY in GitHub Secrets / deployment env, not in git
    api_key: str = ""


def get_settings() -> Settings:
    return Settings()
