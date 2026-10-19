/* Original FA deterministic models. CommonJS export is for dependency-free tests. */
(function(root){
'use strict';
function monthly(rate){if(!Number.isFinite(rate)||rate<=-100)throw Error('Rendite muss größer als -100 % sein.');return Math.expm1(Math.log1p(rate/100)/12);}
function growth(p, annualFee=0){
  const r=monthly(p.rate), fee=1-Math.pow(1-annualFee/100,1/12), rows=[{year:0,value:p.capital,base:p.capital}];
  let value=p.capital,base=p.capital;
  for(let m=1;m<=p.years*12;m++){value=value*(1+r)*(1-fee)+p.payment;base+=p.payment;if(m%12===0)rows.push({year:m/12,value,base});}
  return {value,base,gain:value-base,rows};
}
function withdrawal(p){
 const r=monthly(p.rate),rows=[{year:0,value:p.capital,base:p.capital}];let value=p.capital,paid=0,depleted=null;
 for(let m=1;m<=p.years*12;m++){value*=1+r;const take=Math.min(p.payment,value);value-=take;paid+=take;if(value<1e-8){value=0;if(depleted===null)depleted=m;}if(m%12===0)rows.push({year:m/12,value,base:Math.max(0,p.capital-p.payment*m)});}
 return {value,paid,depleted,rows};
}
function loan(p){
 const n=p.years*12,r=p.rate/1200,payment=r===0?p.capital/n:p.capital*r/(-Math.expm1(-n*Math.log1p(r)));
 let value=p.capital,interest=0;const rows=[{year:0,value,base:value}];
 for(let m=1;m<=n;m++){const cost=value*r;interest+=cost;value=Math.max(0,value+cost-payment);if(m%12===0)rows.push({year:m/12,value,base:Math.max(0,p.capital*(1-m/n))});}
 return {value:payment,interest,total:p.capital+interest,rows};
}
function calculate(type,p){
 if(type==='sparplan'||type==='zinseszins')return growth({...p,payment:type==='zinseszins'?0:p.payment});
 if(type==='etf-kosten'){const a=growth(p,p.feeA),b=growth(p,p.feeB),gross=growth(p);return {...a,other:b.value,difference:b.value-a.value,gross:gross.value,rows:a.rows.map((x,i)=>({...x,base:b.rows[i].value}))};}
 if(type==='entnahmeplan')return withdrawal(p);
 if(type==='kredit')return loan(p);
 if(type==='inflation'){const rows=[];for(let y=0;y<=p.years;y++)rows.push({year:y,value:p.capital/Math.pow(1+p.rate/100,y),base:p.capital*Math.pow(1+p.rate/100,y)});return {value:rows.at(-1).value,future:rows.at(-1).base,rows};}
 if(type==='rendite'){const value=(Math.pow(p.end/p.capital,1/p.years)-1)*100,total=(p.end/p.capital-1)*100;return {value,total,rows:[{year:0,value:p.capital,base:p.capital},{year:p.years,value:p.end,base:p.capital}]};}
 if(type==='dividenden'){const annual=p.capital*p.rate/100;return {value:annual,monthly:annual/12,rows:[]};}
 throw Error('Unbekanntes Rechenmodell');
}
const api={monthly,growth,withdrawal,loan,calculate};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FACalculatorMath=api;
})(typeof globalThis!=='undefined'?globalThis:this);
