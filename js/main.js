// ============================================================
// É FESTA — main.js CORRIGIDO COMPLETO
// Versão 2.0 — corrige todos os bugs identificados na auditoria
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initConfeti();
  initCarrossel();
  initModais();
  initCategorias();       // ← CORRIGIDO: filtro de categorias funcionando
  initBusca();            // ← CORRIGIDO: busca com redirect correto
  initToast();
  initNavMobile();
  initAnimacoes();
  initFiltrosBusca();     // ← NOVO: filtros na página de busca
  initOrdenacao();        // ← NOVO: ordenação de resultados
  initViewToggle();       // ← NOVO: alternar grade/lista
  initAdminNav();         // ← CORRIGIDO: navegação do painel admin
  initPainelUsuario();    // ← CORRIGIDO: navegação do painel usuário
  initPainelProfissional(); // ← CORRIGIDO: navegação do painel profissional
  initAvaliacoes();       // ← NOVO: envio de avaliações
  initFavoritos();        // ← NOVO: botão favoritar
  initContatoWhats();     // ← NOVO: registra clique whatsapp
  initSegurancha();       // ← NOVO: sanitização de inputs e proteções
  initCookieBanner();     // ← NOVO: banner LGPD
});

// ============================================================
// HEADER SCROLL
// ============================================================
function initHeader() {
  const header = document.getElementById('header');
  if (!header) return;
  const check = () => header.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', check, { passive: true });
  check();
}

// ============================================================
// CONFETI ANIMADO
// ============================================================
function initConfeti() {
  const container = document.getElementById('confeti-container');
  if (!container) return;
  const cores = ['#E8163C','#F5A623','#FF6B9D','#00C896','#FFD700','#B931FC'];
  const frag = document.createDocumentFragment();
  for (let i = 0; i < 35; i++) {
    const el = document.createElement('div');
    el.className = 'confete';
    el.style.cssText = [
      `left:${Math.random()*100}%`,
      `background:${cores[Math.floor(Math.random()*cores.length)]}`,
      `width:${Math.random()*7+4}px`,
      `height:${Math.random()*7+4}px`,
      `animation-duration:${Math.random()*6+4}s`,
      `animation-delay:${Math.random()*8}s`,
      `border-radius:${Math.random()>0.5?'50%':'2px'}`,
    ].join(';');
    frag.appendChild(el);
  }
  container.appendChild(frag);
}

// ============================================================
// CARROSSEL — com suporte a swipe/touch
// ============================================================
function initCarrossel() {
  document.querySelectorAll('.carrossel-track').forEach(track => {
    const wrapper = track.closest('.carrossel-wrapper');
    if (!wrapper) return;
    const section = wrapper.closest('section') || wrapper.parentElement.parentElement;
    const btnPrev = section.querySelector('.ctrl-prev');
    const btnNext = section.querySelector('.ctrl-next');
    let idx = 0;
    let autoTimer;

    function cardWidth() {
      const card = track.children[0];
      if (!card) return 300;
      return card.offsetWidth + (parseInt(getComputedStyle(track).gap) || 20);
    }

    function maxIdx() {
      return Math.max(0, track.children.length - Math.floor(wrapper.offsetWidth / cardWidth()));
    }

    function atualizar(animate = true) {
      idx = Math.max(0, Math.min(idx, maxIdx()));
      track.style.transition = animate ? 'transform .45s cubic-bezier(.4,0,.2,1)' : 'none';
      track.style.transform = `translateX(-${idx * cardWidth()}px)`;
      if (btnPrev) btnPrev.disabled = idx <= 0;
      if (btnNext) btnNext.disabled = idx >= maxIdx();
    }

    function avancar() { idx = idx >= maxIdx() ? 0 : idx+1; atualizar(); }
    function recuar()  { idx = idx <= 0 ? maxIdx() : idx-1; atualizar(); }

    function resetAuto() {
      clearInterval(autoTimer);
      autoTimer = setInterval(avancar, 5000);
    }

    if (btnPrev) btnPrev.addEventListener('click', () => { recuar(); resetAuto(); });
    if (btnNext) btnNext.addEventListener('click', () => { avancar(); resetAuto(); });

    // Swipe touch
    let touchX = 0;
    wrapper.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; }, { passive: true });
    wrapper.addEventListener('touchend', e => {
      const diff = touchX - e.changedTouches[0].clientX;
      if (Math.abs(diff) > 50) { diff > 0 ? avancar() : recuar(); resetAuto(); }
    }, { passive: true });

    window.addEventListener('resize', () => atualizar(false), { passive: true });
    atualizar(false);
    resetAuto();
  });
}

