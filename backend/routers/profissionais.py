"""
É FESTA — Router de Profissionais
Arquivo: backend/routers/profissionais.py
CRUD, busca por categoria/cidade, geolocalização, upload de fotos
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List
import os, shutil, uuid
from math import radians, cos, sin, asin, sqrt

from database import get_db
from models.models import (
    Profissional, Usuario, Avaliacao, AnuncioDestaque,
    TipoUsuario, StatusConta, StatusPagamento, CategoriaServico
)
from services.auth_service import obter_usuario_atual
from config import settings

router = APIRouter()


# ── CADASTRAR PROFISSIONAL ────────────────────────────────────────────────────
@router.post("/", status_code=201)
async def cadastrar_profissional(
    dados: dict,
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Cria perfil de profissional/empresa para o usuário logado."""
    # Verificar se já tem perfil
    existente = db.query(Profissional).filter(
        Profissional.usuario_id == usuario.id
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Você já possui um perfil profissional.")

    prof = Profissional(
        usuario_id=usuario.id,
        nome_negocio=dados["nome_negocio"],
        cnpj_cpf=dados.get("cnpj_cpf"),
        categoria=dados["categoria"],
        descricao=dados.get("descricao"),
        whatsapp=dados.get("whatsapp"),
        telefone=dados.get("telefone"),
        email_comercial=dados.get("email_comercial", usuario.email),
        website=dados.get("website"),
        instagram=dados.get("instagram"),
        cep=dados.get("cep"),
        logradouro=dados.get("logradouro"),
        numero=dados.get("numero"),
        bairro=dados.get("bairro"),
        cidade=dados.get("cidade"),
        estado=dados.get("estado"),
        latitude=dados.get("latitude"),
        longitude=dados.get("longitude"),
        preco_minimo=dados.get("preco_minimo"),
        preco_maximo=dados.get("preco_maximo"),
        preco_descricao=dados.get("preco_descricao"),
        atende_brasil=dados.get("atende_brasil", False),
        status=StatusConta.pendente,
    )
    db.add(prof)

    # Atualizar tipo do usuário
    usuario.tipo = TipoUsuario.profissional
    db.commit()
    db.refresh(prof)

    return {"id": prof.id, "mensagem": "Perfil criado! Aguarde aprovação em até 24h."}


# ── BUSCA DE PROFISSIONAIS ────────────────────────────────────────────────────
@router.get("/buscar")
async def buscar_profissionais(
    q: Optional[str] = Query(None, description="Termo de busca"),
    categoria: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    nota_minima: Optional[float] = Query(None, ge=1, le=5),
    preco_max: Optional[float] = Query(None),
    destaque: Optional[bool] = Query(None),
    verificado: Optional[bool] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    raio_km: Optional[float] = Query(50),
    ordenar: Optional[str] = Query("relevancia"),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Busca avançada de profissionais com filtros múltiplos.
    Suporta busca por proximidade geográfica (lat/lng + raio_km).
    """
    query = db.query(Profissional).filter(Profissional.status == StatusConta.ativo)

    # Filtro por texto (nome ou descrição)
    if q:
        query = query.filter(
            or_(
                Profissional.nome_negocio.ilike(f"%{q}%"),
                Profissional.descricao.ilike(f"%{q}%"),
            )
        )

    if categoria:
        query = query.filter(Profissional.categoria == categoria)

    if cidade:
        query = query.filter(Profissional.cidade.ilike(f"%{cidade}%"))

    if estado:
        query = query.filter(Profissional.estado == estado.upper())

    if nota_minima:
        query = query.filter(Profissional.media_avaliacao >= nota_minima)

    if preco_max:
        query = query.filter(
            or_(Profissional.preco_minimo <= preco_max, Profissional.preco_minimo.is_(None))
        )

    if destaque is True:
        query = query.filter(Profissional.destaque_ativo == True)

    if verificado is True:
        query = query.filter(Profissional.verificado == True)

    # Total antes da paginação
    total = query.count()
    profissionais = query.all()

    # Filtro por distância (haversine)
    if lat and lng:
        def distancia_km(p):
            if p.latitude is None or p.longitude is None:
                return float("inf")
            R = 6371
            dlat = radians(p.latitude - lat)
            dlon = radians(p.longitude - lng)
            a = sin(dlat/2)**2 + cos(radians(lat)) * cos(radians(p.latitude)) * sin(dlon/2)**2
            return 2 * R * asin(sqrt(a))

        profissionais = [p for p in profissionais if distancia_km(p) <= raio_km]
        total = len(profissionais)

        if ordenar == "distancia":
            profissionais.sort(key=distancia_km)

    # Ordenação
    if ordenar == "avaliacao":
        profissionais.sort(key=lambda p: p.media_avaliacao, reverse=True)
    elif ordenar == "destaque":
        profissionais.sort(key=lambda p: p.destaque_ativo, reverse=True)
    elif ordenar == "preco_asc":
        profissionais.sort(key=lambda p: p.preco_minimo or 0)
    elif ordenar == "preco_desc":
        profissionais.sort(key=lambda p: p.preco_minimo or 0, reverse=True)

    # Paginação manual (necessária por causa do filtro de distância)
    inicio = (pagina - 1) * por_pagina
    fim = inicio + por_pagina
    pagina_resultados = profissionais[inicio:fim]

    return {
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total_paginas": (total + por_pagina - 1) // por_pagina,
        "resultados": [_serializar_profissional(p) for p in pagina_resultados],
    }


# ── DESTAQUES DA HOMEPAGE ─────────────────────────────────────────────────────
@router.get("/destaques")
async def listar_destaques(db: Session = Depends(get_db)):
    """
    Retorna profissionais com anúncios em destaque ativos (para o carrossel).
    Cada card inclui link para o perfil do anunciante.
    """
    from datetime import datetime
    agora = datetime.utcnow()

    anuncios = (
        db.query(AnuncioDestaque)
        .filter(
            AnuncioDestaque.status == StatusPagamento.aprovado,
            AnuncioDestaque.inicio <= agora,
            AnuncioDestaque.fim >= agora,
        )
        .all()
    )

    resultados = []
    for anuncio in anuncios:
        prof = db.query(Profissional).get(anuncio.profissional_id)
        if prof and prof.status == StatusConta.ativo:
            # Registrar impressão
            anuncio.impressoes = (anuncio.impressoes or 0) + 1
            db.commit()

            resultados.append({
                "anuncio_id": anuncio.id,
                "tipo": anuncio.tipo,
                "profissional_id": prof.id,
                "nome_negocio": prof.nome_negocio,
                "categoria": prof.categoria,
                "foto_principal": prof.foto_principal,
                "cidade": prof.cidade,
                "estado": prof.estado,
                "media_avaliacao": prof.media_avaliacao,
                "total_avaliacoes": prof.total_avaliacoes,
                "preco_descricao": prof.preco_descricao,
                "verificado": prof.verificado,
                "link_perfil": f"/perfil/{prof.id}",
            })

    return resultados


# ── PERFIL PÚBLICO ────────────────────────────────────────────────────────────
@router.get("/{profissional_id}")
async def obter_perfil(
    profissional_id: int,
    db: Session = Depends(get_db)
):
    """Perfil público completo de um profissional."""
    prof = db.query(Profissional).get(profissional_id)
    if not prof or prof.status != StatusConta.ativo:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    # Registrar visualização
    prof.total_visualizacoes = (prof.total_visualizacoes or 0) + 1
    db.commit()

    avaliacoes = (
        db.query(Avaliacao)
        .filter(Avaliacao.profissional_id == profissional_id, Avaliacao.aprovada == True)
        .order_by(Avaliacao.criado_em.desc())
        .limit(20)
        .all()
    )

    from models.models import Servico
    servicos = (
        db.query(Servico)
        .filter(Servico.profissional_id == profissional_id, Servico.ativo == True)
        .all()
    )

    return {
        **_serializar_profissional(prof),
        "descricao": prof.descricao,
        "foto_2": prof.foto_2,
        "foto_3": prof.foto_3,
        "foto_4": prof.foto_4,
        "whatsapp": prof.whatsapp,
        "telefone": prof.telefone,
        "email_comercial": prof.email_comercial,
        "website": prof.website,
        "instagram": prof.instagram,
        "logradouro": prof.logradouro,
        "numero": prof.numero,
        "bairro": prof.bairro,
        "latitude": prof.latitude,
        "longitude": prof.longitude,
        "preco_minimo": prof.preco_minimo,
        "preco_maximo": prof.preco_maximo,
        "atende_brasil": prof.atende_brasil,
        "servicos": [
            {"nome": s.nome, "descricao": s.descricao, "preco": s.preco, "unidade": s.unidade}
            for s in servicos
        ],
        "avaliacoes": [
            {
                "nota": a.nota,
                "comentario": a.comentario,
                "tipo_evento": a.tipo_evento,
                "autor_nome": db.query(Usuario).get(a.autor_id).nome if a.autor_id else "Anônimo",
                "criado_em": a.criado_em,
            }
            for a in avaliacoes
        ],
    }


# ── REGISTRAR CLIQUE NO WHATSAPP ──────────────────────────────────────────────
@router.post("/{profissional_id}/clique-whatsapp")
async def registrar_clique_wp(profissional_id: int, db: Session = Depends(get_db)):
    prof = db.query(Profissional).get(profissional_id)
    if prof:
        prof.total_cliques_wp = (prof.total_cliques_wp or 0) + 1
        db.commit()
    return {"ok": True}


# ── UPLOAD DE FOTOS ───────────────────────────────────────────────────────────
@router.post("/{profissional_id}/fotos/{slot}")
async def upload_foto(
    profissional_id: int,
    slot: int,
    arquivo: UploadFile = File(...),
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    """Upload de foto (slot: 1=principal, 2, 3, 4)."""
    if slot not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Slot inválido (1-4).")

    prof = db.query(Profissional).filter(
        Profissional.id == profissional_id,
        Profissional.usuario_id == usuario.id
    ).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    # Validar tipo de arquivo
    if arquivo.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido. Use JPG, PNG ou WebP.")

    # Salvar arquivo
    ext = arquivo.filename.rsplit(".", 1)[-1]
    nome_arquivo = f"prof_{profissional_id}_slot{slot}_{uuid.uuid4().hex}.{ext}"
    caminho = os.path.join(settings.UPLOAD_DIR, "perfis", nome_arquivo)

    with open(caminho, "wb") as f:
        shutil.copyfileobj(arquivo.file, f)

    url = f"/uploads/perfis/{nome_arquivo}"

    # Salvar no campo correto
    campos = {1: "foto_principal", 2: "foto_2", 3: "foto_3", 4: "foto_4"}
    setattr(prof, campos[slot], url)
    db.commit()

    return {"url": url, "slot": slot}


# ── EDITAR PERFIL ─────────────────────────────────────────────────────────────
@router.put("/{profissional_id}")
async def editar_perfil(
    profissional_id: int,
    dados: dict,
    usuario=Depends(obter_usuario_atual),
    db: Session = Depends(get_db)
):
    prof = db.query(Profissional).filter(
        Profissional.id == profissional_id,
        Profissional.usuario_id == usuario.id
    ).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.")

    campos_editaveis = [
        "nome_negocio", "descricao", "whatsapp", "telefone", "email_comercial",
        "website", "instagram", "facebook", "cep", "logradouro", "numero",
        "bairro", "cidade", "estado", "latitude", "longitude",
        "preco_minimo", "preco_maximo", "preco_descricao", "atende_brasil"
    ]
    for campo in campos_editaveis:
        if campo in dados:
            setattr(prof, campo, dados[campo])

    db.commit()
    return {"mensagem": "Perfil atualizado com sucesso!"}


# ── HELPER: SERIALIZAR PROFISSIONAL ──────────────────────────────────────────
def _serializar_profissional(prof: Profissional) -> dict:
    return {
        "id": prof.id,
        "nome_negocio": prof.nome_negocio,
        "categoria": prof.categoria,
        "foto_principal": prof.foto_principal,
        "cidade": prof.cidade,
        "estado": prof.estado,
        "media_avaliacao": round(prof.media_avaliacao or 0, 1),
        "total_avaliacoes": prof.total_avaliacoes or 0,
        "total_visualizacoes": prof.total_visualizacoes or 0,
        "verificado": prof.verificado,
        "destaque_ativo": prof.destaque_ativo,
        "preco_descricao": prof.preco_descricao,
        "preco_minimo": prof.preco_minimo,
        "link_perfil": f"/perfil/{prof.id}",
    }
