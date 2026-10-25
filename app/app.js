const API_URL = "https://script.google.com/macros/s/AKfycbwt1E1CC6EDlvwmblrzM6vtK4WmYCrmpIhj_SV7NUvMmcsNweZXcr0E4M1X83dvsE7WlQ/exec";
const APP_VERSION = "28";
function appInstallId_(){var k="oddsklubben-install-id",v=localStorage.getItem(k);if(!v){v="ok-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,10);localStorage.setItem(k,v)}return v}
function logApp_(eventName,page,detail){if(!API_URL)return;try{fetch(API_URL,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify({type:"app_log",event:eventName,page:page||"",installation:appInstallId_(),version:APP_VERSION,detail:detail||""})}).catch(function(){})}catch(e){}}

const players={Pingvinus:"🐧 Pingvinus",King:"👑 King",Gorilla:"🦍 Gorilla",Kaninus:"🐰 Kaninus",Kardinalus:"🙏 Kardinalus"};
let program=[
{w:43,r:"Supercup",m:["Kardinalus – King"],toto:["Pingvinus","Gorilla","Kaninus"]},
{w:44,r:"Runde 1",m:["Kardinalus – Kaninus","Gorilla – King"],free:"Pingvinus"},
{w:45,r:"Runde 2",m:["Kardinalus – Pingvinus","Kaninus – Gorilla"],free:"King"},
{w:46,r:"Runde 3 · Julecup 1/4",m:["King – Pingvinus","Kardinalus – Gorilla"],free:"Kaninus"},
{w:47,r:"Pokal · indledende · Julecup 2/4",m:["Pingvinus – Kaninus"],free:"King · Gorilla · Kardinalus"},
{w:48,r:"Runde 4 · Julecup 3/4",m:["Gorilla – Pingvinus","King – Kaninus"],free:"Kardinalus"},
{w:49,r:"Runde 5 · Julecup 4/4",m:["Pingvinus – Kaninus","Kardinalus – King"],free:"Gorilla"},
{w:50,r:"Runde 6",m:["Kaninus – Kardinalus","King – Gorilla"],free:"Pingvinus"},
{w:51,r:"JULEFERIE",m:[]},{w:52,r:"JULEFERIE",m:[]},{w:53,r:"JULEFERIE",m:[]},
{w:1,r:"Runde 7",m:["Pingvinus – Kardinalus","Gorilla – Kaninus"],free:"King"},
{w:2,r:"Pokal · semifinaler",m:["King – vinder af Pingvinus/Kaninus","Gorilla – Kardinalus"],free:"Taberen af Pingvinus/Kaninus"},
{w:3,r:"Runde 8",m:["Pingvinus – King","Gorilla – Kardinalus"],free:"Kaninus"},
{w:4,r:"Fri Odds",m:[],allFree:true},{w:5,r:"Runde 9",m:["Pingvinus – Gorilla","Kaninus – King"],free:"Kardinalus"},
{w:6,r:"Fri Odds",m:[],allFree:true},{w:7,r:"VINTERFERIE",m:[]},{w:8,r:"Pokalfinale",m:["TBD – TBD"]},{w:9,r:"Fri Odds",m:[],allFree:true},
{w:10,r:"Runde 10",m:["Kaninus – Pingvinus","King – Kardinalus"],free:"Gorilla"},{w:11,r:"Fri Odds",m:[],allFree:true},{w:12,r:"Fri Odds · sæsonafslutning",m:[],allFree:true}];
let pos=initialPosition();
let savedEntries=[];
let backendWriteEnabled=false;
function isoWeek(d=new Date()){const x=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));x.setUTCDate(x.getUTCDate()+4-(x.getUTCDay()||7));const y=new Date(Date.UTC(x.getUTCFullYear(),0,1));return Math.ceil((((x-y)/86400000)+1)/7)}
function initialPosition(){const now=new Date(),w=isoWeek(now),y=now.getFullYear();const i=program.findIndex(x=>x.w===w);if(i>=0 && (y===2026||y===2027))return i;return 0}
function updateHomeNextRound_(){
  var panel=document.querySelector("#home .next-round");
  if(!panel||!program.length)return;
  var i=initialPosition(),round=program[i]||program[0];
  var top=panel.querySelector(".next-round-top b");
  var title=panel.querySelector("strong");
  var extra=panel.querySelector(".next-round-line");
  var note=panel.querySelector("small");
  if(top)top.textContent="Uge "+round.w;
  var matches=Array.isArray(round.m)?round.m:[];
  if(title)title.textContent=(round.r||"Sæsonprogram")+(matches.length?" · "+matches.join(" · "):"");
  var details=[];
  if(Array.isArray(round.toto)&&round.toto.length)details.push("Toto Cup · "+round.toto.join(" · "));
  if(round.allFree)details.push("Fri Odds · alle");
  else if(round.free)details.push("Fri Odds · "+round.free);
  if(extra){extra.textContent=details.join(" · ");extra.hidden=!details.length}
  if(note)note.textContent="Sæson 2026/27 · fra sæsonprogrammet";
}
function names(match){return match.split(" – ").filter(n=>players[n]).map(n=>players[n])}
function moneyField(name){return `<div class="player"><label>${players[name]||name}</label><input data-kind="money" data-player="${name}" inputmode="decimal" placeholder="Kr" aria-label="Gevinst ${name}"></div>`}
function card(match,i){const ns=match.split(" – ").filter(n=>players[n]);return `<section class="card ${match.includes("TBD")?"cup":""}" data-match="${match}"><div class="tag">Kamp ${i+1}</div><div class="match">${match}</div>${ns.map(moneyField).join("")}<div class="result"><label>Resultat</label><input data-kind="result" inputmode="text" autocapitalize="off" autocomplete="off" placeholder="fx 2-1" aria-label="Resultat"></div></section>`}
function render(){const x=program[pos];document.getElementById("week").textContent=x.w;document.getElementById("round").textContent=x.r;document.getElementById("subtitle").textContent="Sæson 2026/27";document.getElementById("cards").innerHTML=x.m.length?x.m.map(card).join(""):`<div class="empty">${x.r==="EFTERÅRSFERIE"?"🍂 Efterårsferie":x.r==="VINTERFERIE"?"❄️ Vinterferie":x.r==="JULEFERIE"?"🎄 Juleferie":"🍺 Ingen faste kampe denne uge"}</div>`;if(x.free){var freeNames=String(x.free).split("·").map(function(n){return n.trim()}).filter(function(n){return players[n]});var freeLabel=freeNames.length?freeNames.map(function(n){return players[n]}).join(" · "):String(x.free);var freeFields=freeNames.map(moneyField).join("");document.getElementById("cards").innerHTML+=`<section class="card" data-match="Fri Odds"><div class="tag">Fri Odds</div><div class="match">${freeLabel}</div>${freeFields}</section>`;}if(x.allFree)document.getElementById("cards").innerHTML=`<section class="card" data-match="Alle Fri odds"><div class="tag">Fri Odds · alle</div><div class="match">Hele klubben</div>${Object.keys(players).map(moneyField).join("")}</section>`;if(x.toto)document.getElementById("cards").innerHTML+=`<section class="card" data-match="Toto Cup"><div class="tag">Toto Cup · Fri Odds</div><div class="match">De tre øvrige spillere</div>${x.toto.map(moneyField).join("")}</section>`;document.getElementById("save").style.display=x.r.includes("FERIE")?"none":"block";document.getElementById("notice").textContent="";if(!restoreDraft_(x.w))restoreSaved_(x)}
document.getElementById("prev").onclick=()=>{pos=(pos-1+program.length)%program.length;render()};document.getElementById("next").onclick=()=>{pos=(pos+1)%program.length;render()};
function parseMoney(v){if(!v.trim())return null;const n=Number(v.trim().replace(/\s/g,"").replace(",", "."));return Number.isFinite(n)&&n>=0?n:null}
function validResult(v){return /^\d+\s*[-–]\s*\d+$/.test(v.trim())}
function validate(){const x=program[pos],inputs=[...document.getElementById("cards").querySelectorAll("input")],errors=[];inputs.forEach(el=>el.classList.remove("bad"));inputs.forEach(el=>{const isResult=el.dataset.kind==="result",value=el.value.trim();if(!value)return;const ok=isResult?validResult(value):parseMoney(value)!==null;if(!ok){el.classList.add("bad");errors.push(el)}});if(x.m.some(m=>m.includes("TBD"))){document.getElementById("notice").textContent="Pokalfinalen afventer semifinalernes resultater.";return false}if(errors.length){document.getElementById("notice").textContent="Tjek de markerede felter.";errors[0].focus();return false}const data=summary();if(!data.entries.some(function(e){return e.money!==null||e.result})){document.getElementById("notice").textContent="Indtast mindst ét beløb eller resultat før du gemmer.";return false}return true}
function restoreSaved_(x){var rows=savedEntries.filter(function(e){return Number(e.week)===Number(x.w)&&e.round===x.r});if(!rows.length)return false;document.getElementById("cards").querySelectorAll(".card[data-match]").forEach(function(card){var match=card.dataset.match;card.querySelectorAll('[data-kind="money"]').forEach(function(el){var e=rows.find(function(v){return v.match===match&&v.player===el.dataset.player});if(e&&e.money!=="")el.value=String(e.money).replace(".",",")});var re=card.querySelector('[data-kind="result"]');if(re){var e=rows.find(function(v){return v.match===match&&v.result});if(e)re.value=e.result}});return true}
function restoreDraft_(w){try{const d=JSON.parse(localStorage.getItem("oddsklubben-draft-"+w)||"null");if(!d||!Array.isArray(d.entries)||d.round!==program[pos].r)return false;document.getElementById("cards").querySelectorAll(".card[data-match]").forEach(card=>{const match=card.dataset.match;card.querySelectorAll('[data-kind="money"]').forEach(el=>{const e=d.entries.find(x=>x.match===match&&x.player===el.dataset.player);if(e&&e.money!==null)el.value=String(e.money).replace(".",",")});const re=card.querySelector('[data-kind="result"]');if(re){const e=d.entries.find(x=>x.match===match&&x.result);if(e)re.value=e.result}});return true}catch(_){return false}}
function summary(){const x=program[pos],entries=[];document.getElementById("cards").querySelectorAll(".card[data-match]").forEach(card=>{const match=card.dataset.match,resultEl=card.querySelector('[data-kind="result"]'),result=resultEl?resultEl.value.trim():"";card.querySelectorAll('[data-kind="money"]').forEach(el=>entries.push({match,player:el.dataset.player,money:parseMoney(el.value),result}))});return {week:x.w,round:x.r,entries}}
document.getElementById("cards").addEventListener("input",function(e){
  if(!e.target.matches('input[data-kind="money"],input[data-kind="result"]'))return;
  try{var data=summary();localStorage.setItem("oddsklubben-draft-"+data.week,JSON.stringify(data))}catch(_){}
});
document.getElementById("save").onclick=()=>{if(!validate())return;const data=summary();document.getElementById("notice").innerHTML=`<div class="confirm"><strong>Klar til at gemme uge ${data.week}</strong><span>Kontrollér oplysningerne og tryk Bekræft.</span><button id="confirmSave">Bekræft og gem</button><button id="cancelSave" class="secondary">Ret oplysninger</button></div>`;document.getElementById("cancelSave").onclick=()=>document.getElementById("notice").textContent="";function saveRoundParts_(data){const normal=data.entries.filter(e=>e.match!=="Toto Cup"),toto=data.entries.filter(e=>e.match==="Toto Cup"),parts=[];if(normal.length)parts.push({week:data.week,round:data.round,entries:normal});if(toto.length)parts.push({week:data.week,round:"Toto Cup",entries:toto});return parts.reduce((p,part)=>p.then(()=>fetch(API_URL,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify(part)}).then(r=>r.json()).then(out=>{if(!out.ok)throw Error(part.round+": "+(out.error||"Fejl"));return out.status==="written"}).then(written=>({written}))),Promise.resolve({written:true})).then(out=>({json:()=>Promise.resolve({ok:true,status:out.written?"written":"dry-run"})}))}
document.getElementById("confirmSave").onclick=()=>{localStorage.setItem("oddsklubben-draft-"+data.week,JSON.stringify(data));const btn=document.getElementById("confirmSave");btn.disabled=true;btn.textContent="Gemmer…";if(!API_URL){document.getElementById("notice").innerHTML='<div class="success">✓ Gemt som lokal kladde.<br><small>Backend er endnu ikke deployet.</small></div>';return}saveRoundParts_(data).then(function(res){return res.json()}).then(function(out){if(!out.ok)throw new Error(out.error||"Ukendt fejl");if(out.status==="written"&&localStorage.getItem("oddsklubben-draft-"+data.week)===JSON.stringify(data))localStorage.removeItem("oddsklubben-draft-"+data.week);if(out.status==="written"){window.refreshManagerStandings();window.refreshAllTimeLeader();}document.getElementById("notice").innerHTML=`<div class="success">✓ ${out.status==="written"?"Gemt i Google Sheet":"Test godkendt (dry-run)"}.<br><small>Uge ${data.week} · ${data.round}${backendWriteEnabled?"":" · live-skrivning er slukket"}</small></div>`}).catch(function(err){document.getElementById("notice").innerHTML=`<div class="error">Kunne ikke gemme: ${String(err.message||err)}<br><small>Din lokale kladde er bevaret.</small></div>`})}};render();updateHomeNextRound_();
fetch(API_URL).then(function(res){return res.json()}).then(function(out){if(out && out.ok && Array.isArray(out.program) && out.program.length){backendWriteEnabled=out.writeEnabled===true;var status=document.getElementById("sheetWriteStatus");if(status)status.textContent=backendWriteEnabled?"✓ Google Sheet-forbindelse aktiv · gemning skriver til arket":"⚠️ Google Sheet er forbundet · gemning er i testtilstand";program=out.program;savedEntries=Array.isArray(out.saved)?out.saved:[];paintManagerFromSaved_(savedEntries);paintAllTimeFromSaved_(savedEntries);paintSeasonBalance_(savedEntries);paintWeeklyFinance_(savedEntries);paintHattricks_(savedEntries);pos=initialPosition();render();updateHomeNextRound_();if(window.renderSeasonProgram)window.renderSeasonProgram()}else{var status=document.getElementById("sheetWriteStatus");if(status)status.textContent="⚠️ Kunne ikke bekræfte Google Sheet-forbindelsen"}}).catch(function(){var status=document.getElementById("sheetWriteStatus");if(status)status.textContent="⚠️ Kunne ikke bekræfte Google Sheet-forbindelsen"});
function weeklyFinance_(rows){
  var names=Object.keys(players),weeks=new Map();
  (rows||[]).forEach(function(e){
    var w=Number(e.week),n=String(e.player||"").replace(/^[^A-Za-zÆØÅæøå]+/,"").trim();
    if(!Number.isInteger(w)||!((w>=43&&w<=53)||(w>=1&&w<=12))||!names.includes(n))return;
    var raw=String(e.money==null?"":e.money).trim(),amount=raw?parseMoney(raw):null;
    if(amount===null&&!String(e.result||"").trim())return;
    if(!weeks.has(w))weeks.set(w,Object.fromEntries(names.map(function(x){return [x,0]})));
    if(amount!==null)weeks.get(w)[n]+=amount;
  });
  var ordered=[...weeks.keys()].sort(function(a,b){return (a>=43?a:a+53)-(b>=43?b:b+53)});
  var member=Object.fromEntries(names.map(function(x){return [x,0]})),cumulative=0;
  var series=ordered.map(function(w,i){
    var win=names.reduce(function(v,n){member[n]+=weeks.get(w)[n]-80;return v+weeks.get(w)[n]},0);
    cumulative+=win;
    return {week:w,win:win,total:cumulative,stake:(i+1)*400};
  });
  return {series:series,members:names.map(function(n){return {name:n,balance:member[n]}}),total:names.reduce(function(v,n){return v+member[n]},0)};
}
function weeklyFinanceSvg_(host,w,h){
  var svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
  svg.setAttribute("viewBox","0 0 "+w+" "+h);svg.setAttribute("role","img");
  function add(tag,attrs,caption,parent){
    var node=document.createElementNS("http://www.w3.org/2000/svg",tag);
    Object.keys(attrs||{}).forEach(function(k){node.setAttribute(k,attrs[k])});
    if(caption!==undefined)node.textContent=caption;
    (parent||svg).appendChild(node);return node;
  }
  host.replaceChildren(svg);return {svg:svg,add:add};
}
function paintWeeklyFinance_(rows){
  var club=document.getElementById("weeklyClubChart"),member=document.getElementById("weeklyMemberChart");
  if(!club||!member||!Array.isArray(rows))return;
  var stats=weeklyFinance_(rows),fmt=new Intl.NumberFormat("da-DK",{maximumFractionDigits:2});
  // The full 2026/27 calendar is shown even before every week has been played.
  // Only recorded weeks affect member balances; the purple line is the planned stake.
  var seasonWeeks=[43,44,45,46,47,48,49,50,51,52,1,2,3,4,5,6,7,8,9,10,11,12];
  var actualByWeek=new Map(stats.series.map(function(d){return [d.week,d]}));
  var accumulated=0,series=seasonWeeks.map(function(w,i){
    var saved=actualByWeek.get(w),win=saved?saved.win:0;
    accumulated+=win;
    return {week:w,win:win,total:accumulated,stake:(i+1)*400,recorded:!!saved};
  });
  var W=430,H=245,l=49,r=13,t=17,b=50,baseY=H-b;
  var chart=weeklyFinanceSvg_(club,W,H),add=chart.add;
  chart.svg.setAttribute("aria-label","Alle 22 spilleuger i 2026/27. Faktiske ugegevinster, akkumulerede gevinster og planlagt indsats");
  var high=Math.max(400,...series.flatMap(function(x){return [x.win,x.total,x.stake]}))*1.08;
  var y=function(v){return baseY-(v/high)*(baseY-t)};
  [0,.5,1].forEach(function(f){var yy=y(high*f);add("line",{x1:l,y1:yy,x2:W-r,y2:yy,stroke:"#dbe2dd"});add("text",{x:l-6,y:yy+4,"text-anchor":"end",fill:"#667469","font-size":10},fmt.format(high*f))});
  var step=(W-l-r)/series.length,bw=Math.min(12,step*.68);
  series.forEach(function(d,i){
    var x=l+step*(i+.5);
    if(d.win>0){
      var bar=add("rect",{x:x-bw/2,y:y(d.win),width:bw,height:baseY-y(d.win),rx:2,fill:"#2874b4"});
      add("title",{},"Uge "+d.week+": "+fmt.format(d.win)+" kr vundet",bar);
    }
    add("text",{x:x,y:H-26,"text-anchor":"end",transform:"rotate(-55 "+x+" "+(H-26)+")",fill:"#607068","font-size":10},"U"+d.week);
  });
  [{key:"total",color:"#d85c55"},{key:"stake",color:"#884fce"}].forEach(function(k){
    var points=series.map(function(d,i){return (l+step*(i+.5))+","+y(d[k.key])}).join(" ");
    add("polyline",{points:points,fill:"none",stroke:k.color,"stroke-width":2.5,"stroke-linejoin":"round"});
    series.forEach(function(d,i){
      var dot=add("circle",{cx:l+step*(i+.5),cy:y(d[k.key]),r:2.3,fill:k.color});
      add("title",{},"Uge "+d.week+": "+fmt.format(d[k.key])+" kr "+(k.key==="stake"?"planlagt indsats":"akkumuleret gevinst"),dot);
    });
  });
  var note=document.createElement("p");
  note.textContent="Blå: registrerede gevinster · Rød: faktisk samlet gevinst (videreføres) · Lilla: planlagt indsats, 400 kr pr. uge.";
  club.appendChild(note);
  var M=weeklyFinanceSvg_(member,W,236),ma=M.add;M.svg.setAttribute("aria-label","Sæsonsaldo for hver spiller og Oddsklubben samlet");
  var entries=stats.members.concat([{name:"TOTAL",balance:stats.total}]);
  var min=Math.min(0,...entries.map(function(x){return x.balance})),max=Math.max(0,...entries.map(function(x){return x.balance}));
  var pad=Math.max(80,(max-min)*.12),lower=min-pad,upper=max+pad,top=15,bottom=188;
  var my=function(v){return top+(upper-v)*(bottom-top)/(upper-lower)},zy=my(0);
  ma("line",{x1:30,y1:zy,x2:W-10,y2:zy,stroke:"#7b8980","stroke-width":1.5});
  var colors={Kardinalus:"#1b6e52",King:"#a36e19",Pingvinus:"#2874b4",Kaninus:"#a24e77",Gorilla:"#744eb2",TOTAL:"#3d6651"};
  entries.forEach(function(d,i){
    var cx=32+(i+.5)*(W-43)/entries.length,yy=my(d.balance),height=Math.abs(yy-zy);
    var bar=ma("rect",{x:cx-17,y:Math.min(yy,zy),width:34,height:height,rx:3,fill:colors[d.name]});
    ma("title",{},d.name+": "+fmt.format(d.balance)+" kr",bar);
    ma("text",{x:cx,y:d.balance>=0?Math.max(12,yy-6):Math.min(bottom+14,yy+12),"text-anchor":"middle",fill:"#26382c","font-size":10},fmt.format(d.balance));
    ma("text",{x:cx,y:221,"text-anchor":"middle",fill:"#50645a","font-size":d.name==="TOTAL"?10:16},d.name==="TOTAL"?"TOTAL":players[d.name].split(" ")[0]);
  });
}
function paintHattricks_(rows){
  var panel=document.getElementById("extras");
  if(!panel||!Array.isArray(rows))return;
  var results=new Map();
  rows.forEach(function(e){
    var key=String(e.week)+"|"+String(e.round)+"|"+String(e.match);
    var score=String(e.result||"").trim().match(/^(\\d+)\\s*[-–]\\s*(\\d+)$/);
    if(score)results.set(key,{match:String(e.match),home:Number(score[1]),away:Number(score[2])});
  });
  var counts=Object.fromEntries(Object.keys(players).map(function(n){return [n,0]}));
  results.forEach(function(v){
    var teams=v.match.split(/\\s+[–-]\\s+/).map(function(n){return n.trim()});
    if(teams.length!==2)return;
    if(counts[teams[0]]!==undefined&&v.home>=3)counts[teams[0]]++;
    if(counts[teams[1]]!==undefined&&v.away>=3)counts[teams[1]]++;
  });
  var row=Array.from(panel.querySelectorAll(".extra-row")).find(function(e){return e.textContent.includes("Hattrick")});
  if(!row)return;
  var total=Object.values(counts).reduce(function(n,v){return n+v},0);
  var winner=Object.entries(counts).filter(function(e){return e[1]>0}).map(function(e){return players[e[0]]+" "+e[1]}).join(" · ");
  row.querySelector("strong").textContent=String(total)+(winner?" · "+winner:"");
}
function paintSeasonBalance_(rows){
  var host=document.querySelector(".balance-empty");
  if(!host||!Array.isArray(rows))return;
  var names=Object.keys(players),weeks=new Map();
  rows.forEach(function(e){
    var w=Number(e.week),name=String(e.player||"").replace(/^[^A-Za-zÆØÅæøå]+/,"").trim();
    if(!Number.isInteger(w)||!((w>=43&&w<=53)||(w>=1&&w<=12))||!names.includes(name))return;
    var value=e.money===null||e.money===undefined?"":String(e.money).trim();
    var amount=value?parseMoney(value):null;
    if(amount===null&&!String(e.result||"").trim())return;
    if(!weeks.has(w))weeks.set(w,Object.fromEntries(names.map(function(n){return [n,0]})));
    if(amount!==null)weeks.get(w)[name]+=amount;
  });
  var ordered=[...weeks.keys()].sort(function(a,b){return (a>=43?a:a+53)-(b>=43?b:b+53)});
  if(!ordered.length)return;
  var balances=Object.fromEntries(names.map(function(n){return [n,0]}));
  var series=names.map(function(n){return {name:n,values:[]}});
  ordered.forEach(function(w){
    names.forEach(function(n,i){
      balances[n]+=weeks.get(w)[n]-80;
      series[i].values.push(balances[n]);
    });
  });
  var values=series.flatMap(function(x){return x.values}).concat([0]);
  var min=Math.min.apply(null,values),max=Math.max.apply(null,values);
  if(max===min){min-=1;max+=1}
  var width=350,height=190,left=47,right=12,top=15,bottom=30;
  var xx=function(i){return left+(ordered.length===1?(width-left-right)/2:i*(width-left-right)/(ordered.length-1))};
  var yy=function(v){return top+(max-v)*(height-top-bottom)/(max-min)};
  var svg=document.createElementNS("http://www.w3.org/2000/svg","svg");
  svg.setAttribute("viewBox","0 0 "+width+" "+height);
  svg.setAttribute("role","img");
  svg.setAttribute("aria-label","Akkumuleret sæsonsaldo for "+ordered.length+" registrerede spilleuger");
  function element(tag,attrs,content){
    var node=document.createElementNS("http://www.w3.org/2000/svg",tag);
    Object.keys(attrs).forEach(function(k){node.setAttribute(k,attrs[k])});
    if(content!==undefined)node.textContent=content;
    svg.appendChild(node);return node;
  }
  var zero=yy(0);
  element("line",{x1:left,y1:zero,x2:width-right,y2:zero,stroke:"#a8b1a9","stroke-dasharray":"3 3"});
  [min,max].forEach(function(v){element("text",{x:left-7,y:yy(v)+4,"text-anchor":"end",fill:"#607068","font-size":"10"},Math.round(v)+"")});
  ordered.forEach(function(w,i){element("text",{x:xx(i),y:height-8,"text-anchor":"middle",fill:"#607068","font-size":"10"},"U"+w)});
  var colors={Kardinalus:"#1b6e52",King:"#a36e19",Pingvinus:"#2874b4",Kaninus:"#a24e77",Gorilla:"#744eb2"};
  series.forEach(function(line,i){
    var points=line.values.map(function(v,j){return xx(j)+","+yy(v)}).join(" ");
    if(line.values.length>1)element("polyline",{points:points,fill:"none",stroke:colors[line.name],"stroke-width":"2.5","stroke-linejoin":"round"});
    line.values.forEach(function(v,j){
      var point=element("circle",{cx:xx(j),cy:yy(v),r:3.5,fill:colors[line.name]});
      var tip=document.createElementNS("http://www.w3.org/2000/svg","title");
      tip.textContent=line.name+" · uge "+ordered[j]+": "+v.toFixed(2).replace(".",",")+" kr";
      point.appendChild(tip);
    });
  });
  host.replaceChildren(svg);
  var note=document.createElement("p");
  note.textContent="Registrerede uger: "+ordered.map(function(w){return "uge "+w}).join(", ")+". Saldo = gevinster − 80 kr pr. spiller pr. uge.";
  host.appendChild(note);
}
/* Completed seasons through 2026_2; current season amounts come only from saved entries. */
function paintAllTimeFromSaved_(rows){
  if(!Array.isArray(rows))return;
  var base={King:8164.69,Pingvinus:7359.51,Kardinalus:7196.87,Gorilla:6360.16,Kaninus:6126.99};
  var totals=Object.keys(base).map(function(name){return {name:name,total:base[name]};});
  rows.forEach(function(e){
    var name=String(e.player||"").replace(/^[^A-Za-zÆØÅæøå]+/,"").trim();
    var item=totals.find(function(x){return x.name===name});
    if(!item||e.money===null||e.money===undefined||String(e.money).trim()==="")return;
    var amount=parseMoney(String(e.money));
    if(amount!==null)item.total+=amount;
  });
  totals.sort(function(a,b){return b.total-a.total});
  var fmt=new Intl.NumberFormat("da-DK",{minimumFractionDigits:2,maximumFractionDigits:2});
  var cards=document.querySelectorAll("#allTime .alltime-hero, #allTime .alltime-card");
  cards.forEach(function(card,i){
    var item=totals[i];if(!item)return;
    var nameEl=card.querySelector(".hero-copy strong");
    var amountEl=card.querySelector(".hero-copy span b");
    if(nameEl)nameEl.textContent=players[item.name];
    if(amountEl)amountEl.textContent=fmt.format(item.total)+(i===0?" kr":"");
  });
  document.querySelectorAll("#atRank .alltime-rank").forEach(function(row,i){
    var item=totals[i+3];if(!item)return;
    row.querySelector("span").textContent=players[item.name];
    row.querySelector("strong").textContent=fmt.format(item.total);
  });
  var delta=totals[0].total-totals[1].total;
  var whisper=document.querySelector("#atRank .alltime-whisper");
  if(whisper)whisper.textContent=players[totals[0].name]+" er "+fmt.format(delta)+" kr foran "+totals[1].name+".";
}
window.refreshAllTimeLeader=function(){
  if(!API_URL)return Promise.resolve();
  return fetch(API_URL+"?t="+Date.now(),{cache:"no-store"}).then(function(res){return res.json()}).then(function(out){
    if(out&&out.ok&&Array.isArray(out.saved))paintAllTimeFromSaved_(out.saved);
  }).catch(function(){});
};
function paintManagerFromSaved_(rows){
  var panel=document.getElementById("money");
  if(!panel||!Array.isArray(rows))return;
  var scores=Object.keys(players).map(function(name){return {name:name,total:0}});
  rows.forEach(function(e){
    var player=String(e.player||"").replace(/^[^A-Za-zÆØÅæøå]+/,"").trim();
    var item=scores.find(function(x){return x.name===player});
    if(!item||e.money===null||e.money===undefined||String(e.money).trim()==="")return;
    var amount=parseMoney(String(e.money));
    if(amount!==null)item.total+=amount;
  });
  scores.sort(function(a,b){return b.total-a.total});
  var number=new Intl.NumberFormat("da-DK",{minimumFractionDigits:2,maximumFractionDigits:2});
  panel.querySelectorAll(".srow").forEach(function(row,i){
    var item=scores[i];if(!item)return;
    row.querySelector("b").textContent=String(i+1);
    row.querySelector("span").textContent=players[item.name];
    row.querySelector("strong").textContent=number.format(item.total);
  });
  var mood=panel.querySelector(".mood");
  if(mood)mood.textContent="Beløb fra Google Sheet · opdateres ved åbning";
}
window.refreshManagerStandings=function(){
  return fetch(API_URL+"?t="+Date.now(),{cache:"no-store"}).then(function(res){
    if(!res.ok)throw new Error("forbindelse");
    return res.json();
  }).then(function(out){
    if(!out||!out.ok||!Array.isArray(out.saved))throw new Error("mangler data");
    paintManagerFromSaved_(out.saved);paintSeasonBalance_(out.saved);paintWeeklyFinance_(out.saved);paintHattricks_(out.saved);
  }).catch(function(){
    var mood=document.querySelector("#money .mood");
    if(mood)mood.textContent="Kunne ikke hente aktuel stilling · prøv igen senere";
  });
};
logApp_("app_open","app:forside","");
function programKind_(x){var r=String(x.r||"").toLowerCase();if(r.indexOf("pokal")>=0)return"cup";if(r.indexOf("runde")===0)return"league";if(r.indexOf("supercup")>=0||r.indexOf("toto")>=0||r.indexOf("julecup")>=0)return"special";return"other"}
function prettyMatch_(m){return String(m||"").replace("Kardinalus","🙏 Kardinalus").replace("Pingvinus","🐧 Pingvinus").replace("Kaninus","🐰 Kaninus").replace("Gorilla","🦍 Gorilla").replace("King","👑 King")}
function programCard_(x,i,current){var holiday=/^(EFTERÅRSFERIE|JULEFERIE|VINTERFERIE)$/.test(String(x.r||""));var julecup=(String(x.r||"")+" "+String(x.note||"")).toLowerCase().indexOf("julecup")>=0;var roundLabel=(julecup?"🎄 ":"")+x.r;var t='<article class="program-week '+(i===current?"current ":"")+(holiday?"holiday ":"")+'" data-program-kind="'+programKind_(x)+'"><div class="program-week-head"><b>UGE '+x.w+'</b><span>'+roundLabel+'</span></div>';if(holiday)return t+'<div class="program-holiday">'+(String(x.r)==='VINTERFERIE'?'❄️ Vinterferie':String(x.r)==='EFTERÅRSFERIE'?'🍂 Efterårsferie':'🎄 Juleferie')+'</div></article>';if(x.m&&x.m.length){x.m.forEach(function(m){t+='<div class="program-match">'+(String(m).indexOf("TBD")>=0?'🏆 <strong>Modstandere afgøres ved lodtrækning</strong>':'<strong>'+prettyMatch_(m)+'</strong>')+'</div>'})}if(x.toto)t+='<div class="program-note">🎲 Toto Cup · '+x.toto.map(function(n){return players[n]||n}).join(" · ")+'</div>';if(x.allFree)t+='<div class="program-note">🎯 Fri Odds · hele klubben</div>';else if(x.free)t+='<div class="program-note">🎯 Fri Odds · '+(players[x.free]||x.free)+'</div>';if(julecup){var jc=(String(x.r||'')+' · '+String(x.note||'')).match(/Julecup[^·]*/i);t+='<div class="program-badge">🎄 '+(jc?jc[0].trim():'Julecup')+'</div>'}if(x.w===47)t+='<div class="program-note">2 spiller pokal · de øvrige 3 har Fri Odds</div>';if(x.w===2)t+='<div class="program-note">4 semifinalister · den øvrige spiller har Fri Odds</div>';if(x.w===8)t+='<div class="program-note">2 finalister · de øvrige 3 har Fri Odds</div>';return t+'</article>'}
window.renderSeasonProgram=function(){var wrap=document.getElementById("programTimeline"),hero=document.getElementById("programHero");if(!wrap||!hero)return;var current=initialPosition(),x=program[current];hero.innerHTML='<div><small>NÆSTE / AKTUELLE UGE</small><strong>Uge '+x.w+' · '+x.r+'</strong><span>'+(x.m&&x.m.length?x.m.map(prettyMatch_).join(" · "):x.r)+'</span></div>';function draw(filter){wrap.innerHTML=program.map(function(v,i){return programCard_(v,i,current)}).join("");Array.prototype.forEach.call(wrap.children,function(el){el.style.display=filter==="all"||el.getAttribute("data-program-kind")===filter?"block":"none"})}draw("all");document.querySelectorAll(".program-tab").forEach(function(btn){btn.onclick=function(){document.querySelectorAll(".program-tab").forEach(function(b){b.className="program-tab"});btn.className="program-tab active";draw(btn.getAttribute("data-program-filter"))}})};

