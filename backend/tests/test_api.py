"""
É FESTA — Testes Automatizados (pytest)
Execute: cd backend && pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_efesta.db"
engine_test = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_cadastro_usuario():
    resp = client.post("/api/auth/cadastro", json={
        "nome_completo": "Teste User", "email": "teste@efesta.com",
        "telefone": "11999990000", "senha": "senha123"
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()

def test_email_duplicado():
    client.post("/api/auth/cadastro", json={
        "nome_completo": "A", "email": "dup@efesta.com",
        "telefone": "11000000000", "senha": "abc"
    })
    resp = client.post("/api/auth/cadastro", json={
        "nome_completo": "B", "email": "dup@efesta.com",
        "telefone": "11000000001", "senha": "abc"
    })
    assert resp.status_code == 400

def test_login_correto():
    client.post("/api/auth/cadastro", json={
        "nome_completo": "Login", "email": "login@efesta.com",
        "telefone": "11222222222", "senha": "minhasenha"
    })
    resp = client.post("/api/auth/login",
        data={"username": "login@efesta.com", "password": "minhasenha"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 200

def test_login_erro():
    resp = client.post("/api/auth/login",
        data={"username": "nao@existe.com", "password": "errado"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.status_code == 401

def test_busca_profissionais():
    resp = client.get("/api/profissionais/buscar")
    assert resp.status_code == 200

def test_destaques():
    resp = client.get("/api/profissionais/destaques")
    assert resp.status_code == 200
