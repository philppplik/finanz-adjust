/* Local-only filtering. No cookies, trackers, remote requests or dependencies. */
(function(){
'use strict';
const q=document.getElementById('gl-query');if(!q)return;
const topic=document.getElementById('gl-topic'), reset=document.getElementById('gl-reset'), cards=[...document.querySelectorAll('[data-term]')],groups=[...document.querySelectorAll('.gl-letter')],count=document.getElementById('gl-count');
const norm=s=>s.toLowerCase().replace(/ß/g,'ss').replace(/ae/g,'ä').replace(/oe/g,'ö').replace(/ue/g,'ü').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
const params=new URLSearchParams(location.search);q.value=params.get('q')||'';topic.value=params.get('thema')||'';
function filter(){
 const terms=norm(q.value.trim()).split(/\s+/).filter(Boolean);let n=0;
 cards.forEach(c=>{c.hidden=!(terms.every(t=>c.dataset.term.includes(t))&&(!topic.value||c.dataset.category===topic.value));if(!c.hidden)n++;});
 groups.forEach(g=>{g.hidden=![...g.querySelectorAll('[data-term]')].some(c=>!c.hidden);});
 document.querySelectorAll('[data-letter]').forEach(a=>{const hidden=document.getElementById('letter-'+a.dataset.letter).hidden;a.setAttribute('aria-disabled',String(hidden));if(hidden)a.setAttribute('tabindex','-1');else a.removeAttribute('tabindex');});
 count.textContent=n+' von '+cards.length+' Begriffen';document.getElementById('gl-empty').hidden=n>0;reset.hidden=!q.value&&!topic.value;
 const p=new URLSearchParams();if(q.value)p.set('q',q.value);if(topic.value)p.set('thema',topic.value);history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);
}
q.form.addEventListener('submit',ev=>{ev.preventDefault();filter();});q.addEventListener('input',filter);topic.addEventListener('change',filter);reset.addEventListener('click',()=>{q.value='';topic.value='';filter();q.focus();});filter();
})();
