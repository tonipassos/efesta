# 🎉 É FESTA — Marketplace de Festas e Eventos do Brasil

> O maior marketplace digital de festas e eventos do Brasil.
> Conecta usuários que buscam serviços a profissionais que os ofertam.

---

## 📁 Estrutura Completa do Projeto

```
efesta/
│
├── 📄 README.md                         ← Este arquivo
├── 🐋 Dockerfile                        ← Container da aplicação
├── 🐋 docker-compose.yml                ← Orquestração (App + DB + Nginx)
├── ⚙️  nginx.conf                        ← Configuração do servidor web
│
├── 🐍 backend/                          ← Python (FastAPI)
│   ├── main.py                          ← App FastAPI principal + rotas de página
│   ├── database.py                      ← SQLAlchemy + SQLite/PostgreSQL
│   ├── config.py                        ← Configurações centralizadas
│   ├── requirements.txt                 ← Dependências Python
│   ├── .env.example                     ← Template de variáveis de ambiente
│   ├── seed.py                          ← Dados de exemplo para desenvolvimento
│   ├── migrations_setup.py              ← Guia de migrações Alembic
│   │
│   ├── models/
│   │   └── models.py                   ← 14 modelos ORM (tabelas do banco)
│   │
│   ├── routers/
│   │   ├── auth.py                     ← Login, Cadastro, Google OAuth, JWT
│   │   ├── usuarios.py                 ← Perfil, favoritos
│   │   ├── profissionais.py            ← CRUD, busca geolocalizada, upload fotos
│   │   ├── anuncios.py                 ← Carrossel de destaques + métricas
│   │   ├── pagamentos.py               ← Mercado Pago: checkout + webhooks
│   │   ├── admin.py                    ← Painel admin: KPIs, aprovações, financeiro
│   │   └── avaliacoes.py               ← Sistema de avaliações 1-5 estrelas
│   │
│   ├── services/
│   │   ├── auth_service.py             ← JWT, bcrypt, dependências FastAPI
│   │   ├── pagamento_service.py        ← SDK Mercado Pago, webhooks
│   │   └── email_service.py            ← SMTP, e-mails transacionais
│   │
│   └── tests/
│       └── test_api.py                 ← Testes automatizados (pytest)
│
└── 🌐 frontend/                         ← HTML + CSS + JavaScript
    ├── index.html                       ← Homepage completa
    ├── css/
    │   └── style.css                   ← Design system completo
    ├── js/
    │   ├── main.js                     ← Carrossel, modais, confeti, geolocalização
    │   └── api.js                      ← Cliente da API Python (todas as chamadas)
    ├── pages/
    │   ├── busca.html                  ← Busca + filtros avançados + mapa interativo
    │   ├── perfil-profissional.html    ← Perfil com 4 fotos, avaliações, mapa Leaflet
    │   ├── profissional-cadastro.html  ← Cadastro completo com planos e pagamento
    │   ├── painel-usuario.html         ← Painel do usuário (favoritos, histórico)
    │   ├── painel-profissional.html    ← Painel do profissional (métricas, anúncios)
    │   ├── como-funciona.html          ← Explicação do site + FAQ
    │   ├── planos.html                 ← Planos e preços + anúncios destaque
    │   ├── privacidade.html            ← Política de Privacidade (LGPD)
    │   └── termos.html                 ← Termos de Uso
    └── admin/
        └── index.html                  ← Painel administrativo completo
```

---

## 🚀 Como Rodar o Projeto

### Opção 1: Desenvolvimento Local (mais rápido)

```bash
# 1. Clone ou extraia o projeto
cd efesta/backend

# 2. Crie o ambiente virtual Python
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o ambiente
cp .env.example .env
# Edite .env com suas chaves reais

# 5. Popule o banco com dados de exemplo
python seed.py

# 6. Inicie o servidor
python main.py
# Acesse: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Opção 2: Docker (produção)

```bash
# 1. Configure o .env
cp backend/.env.example backend/.env
# Edite backend/.env com suas chaves

# 2. Suba todos os serviços
docker-compose up -d

# 3. Rode o seed (primeira vez)
docker-compose exec app python seed.py

