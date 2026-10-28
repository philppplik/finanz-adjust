/* Third-party resources are loaded only after a per-page explicit click. */
(() => {
  for (const button of document.querySelectorAll('[data-tv-load]')) {
    button.addEventListener('click', () => {
      const section = button.closest('.stock-tv');
      const host = section.querySelector('.tradingview-widget-container');
      const symbol = section.dataset.tvSymbol;
      if (!/^[A-Z0-9_]+:[A-Z0-9.\/-]+$/.test(symbol)) return;
      const kind = section.dataset.tvWidget || 'symbol-info';
      button.disabled = true;
      section.querySelector('[role="status"]').textContent = 'TradingView wird geladen. Falls keine Daten erscheinen, nutze den Quellenlink unten.';
      const widget = document.createElement('div');
      widget.className = 'tradingview-widget-container__widget';
      host.appendChild(widget);
      const script = document.createElement('script');
      script.async = true;
      if (kind === 'advanced-chart') {
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
        script.textContent = JSON.stringify({symbol, interval: 'D', width: '100%', height: 420, locale: 'de_DE', colorTheme: 'light', isTransparent: true, allow_symbol_change: false, hide_side_toolbar: true, withdateranges: false});
      } else {
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js';
        script.textContent = JSON.stringify({symbol, width: '100%', height: 282, locale: 'de_DE', colorTheme: 'dark', isTransparent: true});
      }
      script.onerror = () => { section.querySelector('[role="status"]').textContent = 'TradingView konnte nicht geladen werden. Bitte nutze den Quellenlink.'; };
      host.appendChild(script);
    }, {once: true});
  }
})();
