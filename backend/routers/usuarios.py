"""
É FESTA — Router de Usuários
Arquivo: backend/routers/usuarios.py
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.models import Usuario, Favorito, Profissional
from database import get_db
from services.auth_service import obter_usuario_atual

router = APIRouter()

@router.get("/perfil")
async def meu_perfil_usuario(usuario=Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    return {"id": usuario.id, "nome": usuario.nome, "email": usuario.email, "telefone": usuario.telefone, "cidade": usuario.cidade, "estado": usuario.estado, "criado_em": usuario.criado_em}

@router.put("/perfil")
async def atualizar_perfil(dados: dict, usuario=Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    for campo in ["nome", "telefone", "cidade", "estado"]:
        if campo in dados:
            setattr(usuario, campo, dados[campo])
    db.commit()
    return {"mensagem": "Perfil atualizado!"}

@router.post("/favoritos/{prof_id}")
async def favoritar(prof_id: int, usuario=Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    existente = db.query(Favorito).filter(Favorito.usuario_id == usuario.id, Favorito.profissional_id == prof_id).first()
    if existente:
        db.delete(existente)
        db.commit()
        return {"mensagem": "Removido dos favoritos.", "favoritado": False}
    fav = Favorito(usuario_id=usuario.id, profissional_id=prof_id)
    db.add(fav)
    db.commit()
    return {"mensagem": "Adicionado aos favoritos!", "favoritado": True}

@router.get("/favoritos")
async def listar_favoritos(usuario=Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    favs = db.query(Favorito).filter(Favorito.usuario_id == usuario.id).all()
    result = []
    for f in favs:
        p = db.query(Profissional).get(f.profissional_id)
        if p:
            result.append({"id": p.id, "nome_negocio": p.nome_negocio, "categoria": p.categoria, "foto_principal": p.foto_principal, "cidade": p.cidade, "media_avaliacao": p.media_avaliacao})
    return result
