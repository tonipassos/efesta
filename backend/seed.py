"""
É FESTA — Seed do Banco de Dados
Arquivo: backend/seed.py
Popula o banco com dados de exemplo para desenvolvimento.
Execute: python seed.py
"""

from database import SessionLocal, engine, Base
from models.models import (
    Usuario, Profissional, Assinatura, AnuncioDestaque,
    Avaliacao, TipoUsuario, StatusConta, CategoriaServico,
    TipoPlano, StatusAssinatura, TipoAnuncio, StatusPagamento
)
from services.auth_service import hash_senha
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Iniciando seed do banco de dados...")

# ── Admin ─────────────────────────────────────────────────────────────────────
admin = Usuario(
    nome="Administrador",
    email="admin@efesta.com.br",
    senha_hash=hash_senha("admin123"),
    tipo=TipoUsuario.admin,
    status=StatusConta.ativo,
    email_verificado=True,
)
db.add(admin)

# ── Usuários comuns ───────────────────────────────────────────────────────────
usuarios = [
    Usuario(nome="Ana Paula Souza", email="ana@teste.com", telefone="11999990001",
            senha_hash=hash_senha("123456"), tipo=TipoUsuario.usuario, status=StatusConta.ativo),
    Usuario(nome="Carlos Mendes", email="carlos@teste.com", telefone="21988880002",
            senha_hash=hash_senha("123456"), tipo=TipoUsuario.usuario, status=StatusConta.ativo),
    Usuario(nome="Beatriz Costa", email="bea@teste.com", telefone="31977770003",
            senha_hash=hash_senha("123456"), tipo=TipoUsuario.usuario, status=StatusConta.ativo),
]
for u in usuarios:
    db.add(u)

# ── Profissionais ─────────────────────────────────────────────────────────────
u_prof1 = Usuario(nome="Ricardo Almeida", email="buffet@teste.com", senha_hash=hash_senha("123456"), tipo=TipoUsuario.profissional, status=StatusConta.ativo)
u_prof2 = Usuario(nome="Mariana Silva", email="deco@teste.com", senha_hash=hash_senha("123456"), tipo=TipoUsuario.profissional, status=StatusConta.ativo)
u_prof3 = Usuario(nome="João Santos", email="foto@teste.com", senha_hash=hash_senha("123456"), tipo=TipoUsuario.profissional, status=StatusConta.ativo)
u_prof4 = Usuario(nome="Marcos DJ", email="dj@teste.com", senha_hash=hash_senha("123456"), tipo=TipoUsuario.profissional, status=StatusConta.ativo)
u_prof5 = Usuario(nome="Fernanda Lima", email="bolo@teste.com", senha_hash=hash_senha("123456"), tipo=TipoUsuario.profissional, status=StatusConta.ativo)

for u in [u_prof1, u_prof2, u_prof3, u_prof4, u_prof5]:
    db.add(u)

db.flush()

