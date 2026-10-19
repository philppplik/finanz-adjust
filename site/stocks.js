/* Local-only search. No third-party request, cookie, or persistent storage. */
(() => {
  const form = document.querySelector('.stock-search');
  const input = document.querySelector('#stock-query');
  const cards = [...document.querySelectorAll('[data-stock]')];
  if (!form || !input || !cards.length) return;
  const normalize = value => value.toLocaleLowerCase('de').replaceAll('ß', 'ss').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const filter = () => {
    const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    for (const card of cards) {
      const match = terms.every(term => card.dataset.stock.includes(term));
      card.hidden = !match;
      if (match) count++;
    }
    document.querySelector('#stock-count').textContent = `${count} ${count === 1 ? 'Aktie' : 'Aktien'}`;
    document.querySelector('#stock-empty').hidden = count !== 0;
  };
  input.value = new URLSearchParams(location.search).get('q') || '';
  input.addEventListener('input', filter);
  form.addEventListener('submit', event => { event.preventDefault(); filter(); });
  filter();
})();
