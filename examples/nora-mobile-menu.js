/* Nora Mobile: menu lateral acessível. Mantém a navegação e o código de negócio existentes. */
(() => {
  'use strict';
  const BREAKPOINT = '(max-width: 790px)';
  const groups = [
    ['Meu dia', ['today', 'calendar', 'medications', 'shopping']],
    ['Organização e foco', ['organizer', 'focus', 'sleep']],
    ['Nora e apoio', ['assistant', 'smart', 'tools', 'acolhe', 'care', 'messages']],
    ['Acompanhamento', ['history', 'essential', 'pilot']],
    ['Personalizar e ajuda', ['accessibility', 'guide', 'sync', 'settings']]
  ];

  function init() {
    const app = document.getElementById('app-page');
    const header = app?.querySelector('.topbar');
    const bottom = app?.querySelector('.mobile-nav');
    const sidebar = app?.querySelector('.sidebar');
    if (!app || !header || !bottom || !sidebar || document.getElementById('nora-mobile-drawer')) return;

    const topToggle = document.createElement('button');
    topToggle.type = 'button';
    topToggle.className = 'nora-mobile-toggle';
    topToggle.setAttribute('aria-label', 'Abrir menu de navegação');
    topToggle.setAttribute('aria-haspopup', 'dialog');
    topToggle.setAttribute('aria-expanded', 'false');
    topToggle.innerHTML = '<span aria-hidden="true">☰</span>';
    header.insertBefore(topToggle, header.firstChild);

    const bottomToggle = document.createElement('button');
    bottomToggle.type = 'button';
    bottomToggle.className = 'mobile-link nora-mobile-more';
    bottomToggle.setAttribute('aria-label', 'Abrir menu com todas as áreas');
    bottomToggle.setAttribute('aria-haspopup', 'dialog');
    bottomToggle.setAttribute('aria-expanded', 'false');
    bottomToggle.innerHTML = '<span class="nora-mobile-menu-icon" aria-hidden="true">☰</span><small>Menu</small>';
    bottom.appendChild(bottomToggle);

    const drawer = document.createElement('dialog');
    drawer.id = 'nora-mobile-drawer';
    drawer.className = 'nora-mobile-drawer';
    drawer.setAttribute('aria-label', 'Menu de navegação da Nora');
    drawer.innerHTML = `
      <div class="nora-drawer-head">
        <strong><span aria-hidden="true">✳</span> nora<span class="nora-drawer-dot">.</span></strong>
        <button type="button" class="nora-drawer-close" aria-label="Fechar menu">✕</button>
      </div>
      <div class="nora-drawer-search-wrap">
        <label for="nora-menu-search">Encontrar uma função</label>
        <input id="nora-menu-search" type="search" placeholder="Buscar: agenda, foco, saúde..." autocomplete="off">
      </div>
      <nav class="nora-drawer-sections" aria-label="Todas as áreas da Nora"></nav>
      <p class="nora-drawer-empty" hidden>Nenhuma função encontrada.</p>
      <p class="nora-drawer-foot">Seu espaço, do seu jeito. ♡</p>`;
    app.appendChild(drawer);
    const nav = drawer.querySelector('.nora-drawer-sections');
    const search = drawer.querySelector('#nora-menu-search');
    const empty = drawer.querySelector('.nora-drawer-empty');
    const closeButton = drawer.querySelector('.nora-drawer-close');
    const toggles = [topToggle, bottomToggle];
    let lastOpener = topToggle;

    function populate() {
      nav.replaceChildren();
      for (const [heading, ids] of groups) {
        const section = document.createElement('section');
        section.className = 'nora-drawer-group';
        const title = document.createElement('h2');
        title.textContent = heading;
        section.appendChild(title);
        for (const id of ids) {
          if (id === 'pilot' && typeof window.Nora27?.isPilot === 'function' && !window.Nora27.isPilot()) continue;
          const source = sidebar.querySelector(`[data-view="${id}"]`);
          if (!source) continue;
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'nora-drawer-item';
          btn.dataset.view = id;
          const sourceIcon = source.querySelector('[data-icon], svg');
          if (sourceIcon) {
            const icon = sourceIcon.cloneNode(true);
            icon.removeAttribute('id');
            icon.setAttribute('aria-hidden', 'true');
            btn.appendChild(icon);
          }
          const text = document.createElement('span');
          // Uso do nome existente evita duas listas diferentes de funcionalidades.
          text.textContent = source.textContent.trim().replace(/\s+/g, ' ');
          btn.appendChild(text);
          if (source.classList.contains('active')) {
            btn.classList.add('active');
            btn.setAttribute('aria-current', 'page');
          }
          section.appendChild(btn);
        }
        if (section.querySelector('button')) nav.appendChild(section);
      }
      const guided = sidebar.querySelector('[data-action="n13-open"]');
      if (guided) {
        const section = document.createElement('section');
        section.className = 'nora-drawer-group';
        const title = document.createElement('h2');
        title.textContent = 'Acesso facilitado';
        section.appendChild(title);
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'nora-drawer-item';
        btn.dataset.action = 'n13-open';
        btn.textContent = '◉ Modo guiado (botões grandes)';
        section.appendChild(btn);
        nav.appendChild(section);
      }
      filter();
    }

    function filter() {
      const q = search.value.toLocaleLowerCase('pt-BR').trim();
      let visible = 0;
      nav.querySelectorAll('.nora-drawer-group').forEach(group => {
        let count = 0;
        group.querySelectorAll('.nora-drawer-item').forEach(button => {
          const match = button.textContent.toLocaleLowerCase('pt-BR').includes(q);
          button.hidden = !match;
          if (match) { visible++; count++; }
        });
        group.hidden = count === 0;
      });
      empty.hidden = visible !== 0;
    }

    function open(trigger) {
      if (!window.matchMedia(BREAKPOINT).matches || app.classList.contains('hidden')) return;
      lastOpener = trigger;
      search.value = '';
      populate();
      if (!drawer.open) drawer.showModal();
      toggles.forEach(button => button.setAttribute('aria-expanded', 'true'));
      search.focus();
    }
    function close(restoreFocus = true) {
      if (drawer.open) drawer.close();
      toggles.forEach(button => button.setAttribute('aria-expanded', 'false'));
      if (restoreFocus && lastOpener?.isConnected && !app.classList.contains('hidden')) lastOpener.focus();
    }
    toggles.forEach(trigger => trigger.addEventListener('click', () => open(trigger)));
    closeButton.addEventListener('click', () => close());
    search.addEventListener('input', filter);
    drawer.addEventListener('cancel', () => {
      toggles.forEach(button => button.setAttribute('aria-expanded', 'false'));
    });
    drawer.addEventListener('click', event => {
      // O listener global da Nora continua responsável por navegar: não duplicar lógica.
      if (event.target.closest('[data-view], [data-action="n13-open"]')) close(false);
      const bounds = drawer.getBoundingClientRect();
      if (event.clientX > bounds.right || event.clientX < bounds.left || event.clientY > bounds.bottom || event.clientY < bounds.top) close();
    }, true);
    const mq = window.matchMedia(BREAKPOINT);
    mq.addEventListener('change', event => { if (!event.matches) close(false); });
    // Em logout, fechar o diálogo evita bloquear o formulário de login.
    new MutationObserver(() => { if (app.classList.contains('hidden')) close(false); })
      .observe(app, { attributes: true, attributeFilter: ['class'] });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