profissionais = [
    Profissional(
        usuario_id=u_prof1.id, nome_negocio="Buffet Sabor & Arte",
        categoria=CategoriaServico.buffet, descricao="Buffet completo para casamentos e eventos. 15 anos de experiência.",
        whatsapp="11999990001", telefone="1130000001", email_comercial="buffet@saborearte.com",
        cidade="São Paulo", estado="SP", latitude=-23.561, longitude=-46.655,
        preco_minimo=89.0, preco_maximo=200.0, preco_descricao="A partir de R$89/pessoa",
        status=StatusConta.ativo, verificado=True, destaque_ativo=True,
        media_avaliacao=4.9, total_avaliacoes=247, total_visualizacoes=1240,
    ),
    Profissional(
        usuario_id=u_prof2.id, nome_negocio="Studio Flor & Vida",
        categoria=CategoriaServico.decoracao, descricao="Decoração floral e temática para todos os eventos.",
        whatsapp="21988880002", cidade="Rio de Janeiro", estado="RJ",
        latitude=-22.90, longitude=-43.17,
        preco_descricao="Orçamento sob consulta",
        status=StatusConta.ativo, verificado=True, destaque_ativo=True,
        media_avaliacao=5.0, total_avaliacoes=183, total_visualizacoes=890,
    ),
    Profissional(
        usuario_id=u_prof3.id, nome_negocio="Lente Mágica Fotografia",
        categoria=CategoriaServico.foto_video, descricao="Fotografia e filmagem profissional para eventos.",
        whatsapp="31977770003", cidade="Belo Horizonte", estado="MG",
        latitude=-19.91, longitude=-43.94,
        preco_minimo=1200.0, preco_descricao="A partir de R$1.200",
        status=StatusConta.ativo, verificado=False, destaque_ativo=False,
        media_avaliacao=4.8, total_avaliacoes=319, total_visualizacoes=650,
    ),
    Profissional(
        usuario_id=u_prof4.id, nome_negocio="DJ Marcos Vibe",
        categoria=CategoriaServico.dj_musica, descricao="DJ para festas, casamentos e formaturas.",
        whatsapp="41966660004", cidade="Curitiba", estado="PR",
        latitude=-25.42, longitude=-49.26,
        preco_minimo=800.0, preco_descricao="A partir de R$800/evento",
        status=StatusConta.ativo, verificado=True, destaque_ativo=True,
        media_avaliacao=4.9, total_avaliacoes=412, total_visualizacoes=1100,
    ),
    Profissional(
        usuario_id=u_prof5.id, nome_negocio="Doce Vida Confeitaria",
        categoria=CategoriaServico.bolos_doces, descricao="Bolos artísticos e doces finos para eventos especiais.",
        whatsapp="71955550005", cidade="Salvador", estado="BA",
        latitude=-12.97, longitude=-38.50,
        preco_minimo=280.0, preco_descricao="A partir de R$280",
        status=StatusConta.ativo, verificado=True, destaque_ativo=True,
        media_avaliacao=5.0, total_avaliacoes=289, total_visualizacoes=780,
    ),
]

for p in profissionais:
    db.add(p)

db.flush()

# ── Assinaturas ───────────────────────────────────────────────────────────────
for p in profissionais[:2]:
    ass = Assinatura(
        profissional_id=p.id, plano=TipoPlano.premium, preco=159.0,
        status=StatusAssinatura.ativa,
        inicio=datetime.utcnow() - timedelta(days=15),
        proximo_vencimento=datetime.utcnow() + timedelta(days=15),
    )
    db.add(ass)

# ── Anúncios em Destaque ──────────────────────────────────────────────────────
for p in profissionais[:4]:
    if p.destaque_ativo:
        an = AnuncioDestaque(
            profissional_id=p.id, tipo=TipoAnuncio.mensal, preco_pago=149.0,
            status=StatusPagamento.aprovado,
            inicio=datetime.utcnow() - timedelta(days=5),
            fim=datetime.utcnow() + timedelta(days=25),
            cliques=47, impressoes=820,
        )
        db.add(an)

# ── Avaliações ────────────────────────────────────────────────────────────────
db.flush()
av1 = Avaliacao(
    profissional_id=profissionais[0].id, autor_id=usuarios[0].id,
    nota=5, comentario="Simplesmente perfeito! Todos adoraram.", tipo_evento="Casamento",
)
av2 = Avaliacao(
    profissional_id=profissionais[3].id, autor_id=usuarios[1].id,
    nota=5, comentario="DJ incrível, animou muito a festa!", tipo_evento="Formatura",
)
db.add_all([av1, av2])

db.commit()
print("✅ Seed concluído com sucesso!")
print("\n📋 Credenciais de acesso:")
print("   Admin:       admin@efesta.com.br / admin123")
print("   Usuário:     ana@teste.com / 123456")
print("   Profissional: buffet@teste.com / 123456")
print("\n🚀 Inicie o servidor: python main.py")
print("📖 Docs da API: http://localhost:8000/api/docs")
db.close()
