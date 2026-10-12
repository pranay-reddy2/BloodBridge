from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Every field can be overridden by an environment variable
    of the same name (e.g. DATABASE_URL, LOW_STOCK_THRESHOLD)."""

    app_name: str = "BloodBridge API"
    # Injected at image build time with the Git commit SHA so every running pod
    # can be traced back to the exact commit that produced it.
    app_version: str = "dev"
    environment: str = "local"

    database_url: str = "postgresql+psycopg://bloodbridge:bloodbridge@localhost:5432/bloodbridge"
    db_pool_size: int = 5

    # Business rules
    donation_interval_days: int = 90  # minimum gap between two whole-blood donations
    low_stock_threshold: int = 5  # units per blood group below which we raise a low-stock flag
    expiring_soon_days: int = 7

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
