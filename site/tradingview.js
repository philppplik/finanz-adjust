/* Third-party resources are loaded only after a per-page explicit click. */
(() => {
  for (const button of document.querySelectorAll('[data-tv-load]')) {
    button.addEventListener('click', () => {
      const section = button.closest('.stock-tv');
      const host = section.querySelector('.tradingview-widget-container');
      const symbol = section.dataset.tvSymbol;
      if (!/^[A-Z0-9_]+:[A-Z0-9.\/-]+$/.test(symbol)) return;
      button.disabled = true;
      section.querySelector('[role="status"]').textContent = 'TradingView wird geladen. Falls keine Daten erscheinen, nutze den Quellenlink unten.';
      const widget = document.createElement('div');
      widget.className = 'tradingview-widget-container__widget';
      host.appendChild(widget);
      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js';
      script.async = true;
      script.textContent = JSON.stringify({symbol, width: '100%', height: 282, locale: 'de_DE', colorTheme: 'dark', isTransparent: true});
      script.onerror = () => { section.querySelector('[role="status"]').textContent = 'TradingView konnte nicht geladen werden. Bitte nutze den Quellenlink.'; };
      host.appendChild(script);
    }, {once: true});
  }
})();