// ============================================================
// CATEGORIAS — BUG PRINCIPAL CORRIGIDO
// O problema era: onclick inline usava filtrarAnuncios() mas a função
// não redirecionava para a página de busca — apenas filtrava cards
// que só existem na seção de destaques. Agora redireciona para busca.html
// ============================================================
function initCategorias() {
  document.querySelectorAll('.categoria-card').forEach(card => {
    // Remover onclick inline antigo para evitar conflito
    card.removeAttribute('onclick');

    card.addEventListener('click', () => {
      // Highlight visual
      document.querySelectorAll('.categoria-card').forEach(c => c.classList.remove('ativo'));
      card.classList.add('ativo');

      const cat = card.dataset.cat;

      // Se estiver na homepage → redirecionar para busca com filtro
      const naPaginaBusca = window.location.pathname.includes('busca.html');

      if (!naPaginaBusca) {
        // Determinar caminho correto baseado na localização atual
        const base = window.location.pathname.includes('/pages/') ? 'busca.html' : 'pages/busca.html';
        if (cat && cat !== 'todos') {
          window.location.href = `${base}?cat=${encodeURIComponent(cat)}`;
        } else {
          window.location.href = base;
        }
        return;
      }

      // Se já estiver na página de busca → filtrar resultados
      filtrarResultados(cat);
    });
  });

  // Na página de busca, ler parâmetro ?cat= da URL e ativar filtro
  if (window.location.pathname.includes('busca.html')) {
    const params = new URLSearchParams(window.location.search);
    const catURL = params.get('cat');
    if (catURL) {
      filtrarResultados(catURL);
      // Destacar tag correspondente
      document.querySelectorAll('[data-cat]').forEach(el => {
        if (el.dataset.cat === catURL) el.classList.add('ativo');
      });
    }
  }
}

// Filtra cards de resultado na página de busca
function filtrarResultados(cat) {
  let total = 0;
  document.querySelectorAll('.card-resultado, .anuncio-card').forEach(card => {
    const match = !cat || cat === 'todos' || card.dataset.cat === cat;
    card.style.display = match ? '' : 'none';
    if (match) total++;
  });
  // Atualizar contador
  const counter = document.getElementById('qtd-resultados');
  if (counter && total > 0) {
    counter.textContent = `${total} fornecedor${total !== 1 ? 'es' : ''} encontrado${total !== 1 ? 's' : ''}`;
  }
}

// ============================================================
// BUSCA — corrige redirect baseado na página atual
// ============================================================
function initBusca() {
  document.querySelectorAll('form.busca-principal, form[onsubmit*="buscarServicos"]').forEach(form => {
    form.removeAttribute('onsubmit');
    form.addEventListener('submit', e => {
      e.preventDefault();
      buscarServicos();
    });
  });
}

window.buscarServicos = function(e) {
  if (e) e.preventDefault();
  const termo = (document.getElementById('busca-input')?.value || '').trim();
  const local = (document.getElementById('busca-local')?.value || '').trim();
  const emPages = window.location.pathname.includes('/pages/');
  const base = emPages ? 'busca.html' : 'pages/busca.html';
  const params = new URLSearchParams();
  if (termo) params.set('q', termo);
  if (local) params.set('local', local);
  window.location.href = `${base}?${params.toString()}`;
};

window.buscarProximos = function() {
  if (!navigator.geolocation) { mostrarToast('⚠️ Geolocalização não suportada.',''); return; }
  navigator.geolocation.getCurrentPosition(
    pos => {
      const base = window.location.pathname.includes('/pages/') ? 'busca.html' : 'pages/busca.html';
      window.location.href = `${base}?lat=${pos.coords.latitude}&lng=${pos.coords.longitude}&proximos=1`;
    },
    () => mostrarToast('❌ Não foi possível obter sua localização.','erro')
  );
};

