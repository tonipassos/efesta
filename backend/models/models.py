"""
É FESTA — Modelos do Banco de Dados (SQLAlchemy ORM)
Arquivo: backend/models/models.py
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


# ══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════════════════

class TipoUsuario(str, enum.Enum):
    usuario     = "usuario"
    profissional = "profissional"
    admin       = "admin"


class StatusConta(str, enum.Enum):
    pendente  = "pendente"
    ativo     = "ativo"
    bloqueado = "bloqueado"
    cancelado = "cancelado"


class TipoPlano(str, enum.Enum):
    profissional = "profissional"
    premium      = "premium"


class StatusAssinatura(str, enum.Enum):
    ativa    = "ativa"
    pausada  = "pausada"
    cancelada = "cancelada"
    expirada = "expirada"


class TipoAnuncio(str, enum.Enum):
    semanal    = "semanal"     # 7 dias  – R$49
    quinzenal  = "quinzenal"   # 15 dias – R$89
    mensal     = "mensal"      # 30 dias – R$149
    banner_topo = "banner_topo" # 30 dias – R$249


class StatusPagamento(str, enum.Enum):
    pendente  = "pendente"
    aprovado  = "aprovado"
    recusado  = "recusado"
    cancelado = "cancelado"
    reembolsado = "reembolsado"


class CategoriaServico(str, enum.Enum):
    buffet          = "buffet"
    decoracao       = "decoracao"
    foto_video      = "foto_video"
    dj_musica       = "dj_musica"
    salao_festas    = "salao_festas"
    casamento       = "casamento"
    formatura       = "formatura"
    bolos_doces     = "bolos_doces"
    floricultura    = "floricultura"
    iluminacao      = "iluminacao"
    locacao_itens   = "locacao_itens"
    estruturas      = "estruturas"
    shows_ingressos = "shows_ingressos"
    animacao        = "animacao"
    transporte      = "transporte"
    open_bar        = "open_bar"
    convites        = "convites"
    seguranca       = "seguranca"
    assessoria      = "assessoria"
    fotocabine      = "fotocabine"
    cerimonia       = "cerimonia"
    musica_ao_vivo  = "musica_ao_vivo"
    master_cerimonia = "master_cerimonia"
    brinquedos      = "brinquedos"
    lembrancinhas   = "lembrancinhas"
    outros          = "outros"


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: USUÁRIO
# ══════════════════════════════════════════════════════════════════════════════

class Usuario(Base):
    __tablename__ = "usuarios"

    id               = Column(Integer, primary_key=True, index=True)
    nome             = Column(String(150), nullable=False)
    email            = Column(String(200), unique=True, index=True, nullable=False)
    telefone         = Column(String(20))
    senha_hash       = Column(String(256))
    google_id        = Column(String(100), unique=True, nullable=True)
    foto_perfil      = Column(String(500), nullable=True)
    tipo             = Column(SAEnum(TipoUsuario), default=TipoUsuario.usuario)
    status           = Column(SAEnum(StatusConta), default=StatusConta.ativo)
    email_verificado = Column(Boolean, default=False)
    cidade           = Column(String(100), nullable=True)
    estado           = Column(String(2), nullable=True)
    criado_em        = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em    = Column(DateTime(timezone=True), onupdate=func.now())
    ultimo_acesso    = Column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    avaliacoes_feitas = relationship("Avaliacao", back_populates="autor", foreign_keys="Avaliacao.autor_id")
    favoritos         = relationship("Favorito", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario(id={self.id}, email={self.email}, tipo={self.tipo})>"


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: PROFISSIONAL / EMPRESA
# ══════════════════════════════════════════════════════════════════════════════

class Profissional(Base):
    __tablename__ = "profissionais"

    id              = Column(Integer, primary_key=True, index=True)
    usuario_id      = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nome_negocio    = Column(String(200), nullable=False)
    cnpj_cpf        = Column(String(20), nullable=True)
    categoria       = Column(SAEnum(CategoriaServico), nullable=False)
    descricao       = Column(Text, nullable=True)

    # Contato
    whatsapp        = Column(String(20), nullable=True)
    telefone        = Column(String(20), nullable=True)
    email_comercial = Column(String(200), nullable=True)
    website         = Column(String(300), nullable=True)
    instagram       = Column(String(100), nullable=True)
    facebook        = Column(String(100), nullable=True)

    # Endereço e geolocalização
    cep             = Column(String(10), nullable=True)
    logradouro      = Column(String(300), nullable=True)
    numero          = Column(String(10), nullable=True)
    complemento     = Column(String(100), nullable=True)
    bairro          = Column(String(100), nullable=True)
    cidade          = Column(String(100), nullable=True)
    estado          = Column(String(2), nullable=True)
    latitude        = Column(Float, nullable=True)
    longitude       = Column(Float, nullable=True)

    # Imagens (máximo 4)
    foto_principal  = Column(String(500), nullable=True)  # usada no destaque
    foto_2          = Column(String(500), nullable=True)
    foto_3          = Column(String(500), nullable=True)
    foto_4          = Column(String(500), nullable=True)

    # Preços
    preco_minimo    = Column(Float, nullable=True)
    preco_maximo    = Column(Float, nullable=True)
    preco_descricao = Column(String(200), nullable=True)

    # Status e verificação
    status          = Column(SAEnum(StatusConta), default=StatusConta.pendente)
    verificado      = Column(Boolean, default=False)
    destaque_ativo  = Column(Boolean, default=False)
    atende_brasil   = Column(Boolean, default=False)

    # Métricas
    total_visualizacoes = Column(Integer, default=0)
    total_cliques_wp    = Column(Integer, default=0)
    media_avaliacao     = Column(Float, default=0.0)
    total_avaliacoes    = Column(Integer, default=0)

    criado_em       = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em   = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamentos
    usuario         = relationship("Usuario")
    assinaturas     = relationship("Assinatura", back_populates="profissional")
    anuncios        = relationship("AnuncioDestaque", back_populates="profissional")
    avaliacoes      = relationship("Avaliacao", back_populates="profissional", foreign_keys="Avaliacao.profissional_id")
    servicos        = relationship("Servico", back_populates="profissional")

    def __repr__(self):
        return f"<Profissional(id={self.id}, nome={self.nome_negocio})>"


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: SERVIÇO (itens de serviço do profissional)
# ══════════════════════════════════════════════════════════════════════════════

class Servico(Base):
    __tablename__ = "servicos"

    id              = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    nome            = Column(String(200), nullable=False)
    descricao       = Column(Text, nullable=True)
    preco           = Column(Float, nullable=True)
    unidade         = Column(String(50), nullable=True)  # "por pessoa", "por evento", etc.
    ativo           = Column(Boolean, default=True)
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())

    profissional    = relationship("Profissional", back_populates="servicos")


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: ASSINATURA
# ══════════════════════════════════════════════════════════════════════════════

class Assinatura(Base):
    __tablename__ = "assinaturas"

    id                  = Column(Integer, primary_key=True, index=True)
    profissional_id     = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    plano               = Column(SAEnum(TipoPlano), nullable=False)
    status              = Column(SAEnum(StatusAssinatura), default=StatusAssinatura.ativa)
    preco               = Column(Float, nullable=False)
    mp_subscription_id  = Column(String(200), nullable=True)  # ID da assinatura no MP
    mp_preapproval_id   = Column(String(200), nullable=True)
    inicio             = Column(DateTime(timezone=True), nullable=False)
    proximo_vencimento = Column(DateTime(timezone=True), nullable=True)
    cancelado_em       = Column(DateTime(timezone=True), nullable=True)
    criado_em          = Column(DateTime(timezone=True), server_default=func.now())

    profissional        = relationship("Profissional", back_populates="assinaturas")
    pagamentos          = relationship("Pagamento", back_populates="assinatura")


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: ANÚNCIO EM DESTAQUE
# ══════════════════════════════════════════════════════════════════════════════

class AnuncioDestaque(Base):
    __tablename__ = "anuncios_destaque"

    id              = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    tipo            = Column(SAEnum(TipoAnuncio), nullable=False)
    preco_pago      = Column(Float, nullable=False)
    status          = Column(SAEnum(StatusPagamento), default=StatusPagamento.pendente)
    inicio          = Column(DateTime(timezone=True), nullable=True)
    fim             = Column(DateTime(timezone=True), nullable=True)
    cliques         = Column(Integer, default=0)
    impressoes      = Column(Integer, default=0)
    mp_payment_id   = Column(String(200), nullable=True)
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())

    profissional    = relationship("Profissional", back_populates="anuncios")


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: PAGAMENTO
# ══════════════════════════════════════════════════════════════════════════════

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id              = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    assinatura_id   = Column(Integer, ForeignKey("assinaturas.id"), nullable=True)
    anuncio_id      = Column(Integer, ForeignKey("anuncios_destaque.id"), nullable=True)
    valor           = Column(Float, nullable=False)
    descricao       = Column(String(300), nullable=True)
    status          = Column(SAEnum(StatusPagamento), default=StatusPagamento.pendente)
    mp_payment_id   = Column(String(200), nullable=True)
    mp_preference_id = Column(String(200), nullable=True)
    metodo_pagamento = Column(String(50), nullable=True)  # pix, cartao, boleto
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())
    pago_em         = Column(DateTime(timezone=True), nullable=True)

    assinatura      = relationship("Assinatura", back_populates="pagamentos")


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: AVALIAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

class Avaliacao(Base):
    __tablename__ = "avaliacoes"

    id              = Column(Integer, primary_key=True, index=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    autor_id        = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nota            = Column(Integer, nullable=False)  # 1–5
    comentario      = Column(Text, nullable=True)
    tipo_evento     = Column(String(100), nullable=True)  # "Casamento", "Formatura", etc.
    aprovada        = Column(Boolean, default=True)
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())

    profissional    = relationship("Profissional", back_populates="avaliacoes", foreign_keys=[profissional_id])
    autor           = relationship("Usuario", back_populates="avaliacoes_feitas", foreign_keys=[autor_id])


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: FAVORITO
# ══════════════════════════════════════════════════════════════════════════════

class Favorito(Base):
    __tablename__ = "favoritos"

    id              = Column(Integer, primary_key=True, index=True)
    usuario_id      = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())

    usuario         = relationship("Usuario", back_populates="favoritos")
    profissional    = relationship("Profissional")


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: DENÚNCIA
# ══════════════════════════════════════════════════════════════════════════════

class Denuncia(Base):
    __tablename__ = "denuncias"

    id              = Column(Integer, primary_key=True, index=True)
    denunciante_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    motivo          = Column(String(200), nullable=False)
    descricao       = Column(Text, nullable=True)
    resolvida       = Column(Boolean, default=False)
    criado_em       = Column(DateTime(timezone=True), server_default=func.now())


# ══════════════════════════════════════════════════════════════════════════════
# MODELO: TOKEN DE RESET DE SENHA
# ══════════════════════════════════════════════════════════════════════════════

class TokenResetSenha(Base):
    __tablename__ = "tokens_reset_senha"

    id          = Column(Integer, primary_key=True, index=True)
    usuario_id  = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    token       = Column(String(200), unique=True, nullable=False)
    expira_em   = Column(DateTime(timezone=True), nullable=False)
    usado       = Column(Boolean, default=False)
    criado_em   = Column(DateTime(timezone=True), server_default=func.now())