var TIPS_URL="data/latest-tips.json";
var bettingTips={"updated":"2026-10-03 13:51 UTC","model_80kr_portfolio":{"budget_kr":80,"bets":[{"type":"single","stake_kr":40,"combined_probability":0.7684,"legs":[{"date":"2026-10-10","match":"FC Barcelona vs Getafe CF","selection":"FC Barcelona","probability":0.7684}]},{"type":"single","stake_kr":40,"combined_probability":0.7349,"legs":[{"date":"2026-10-10","match":"FC Internazionale Milano vs Parma Calcio 1913","selection":"FC Internazionale Milano","probability":0.7349}]}]},"smart_double":null,"smart_triple":{"combined_probability":0.3846,"legs":[{"role":"best_available","date":"2026-10-10","match":"FC Barcelona vs Getafe CF","selection":"FC Barcelona","probability":0.7684},{"role":"best_available","date":"2026-10-10","match":"FC Internazionale Milano vs Parma Calcio 1913","selection":"FC Internazionale Milano","probability":0.7349},{"role":"best_available","date":"2026-10-09","match":"Borussia Dortmund vs SV Werder Bremen","selection":"Borussia Dortmund","probability":0.681}]},"favorites":[{"date":"2026-10-10","match":"FC Barcelona vs Getafe CF","selection":"FC Barcelona","probability":0.7684},{"date":"2026-10-10","match":"FC Internazionale Milano vs Parma Calcio 1913","selection":"FC Internazionale Milano","probability":0.7349},{"date":"2026-10-09","match":"Borussia Dortmund vs SV Werder Bremen","selection":"Borussia Dortmund","probability":0.681}],"upsets":[{"date":"2026-10-10","match":"AFC Ajax vs NEC","selection":"NEC","probability":0.369,"uncertain":true},{"date":"2026-10-10","match":"Chelsea vs Bournemouth","selection":"Chelsea","probability":0.3665,"uncertain":true},{"date":"2026-10-10","match":"FC Lorient vs Paris FC","selection":"Paris FC","probability":0.3645,"uncertain":true}],"bold_upsets":[{"date":"2026-10-10","match":"1. FC Union Berlin vs SV 07 Elversberg","selection":"1. FC Union Berlin","probability":0.3427,"favorite_probability":0.4331,"tier":"bold"},{"date":"2026-10-10","match":"Swansea City AFC vs Norwich City FC","selection":"Norwich City FC","probability":0.3154,"favorite_probability":0.4323,"tier":"bold"},{"date":"2026-10-10","match":"Aston Villa vs Brentford","selection":"Brentford","probability":0.3078,"favorite_probability":0.4465,"tier":"bold"}]};
function pctTip_(p){return (Number(p)*100).toFixed(1).replace(".",",")+"%"}
function shortDate_(d){var a=String(d||"").split("-");return a.length===3?Number(a[2])+"/"+Number(a[1]):d}
function tipExplain_(x){var e=x.explanation;if(!e)return "";return '<details class="tip-explain"><summary>Hvorfor tror Bot’en på den?</summary><p>'+e.summary+'</p><div class="tip-explain-stats"><span>Forventede mål <b>'+Number(e.home_expected_goals).toFixed(2).replace(".",",")+' – '+Number(e.away_expected_goals).toFixed(2).replace(".",",")+'</b></span><span>Angrebsstyrke H/U <b>'+Number(e.home_attack_strength).toFixed(2).replace(".",",")+' / '+Number(e.away_attack_strength).toFixed(2).replace(".",",")+'</b></span><span>Forsvarsstyrke H/U <b>'+Number(e.home_defence_strength).toFixed(2).replace(".",",")+' / '+Number(e.away_defence_strength).toFixed(2).replace(".",",")+'</b></span></div></details>'}
function tipRows_(items,kind){return items.map(function(x,i){var doubt=x.uncertain?'<span class="tip-doubt">Bot’en er lidt i tvivl om det her · bedste tilgængelige bud</span>':'';return '<article class="tip-card '+kind+'"><div class="tip-rank">'+(i+1)+'</div><div class="tip-copy"><small>'+shortDate_(x.date)+'</small><strong>'+x.match.replace(" vs "," – ")+'</strong><span>'+x.selection+doubt+'</span>'+tipExplain_(x)+'</div><b>'+pctTip_(x.probability)+'</b></article>'}).join("")}
function tripleRole_(r){return r==="solid"?"Solid":r==="value"?"Værdi-signal":r==="best_available"?"Bedste tilgængelige":"Lille fidus"}
function paintSmartTriple_(){var el=document.getElementById("smartTriple"),t=bettingTips.smart_triple,d=bettingTips.smart_double,combo=t&&t.legs&&t.legs.length?t:d;if(!el)return;if(!combo||!combo.legs||!combo.legs.length){el.innerHTML='<p class="tips-empty">Ingen Smart Triple eller Smart Double i den aktuelle analyse.</p>';return}var title=t?"Smart Triple":"Smart Double";el.innerHTML='<div class="smart-combo-label">'+title+'</div><div class="smart-triple-card">'+combo.legs.map(function(x){return '<div class="triple-leg"><small>'+tripleRole_(x.role)+' · '+shortDate_(x.date)+'</small><strong>'+x.selection+'</strong><span>'+x.match.replace(" vs "," – ")+' · '+pctTip_(x.probability)+'</span></div>'}).join("")+(combo.note?'<div class="tip-doubt">'+combo.note+'</div>':'')+'<div class="triple-total"><span>Samlet modelchance</span><b>'+pctTip_(combo.combined_probability)+'</b></div><div class="triple-odds"><span>Forventet odds · 90% tilbagebetaling</span><b>'+Number(combo.expected_odds_90||(.90/Number(combo.combined_probability))).toFixed(2).replace(".",",")+'</b></div></div>'}
function paintPortfolio80_(){var el=document.getElementById("portfolio80"),p=bettingTips.model_80kr_portfolio;if(!el)return;if(!p||!p.bets||!p.bets.length){el.innerHTML='<p class="tips-empty">Intet 80 kr-forslag i den aktuelle analyse.</p>';return}el.innerHTML='<div class="portfolio-card">'+p.bets.map(function(b,i){var legs=b.legs.map(function(x){return '<span>'+x.selection+' · '+pctTip_(x.probability)+'</span><small>'+x.match.replace(" vs "," – ")+'</small>'}).join("");return '<div class="portfolio-bet"><div class="portfolio-stake"><b>'+b.stake_kr+' kr</b><span>'+(b.type==="double"?"Double":"Single")+'</span></div><div class="portfolio-legs">'+legs+'</div></div>'}).join("")+'<div class="portfolio-total"><span>Samlet indsats</span><b>'+p.budget_kr+' kr</b></div></div>'}
function paintBettingTips_(){paintPortfolio80_();paintSmartTriple_();var f=document.getElementById("favoriteTips"),u=document.getElementById("upsetTips"),b=document.getElementById("boldUpsetTips");if(f)f.innerHTML=bettingTips.favorites.length?tipRows_(bettingTips.favorites,"favorite"):'<p class="tips-empty">Ingen favoritsignaler i den aktuelle analyse.</p>';if(u)u.innerHTML=bettingTips.upsets.length?tipRows_(bettingTips.upsets,"upset"):'<p class="tips-empty">Ingen upset-signaler i den aktuelle analyse.</p>';if(b)b.innerHTML=bettingTips.bold_upsets&&bettingTips.bold_upsets.length?tipRows_(bettingTips.bold_upsets,"bold-upset"):'<p class="tips-empty">Ingen helt frække bud i den aktuelle analyse.</p>'}
window.renderBettingTips=function(){paintBettingTips_();fetch(TIPS_URL+"?t="+Date.now(),{cache:"no-store"}).then(function(r){if(!r.ok)throw new Error("feed");return r.json()}).then(function(data){bettingTips=data||bettingTips;paintBettingTips_()}).catch(function(){});logApp_("view","app:spilforslag","live feed")}

