"""Official click-to-load TradingView fallback; no pre-consent network request."""
from html import escape as e
import re

def fallback(stock):
    symbol=stock.get('tv_symbol')
    if not symbol or not re.fullmatch(r'[A-Z0-9_]+:[A-Z0-9.\/-]+',symbol):return ''
    return '<section class="stock-tv stock-panel" data-tv-symbol="'+e(symbol,quote=True)+'"><h2>Kurs-Fallback: TradingView</h2><p>Die API liefert aktuell keinen nutzbaren Kurs. Optional kannst du Kursinformationen direkt von TradingView laden.</p><p class="stock-note">Erst beim Klick wird eine Verbindung zu TradingView hergestellt. Dabei werden IP-Adresse, Seitenadresse, Widgettyp und das Symbol übertragen. Laut Anbieter setzt das Widget keine Cookies. Handelsplatz: '+e(stock['exchange'])+'; die Daten können verzögert oder nur als Tagesendstand vorliegen.</p><button type="button" data-tv-load>TradingView laden und Daten übertragen</button><p role="status" aria-live="polite">Noch nicht geladen.</p><div class="tradingview-widget-container"><div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener noreferrer" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div></div><p class="stock-note">Falls für dieses Symbol keine Widgetdaten verfügbar sind, bleibt der Kurs leer. Keine geschätzten Werte.</p></section>'


def chart(stock):
    """Optional chart for every verified exchange-qualified symbol, even with a quote."""
    symbol = stock.get('tv_symbol')
    if not symbol or not re.fullmatch(r'[A-Z0-9_]+:[A-Z0-9.\/-]+', symbol):
        return ''
    url = 'https://www.tradingview.com/symbols/' + symbol.replace(':', '-') + '/'
    return ('<section id="chart" class="stock-tv stock-panel" data-tv-widget="advanced-chart" data-tv-symbol="' + e(symbol, quote=True) + '">'
            '<h2>Kurschart</h2><p>Optionaler Kursverlauf von TradingView für ' + e(symbol) + '. Der Chart ist unabhängig vom oben angezeigten einzelnen Kursstand.</p>'
            '<p class="stock-note">Erst beim Klick werden IP-Adresse, Seitenadresse, Widgettyp und Symbol an TradingView übertragen. '
            'Laut TradingView setzt das Widget keine Cookies. Die Zustimmung gilt nur für diese geladene Seite. '
            'Kurse können verzögert sein; historische Kurse sind keine Prognose.</p>'
            '<button type="button" data-tv-load>Kurschart laden und Daten übertragen</button>'
            '<p role="status" aria-live="polite">Noch nicht geladen. Ohne Zustimmung bleibt der Chart deaktiviert.</p>'
            '<div class="tradingview-widget-container"><div class="tradingview-widget-copyright">'
            '<a href="' + e(url, quote=True) + '" rel="noopener noreferrer" target="_blank">' + e(symbol) + ' auf TradingView öffnen ↗</a></div></div>'
            '<p class="stock-note">Wenn das Widget keine Daten zeigt, nutze den Quellenlink. Die angezeigte Notierung lautet ' + e(stock['exchange']) + ' · ' + e(stock['currency']) + '.</p></section>')