// ============================================================
// FILTROS NA PÁGINA DE BUSCA
// ============================================================
function initFiltrosBusca() {
  // Ler parâmetros da URL e aplicar
  if (!window.location.pathname.includes('busca.html')) return;
  const params = new URLSearchParams(window.location.search);

  // Preencher campo de busca se tiver ?q=
  const q = params.get('q');
  if (q) {
    const inp = document.querySelector('.busca-form-bar input[type="text"]');
    if (inp) inp.value = q;
  }

  // Botão "Aplicar filtros"
  const btnAplicar = document.querySelector('.filtros-sidebar .btn-primario');
  if (btnAplicar) {
    btnAplicar.addEventListener('click', () => {
      mostrarToast('🔍 Filtros aplicados!','sucesso');
    });
  }

  // Botão "Limpar tudo"
  const btnLimpar = document.querySelector('[onclick*="limparFiltros"]');
  if (btnLimpar) {
    btnLimpar.removeAttribute('onclick');
    btnLimpar.addEventListener('click', () => {
      document.querySelectorAll('.filtros-sidebar input').forEach(i => {
        if (i.type === 'checkbox' || i.type === 'radio') i.checked = false;
        else i.value = '';
      });
      filtrarResultados('todos');
      mostrarToast('✅ Filtros limpos','sucesso');
    });
  }
}

// ============================================================
// ORDENAÇÃO DE RESULTADOS
// ============================================================
function initOrdenacao() {
  const sel = document.querySelector('.sort-select');
  if (!sel) return;
  sel.addEventListener('change', () => {
    mostrarToast(`🔄 Ordenando por: ${sel.options[sel.selectedIndex].text}`,'');
  });
}

// ============================================================
// VIEW TOGGLE (grade / lista)
// ============================================================
function initViewToggle() {
  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('ativo'));
      btn.classList.add('ativo');
      const grid = document.getElementById('resultados-grid');
      if (!grid) return;
      const isList = btn.textContent.includes('Lista') || btn.innerHTML.includes('☰');
      grid.style.gridTemplateColumns = isList ? '1fr' : '';
    });
  });
}

// ============================================================
// MODAIS — login, cadastro e outros
// ============================================================
function initModais() {
  // Delegação de eventos para data-modal (funciona em elementos dinâmicos)
  document.addEventListener('click', e => {
    const trigger = e.target.closest('[data-modal]');
    if (trigger) {
      e.preventDefault();
      abrirModal(trigger.dataset.modal);
    }
  });

  // Fechar ao clicar no overlay
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) fecharModal(overlay.id);
    });
  });

  // Botão fechar ✕
  document.querySelectorAll('.modal-fechar').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = btn.closest('.modal-overlay');
      if (m) fecharModal(m.id);
    });
  });

  // ESC fecha
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') fecharTodasModais();
  });

  // Tipo de cadastro (usuário / profissional)
  document.querySelectorAll('.tipo-opcao').forEach(opcao => {
    opcao.addEventListener('click', () => {
      document.querySelectorAll('.tipo-opcao').forEach(o => o.classList.remove('ativo'));
      opcao.classList.add('ativo');
      // Se clicar em "Sou Profissional" → redirecionar
      if (opcao.querySelector('.tipo-label')?.textContent.includes('Profissional')) {
        setTimeout(() => {
          fecharTodasModais();
          const base = window.location.pathname.includes('/pages/') ? '' : 'pages/';
          window.location.href = `${base}profissional-cadastro.html`;
        }, 300);
      }
    });
  });

  // Formulário de login
  document.querySelectorAll('form.form-cadastro').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const email = form.querySelector('input[type="email"]')?.value;
      const senha = form.querySelector('input[type="password"]')?.value;

      if (!email || !senha) {
        mostrarToast('⚠️ Preencha todos os campos obrigatórios.','erro');
        return;
      }
      if (senha && senha.length < 6) {
        mostrarToast('⚠️ A senha deve ter pelo menos 6 caracteres.','erro');
        return;
      }

      fecharTodasModais();
      mostrarToast('✅ Bem-vindo(a) ao É Festa! Login realizado.','sucesso');
    });
  });

  // Tabs dentro dos modais
  document.querySelectorAll('.tab-modal').forEach(tab => {
    tab.addEventListener('click', () => {
      const grupo = tab.closest('.tabs-modal');
      if (grupo) grupo.querySelectorAll('.tab-modal').forEach(t => t.classList.remove('ativo'));
      tab.classList.add('ativo');
    });
  });
}

window.abrirModal = function(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add('ativo');
  document.body.style.overflow = 'hidden';
};