# Acesse: http://localhost
```

---

## 🔐 Credenciais de Teste (após rodar seed.py)

| Perfil        | E-mail                  | Senha     |
|--------------|-------------------------|-----------|
| Admin         | admin@efesta.com.br     | admin123  |
| Usuário       | ana@teste.com           | 123456    |
| Profissional  | buffet@teste.com        | 123456    |

---

## 📡 API REST — Endpoints Principais

| Método | Endpoint                              | Descrição                        |
|--------|---------------------------------------|----------------------------------|
| GET    | /api/health                           | Health check                     |
| POST   | /api/auth/cadastro                    | Cadastro de usuário              |
| POST   | /api/auth/login                       | Login com e-mail/senha           |
| POST   | /api/auth/google                      | Login com Google OAuth           |
| GET    | /api/auth/me                          | Dados do usuário logado          |
| GET    | /api/profissionais/buscar             | Busca com filtros                |
| GET    | /api/profissionais/destaques          | Anúncios em destaque             |
| GET    | /api/profissionais/{id}               | Perfil público                   |
| POST   | /api/profissionais/                   | Cadastrar profissional           |
| PUT    | /api/profissionais/{id}               | Editar perfil                    |
| POST   | /api/profissionais/{id}/fotos/{slot}  | Upload de foto (1–4)             |
| GET    | /api/anuncios/ativos                  | Anúncios ativos para carrossel   |
| POST   | /api/pagamentos/assinar               | Checkout de assinatura (MP)      |
| POST   | /api/pagamentos/anuncio-destaque      | Checkout de anúncio (MP)         |
| POST   | /api/pagamentos/webhook               | Webhook Mercado Pago             |
| GET    | /api/pagamentos/historico             | Histórico de pagamentos          |
| POST   | /api/avaliacoes/                      | Criar avaliação                  |
| GET    | /api/usuarios/favoritos               | Listar favoritos                 |
| POST   | /api/usuarios/favoritos/{id}          | Favoritar/desfavoritar           |
| GET    | /api/admin/dashboard                  | KPIs admin                       |
| GET    | /api/admin/usuarios                   | Listar usuários                  |
| GET    | /api/admin/profissionais              | Listar profissionais             |
| PATCH  | /api/admin/profissionais/{id}/aprovar | Aprovar/rejeitar profissional    |
| GET    | /api/admin/financeiro                 | Extrato financeiro               |
| GET    | /api/admin/denuncias                  | Listar denúncias                 |

📖 Documentação interativa completa: `http://localhost:8000/api/docs`

---

## 💳 Integração Mercado Pago

1. Crie uma conta em [mercadopago.com.br/developers](https://www.mercadopago.com.br/developers)
2. Obtenha suas credenciais (Access Token + Public Key)
3. Configure no `.env`:
   ```
   MERCADO_PAGO_ACCESS_TOKEN=TEST-seu-token
   MERCADO_PAGO_PUBLIC_KEY=TEST-sua-chave
   ```
4. Para webhooks em desenvolvimento, use [ngrok](https://ngrok.com):
   ```bash
   ngrok http 8000
   # Configure a URL gerada como MERCADO_PAGO_WEBHOOK_URL no .env
   ```

---

## 🗺️ Geolocalização (Leaflet + OpenStreetMap)

- **Busca por proximidade**: filtro por lat/lng + raio em km
- **Mapa na busca**: pinos de todos os fornecedores encontrados
- **Mapa no perfil**: localização exata do estabelecimento
- **Gratuito e sem limites**: usa OpenStreetMap via Leaflet.js

---

## 📊 Banco de Dados — Tabelas

| Tabela              | Descrição                              |
|--------------------|----------------------------------------|
| usuarios           | Usuários e administradores             |
| profissionais      | Perfis de empresas/profissionais       |
| servicos           | Itens de serviço dos profissionais     |
| assinaturas        | Assinaturas mensais (Plano Prof/Prem)  |
| anuncios_destaque  | Anúncios no carrossel da homepage      |
| pagamentos         | Histórico de todos os pagamentos       |
| avaliacoes         | Avaliações de 1–5 estrelas             |
| favoritos          | Favoritos dos usuários                 |
| denuncias          | Denúncias de perfis                    |
| tokens_reset_senha | Tokens de redefinição de senha         |

---

## 🧪 Testes

```bash
cd backend
pytest tests/ -v
```

---

## ✅ Checklist de Produção

- [ ] Substituir `SECRET_KEY` por chave aleatória forte (32+ chars)
- [ ] Trocar credenciais MP de TEST para PROD
- [ ] Configurar PostgreSQL (trocar DATABASE_URL)
- [ ] Configurar SMTP real para e-mails
- [ ] Configurar Google OAuth (Client ID real)
- [ ] Configurar HTTPS (SSL/TLS) no Nginx
- [ ] Configurar domínio em ALLOWED_ORIGINS
- [ ] Rodar `python seed.py` para criar o admin inicial
- [ ] Configurar backup automático do banco de dados
- [ ] Monitorar webhooks do Mercado Pago

---

## 🎨 Identidade Visual

| Elemento         | Valor                                   |
|------------------|-----------------------------------------|
| Cor primária     | #E8163C (Vermelho festivo)              |
| Cor secundária   | #F5A623 (Dourado vibrante)              |
| Cor terciária    | #1A0A2E (Roxo escuro profundo)          |
| Cor destaque     | #00C896 (Verde sucesso)                 |
| Fonte display    | Playfair Display (títulos)              |
| Fonte corpo      | Plus Jakarta Sans (textos)              |

---

## 📋 Categorias de Serviço (25+)

Buffet · Decoração · Foto & Vídeo · DJ & Música · Salões de Festa ·
Casamentos · Formaturas · Bolos & Confeitaria · Floricultura ·
Iluminação & Sonorização · Locação de Itens · Estruturas para Eventos ·
Shows & Ingressos · Animação & Recreação · Transporte · Open Bar & Drinks ·
Convites & Papelaria · Segurança · Assessoria de Eventos · Fotocabine ·
Cerimônia · Música ao Vivo · Mestre de Cerimônias · Brinquedos ·
Lembrancinhas · Outros

---

**É Festa** © 2025 — Desenvolvido com 🎉 para o Brasil
