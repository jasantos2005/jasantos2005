import os
from dotenv import load_dotenv

# Força a carga do .env usando o caminho absoluto
load_dotenv(dotenv_path="/opt/automacoes/GSG/gestao/diretoria/dashboards/app/.env")

class Settings:
    APP_NAME: str = "Iatch Axiom Enterprise"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "AXIOM_SUPER_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # DATABASE IXC (NEGÓCIO)
    DB_HOST: str = os.getenv("DB_HOST", "168.232.240.18")
    DB_USER: str = os.getenv("DB_USER", "leitura")
    DB_PASS: str = os.getenv("DB_PASS", "oxqEduwK6yMBioT5amEBRvmcsih8UTvu")
    DB_NAME: str = os.getenv("DB_NAME", "ixcprovedor")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))

    # DATABASE LOCAL (GOVERNANÇA)
    DB_LOCAL_PATH: str = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/core/axiom_auth.db"

settings = Settings()