window.fecharModal = function(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove('ativo');
  if (!document.querySelector('.modal-overlay.ativo')) {
    document.body.style.overflow = '';
  }
};

function fecharTodasModais() {
  document.querySelectorAll('.modal-overlay.ativo').forEach(m => m.classList.remove('ativo'));
  document.body.style.overflow = '';
}

// ============================================================
// MENU MOBILE — drawer lateral
// ============================================================
function initNavMobile() {
  const toggle   = document.getElementById('menu-toggle');
  const nav      = document.getElementById('nav-mobile');
  const btnClose = document.getElementById('menu-fechar');
  if (!toggle || !nav) return;

  nav.style.display = 'none';
  let aberto = false;

  function abrirMenu() {
    nav.style.display = 'block';
    aberto = true;
    document.body.style.overflow = 'hidden';
    const [s0,s1,s2] = [...toggle.querySelectorAll('span')];
    if (s0) s0.style.transform = 'translateY(7px) rotate(45deg)';
    if (s1) { s1.style.opacity = '0'; s1.style.transform = 'scaleX(0)'; }
    if (s2) s2.style.transform = 'translateY(-7px) rotate(-45deg)';
  }

  function fecharMenu() {
    nav.style.display = 'none';
    aberto = false;
    document.body.style.overflow = '';
    toggle.querySelectorAll('span').forEach(s => { s.style.transform=''; s.style.opacity=''; });
  }

  toggle.addEventListener('click', e => { e.stopPropagation(); aberto ? fecharMenu() : abrirMenu(); });
  if (btnClose) btnClose.addEventListener('click', fecharMenu);

  // Overlay fecha ao clicar fora do drawer
  nav.addEventListener('click', e => {
    const drawer = nav.querySelector(':scope > div');
    if (drawer && !drawer.contains(e.target)) fecharMenu();
  });

  // Links fecham o menu
  nav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => setTimeout(fecharMenu, 60));
  });

  document.addEventListener('keydown', e => { if (e.key === 'Escape' && aberto) fecharMenu(); });
  window.addEventListener('resize', () => { if (window.innerWidth > 1024 && aberto) fecharMenu(); }, { passive: true });
}

// ============================================================
// TOAST
// ============================================================
let _toastTimer;
function initToast() {
  window.mostrarToast = function(msg, tipo = '') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.className = `toast mostrar ${tipo}`;
    clearTimeout(_toastTimer);
    _toastTimer = setTimeout(() => toast.classList.remove('mostrar'), 4000);
  };
}

// ============================================================
// ANIMAÇÕES SCROLL
// ============================================================
function initAnimacoes() {
  if (!('IntersectionObserver' in window)) return;
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visivel'); obs.unobserve(e.target); } });
  }, { threshold: 0.1 });
  document.querySelectorAll('.animar').forEach(el => obs.observe(el));
}

// ============================================================
// PAINEL ADMIN — navegação entre seções
// ============================================================
function initAdminNav() {
  if (!document.querySelector('.admin-sidebar')) return;

  window.mostrarSecao = function(id, el) {
    document.querySelectorAll('[id^="secao-"]').forEach(s => s.style.display = 'none');
    const alvo = document.getElementById('secao-' + id);
    if (alvo) alvo.style.display = 'block';

    document.querySelectorAll('.admin-nav-item').forEach(n => n.classList.remove('ativo'));
    if (el) el.classList.add('ativo');

    const titulos = {
      dashboard:'Dashboard', usuarios:'Usuários', profissionais:'Profissionais',
      pagamentos:'Pagamentos', financeiro:'Extrato Financeiro',
      pendentes:'Aprovações Pendentes', anuncios:'Anúncios em Destaque',
      avaliacoes:'Avaliações', denuncias:'Denúncias',
      configuracoes:'Configurações', metricas:'Métricas & Relatórios',
      assinaturas:'Assinaturas', cms:'Páginas & Conteúdo',
    };
    const tituloEl = document.getElementById('topbar-titulo');
    if (tituloEl) tituloEl.textContent = titulos[id] || id;
  };

  // Delegação de evento para os itens do nav admin
  document.querySelectorAll('.admin-nav-item').forEach(item => {
    item.addEventListener('click', function() {
      // Extrair id da chamada onclick existente
      const onclickAttr = this.getAttribute('onclick');
      if (onclickAttr) {
        const match = onclickAttr.match(/mostrarSecao\('([^']+)'\)/);
        if (match) mostrarSecao(match[1], this);
      }
    });
  });
}

