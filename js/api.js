/**
 * É FESTA — Cliente da API Python (FastAPI)
 * Arquivo: js/api.js
 * Todas as chamadas ao backend são feitas aqui.
 */

const API_BASE = window.location.origin + '/api';

// ── Token JWT ────────────────────────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('efesta_token'),
  setToken: (t) => localStorage.setItem('efesta_token', t),
  removeToken: () => localStorage.removeItem('efesta_token'),
  getUser: () => {
    const u = localStorage.getItem('efesta_user');
    return u ? JSON.parse(u) : null;
  },
  setUser: (u) => localStorage.setItem('efesta_user', JSON.stringify(u)),
  removeUser: () => localStorage.removeItem('efesta_user'),
  isLogado: () => !!Auth.getToken(),
  logout: () => { Auth.removeToken(); Auth.removeUser(); window.location.href = '/'; },
};

// ── Fetch com JWT ─────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (resp.status === 401) { Auth.logout(); return null; }

  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || 'Erro na requisição');
  return data;
}

// ── Autenticação ──────────────────────────────────────────────────────────────
const AuthAPI = {
  async cadastrar({ nome_completo, email, telefone, senha }) {
    const data = await apiFetch('/auth/cadastro', {
      method: 'POST',
      body: JSON.stringify({ nome_completo, email, telefone, senha }),
    });
    if (data?.access_token) { Auth.setToken(data.access_token); Auth.setUser(data.usuario); }
    return data;
  },

  async login(email, senha) {
    const form = new FormData();
    form.append('username', email);
    form.append('password', senha);
    const resp = await fetch(`${API_BASE}/auth/login`, { method: 'POST', body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || 'Erro ao fazer login');
    Auth.setToken(data.access_token);
    Auth.setUser(data.usuario);
    return data;
  },

  async loginGoogle(credential) {
    const data = await apiFetch('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });
    if (data?.access_token) { Auth.setToken(data.access_token); Auth.setUser(data.usuario); }
    return data;
  },

  async recuperarSenha(email) {
    return apiFetch('/auth/recuperar-senha', { method: 'POST', body: JSON.stringify({ email }) });
  },

  async me() { return apiFetch('/auth/me'); },
};

// ── Profissionais ─────────────────────────────────────────────────────────────
const ProfissionaisAPI = {
  async buscar(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/profissionais/buscar?${qs}`);
  },

  async destaques() { return apiFetch('/profissionais/destaques'); },

  async obterPerfil(id) { return apiFetch(`/profissionais/${id}`); },

  async cadastrar(dados) {
    return apiFetch('/profissionais/', { method: 'POST', body: JSON.stringify(dados) });
  },

  async editar(id, dados) {
    return apiFetch(`/profissionais/${id}`, { method: 'PUT', body: JSON.stringify(dados) });
  },

  async registrarCliqueWhatsApp(id) {
    return apiFetch(`/profissionais/${id}/clique-whatsapp`, { method: 'POST' });
  },

  async uploadFoto(profId, slot, file) {
    const token = Auth.getToken();
    const form = new FormData();
    form.append('arquivo', file);
    const resp = await fetch(`${API_BASE}/profissionais/${profId}/fotos/${slot}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: form,
    });
    if (!resp.ok) { const e = await resp.json(); throw new Error(e.detail); }
    return resp.json();
  },
};

// ── Anúncios ──────────────────────────────────────────────────────────────────
const AnunciosAPI = {
  async ativos() { return apiFetch('/anuncios/ativos'); },
  async registrarClique(anuncioId) {
    return apiFetch(`/anuncios/${anuncioId}/clique`, { method: 'POST' });
  },
};

// ── Pagamentos ────────────────────────────────────────────────────────────────
const PagamentosAPI = {
  async assinar(plano) {
    const data = await apiFetch('/pagamentos/assinar', {
      method: 'POST', body: JSON.stringify({ plano }),
    });
    if (data?.init_point) window.location.href = data.init_point;
    return data;
  },

  async anuncioDestaque(tipo) {
    const data = await apiFetch('/pagamentos/anuncio-destaque', {
      method: 'POST', body: JSON.stringify({ tipo }),
    });
    if (data?.init_point) window.location.href = data.init_point;
    return data;
  },

  async historico() { return apiFetch('/pagamentos/historico'); },

  async cancelarAssinatura() {
    return apiFetch('/pagamentos/cancelar-assinatura', { method: 'POST' });
  },
};

// ── Usuários ──────────────────────────────────────────────────────────────────
const UsuariosAPI = {
  async perfil() { return apiFetch('/usuarios/perfil'); },
  async atualizar(dados) {
    return apiFetch('/usuarios/perfil', { method: 'PUT', body: JSON.stringify(dados) });
  },
  async favoritar(profId) {
    return apiFetch(`/usuarios/favoritos/${profId}`, { method: 'POST' });
  },
  async favoritos() { return apiFetch('/usuarios/favoritos'); },
};

// ── Avaliações ────────────────────────────────────────────────────────────────
const AvaliacoesAPI = {
  async criar({ profissional_id, nota, comentario, tipo_evento }) {
    return apiFetch('/avaliacoes/', {
      method: 'POST',
      body: JSON.stringify({ profissional_id, nota, comentario, tipo_evento }),
    });
  },
};

// ── Admin ─────────────────────────────────────────────────────────────────────
const AdminAPI = {
  async dashboard()        { return apiFetch('/admin/dashboard'); },
  async usuarios(p={})     { return apiFetch(`/admin/usuarios?${new URLSearchParams(p)}`); },
  async profissionais(p={}) { return apiFetch(`/admin/profissionais?${new URLSearchParams(p)}`); },
  async aprovarProfissional(id, acao, verificado=false) {
    return apiFetch(`/admin/profissionais/${id}/aprovar`, {
      method: 'PATCH', body: JSON.stringify({ acao, verificado }),
    });
  },
  async alterarStatusUsuario(id, status) {
    return apiFetch(`/admin/usuarios/${id}/status`, {
      method: 'PATCH', body: JSON.stringify({ status }),
    });
  },
  async financeiro(p={})  { return apiFetch(`/admin/financeiro?${new URLSearchParams(p)}`); },
  async denuncias()       { return apiFetch('/admin/denuncias'); },
  async resolverDenuncia(id) {
    return apiFetch(`/admin/denuncias/${id}/resolver`, { method: 'PATCH' });
  },
  async estatsCategorias() { return apiFetch('/admin/estatisticas/categorias'); },
};

// ── Exportar tudo globalmente ─────────────────────────────────────────────────
window.EF = { Auth, AuthAPI, ProfissionaisAPI, AnunciosAPI, PagamentosAPI, UsuariosAPI, AvaliacoesAPI, AdminAPI };
