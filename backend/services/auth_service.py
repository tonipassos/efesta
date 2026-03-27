"""
É FESTA — Serviço de Autenticação
Arquivo: backend/services/auth_service.py
JWT, hash de senha, dependências de autenticação
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def criar_token_acesso(dados: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = dados.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verificar_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def obter_usuario_atual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    from models.models import Usuario
    credencial_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado. Faça login para continuar.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verificar_token(token)
    if payload is None:
        raise credencial_exception

    usuario_id: str = payload.get("sub")
    if usuario_id is None:
        raise credencial_exception

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise credencial_exception
    return usuario


def exigir_admin(usuario=Depends(obter_usuario_atual)):
    from models.models import TipoUsuario
    if usuario.tipo != TipoUsuario.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores."
        )
    return usuario


def exigir_profissional(usuario=Depends(obter_usuario_atual)):
    from models.models import TipoUsuario
    if usuario.tipo not in [TipoUsuario.profissional, TipoUsuario.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a profissionais cadastrados."
        )
    return usuario