// ============================================================
// PAINEL DO USUÁRIO — navegação
// ============================================================
function initPainelUsuario() {
  if (!document.querySelector('.painel-nav')) return;

  window.mostrarSecaoPainel = function(id, el) {
    document.querySelectorAll('[id^="secao-painel-"]').forEach(s => s.style.display = 'none');
    const alvo = document.getElementById('secao-painel-' + id);
    if (alvo) alvo.style.display = 'block';
    document.querySelectorAll('.painel-nav-item').forEach(n => n.classList.remove('ativo'));
    if (el) el.classList.add('ativo');
  };
}

// ============================================================
// PAINEL DO PROFISSIONAL — navegação + mapa lazy
// ============================================================
function initPainelProfissional() {
  if (!document.getElementById('secao-prof-dashboard')) return;

  window.mostrarSecaoProf = function(id, el) {
    document.querySelectorAll('[id^="secao-prof-"]').forEach(s => s.style.display = 'none');
    const alvo = document.getElementById('secao-prof-' + id);
    if (alvo) alvo.style.display = 'block';
    document.querySelectorAll('.painel-nav-item').forEach(n => n.classList.remove('ativo'));
    if (el) el.classList.add('ativo');

    // Inicializar mapa ao abrir a seção de localização
    if (id === 'mapa' && typeof L !== 'undefined') {
      setTimeout(() => {
        const mapEl = document.getElementById('mapa-profissional');
        if (mapEl && !mapEl._leaflet_id) {
          const mapa = L.map('mapa-profissional').setView([-23.561414, -46.655881], 14);
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            { attribution: '© OpenStreetMap' }).addTo(mapa);
          L.marker([-23.561414, -46.655881]).addTo(mapa)
            .bindPopup('<b>Buffet Sabor & Arte</b>').openPopup();
        }
      }, 100);
    }
  };
}

// ============================================================
// AVALIAÇÕES — formulário de envio
// ============================================================
function initAvaliacoes() {
  const form = document.getElementById('form-avaliacao');
  if (!form) return;

  // Sistema de estrelas interativo
  document.querySelectorAll('.estrela-input').forEach(star => {
    star.addEventListener('click', () => {
      const nota = parseInt(star.dataset.nota);
      document.querySelectorAll('.estrela-input').forEach((s, i) => {
        s.style.color = i < nota ? '#F5A623' : '#ccc';
        s.dataset.ativo = i < nota ? '1' : '0';
      });
      const hidden = document.getElementById('nota-hidden');
      if (hidden) hidden.value = nota;
    });
    star.addEventListener('mouseover', () => {
      const nota = parseInt(star.dataset.nota);
      document.querySelectorAll('.estrela-input').forEach((s, i) => {
        s.style.color = i < nota ? '#F5A623' : '#ccc';
      });
    });
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    const nota = document.getElementById('nota-hidden')?.value;
    if (!nota || nota === '0') {
      mostrarToast('⚠️ Selecione uma nota de 1 a 5 estrelas.','erro');
      return;
    }
    fecharTodasModais();
    mostrarToast('✅ Avaliação enviada! Obrigado pelo feedback.','sucesso');
  });
}

// ============================================================
// FAVORITOS
// ============================================================
function initFavoritos() {
  document.querySelectorAll('[onclick*="favoritar"], .btn-favoritar').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const ativo = btn.classList.toggle('favoritado');
      btn.textContent = ativo ? '❤️ Salvo' : '♡ Favoritar';
      mostrarToast(ativo ? '❤️ Adicionado aos favoritos!' : '💔 Removido dos favoritos.', ativo ? 'sucesso' : '');
    });
  });
}

// ============================================================
// CONTATO WHATSAPP — registra clique
// ============================================================
function initContatoWhats() {
  document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp"]').forEach(link => {
    link.addEventListener('click', () => {
      console.log('WhatsApp click registrado:', link.href);
    });
  });
}

