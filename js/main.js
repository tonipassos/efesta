// ============================================
// É FESTA — JavaScript Principal
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initConfeti();
  initCarrossel();
  initModais();
  initCategoriasFilter();
  initToast();
  initNavMobile();
  initAnimacoes();
});

// ====== HEADER SCROLL ======
function initHeader() {
  const header = document.getElementById('header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// ====== CONFETI ANIMADO ======
function initConfeti() {
  const container = document.getElementById('confeti-container');
  if (!container) return;
  const cores = ['#E8163C', '#F5A623', '#FF6B9D', '#00C896', '#FFD700', '#B931FC'];
  for (let i = 0; i < 40; i++) {
    const el = document.createElement('div');
    el.className = 'confete';
    el.style.cssText = `
      left: ${Math.random() * 100}%;
      background: ${cores[Math.floor(Math.random() * cores.length)]};
      width: ${Math.random() * 8 + 4}px;
      height: ${Math.random() * 8 + 4}px;
      animation-duration: ${Math.random() * 6 + 4}s;
      animation-delay: ${Math.random() * 8}s;
      border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
    `;
    container.appendChild(el);
  }
}

// ====== CARROSSEL ======
function initCarrossel() {
  const tracks = document.querySelectorAll('.carrossel-track');
  tracks.forEach(track => {
    const wrapper = track.closest('.carrossel-wrapper');
    const btnPrev = wrapper?.parentElement.querySelector('.ctrl-prev');
    const btnNext = wrapper?.parentElement.querySelector('.ctrl-next');
    let idx = 0;
    const cardWidth = 324; // 300 + 24 gap

    function atualizar() {
      const maxIdx = track.children.length - Math.floor(wrapper.offsetWidth / cardWidth);
      idx = Math.max(0, Math.min(idx, maxIdx));
      track.style.transform = `translateX(-${idx * cardWidth}px)`;
      if (btnPrev) btnPrev.disabled = idx === 0;
      if (btnNext) btnNext.disabled = idx >= maxIdx;
    }

    if (btnPrev) btnPrev.addEventListener('click', () => { idx--; atualizar(); });
    if (btnNext) btnNext.addEventListener('click', () => { idx++; atualizar(); });
    atualizar();

    // Auto-play
    setInterval(() => {
      const maxIdx = track.children.length - Math.floor(wrapper.offsetWidth / cardWidth);
      idx = idx >= maxIdx ? 0 : idx + 1;
      atualizar();
    }, 5000);
  });
}

// ====== MODAIS ======
function initModais() {
  // Abrir modal de login/cadastro
  document.querySelectorAll('[data-modal]').forEach(trigger => {
    trigger.addEventListener('click', () => {
      const id = trigger.dataset.modal;
      abrirModal(id);
    });
  });

  // Fechar modais
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) fecharModal(overlay.id);
    });
  });

  document.querySelectorAll('.modal-fechar').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) fecharModal(modal.id);
    });
  });

  // Tabs de cadastro
  document.querySelectorAll('.tab-modal').forEach(tab => {
    tab.addEventListener('click', () => {
      const grupo = tab.closest('.tabs-modal');
      grupo?.querySelectorAll('.tab-modal').forEach(t => t.classList.remove('ativo'));
      tab.classList.add('ativo');
      const alvo = tab.dataset.tab;
      const modal = tab.closest('.modal');
      modal?.querySelectorAll('[data-tab-content]').forEach(c => {
        c.style.display = c.dataset.tabContent === alvo ? 'block' : 'none';
      });
    });
  });

  // Tipo de cadastro (usuario / profissional)
  document.querySelectorAll('.tipo-opcao').forEach(opcao => {
    opcao.addEventListener('click', () => {
      document.querySelectorAll('.tipo-opcao').forEach(o => o.classList.remove('ativo'));
      opcao.classList.add('ativo');
    });
  });

  // Formulários
  document.querySelectorAll('.form-cadastro').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      fecharTodasModais();
      mostrarToast('✅ Cadastro realizado com sucesso! Bem-vindo(a) ao É Festa!', 'sucesso');
    });
  });
}

function abrirModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.add('ativo');
    document.body.style.overflow = 'hidden';
  }
}

function fecharModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('ativo');
    document.body.style.overflow = '';
  }
}

function fecharTodasModais() {
  document.querySelectorAll('.modal-overlay.ativo').forEach(m => {
    m.classList.remove('ativo');
  });
  document.body.style.overflow = '';
}

// ====== TOAST ======
let toastTimer;
function initToast() {
  window.mostrarToast = function(msg, tipo = '') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `toast mostrar ${tipo}`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('mostrar'), 4000);
  };
}

// ====== CATEGORIAS FILTRO ======
function initCategoriasFilter() {
  document.querySelectorAll('.categoria-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.categoria-card').forEach(c => c.classList.remove('ativo'));
      card.classList.add('ativo');
      const cat = card.dataset.cat;
      filtrarAnuncios(cat);
    });
  });
}

function filtrarAnuncios(cat) {
  document.querySelectorAll('.anuncio-card').forEach(card => {
    const cardCat = card.dataset.cat;
    card.style.display = (!cat || cat === 'todos' || cardCat === cat) ? 'block' : 'none';
  });
}

// ====== MENU MOBILE ======
function initNavMobile() {
  const toggle = document.getElementById('menu-toggle');
  const nav = document.getElementById('nav-mobile');
  if (!toggle || !nav) return;
  toggle.addEventListener('click', () => {
    nav.classList.toggle('aberto');
  });
}

// ====== ANIMAÇÕES SCROLL ======
function initAnimacoes() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visivel');
      }
    });
  }, { threshold: 0.15 });

  document.querySelectorAll('.animar').forEach(el => observer.observe(el));
}

// ====== BUSCA ======
function buscarServicos(e) {
  if (e) e.preventDefault();
  const termo = document.getElementById('busca-input')?.value;
  const local = document.getElementById('busca-local')?.value;
  if (termo || local) {
    window.location.href = `pages/busca.html?q=${encodeURIComponent(termo || '')}&local=${encodeURIComponent(local || '')}`;
  }
}

// ====== MERCADO PAGO (integração) ======
const MercadoPago = {
  PUBLIC_KEY: 'TEST-sua-public-key-aqui', // Substituir pela chave real

  async criarPreferencia(dados) {
    try {
      const resp = await fetch('/api/pagamento/criar-preferencia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
      });
      return await resp.json();
    } catch (err) {
      console.error('Erro ao criar preferência de pagamento:', err);
      return null;
    }
  },

  async assinar(plano, profissionalId) {
    const dados = {
      titulo: `É Festa — Plano ${plano.nome}`,
      preco: plano.preco,
      periodo: plano.periodo,
      profissionalId,
      back_url: window.location.origin + '/pages/pagamento-confirmado.html'
    };
    const pref = await this.criarPreferencia(dados);
    if (pref?.init_point) {
      window.location.href = pref.init_point;
    }
  }
};

// ====== GEOLOCALIZAÇÃO ======
function obterLocalizacao(callback) {
  if (!navigator.geolocation) {
    mostrarToast('⚠️ Geolocalização não suportada neste navegador.', '');
    return;
  }
  navigator.geolocation.getCurrentPosition(
    pos => callback(pos.coords.latitude, pos.coords.longitude),
    () => mostrarToast('❌ Não foi possível obter sua localização.', 'erro')
  );
}

// Usar geolocalização para buscar próximos
function buscarProximos() {
  obterLocalizacao((lat, lng) => {
    window.location.href = `pages/busca.html?lat=${lat}&lng=${lng}&proximos=1`;
  });
}

// ====== EXPORTAR FUNÇÕES GLOBAIS ======
window.abrirModal = abrirModal;
window.fecharModal = fecharModal;
window.buscarServicos = buscarServicos;
window.buscarProximos = buscarProximos;
window.MercadoPago = MercadoPago;
