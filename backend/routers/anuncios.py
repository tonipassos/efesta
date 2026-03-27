"""
É FESTA — Router de Anúncios
Arquivo: backend/routers/anuncios.py
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.models import AnuncioDestaque, Profissional, StatusPagamento, StatusConta
from datetime import datetime

router = APIRouter()

@router.get("/ativos")
async def anuncios_ativos(db: Session = Depends(get_db)):
    agora = datetime.utcnow()
    anuncios = db.query(AnuncioDestaque).filter(
        AnuncioDestaque.status == StatusPagamento.aprovado,
        AnuncioDestaque.inicio <= agora,
        AnuncioDestaque.fim >= agora,
    ).all()
    resultado = []
    for a in anuncios:
        p = db.query(Profissional).filter(Profissional.id == a.profissional_id, Profissional.status == StatusConta.ativo).first()
        if p:
            a.impressoes = (a.impressoes or 0) + 1
            db.commit()
            resultado.append({
                "anuncio_id": a.id, "tipo": a.tipo,
                "profissional_id": p.id, "nome_negocio": p.nome_negocio,
                "categoria": p.categoria, "foto_principal": p.foto_principal,
                "cidade": p.cidade, "estado": p.estado,
                "media_avaliacao": p.media_avaliacao,
                "total_avaliacoes": p.total_avaliacoes,
                "verificado": p.verificado,
                "link_perfil": f"/perfil/{p.id}",
            })
    return resultado

@router.post("/{anuncio_id}/clique")
async def registrar_clique(anuncio_id: int, db: Session = Depends(get_db)):
    a = db.query(AnuncioDestaque).get(anuncio_id)
    if a:
        a.cliques = (a.cliques or 0) + 1
        db.commit()
    return {"ok": True}
