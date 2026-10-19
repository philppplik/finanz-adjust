const assert=require('node:assert/strict'),m=require('./comparison-math.js');const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);
const promo={kind:'promo',promo:3.5,promoMonths:6,base:.6,cap:250000};
close(m.deposit(10000,6,promo).interest,175);close(m.deposit(10000,12,promo).interest,205);close(m.deposit(10000,12,promo,false).interest,60);close(m.deposit(300000,6,promo).interest,4525);
const band={kind:'band',base:2.4,min:10000,cap:500000};close(m.deposit(9999,12,band).interest,0);close(m.deposit(10000,12,band).interest,240);close(m.deposit(500000,12,band).interest,12000);close(m.deposit(500001,12,band).interest,0);
close(m.deposit(200000,12,{kind:'cap',cap:150000,base:2.4}).interest,3600);close(m.deposit(0,12,band).interest,0);
close(m.brokerCost(12,1,0,1000,0),12);close(m.brokerCost(12,5,.25,1000,2),114);assert.throws(()=>m.deposit(-1,12,band));assert.throws(()=>m.deposit(10,1.5,band));console.log('14 comparison math assertions passed');