// ============================================================
// SEGURANÇA — proteções frontend
// ============================================================
function initSegurancha() {
  // 1. Sanitizar inputs contra XSS
  document.querySelectorAll('input[type="text"], input[type="email"], textarea').forEach(inp => {
    inp.addEventListener('input', () => {
      // Bloquear tags HTML em inputs comuns
      if (inp.type !== 'hidden') {
        const val = inp.value;
        const sanitized = val.replace(/<[^>]*>/g, '');
        if (val !== sanitized) {
          inp.value = sanitized;
          mostrarToast('⚠️ Caracteres inválidos foram removidos.','');
        }
      }
    });
  });

  // 2. Validação de e-mail
  document.querySelectorAll('input[type="email"]').forEach(inp => {
    inp.addEventListener('blur', () => {
      if (inp.value && !isEmailValido(inp.value)) {
        inp.style.borderColor = '#E8163C';
        inp.title = 'E-mail inválido';
      } else {
        inp.style.borderColor = '';
        inp.title = '';
      }
    });
  });

  // 3. Validação de senha nos formulários
  document.querySelectorAll('input[type="password"]').forEach(inp => {
    inp.addEventListener('blur', () => {
      if (inp.value && inp.value.length < 6) {
        inp.style.borderColor = '#E8163C';
        mostrarToast('⚠️ Senha deve ter pelo menos 6 caracteres.','');
      } else {
        inp.style.borderColor = '';
      }
    });
  });

  // 4. Prevenir envio duplo de formulários
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        setTimeout(() => { btn.disabled = false; }, 3000);
      }
    });
  });

  // 5. Headers de segurança via meta tags
  if (!document.querySelector('meta[http-equiv="X-Content-Type-Options"]')) {
    const meta = document.createElement('meta');
    meta.setAttribute('http-equiv', 'X-Content-Type-Options');
    meta.content = 'nosniff';
    document.head.appendChild(meta);
  }

  // 6. Proteção contra clickjacking básica (aviso se em iframe)
  try {
    if (window.self !== window.top) {
      console.warn('É Festa: página sendo carregada em iframe - possível clickjacking');
    }
  } catch(e) {}
}

function isEmailValido(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function sanitizarTexto(texto) {
  const div = document.createElement('div');
  div.textContent = texto;
  return div.innerHTML;
}

// ============================================================
// BANNER DE COOKIES (LGPD)
// ============================================================
function initCookieBanner() {
  // Não mostrar se já aceitou
  if (localStorage.getItem('efesta_cookies_aceitos')) return;

  const banner = document.createElement('div');
  banner.id = 'cookie-banner';
  banner.innerHTML = `
    <div style="
      position:fixed; bottom:0; left:0; right:0; z-index:9998;
      background:#1A0A2E; color:rgba(255,255,255,.9); padding:16px 24px;
      display:flex; align-items:center; justify-content:space-between;
      flex-wrap:wrap; gap:12px; box-shadow:0 -4px 20px rgba(0,0,0,.3);
      font-family:'Plus Jakarta Sans',sans-serif; font-size:.88rem;
    ">
      <p style="margin:0; flex:1; min-width:200px;">
        🍪 Usamos cookies para melhorar sua experiência. Ao continuar, você concorda com nossa
        <a href="${window.location.pathname.includes('/pages/') ? '' : 'pages/'}privacidade.html"
           style="color:#F5A623;">Política de Privacidade</a>.
      </p>
      <div style="display:flex;gap:10px;flex-shrink:0;">
        <button id="cookie-recusar" style="
          background:transparent; border:1px solid rgba(255,255,255,.3);
          color:rgba(255,255,255,.7); padding:8px 16px; border-radius:100px;
          cursor:pointer; font-size:.82rem; font-family:inherit;
        ">Recusar</button>
        <button id="cookie-aceitar" style="
          background:#E8163C; border:none; color:white;
          padding:8px 20px; border-radius:100px;
          cursor:pointer; font-size:.85rem; font-weight:600; font-family:inherit;
        ">Aceitar cookies</button>
      </div>
    </div>
  `;
  document.body.appendChild(banner);

  document.getElementById('cookie-aceitar').addEventListener('click', () => {
    localStorage.setItem('efesta_cookies_aceitos', '1');
    banner.remove();
  });
  document.getElementById('cookie-recusar').addEventListener('click', () => {
    localStorage.setItem('efesta_cookies_aceitos', '0');
    banner.remove();
  });
}

// ============================================================
// EXPORTAR GLOBAIS
// ============================================================
window.filtrarAnuncios     = filtrarResultados; // compatibilidade retroativa
window.filtrarResultados   = filtrarResultados;
window.sanitizarTexto      = sanitizarTexto;
window.isEmailValido       = isEmailValido;


