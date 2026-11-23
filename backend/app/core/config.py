from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


    # ZaloPay
    zalopay_appid: int
    zalopay_key1: str
    zalopay_key2: str
    zalopay_endpoint: str
    zalopay_redirect_url: str


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()