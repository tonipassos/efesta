/**
 * É FESTA — Proteção de Sessão do Painel Admin
 * Arquivo: admin/session-guard.js
 *
 * COMO USAR: Coloque este script como PRIMEIRO script do admin/index.html:
 * <script src="session-guard.js"></script>
 *
 * Ele verifica se o admin está autenticado antes de mostrar qualquer coisa.
 * Se não estiver → redireciona para o login imediatamente.
 */

(function() {
  'use strict';

  const SESSION_KEY = 'ef_admin_session';
  const LOGIN_URL   = 'login.html'; // Caminho relativo ao admin/

  // Ocultar a página imediatamente enquanto verifica
  document.documentElement.style.visibility = 'hidden';

  function verificarSessao() {
    try {
      const sessao = sessionStorage.getItem(SESSION_KEY);

      // Sem sessão → login
      if (!sessao) return redirecionar('SEM_SESSAO');

      const dados = JSON.parse(atob(sessao));

      // Sessão sem dados válidos → login
      if (!dados || !dados.tipo || !dados.expira) return redirecionar('SESSAO_INVALIDA');

      // Tipo incorreto → login
      if (dados.tipo !== 'admin') return redirecionar('TIPO_INVALIDO');

      // Sessão expirada → login
      if (Date.now() > dados.expira) {
        sessionStorage.removeItem(SESSION_KEY);
        return redirecionar('SESSAO_EXPIRADA');
      }

      // Tudo OK → mostrar a página
      document.documentElement.style.visibility = 'visible';
      registrarAtividade(dados.email);

    } catch(e) {
      sessionStorage.removeItem(SESSION_KEY);
      return redirecionar('ERRO_SESSAO');
    }
  }

  function redirecionar(motivo) {
    console.warn('[É Festa Admin] Acesso negado:', motivo);
    window.location.replace(LOGIN_URL + '?motivo=' + motivo);
  }

  function registrarAtividade(email) {
    const log = {
      tipo: 'PAINEL_ACESSO',
      email: email || '',
      timestamp: new Date().toISOString(),
      pagina: window.location.pathname,
    };
    const logs = JSON.parse(localStorage.getItem('ef_admin_logs') || '[]');
    logs.unshift(log);
    localStorage.setItem('ef_admin_logs', JSON.stringify(logs.slice(0, 50)));
  }

  // Botão de logout (para usar em qualquer lugar do painel)
  window.adminLogout = function() {
    if (confirm('Deseja realmente sair do painel?')) {
      sessionStorage.removeItem(SESSION_KEY);
      window.location.replace(LOGIN_URL);
    }
  };

  // Auto-logout por inatividade (30 minutos)
  let timerInatividade;
  const INATIVIDADE_MS = 30 * 60 * 1000;

  function resetarTimer() {
    clearTimeout(timerInatividade);
    timerInatividade = setTimeout(() => {
      alert('Sessão expirada por inatividade. Você será redirecionado para o login.');
      sessionStorage.removeItem(SESSION_KEY);
      window.location.replace(LOGIN_URL);
    }, INATIVIDADE_MS);
  }

  ['mousemove','keydown','click','scroll','touchstart'].forEach(ev => {
    document.addEventListener(ev, resetarTimer, { passive: true });
  });

  // Executar verificação imediatamente
  verificarSessao();
  resetarTimer();

})();
