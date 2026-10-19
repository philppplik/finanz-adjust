/* Local-only UI: no fetch, telemetry, cookies or persistent storage. */
(function(){
'use strict';
const host=document.querySelector('[data-calculator]');if(!host)return;
const type=JSON.parse(host.dataset.calculator).type,form=document.getElementById('calc-form'),fields=[...form.querySelectorAll('[data-min]')],error=document.getElementById('calc-error'),summary=document.getElementById('calc-summary'),chart=document.getElementById('calc-chart'),detail=document.getElementById('calc-detail');
const axis=new Intl.NumberFormat('de-DE',{notation:'compact',maximumFractionDigits:1});
const euro=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:2}),num=new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}),pct=x=>num.format(x)+' %',money=x=>euro.format(x);
// German grouped notation only; no silent parseFloat truncation or US-format ambiguity.
function parse(s){s=s.trim().replace(/[\s\u00a0\u202f]/g,'');if(!/^-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d{1,8})?$/.test(s))return NaN;return Number(s.replace(/\./g,'').replace(',','.'));}
function inputs(){const p={};for(const f of fields){f.setCustomValidity('');f.removeAttribute('aria-invalid');const v=parse(f.value),min=Number(f.dataset.min),max=Number(f.dataset.max);if(!Number.isFinite(v)||v<min||v>max||(f.dataset.integer==='true'&&!Number.isInteger(v))){const msg='Bitte '+num.format(min)+' bis '+num.format(max)+(f.dataset.integer==='true'?' als ganze Zahl':' in deutscher Schreibweise')+' eingeben.';f.setCustomValidity(msg);f.setAttribute('aria-invalid','true');throw {message:msg,field:f};}p[f.name]=v;}return p;}
for(const f of fields){const hint=document.createElement('small');hint.id=f.id+'-bounds';hint.textContent=num.format(Number(f.dataset.min))+' bis '+num.format(Number(f.dataset.max))+(f.dataset.integer==='true'?' · ganze Jahre':'');f.after(hint);f.setAttribute('aria-describedby','calc-format '+hint.id);f.addEventListener('input',()=>f.setCustomValidity(''));}
form.noValidate=true;document.getElementById('calc-controls').disabled=false;
function svg(rows,labelA,labelB){
 const max=Math.max(1,...rows.flatMap(x=>[x.value,x.base])),min=Math.min(0,...rows.flatMap(x=>[x.value,x.base])),range=max-min||1,w=650,h=245,left=76,right=20,top=20,bottom=34,last=rows.at(-1).year||1;
 const x=y=>left+y/last*(w-left-right),y=v=>top+(max-v)/range*(h-top-bottom),points=k=>rows.map(r=>x(r.year).toFixed(2)+','+y(r[k]).toFixed(2)).join(' ');
 let guides='';for(let i=0;i<=3;i++){const v=min+range*i/3,yy=y(v);guides+='<line x1="'+left+'" y1="'+yy+'" x2="'+(w-right)+'" y2="'+yy+'" stroke="currentColor" opacity=".12"/><text x="'+(left-8)+'" y="'+(yy+4)+'" text-anchor="end">'+num.format(v/1000)+' T€</text>';}
 return '<svg viewBox="0 0 '+w+' '+h+'" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">Modellverlauf in Euro</title><desc id="chart-desc">'+labelA+' und '+labelB+'. Jahreswerte stehen auch in der Tabelle darunter. Keine Prognose.</desc>'+guides+'<polyline points="'+points('base')+'" fill="none" stroke="var(--calc-alt)" stroke-width="2.5" stroke-dasharray="7 5"/><polyline points="'+points('value')+'" fill="none" stroke="var(--ac)" stroke-width="3.5"/><text x="'+left+'" y="'+(h-9)+'">Start</text><text x="'+(w-right)+'" y="'+(h-9)+'" text-anchor="end">Jahr '+last+'</text></svg><figcaption><span><i></i>'+labelA+'</span><span><i class="calc-dashed"></i>'+labelB+'</span></figcaption>';
}
let current=null;
function render(focusError=false){try{
 const p=inputs(),r=FACalculatorMath.calculate(type,p);if(!Number.isFinite(r.value))throw Error('Mit diesen Werten ist keine endliche Berechnung möglich.');current=p;error.hidden=true;
 let headline='Modell-Endvermögen',primary=money(r.value),stats=[],a='Vermögen',b='Einzahlungen',note='Nominale Werte, ohne Steuern. Keine Prognose.';
 if(type==='sparplan'||type==='zinseszins'){stats=[['Eingezahlt',money(r.base)],['Modell-Ertrag',money(r.gain)]];}
 if(type==='etf-kosten'){headline='Endvermögen mit Kostenquote A';a='Variante A';b='Variante B';stats=[['Endvermögen B',money(r.other)],['Differenz B − A',money(r.difference)],['Ohne Kosten (Modell)',money(r.gross)]];}
 if(type==='entnahmeplan'){headline='Restvermögen';b='Ohne Rendite (rechnerisch)';stats=[['Tatsächlich entnommen',money(r.paid)],['Kapital aufgezehrt',r.depleted===null?'Nicht im Zeitraum':'Nach '+r.depleted+' Monaten']];}
 if(type==='inflation'){headline='Kaufkraft in heutigen Euro';a='Heutige Kaufkraft';b='Künftiges Preisäquivalent';stats=[['Nötig für gleiche Kaufkraft',money(r.future)],['Kaufkraft-Veränderung',money(r.value-p.capital)]];note='Konstante Inflationsannahme. Keine aktuelle Inflationsmessung.';}
 if(type==='kredit'){headline='Monatliche Modellrate';a='Restschuld';b='Lineare Vergleichstilgung';stats=[['Zinsen insgesamt',money(r.interest)],['Rückzahlung insgesamt',money(r.total)]];note='Vollständige Tilgung, konstanter nominaler Sollzins, keine Gebühren. Kein Kreditangebot.';}
 if(type==='rendite'){headline='Jährliche Rendite (CAGR)';primary=pct(r.value);a='Anfangs- und Endwert';b='Anfangskapital';stats=[['Gesamtrendite',pct(r.total)],['Wertveränderung',money(p.end-p.capital)]];note='Ohne zwischenzeitliche Ein- oder Auszahlungen. Die Verbindung ist nur eine Illustration, kein tatsächlicher Kursverlauf.';}
 if(type==='dividenden'){headline='Brutto-Dividende pro Jahr';stats=[['Rechnerisch pro Monat',money(r.monthly)],['Angenommene Rendite',pct(p.rate)]];note='Monatsdurchschnitt, kein Auszahlungstermin. Vor allen Steuern und Kosten; Dividenden nicht garantiert.';}
 summary.innerHTML='<p class="calc-result-label">'+headline+'</p><h2 class="calc-result">'+primary+'</h2><dl class="calc-stats">'+stats.map(([k,v])=>'<div><dt>'+k+'</dt><dd>'+v+'</dd></div>').join('')+'</dl><p class="calc-output-note">'+note+'</p>';
 chart.innerHTML=r.rows.length?svg(r.rows,a,b):'<div class="calc-dividend"><span>12 ×</span><b>'+money(r.monthly)+'</b><p>rechnerischer Monatsdurchschnitt brutto</p></div>';
 detail.innerHTML=r.rows.length?'<details><summary>Jahreswerte als Tabelle</summary><div class="calc-table"><table><caption>Modellwerte zum Jahresende, in Euro</caption><thead><tr><th scope="col">Jahr</th><th scope="col">'+a+'</th><th scope="col">'+b+'</th></tr></thead><tbody>'+r.rows.map(x=>'<tr><th scope="row">'+x.year+'</th><td>'+money(x.value)+'</td><td>'+money(x.base)+'</td></tr>').join('')+'</tbody></table></div></details>':'';
 return true;
 }catch(err){current=null;error.textContent=err.message||'Bitte Eingaben prüfen.';error.hidden=false;summary.innerHTML='<p>Keine aktuelle Berechnung. Bitte Eingaben korrigieren.</p>';chart.innerHTML='';detail.innerHTML='';if(focusError&&err.field)err.field.focus();return false;}}
form.addEventListener('submit',ev=>{ev.preventDefault();document.getElementById('calc-share-box').hidden=true;render(true);});
form.addEventListener('reset',()=>{setTimeout(()=>{for(const f of fields){f.setCustomValidity('');f.removeAttribute('aria-invalid');}document.getElementById('calc-share-box').hidden=true;history.replaceState(null,'',location.pathname);render();},0);});
document.getElementById('calc-share').addEventListener('click',()=>{if(!render(true))return;const url=new URL(location.href);url.search='';url.hash='';for(const [k,v] of Object.entries(current))url.searchParams.set(k,String(v));history.replaceState(null,'',url.pathname+url.search);const input=document.getElementById('calc-link');input.value=url.href;document.getElementById('calc-share-box').hidden=false;input.focus();input.select();});
const params=new URLSearchParams(location.search);for(const f of fields)if(params.has(f.name)){const value=params.get(f.name);f.value=/^-?\d+(?:\.\d+)?$/.test(value)?new Intl.NumberFormat('de-DE',{maximumFractionDigits:8}).format(Number(value)):value;}
render();
})();
