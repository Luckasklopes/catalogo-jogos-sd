from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Microsserviço de Catálogo de Jogos"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    
    # Configurações de JWT
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_PUBLIC_KEY_PEM: str

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
