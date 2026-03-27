"""
É FESTA — Router de Avaliações
Arquivo: backend/routers/avaliacoes.py
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Avaliacao, Profissional
from database import get_db
from services.auth_service import obter_usuario_atual

router = APIRouter()

@router.post("/")
async def criar_avaliacao(dados: dict, usuario=Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    prof_id = dados.get("profissional_id")
    nota = dados.get("nota")
    if not (1 <= nota <= 5):
        raise HTTPException(status_code=400, detail="Nota deve ser entre 1 e 5.")
    existente = db.query(Avaliacao).filter(Avaliacao.profissional_id == prof_id, Avaliacao.autor_id == usuario.id).first()
    if existente:
        raise HTTPException(status_code=400, detail="Você já avaliou este profissional.")
    av = Avaliacao(profissional_id=prof_id, autor_id=usuario.id, nota=nota, comentario=dados.get("comentario"), tipo_evento=dados.get("tipo_evento"))
    db.add(av)
    prof = db.query(Profissional).get(prof_id)
    if prof:
        avaliacoes = db.query(Avaliacao).filter(Avaliacao.profissional_id == prof_id, Avaliacao.aprovada == True).all()
        total = len(avaliacoes) + 1
        soma = sum(a.nota for a in avaliacoes) + nota
        prof.media_avaliacao = round(soma / total, 2)
        prof.total_avaliacoes = total
    db.commit()
    return {"mensagem": "Avaliação enviada com sucesso! Obrigado pelo feedback."}
