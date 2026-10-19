/* Original simplified comparisons. All values are scenarios, not bank calculations. */
(function(root){'use strict';
function deposit(amount,months,offer,eligible=true){
 if(!Number.isFinite(amount)||amount<0||!Number.isInteger(months)||months<1||months>24)throw Error('Ungültiger Betrag oder Zeitraum');
 let total=0;const rows=[];
 for(let month=1;month<=months;month++){
  let rate=offer.base,principal=amount;
  if(offer.kind==='promo'&&eligible&&month<=offer.promoMonths)total+=(Math.min(amount,offer.cap)*offer.promo+Math.max(0,amount-offer.cap)*offer.base)/1200;
  else if(offer.kind==='band'){rate=amount>=offer.min&&amount<=offer.cap?offer.base:0;total+=amount*rate/1200;}
  else{if(offer.kind==='cap')principal=Math.min(amount,offer.cap);total+=principal*rate/1200;}
  rows.push(total);
 }
 return {interest:total,rows};
}
function brokerCost(orders,fixed,percent,volume,monthly){
 if([orders,fixed,percent,volume,monthly].some(x=>!Number.isFinite(x)||x<0))throw Error('Ungültige Kosten');
 return orders*(fixed+volume*percent/100)+monthly*12;
}
const api={deposit,brokerCost};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.FAComparisonMath=api;
})(typeof globalThis!=='undefined'?globalThis:this);
