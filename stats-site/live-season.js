/* Website projection of the app's read-only Apps Script feed. No Sheet writes. */
(function(){
"use strict";
var API="https://script.google.com/macros/s/AKfycbwt1E1CC6EDlvwmblrzM6vtK4WmYCrmpIhj_SV7NUvMmcsNweZXcr0E4M1X83dvsE7WlQ/exec";
var names=["Kardinalus","King","Pingvinus","Gorilla","Kaninus"];
var icons={Kardinalus:"🙏",King:"👑",Pingvinus:"🐧",Gorilla:"🦍",Kaninus:"🐰"};
var historical={King:8164.69,Pingvinus:7359.51,Kardinalus:7196.87,Gorilla:6360.16,Kaninus:6126.99};
var fmt=new Intl.NumberFormat("da-DK",{minimumFractionDigits:2,maximumFractionDigits:2});
function find(id){return document.getElementById(id)}
function el(tag,cls,value){var node=document.createElement(tag);if(cls)node.className=cls;if(value!==undefined)node.textContent=value;return node}
function money(raw){if(raw===null||raw===undefined||String(raw).trim()==="")return null;var n=Number(String(raw).replace(/\s/g,"").replace(",","."));return Number.isFinite(n)&&n>=0?n:null}
function player(raw){var m=String(raw||"").match(/Pingvinus|King|Gorilla|Kaninus|Kardinalus/);return m?m[0]:null}
function listed(rows){
 var totals={};names.forEach(function(n){totals[n]=0});
 rows.forEach(function(e){var n=player(e.player),v=money(e.money);if(n&&v!==null)totals[n]+=v});
 return totals;
}
function renderBars(host,totals,unit){
 if(!host)return;
 var sorted=names.slice().sort(function(a,b){return totals[b]-totals[a]});
 var maximum=Math.max(1,totals[sorted[0]]);host.replaceChildren();
 sorted.forEach(function(n){var r=el("div"),label=el("label"),name=el("span",null,icons[n]+" "+n),value=el("b",null,fmt.format(totals[n])+(unit||"")),bar=el("i");
  bar.style.setProperty("--w",(100*totals[n]/maximum).toFixed(1)+"%");
  label.append(name,value);r.append(label,bar);host.appendChild(r);
 });
}
function renderStandings(rows){
 var host=find("website-league");if(!host)return;
 var teams={};names.forEach(function(n){teams[n]={name:n,played:0,gf:0,ga:0,points:0}});
 var matches=new Map();
 rows.forEach(function(e){
  if(!/^Runde\s+\d+\b/i.test(String(e.round||"")))return;
  var match=String(e.match||"").split(/\s+[–-]\s+/);
  if(match.length!==2||!teams[match[0]]||!teams[match[1]])return;
  var key=e.week+"|"+e.round+"|"+e.match;
  if(!matches.has(key))matches.set(key,{home:match[0],away:match[1],result:"",winnings:{}});
  var rec=matches.get(key),n=player(e.player),v=money(e.money);
  if(n&&v!==null)rec.winnings[n]=v;
  if(String(e.result||"").trim())rec.result=String(e.result).trim();
 });
 matches.forEach(function(m){
  var score=m.result.match(/^(\d+)\s*[-–]\s*(\d+)$/);if(!score)return;
  var a=+score[1],b=+score[2],h=teams[m.home],v=teams[m.away];
  h.played++;v.played++;h.gf+=a;h.ga+=b;v.gf+=b;v.ga+=a;
  if(a>b)h.points+=3;else if(b>a)v.points+=3;
  else if(a===0&&b===0){h.points++;v.points++}
  else {var hm=m.winnings[m.home]||0,vm=m.winnings[m.away]||0;
   if(hm>vm){h.points+=3;v.points++}else if(vm>hm){v.points+=3;h.points++}else{h.points++;v.points++}
  }
 });
 var sorted=Object.values(teams).sort(function(a,b){return b.points-a.points||(b.gf-b.ga)-(a.gf-a.ga)||b.gf-a.gf||names.indexOf(a.name)-names.indexOf(b.name)});
 host.replaceChildren();var head=el("div","tr th");["#","Spiller","K","Mål","+/-","Point"].forEach(function(v){head.appendChild(el("span",null,v))});host.appendChild(head);
 sorted.forEach(function(t,i){var r=el("div","tr");[
 String(i+1),icons[t.name]+" "+t.name,String(t.played),t.gf+"–"+t.ga,String(t.gf-t.ga),String(t.points)
 ].forEach(function(v,j){r.appendChild(el(j===1?"strong":j===5?"b":"span",null,v))});host.appendChild(r)});
 var note=find("website-league-note");if(note)note.textContent=matches.size?"Beregnet fra gemte ligakampe · opdateres ved indlæsning":"Ingen afsluttede ligarunder registreret endnu.";
}
function renderProgram(program){
 var host=find("website-program");if(!host||!Array.isArray(program))return;
 var header=host.firstElementChild;host.replaceChildren();if(header)host.appendChild(header);
 program.forEach(function(p){
  var desc=(p.m||[]).join(" · ");
  if(p.free)desc+=(desc?" · ":"")+"Fri Odds: "+p.free;
  if(p.allFree)desc+=(desc?" · ":"")+"Alle Fri Odds";
  if(p.toto&&p.toto.length)desc+=(desc?" · ":"")+"Toto Cup: "+p.toto.join(", ");
  if(!desc)desc=p.note||"Pause";
  var row=el("div","program-list-row");
  row.append(el("b",null,"Uge "+p.w),el("strong",null,p.r||"–"),el("span",null,desc));
  host.appendChild(row);
 });
}
function renderAwards(rows){
 var best=null,counts={};names.forEach(function(n){counts[n]=0});
 var unique=new Map();
 rows.forEach(function(e){
  var n=player(e.player),v=money(e.money);if(n&&v!==null&&(!best||v>best.value))best={name:n,value:v};
  var score=String(e.result||"").trim().match(/^(\d+)\s*[-–]\s*(\d+)$/);
  if(score)unique.set(String(e.week)+"|"+e.round+"|"+e.match,{match:e.match,a:+score[1],b:+score[2]});
 });
 unique.forEach(function(e){var parts=String(e.match).split(/\s+[–-]\s+/);if(parts.length!==2)return;if(counts[parts[0]]!==undefined&&e.a>=3)counts[parts[0]]++;if(counts[parts[1]]!==undefined&&e.b>=3)counts[parts[1]]++});
 var goal=find("website-goal-of-year"),hat=find("website-hattrick");
 if(goal)goal.textContent=best?icons[best.name]+" "+best.name+" · "+fmt.format(best.value)+" kr":"Ingen gevinst registreret";
 var winners=names.filter(function(n){return counts[n]>0});
 if(hat)hat.textContent=winners.length?winners.map(function(n){return icons[n]+" "+n+": "+counts[n]}).join(" · "):"Ingen hattricks registreret";
}
function render(rows,program){
 var current=listed(rows),all={};names.forEach(function(n){all[n]=historical[n]+current[n]});
 renderBars(find("manager-bars"),current," kr");renderBars(find("website-alltime-bars"),all,"");
 var kpi=find("website-alltime-kpi");if(kpi){var lead=names.slice().sort(function(a,b){return all[b]-all[a]});kpi.querySelector("strong").textContent=icons[lead[0]]+" "+lead[0];kpi.querySelector("b").textContent=fmt.format(all[lead[0]])+" kr";kpi.querySelector("span").textContent=fmt.format(all[lead[0]]-all[lead[1]])+" kr foran nr. 2"}
 renderStandings(rows);renderProgram(program);renderAwards(rows);
 var s=find("manager-source");if(s)s.textContent="Opdateret fra appens data";
 var updated=find("website-live-status");if(updated)updated.textContent="Aktuelle data fra Google Sheet";
 var hero=find("website-next");if(hero&&Array.isArray(program)){
  var next=program.find(function(p){return (p.m&&p.m.length)||(p.toto&&p.toto.length)||p.allFree||p.free});
  if(next){hero.replaceChildren();hero.append(el("small",null,"SÆSONPROGRAM · UGE "+next.w),el("strong",null,next.r),el("span",null,(next.m||[]).join(" · ")+(next.toto&&next.toto.length?" · Toto Cup: "+next.toto.join(", "):"")))}
 }
}
function failure(){
 var source=find("manager-source");if(source)source.textContent="Data utilgængelige";
 var live=find("website-live-status");if(live)live.textContent="Live-data kan ikke hentes";
 ["manager-bars","website-alltime-bars","website-league","website-program"].forEach(function(id){var h=find(id);if(h)h.textContent="Aktuelle data er utilgængelige. Se appen og prøv igen senere."});
 var note=find("website-league-note");if(note)note.textContent="";
}
fetch(API+"?t="+Date.now(),{cache:"no-store"}).then(function(r){if(!r.ok)throw Error("API fejl");return r.json()}).then(function(out){if(!out||!out.ok||!Array.isArray(out.saved)||!Array.isArray(out.program))throw Error("Ugyldigt feed");render(out.saved,out.program)}).catch(failure);
})();
