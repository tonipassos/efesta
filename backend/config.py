"""
É FESTA — Configurações da Aplicação
Arquivo: backend/config.py
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────────
    APP_NAME: str = "É Festa"
    APP_URL: str = "http://localhost:8000"
    DEBUG: bool = True
    SECRET_KEY: str = "TROQUE-POR-UMA-CHAVE-SECRETA-FORTE-EM-PRODUCAO"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 dias

    # ── Banco de Dados ────────────────────────────────────────────────────────
    # SQLite para desenvolvimento; troque para PostgreSQL em produção:
    # DATABASE_URL = "postgresql://usuario:senha@localhost/efesta"
    DATABASE_URL: str = "sqlite:///./efesta.db"

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://efesta.com.br",
        "https://www.efesta.com.br",
    ]

    # ── Mercado Pago ──────────────────────────────────────────────────────────
    MERCADO_PAGO_ACCESS_TOKEN: str = "APP_USR-1569466397106827-032216-916ad93d4198e7b64594030ab0701056-1318215042"
    MERCADO_PAGO_PUBLIC_KEY: str = "APP_USR-1569466397106827-032216-916ad93d4198e7b64594030ab0701056-1318215042"
    MERCADO_PAGO_WEBHOOK_SECRET: str = "seu-webhook-secret"

    # ── Google OAuth ──────────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = "seu-google-client-id.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "seu-google-client-secret"

    # ── E-mail (SMTP) ─────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@efesta.com.br"
    SMTP_PASSWORD: str = "sua-senha-smtp"
    SMTP_FROM: str = "É Festa <noreply@efesta.com.br>"

    # ── Upload de imagens ─────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_IMAGE_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # ── Planos e preços ───────────────────────────────────────────────────────
    PRECO_PLANO_PROFISSIONAL: float = 89.00
    PRECO_PLANO_PREMIUM: float = 159.00
    PRECO_DESTAQUE_SEMANAL: float = 49.00
    PRECO_DESTAQUE_QUINZENAL: float = 89.00
    PRECO_DESTAQUE_MENSAL: float = 149.00
    PRECO_BANNER_TOPO: float = 249.00

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Criar diretório de uploads se não existir
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/perfis", exist_ok=True)
os.makedirs(f"{settings.UPLOAD_DIR}/banners", exist_ok=True)