var BOT_BET_URL="data/bot-bets.json";
var botBetFallback={"name":"Bot'ens Bet","currency":"fiktive kr","bookmaker":"Bot’ens egne sandsynligheder med 90% tilbagebetaling","weeks":[{"coupon_date":"2026-10-03","model_updated":"2026-10-03 14:02 UTC","stake_kr":80,"rtp":0.9,"status":"open","return_kr":null,"profit_kr":null,"bets":[{"type":"single","stake_kr":40,"fake_odds":1.17,"legs":[{"date":"2026-10-10","match":"FC Barcelona vs Getafe CF","selection":"FC Barcelona","probability":0.7684,"fake_odds":1.17}],"result":"pending","return_kr":null},{"type":"single","stake_kr":40,"fake_odds":1.22,"legs":[{"date":"2026-10-10","match":"FC Internazionale Milano vs Parma Calcio 1913","selection":"FC Internazionale Milano","probability":0.7349,"fake_odds":1.22}],"result":"pending","return_kr":null}]}],"totals":{"settled_weeks":0,"stake_kr":0,"return_kr":0,"profit_kr":0,"return_pct":null},"updated":"2026-10-03 14:02 UTC"};
function botMoney_(n){return Number(n||0).toFixed(2).replace(".",",")+" kr"}
function botBetCards_(week){return week.bets.map(function(b,i){var state=b.result==="won"?"🟢 Vundet":b.result==="lost"?"🔴 Tabt":"⏳ Afventer resultat";var ret=b.return_kr===null||typeof b.return_kr==="undefined"?"":'<span class="botbet-return">Retur '+botMoney_(b.return_kr)+'</span>';return '<article class="botbet-bet '+(b.result||"pending")+'"><div class="botbet-bet-top"><b>Bet '+(i+1)+' · '+b.stake_kr+' kr</b><span>Fiktivt odds '+Number(b.fake_odds).toFixed(2).replace(".",",")+'</span></div>'+b.legs.map(function(x){return '<div class="botbet-leg"><strong>'+x.selection+'</strong><span>'+x.match.replace(" vs "," – ")+' · '+pctTip_(x.probability)+' · odds '+Number(x.fake_odds).toFixed(2).replace(".",",")+'</span></div>'}).join("")+'<div class="botbet-result"><strong>'+state+'</strong>'+ret+'</div></article>'}).join("")}
function botMood_(current,t){var mode=current&&current.risk_mode;var profit=Number(t&&t.profit_kr||0);if(!mode){mode=profit>=80?"protect":profit<=-240?"high":profit<=-80?"attack":"normal"}var moods={protect:{icon:"😌",title:"Bot’en er kølig",text:"Saldoen er solidt i plus. Bot’en beskytter føringen og går efter stærkere modelvalg."},normal:{icon:"🤖",title:"Bot’en er fokuseret",text:"Saldoen er omkring neutral. Bot’en følger sin normale 80 kr-strategi."},attack:{icon:"😤",title:"Bot’en er på jagt",text:"Saldoen er i minus. Bot’en accepterer mere risiko for at forsøge at hente underskuddet."},high:{icon:"😈",title:"Bot’en går til stålet",text:"Saldoen er markant i minus. Bot’en vælger sin højeste risiko blandt de aktuelle modelsignaler."}};return moods[mode]||moods.normal}
function botBetWarning_(week,weeks){
  if(!week)return "";
  var today=new Date().toLocaleDateString("sv-SE",{timeZone:"Europe/Copenhagen"});
  var legs=(week.bets||[]).reduce(function(a,b){return a.concat(b.legs||[])},[]);
  if(legs.some(function(l){return !/^\d{4}-\d{2}-\d{2}$/.test(l.date||"")||l.date<today}))
    return "⚠️ Kuponen indeholder en kamp fra en tidligere dato eller med ugyldig dato. Den er ikke et nyt spilforslag.";
  var previous=(weeks||[]).slice(0,-1).reduce(function(a,w){return a.concat((w.bets||[]).reduce(function(c,b){return c.concat(b.legs||[])},[]))},[]);
  if(legs.some(function(l){return previous.some(function(p){return p.date===l.date&&p.match===l.match&&p.selection===l.selection})}))
    return "⚠️ Kuponen genbruger kampvalg fra en tidligere kupon.";
  return "";
}
function paintBotBet_(data){var el=document.getElementById("botBetContent");if(!el)return;var weeks=data&&data.weeks?data.weeks:[],current=weeks.filter(function(w){return !w.excluded_from_totals}).slice(-1)[0]||null,t=data&&data.totals?data.totals:{};var mood=botMood_(current,t);var moodHtml='<section class="botbet-mood"><span class="botbet-mood-icon">'+mood.icon+'</span><div><small>BOT’ENS HUMØR</small><strong>'+mood.title+'</strong><p>'+mood.text+'</p></div></section>';var summary='<section class="botbet-score"><div><small>INDSAT</small><strong>'+botMoney_(t.stake_kr)+'</strong></div><div><small>RETUR</small><strong>'+botMoney_(t.return_kr)+'</strong></div><div><small>SALDO</small><strong>'+botMoney_(t.profit_kr)+'</strong></div></section>';if(!current){el.innerHTML='<section class="botbet-hero"><small>FØRSTE KUPON</small><strong>Bot’en gør klar 🤖</strong><span>Næste søndag morgen låses 80 fiktive kr på 2–4 modelspil.</span></section>'+moodHtml+summary;return}var warning=botBetWarning_(current,weeks);var warningHtml=warning?'<section class="botbet-history-empty" role="status">'+warning+'</section>':"";var history=weeks.filter(function(w){return w!==current}).reverse();var historyHtml=history.length?'<section class="botbet-history"><h2>Tidligere kuponer</h2><p>Bot’ens låste væddemål uge for uge.</p>'+history.map(function(w){return '<section class="botbet-week"><div class="botbet-week-head"><strong>'+w.coupon_date+'</strong><span>'+(w.excluded_from_totals?'Dublet af '+String(w.duplicate_of||'tidligere kupon')+' · tæller ikke i saldo':botMoney_(w.stake_kr)+' indsat · '+(w.status==="settled"?'afgjort':'afventer'))+'</span></div>'+(w.excluded_from_totals?'<p>Historisk kopi – ingen ny indsats eller gevinst.</p>':'')+botBetCards_(w)+'</section>'}).join("")+'</section>':'<section class="botbet-history-empty">Historikken kommer her efter professorens første afsluttede uge.</section>';el.innerHTML='<section class="botbet-hero"><small>AKTUEL KUPON · '+current.coupon_date+'</small><strong>Bot’ens 80 kr</strong><span>Fiktiv bookmaker · 90% tilbagebetaling</span></section>'+warningHtml+moodHtml+botBetCards_(current)+summary+historyHtml}
window.renderBotBet=function(){var el=document.getElementById("botBetContent");if(el)el.innerHTML='<section class="botbet-history-empty" role="status">Henter Bot’ens seneste kupon…</section>';fetch(BOT_BET_URL+"?t="+Date.now(),{cache:"no-store"}).then(function(r){if(!r.ok)throw new Error("botbet");return r.json()}).then(function(data){if(!data||!Array.isArray(data.weeks))throw new Error("invalid feed");paintBotBet_(data)}).catch(function(){if(el)el.innerHTML='<section class="botbet-history-empty" role="alert">⚠️ Kunne ikke hente Bot’ens aktuelle data. Ældre kuponer vises ikke som nye.</section>'})}
