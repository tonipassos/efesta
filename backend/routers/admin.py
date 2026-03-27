"""
É FESTA — Router Administrativo
Arquivo: backend/routers/admin.py
Controle total: usuários, profissionais, pagamentos, anúncios, denúncias
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from database import get_db
from models.models import (
    Usuario, Profissional, Pagamento, Assinatura, AnuncioDestaque,
    Avaliacao, Denuncia, StatusConta, StatusPagamento, TipoUsuario
)
from services.auth_service import exigir_admin

router = APIRouter()


# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@router.get("/dashboard")
async def dashboard(
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    """KPIs e métricas em tempo real para o painel administrativo."""
    hoje = datetime.utcnow().date()
    inicio_mes = datetime(hoje.year, hoje.month, 1)

    total_usuarios      = db.query(Usuario).filter(Usuario.tipo == TipoUsuario.usuario).count()
    total_profissionais = db.query(Profissional).filter(Profissional.status == StatusConta.ativo).count()
    pendentes_aprovacao = db.query(Profissional).filter(Profissional.status == StatusConta.pendente).count()
    denuncias_abertas   = db.query(Denuncia).filter(Denuncia.resolvida == False).count()

    receita_mes = (
        db.query(func.sum(Pagamento.valor))
        .filter(
            Pagamento.status == StatusPagamento.aprovado,
            Pagamento.pago_em >= inicio_mes
        )
        .scalar() or 0
    )

    assinaturas_ativas = (
        db.query(Assinatura)
        .filter(Assinatura.status == "ativa")
        .count()
    )

    anuncios_ativos = (
        db.query(AnuncioDestaque)
        .filter(
            AnuncioDestaque.status == StatusPagamento.aprovado,
            AnuncioDestaque.fim >= datetime.utcnow()
        )
        .count()
    )

    novos_usuarios_semana = (
        db.query(Usuario)
        .filter(Usuario.criado_em >= datetime.utcnow() - timedelta(days=7))
        .count()
    )

    return {
        "total_usuarios":       total_usuarios,
        "total_profissionais":  total_profissionais,
        "pendentes_aprovacao":  pendentes_aprovacao,
        "denuncias_abertas":    denuncias_abertas,
        "receita_mes":          round(float(receita_mes), 2),
        "assinaturas_ativas":   assinaturas_ativas,
        "anuncios_ativos":      anuncios_ativos,
        "novos_usuarios_semana": novos_usuarios_semana,
    }


# ── LISTAR USUÁRIOS ───────────────────────────────────────────────────────────
@router.get("/usuarios")
async def listar_usuarios(
    q: Optional[str] = None,
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Usuario)
    if q:
        query = query.filter(
            Usuario.nome.ilike(f"%{q}%") | Usuario.email.ilike(f"%{q}%")
        )
    if status:
        query = query.filter(Usuario.status == status)
    if tipo:
        query = query.filter(Usuario.tipo == tipo)

    total = query.count()
    usuarios = query.order_by(desc(Usuario.criado_em)).offset((pagina-1)*por_pagina).limit(por_pagina).all()

    return {
        "total": total,
        "pagina": pagina,
        "resultados": [
            {
                "id": u.id, "nome": u.nome, "email": u.email,
                "telefone": u.telefone, "tipo": u.tipo,
                "status": u.status, "criado_em": u.criado_em,
                "ultimo_acesso": u.ultimo_acesso,
            }
            for u in usuarios
        ]
    }


# ── BLOQUEAR / DESBLOQUEAR USUÁRIO ───────────────────────────────────────────
@router.patch("/usuarios/{usuario_id}/status")
async def alterar_status_usuario(
    usuario_id: int,
    dados: dict,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).get(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    usuario.status = dados.get("status", usuario.status)
    db.commit()
    return {"mensagem": f"Status atualizado para {usuario.status}"}


# ── LISTAR PROFISSIONAIS ──────────────────────────────────────────────────────
@router.get("/profissionais")
async def listar_profissionais(
    q: Optional[str] = None,
    status: Optional[str] = None,
    categoria: Optional[str] = None,
    pagina: int = 1,
    por_pagina: int = 20,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Profissional)
    if q:
        query = query.filter(Profissional.nome_negocio.ilike(f"%{q}%"))
    if status:
        query = query.filter(Profissional.status == status)
    if categoria:
        query = query.filter(Profissional.categoria == categoria)

    total = query.count()
    profs = query.order_by(desc(Profissional.criado_em)).offset((pagina-1)*por_pagina).limit(por_pagina).all()

    return {
        "total": total,
        "resultados": [
            {
                "id": p.id, "nome_negocio": p.nome_negocio,
                "categoria": p.categoria, "cidade": p.cidade,
                "estado": p.estado, "status": p.status,
                "verificado": p.verificado, "destaque_ativo": p.destaque_ativo,
                "media_avaliacao": p.media_avaliacao,
                "total_visualizacoes": p.total_visualizacoes,
                "criado_em": p.criado_em,
            }
            for p in profs
        ]
    }


# ── APROVAR / REJEITAR PROFISSIONAL ──────────────────────────────────────────
@router.patch("/profissionais/{prof_id}/aprovar")
async def aprovar_profissional(
    prof_id: int,
    dados: dict,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    prof = db.query(Profissional).get(prof_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    acao = dados.get("acao")  # "aprovar" ou "rejeitar"
    if acao == "aprovar":
        prof.status = StatusConta.ativo
        prof.verificado = dados.get("verificado", False)
    elif acao == "rejeitar":
        prof.status = StatusConta.bloqueado
    else:
        raise HTTPException(status_code=400, detail="Ação inválida.")

    db.commit()
    return {"mensagem": f"Profissional {acao}ado com sucesso."}


# ── EXTRATO FINANCEIRO ────────────────────────────────────────────────────────
@router.get("/financeiro")
async def extrato_financeiro(
    pagina: int = 1,
    por_pagina: int = 30,
    status: Optional[str] = None,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Pagamento)
    if status:
        query = query.filter(Pagamento.status == status)

    total = query.count()
    receita_total = (
        db.query(func.sum(Pagamento.valor))
        .filter(Pagamento.status == StatusPagamento.aprovado)
        .scalar() or 0
    )

    pagamentos = (
        query.order_by(desc(Pagamento.criado_em))
        .offset((pagina-1)*por_pagina)
        .limit(por_pagina)
        .all()
    )

    return {
        "total": total,
        "receita_total": round(float(receita_total), 2),
        "pagamentos": [
            {
                "id": p.id, "valor": p.valor, "descricao": p.descricao,
                "status": p.status, "metodo": p.metodo_pagamento,
                "criado_em": p.criado_em, "pago_em": p.pago_em,
                "profissional_id": p.profissional_id,
            }
            for p in pagamentos
        ]
    }


# ── DENÚNCIAS ─────────────────────────────────────────────────────────────────
@router.get("/denuncias")
async def listar_denuncias(
    resolvida: Optional[bool] = False,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    denuncias = (
        db.query(Denuncia)
        .filter(Denuncia.resolvida == resolvida)
        .order_by(desc(Denuncia.criado_em))
        .all()
    )
    return [
        {
            "id": d.id, "profissional_id": d.profissional_id,
            "denunciante_id": d.denunciante_id,
            "motivo": d.motivo, "descricao": d.descricao,
            "resolvida": d.resolvida, "criado_em": d.criado_em,
        }
        for d in denuncias
    ]


@router.patch("/denuncias/{denuncia_id}/resolver")
async def resolver_denuncia(
    denuncia_id: int,
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    d = db.query(Denuncia).get(denuncia_id)
    if not d:
        raise HTTPException(status_code=404)
    d.resolvida = True
    db.commit()
    return {"mensagem": "Denúncia marcada como resolvida."}


# ── ESTATÍSTICAS DE CATEGORIAS ────────────────────────────────────────────────
@router.get("/estatisticas/categorias")
async def stats_categorias(
    admin=Depends(exigir_admin),
    db: Session = Depends(get_db)
):
    resultado = (
        db.query(Profissional.categoria, func.count(Profissional.id).label("total"))
        .filter(Profissional.status == StatusConta.ativo)
        .group_by(Profissional.categoria)
        .order_by(desc("total"))
        .all()
    )
    return [{"categoria": r.categoria, "total": r.total} for r in resultado]
