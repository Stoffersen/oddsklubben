const players={Pingvinus:"🐧 Pingvinus",King:"👑 King",Gorilla:"🦍 Gorilla",Kaninus:"🐰 Kaninus",Kardinalus:"🙏 Kardinalus"};
const program=[
{w:43,r:"Supercup",m:["Kardinalus – King"],note:"Toto Cup: Pingvinus · Gorilla · Kaninus"},
{w:44,r:"Runde 1",m:["Kardinalus – Kaninus","Gorilla – King"],free:"Pingvinus"},
{w:45,r:"Runde 2",m:["Kardinalus – Pingvinus","Kaninus – Gorilla"],free:"King"},
{w:46,r:"Runde 3 · Julecup 1/4",m:["King – Pingvinus","Kardinalus – Gorilla"],free:"Kaninus"},
{w:47,r:"Pokal · indledende · Julecup 2/4",m:["TBD – TBD"]},
{w:48,r:"Runde 4 · Julecup 3/4",m:["Gorilla – Pingvinus","King – Kaninus"],free:"Kardinalus"},
{w:49,r:"Runde 5 · Julecup 4/4",m:["Pingvinus – Kaninus","Kardinalus – King"],free:"Gorilla"},
{w:50,r:"Runde 6",m:["Kaninus – Kardinalus","King – Gorilla"],free:"Pingvinus"},
{w:51,r:"JULEFERIE",m:[]},{w:52,r:"JULEFERIE",m:[]},{w:1,r:"JULEFERIE",m:[]},
{w:2,r:"Runde 7",m:["Pingvinus – Kardinalus","Gorilla – Kaninus"],free:"King"},
{w:3,r:"Pokal · semifinaler",m:["TBD – TBD","TBD – TBD"]},
{w:4,r:"Runde 8",m:["Pingvinus – King","Gorilla – Kardinalus"],free:"Kaninus"},
{w:5,r:"Fri Odds",m:[]},{w:6,r:"Runde 9",m:["Pingvinus – Gorilla","Kaninus – King"],free:"Kardinalus"},
{w:7,r:"Fri Odds",m:[]},{w:8,r:"Pokalfinale",m:["TBD – TBD"]},{w:9,r:"Fri Odds",m:[]},
{w:10,r:"Runde 10",m:["Kaninus – Pingvinus","King – Kardinalus"],free:"Gorilla"},{w:11,r:"Fri Odds",m:[]},{w:12,r:"Fri Odds · sæsonafslutning",m:[]}];
let pos=0;
function names(match){return match.split(" – ").filter(n=>players[n]).map(n=>players[n])}
function card(match,i){const ns=names(match);return `<section class="card ${match.includes("TBD")?"cup":""}"><div class="tag">Kamp ${i+1}</div><div class="match">${match}</div>${ns.map(n=>`<div class="player"><label>${n}</label><input inputmode="decimal" placeholder="Kr" aria-label="Gevinst ${n}"></div>`).join("")}<div class="result"><label>Resultat</label><input inputmode="numeric" placeholder="fx 2-1" aria-label="Resultat"></div></section>`}
function render(){const x=program[pos];week.textContent=x.w;round.textContent=x.r;subtitle.textContent="Sæson 2026/27";cards.innerHTML=x.m.length?x.m.map(card).join(""):`<div class="empty">${x.r.includes("FERIE")?"🎄 Juleferie":"🍺 Ingen faste kampe denne uge"}</div>`;if(x.free)cards.innerHTML+=`<section class="card"><div class="tag">Fri Odds</div><div class="match">${players[x.free]}</div><div class="player"><label>Gevinst</label><input inputmode="decimal" placeholder="Kr"></div></section>`;if(x.note)cards.innerHTML+=`<section class="card"><div class="tag">Toto Cup</div><div class="match">${x.note.replace("Toto Cup: ","")}</div><p>Alle tre har Fri Odds.</p></section>`;save.style.display=x.r.includes("FERIE")?"none":"block";notice.textContent=""}
prev.onclick=()=>{pos=(pos-1+program.length)%program.length;render()};next.onclick=()=>{pos=(pos+1)%program.length;render()};
function parseMoney(v){if(!v.trim())return null;const n=Number(v.trim().replace(/\s/g,"").replace(",", "."));return Number.isFinite(n)&&n>=0?n:null}
function validResult(v){return /^\d+\s*[-–]\s*\d+$/.test(v.trim())}
function validate(){const x=program[pos],inputs=[...cards.querySelectorAll("input")],errors=[];inputs.forEach(el=>el.classList.remove("bad"));inputs.forEach(el=>{const isResult=el.getAttribute("aria-label")==="Resultat";const ok=isResult?validResult(el.value):parseMoney(el.value)!==null;if(!ok){el.classList.add("bad");errors.push(el)}});if(x.m.some(m=>m.includes("TBD"))){notice.textContent="Pokalkampen afventer lodtrækning.";return false}if(errors.length){notice.textContent="Tjek de markerede felter.";errors[0].focus();return false}return true}
function summary(){const x=program[pos],vals=[...cards.querySelectorAll("input")].map(el=>({label:el.getAttribute("aria-label")||"Gevinst",value:el.value.trim()}));return {week:x.w,round:x.r,values:vals}}
save.onclick=()=>{if(!validate())return;const data=summary();notice.innerHTML=`<div class="confirm"><strong>Klar til at gemme uge ${data.week}</strong><span>Kontrollér oplysningerne og tryk Bekræft.</span><button id="confirmSave">Bekræft og gem</button><button id="cancelSave" class="secondary">Ret oplysninger</button></div>`;document.getElementById("cancelSave").onclick=()=>notice.textContent="";document.getElementById("confirmSave").onclick=()=>{localStorage.setItem("oddsklubben-draft-"+data.week,JSON.stringify(data));notice.innerHTML='<div class="success">✓ Gemt som sikker lokal kladde.<br><small>Der skrives endnu ikke til Google Sheet.</small></div>'}};render();