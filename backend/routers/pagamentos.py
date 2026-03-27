"""
É FESTA — Router de Pagamentos
Arquivo: backend/routers/pagamentos.py
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.models import (
    Pagamento, Assinatura, AnuncioDestaque,
    TipoPlano, TipoAnuncio, StatusPagamento, Profissional
)
from services.pagamento_service import (
    criar_preferencia_assinatura,
    criar_preferencia_anuncio,
    processar_webhook,
)
from services.auth_service import obter_usuario_atual, exigir_profissional
from config import settings

router = APIRouter()

# Mapeamento de preços
PRECOS_PLANOS = {
    "profissional": settings.PRECO_PLANO_PROFISSIONAL,
    "premium":      settings.PRECO_PLANO_PREMIUM,
}

PRECOS_ANUNCIOS = {
    "semanal":    settings.PRECO_DESTAQUE_SEMANAL,
    "quinzenal":  settings.PRECO_DESTAQUE_QUINZENAL,
    "mensal":     settings.PRECO_DESTAQUE_MENSAL,
    "banner_topo": settings.PRECO_BANNER_TOPO,
}


# ── CHECKOUT ASSINATURA ───────────────────────────────────────────────────────
@router.post("/assinar")
async def checkout_assinatura(
    dados: dict,
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """
    Inicia checkout de assinatura via Mercado Pago.
    Retorna init_point para redirecionar o profissional.
    """
    plano = dados.get("plano", "profissional")
    if plano not in PRECOS_PLANOS:
        raise HTTPException(status_code=400, detail="Plano inválido.")

    profissional = (
        db.query(Profissional)
        .filter(Profissional.usuario_id == usuario.id)
        .first()
    )
    if not profissional:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado.")

    preco = PRECOS_PLANOS[plano]

    # Criar preferência no MP
    preferencia = criar_preferencia_assinatura(
        profissional_id=profissional.id,
        plano=plano,
        preco=preco,
        email_payer=usuario.email,
    )

    # Registrar assinatura pendente
    assinatura = Assinatura(
        profissional_id=profissional.id,
        plano=plano,
        preco=preco,
        inicio=datetime.utcnow(),
        mp_preference_id=preferencia["preference_id"],
    )
    db.add(assinatura)
    db.flush()

    # Registrar pagamento pendente
    pagamento = Pagamento(
        profissional_id=profissional.id,
        assinatura_id=assinatura.id,
        valor=preco,
        descricao=f"Assinatura plano {plano}",
        mp_preference_id=preferencia["preference_id"],
    )
    db.add(pagamento)
    db.commit()

    return {
        "init_point": preferencia["init_point"],
        "sandbox_init_point": preferencia.get("sandbox_init_point"),
        "preference_id": preferencia["preference_id"],
        "preco": preco,
        "plano": plano,
    }


# ── CHECKOUT ANÚNCIO DESTAQUE ─────────────────────────────────────────────────
@router.post("/anuncio-destaque")
async def checkout_anuncio(
    dados: dict,
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Inicia checkout para anúncio em destaque."""
    tipo = dados.get("tipo", "mensal")
    if tipo not in PRECOS_ANUNCIOS:
        raise HTTPException(status_code=400, detail="Tipo de anúncio inválido.")

    profissional = (
        db.query(Profissional)
        .filter(Profissional.usuario_id == usuario.id)
        .first()
    )
    if not profissional:
        raise HTTPException(status_code=404, detail="Perfil profissional não encontrado.")

    preco = PRECOS_ANUNCIOS[tipo]

    preferencia = criar_preferencia_anuncio(
        profissional_id=profissional.id,
        tipo_anuncio=tipo,
        preco=preco,
        email_payer=usuario.email,
    )

    # Criar anúncio pendente
    anuncio = AnuncioDestaque(
        profissional_id=profissional.id,
        tipo=tipo,
        preco_pago=preco,
        status=StatusPagamento.pendente,
    )
    db.add(anuncio)
    db.flush()

    pagamento = Pagamento(
        profissional_id=profissional.id,
        anuncio_id=anuncio.id,
        valor=preco,
        descricao=f"Anúncio destaque {tipo}",
        mp_preference_id=preferencia["preference_id"],
    )
    db.add(pagamento)
    db.commit()

    return {
        "init_point": preferencia["init_point"],
        "sandbox_init_point": preferencia.get("sandbox_init_point"),
        "preco": preco,
        "tipo": tipo,
    }


# ── WEBHOOK MERCADO PAGO ──────────────────────────────────────────────────────
@router.post("/webhook")
async def webhook_mercado_pago(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recebe notificações IPN/Webhook do Mercado Pago.
    Atualiza status de pagamentos e assinaturas.
    """
    dados = await request.json()
    background_tasks.add_task(processar_webhook, dados, db)
    return {"status": "received"}


# ── HISTÓRICO DE PAGAMENTOS ───────────────────────────────────────────────────
@router.get("/historico")
async def historico_pagamentos(
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Histórico de pagamentos do profissional logado."""
    profissional = (
        db.query(Profissional)
        .filter(Profissional.usuario_id == usuario.id)
        .first()
    )
    if not profissional:
        return []

    pagamentos = (
        db.query(Pagamento)
        .filter(Pagamento.profissional_id == profissional.id)
        .order_by(Pagamento.criado_em.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": p.id,
            "valor": p.valor,
            "descricao": p.descricao,
            "status": p.status,
            "metodo": p.metodo_pagamento,
            "criado_em": p.criado_em,
            "pago_em": p.pago_em,
        }
        for p in pagamentos
    ]


# ── CANCELAR ASSINATURA ───────────────────────────────────────────────────────
@router.post("/cancelar-assinatura")
async def cancelar_assinatura(
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Cancela a assinatura ativa do profissional."""
    from models.models import StatusAssinatura
    profissional = (
        db.query(Profissional)
        .filter(Profissional.usuario_id == usuario.id)
        .first()
    )
    if not profissional:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    assinatura = (
        db.query(Assinatura)
        .filter(
            Assinatura.profissional_id == profissional.id,
            Assinatura.status == StatusAssinatura.ativa
        )
        .order_by(Assinatura.criado_em.desc())
        .first()
    )

    if not assinatura:
        raise HTTPException(status_code=404, detail="Nenhuma assinatura ativa encontrada.")

    assinatura.status = StatusAssinatura.cancelada
    assinatura.cancelado_em = datetime.utcnow()
    db.commit()

    return {"mensagem": "Assinatura cancelada. Seu perfil permanece ativo até o fim do período pago."}
