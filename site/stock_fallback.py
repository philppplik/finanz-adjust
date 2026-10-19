"""Official click-to-load TradingView fallback; no pre-consent network request."""
from html import escape as e
import re

def fallback(stock):
    symbol=stock.get('tv_symbol')
    if not symbol or not re.fullmatch(r'[A-Z0-9_]+:[A-Z0-9.\/-]+',symbol):return ''
    return '<section class="stock-tv stock-panel" data-tv-symbol="'+e(symbol,quote=True)+'"><h2>Kurs-Fallback: TradingView</h2><p>Die API liefert aktuell keinen nutzbaren Kurs. Optional kannst du Kursinformationen direkt von TradingView laden.</p><p class="stock-note">Erst beim Klick wird eine Verbindung zu TradingView hergestellt. Dabei werden IP-Adresse, Seitenadresse, Widgettyp und das Symbol übertragen. Laut Anbieter setzt das Widget keine Cookies. Handelsplatz: '+e(stock['exchange'])+'; die Daten können verzögert oder nur als Tagesendstand vorliegen.</p><button type="button" data-tv-load>TradingView laden und Daten übertragen</button><p role="status" aria-live="polite">Noch nicht geladen.</p><div class="tradingview-widget-container"><div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener noreferrer" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div></div><p class="stock-note">Falls für dieses Symbol keine Widgetdaten verfügbar sind, bleibt der Kurs leer. Keine geschätzten Werte.</p></section>'
