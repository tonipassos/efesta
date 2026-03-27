"""
É FESTA — Backend Principal (FastAPI + Python)
Arquivo: backend/main.py
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn
import os

from database import engine, Base, get_db
from routers import auth, usuarios, profissionais, anuncios, pagamentos, admin, avaliacoes
from config import settings


# ── Criar tabelas no startup ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado")
    yield
    print("👋 Servidor encerrado")


# ── App FastAPI ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="É Festa API",
    description="API do maior marketplace de festas e eventos do Brasil 🎉",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Servir arquivos estáticos do frontend ─────────────────────────────────────
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# ── Templates Jinja2 (páginas HTML servidas pelo backend) ────────────────────
templates = Jinja2Templates(directory="../frontend")


# ── Routers da API ────────────────────────────────────────────────────────────
app.include_router(auth.router,          prefix="/api/auth",          tags=["Autenticação"])
app.include_router(usuarios.router,      prefix="/api/usuarios",      tags=["Usuários"])
app.include_router(profissionais.router, prefix="/api/profissionais", tags=["Profissionais"])
app.include_router(anuncios.router,      prefix="/api/anuncios",      tags=["Anúncios"])
app.include_router(pagamentos.router,    prefix="/api/pagamentos",    tags=["Pagamentos"])
app.include_router(admin.router,         prefix="/api/admin",         tags=["Administração"])
app.include_router(avaliacoes.router,    prefix="/api/avaliacoes",    tags=["Avaliações"])


# ── Rotas de página (SPA-like) ────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/busca", response_class=HTMLResponse)
async def busca(request: Request):
    return templates.TemplateResponse("pages/busca.html", {"request": request})


@app.get("/perfil/{profissional_id}", response_class=HTMLResponse)
async def perfil(request: Request, profissional_id: int):
    return templates.TemplateResponse(
        "pages/perfil-profissional.html",
        {"request": request, "profissional_id": profissional_id}
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin/index.html", {"request": request})


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "É Festa API", "version": "1.0.0"}


# ── Entrypoint ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
