"""
É FESTA — Router de Autenticação
Arquivo: backend/routers/auth.py
Funcionalidades: Login, Cadastro, Google OAuth, JWT, Refresh Token, Reset Senha
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import secrets
import httpx

from database import get_db
from models.models import Usuario, TokenResetSenha, TipoUsuario, StatusConta
from config import settings
from services.email_service import enviar_email_boas_vindas, enviar_email_reset_senha
from services.auth_service import (
    verificar_senha, hash_senha, criar_token_acesso,
    verificar_token, obter_usuario_atual
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── CADASTRO DE USUÁRIO ───────────────────────────────────────────────────────
@router.post("/cadastro", status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(
    dados: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cadastro rápido de usuário (gratuito):
    - nome_completo, email, telefone, senha
    """
    # Verificar se e-mail já existe
    existente = db.query(Usuario).filter(Usuario.email == dados["email"]).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado. Faça login ou use outro e-mail."
        )

    usuario = Usuario(
        nome=dados["nome_completo"],
        email=dados["email"],
        telefone=dados.get("telefone"),
        senha_hash=hash_senha(dados["senha"]),
        tipo=TipoUsuario.usuario,
        status=StatusConta.ativo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    # Enviar e-mail de boas-vindas em background
    background_tasks.add_task(enviar_email_boas_vindas, usuario.email, usuario.nome)

    token = criar_token_acesso({"sub": str(usuario.id), "tipo": usuario.tipo})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo,
        }
    }


# ── LOGIN ─────────────────────────────────────────────────────────────────────
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login com e-mail e senha."""
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not usuario or not verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if usuario.status == StatusConta.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta bloqueada. Entre em contato com o suporte."
        )

    # Atualizar último acesso
    usuario.ultimo_acesso = datetime.utcnow()
    db.commit()

    token = criar_token_acesso({"sub": str(usuario.id), "tipo": usuario.tipo})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo,
        }
    }


# ── GOOGLE OAUTH ──────────────────────────────────────────────────────────────
@router.post("/google")
async def login_google(
    dados: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Login/Cadastro via Google OAuth.
    Recebe o id_token do frontend e valida com a API do Google.
    """
    google_token = dados.get("credential")
    if not google_token:
        raise HTTPException(status_code=400, detail="Token Google inválido.")

    # Verificar token com Google
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Token Google inválido.")
        info = resp.json()

    google_id = info.get("sub")
    email     = info.get("email")
    nome      = info.get("name", email)
    foto      = info.get("picture")

    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Dados insuficientes do Google.")

    # Buscar ou criar usuário
    usuario = (
        db.query(Usuario).filter(Usuario.google_id == google_id).first()
        or db.query(Usuario).filter(Usuario.email == email).first()
    )

    novo = False
    if not usuario:
        usuario = Usuario(
            nome=nome,
            email=email,
            google_id=google_id,
            foto_perfil=foto,
            tipo=TipoUsuario.usuario,
            status=StatusConta.ativo,
            email_verificado=True,
        )
        db.add(usuario)
        novo = True
    else:
        if not usuario.google_id:
            usuario.google_id = google_id
        usuario.foto_perfil = foto

    usuario.ultimo_acesso = datetime.utcnow()
    db.commit()
    db.refresh(usuario)

    if novo:
        background_tasks.add_task(enviar_email_boas_vindas, usuario.email, usuario.nome)

    token = criar_token_acesso({"sub": str(usuario.id), "tipo": usuario.tipo})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "tipo": usuario.tipo,
        }
    }


# ── RECUPERAR SENHA ───────────────────────────────────────────────────────────
@router.post("/recuperar-senha")
async def recuperar_senha(
    dados: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Envia e-mail com link para redefinição de senha."""
    email = dados.get("email")
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    # Sempre retornar 200 para não vazar se e-mail existe ou não
    if usuario:
        token_str = secrets.token_urlsafe(32)
        token_obj = TokenResetSenha(
            usuario_id=usuario.id,
            token=token_str,
            expira_em=datetime.utcnow() + timedelta(hours=2)
        )
        db.add(token_obj)
        db.commit()

        link = f"{settings.APP_URL}/redefinir-senha?token={token_str}"
        background_tasks.add_task(
            enviar_email_reset_senha, usuario.email, usuario.nome, link
        )

    return {"mensagem": "Se o e-mail existir, você receberá instruções em breve."}


# ── REDEFINIR SENHA ───────────────────────────────────────────────────────────
@router.post("/redefinir-senha")
async def redefinir_senha(dados: dict, db: Session = Depends(get_db)):
    """Redefine a senha usando o token enviado por e-mail."""
    token_str = dados.get("token")
    nova_senha = dados.get("nova_senha")

    token_obj = (
        db.query(TokenResetSenha)
        .filter(TokenResetSenha.token == token_str, TokenResetSenha.usado == False)
        .first()
    )

    if not token_obj or token_obj.expira_em < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    usuario = db.query(Usuario).filter(Usuario.id == token_obj.usuario_id).first()
    usuario.senha_hash = hash_senha(nova_senha)
    token_obj.usado = True
    db.commit()

    return {"mensagem": "Senha redefinida com sucesso!"}


# ── PERFIL DO USUÁRIO LOGADO ──────────────────────────────────────────────────
@router.get("/me")
async def meu_perfil(usuario: Usuario = Depends(obter_usuario_atual)):
    """Retorna os dados do usuário autenticado."""
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": usuario.telefone,
        "tipo": usuario.tipo,
        "foto_perfil": usuario.foto_perfil,
        "criado_em": usuario.criado_em,
    }
