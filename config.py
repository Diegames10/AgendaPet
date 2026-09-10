import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # =====================================================
    # ARMAZENAMENTO DE ARQUIVOS
    # =====================================================

    STORAGE_PATH = os.getenv(
        "STORAGE_PATH",
        os.path.join(
            os.getcwd(),
            "storage"
        )
    )
    
    
    # =====================================================
    # OAUTH - GOOGLE
    # =====================================================

    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID"
    )

    GOOGLE_CLIENT_SECRET = os.getenv(
        "GOOGLE_CLIENT_SECRET"
    )


    # =====================================================
    # OAUTH - MICROSOFT
    # =====================================================

    MICROSOFT_CLIENT_ID = os.getenv(
        "MICROSOFT_CLIENT_ID"
    )

    MICROSOFT_CLIENT_SECRET = os.getenv(
        "MICROSOFT_CLIENT_SECRET"
    )
    
    # =====================================================
    # SESSÃO / REMEMBER ME
    # =====================================================

    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    
    # =====================================================
    # BREVO - EMAIL TRANSACIONAL
    # =====================================================

    BREVO_API_KEY = os.getenv(
        "BREVO_API_KEY"
    )

    BREVO_SENDER_EMAIL = os.getenv(
        "BREVO_SENDER_EMAIL"
    )

    BREVO_SENDER_NAME = os.getenv(
        "BREVO_SENDER_NAME",
        "AgendaPet Paranaguá"
    )