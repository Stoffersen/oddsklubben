/**
 * Oddsklubben mobile app – Apps Script backend.
 *
 * Safety model:
 * - Dry-run is ON by default.
 * - Only columns A:E and I are ever written.
 * - F:H and J:K are never touched.
 * - Existing week/round rows are replaced in-place only when writes are enabled.
 *
 * Script properties:
 * SPREADSHEET_ID = target spreadsheet id
 * WRITE_ENABLED = true   (omit/anything else = dry-run)
 */
const SHEET_NAME = '📲 Rundeindtastning';
const PROGRAM_SHEET_NAME = '📅 Program 26-27';
const APP_LOG_SHEET_NAME = '📊 App-log';
const FIRST_DATA_ROW = 110;
const MAX_SCAN_ROWS = 594;


function doGet() {
  try {
    const props = PropertiesService.getScriptProperties();
    const spreadsheetId = props.getProperty('SPREADSHEET_ID');
    const ss = spreadsheetId ? SpreadsheetApp.openById(spreadsheetId) : SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) throw new Error('Google Sheet kunne ikke åbnes');
    const sheet = ss.getSheetByName(PROGRAM_SHEET_NAME);
    if (!sheet) throw new Error('Fanen '+PROGRAM_SHEET_NAME+' findes ikke');
    const lastRow = Math.max(4, sheet.getLastRow());
    const values = sheet.getRange(4,1,lastRow-3,6).getDisplayValues();
    const program = [];
    values.forEach(function(row){
      const week = Number(row[0]);
      const round = String(row[1] || '').trim();
      if (!week || !round) return;
      if (round === 'Toto Cup') {
        const target = program.length && program[program.length-1].w === week ? program[program.length-1] : null;
        const toto = String(row[4] || '').split('·').map(function(x){return x.trim()}).filter(Boolean);
        if (target) target.toto = toto;
        else program.push({w:week,r:round,m:[],toto:toto,note:String(row[5]||'')});
        return;
      }
      const item = {w:week,r:round,m:[row[2],row[3]].map(function(x){return String(x||'').trim()}).filter(Boolean),note:String(row[5]||'')};
      const free = String(row[4] || '').trim();
      if (free === 'Alle') item.allFree = true;
      else if (free) item.free = free;
      program.push(item);
    });
    const entrySheet = ss.getSheetByName(SHEET_NAME);
    const saved = entrySheet ? readSavedEntries_(entrySheet) : [];
    return json_({ok:true,status:'online',writeEnabled:props.getProperty('WRITE_ENABLED')==='true',program:program,saved:saved});
  } catch (err) {
    return json_({ok:false,error:String(err && err.message || err)});
  }
}

function readSavedEntries_(sheet) {
  const last = sheet.getLastRow();
  if (last < FIRST_DATA_ROW) return [];
  const values = sheet.getRange(FIRST_DATA_ROW,1,last-FIRST_DATA_ROW+1,11).getDisplayValues();
  const saved = [];
  let currentWeek = '', currentRound = '', currentMatch = '';
  values.forEach(function(row) {
    if (String(row[0] || '').trim()) currentWeek = String(row[0]).trim();
    if (String(row[1] || '').trim()) currentRound = String(row[1]).trim();
    if (String(row[2] || '').trim()) currentMatch = String(row[2]).trim();
    const playerText = String(row[3] || '').trim();
    if (!playerText || !currentWeek || !currentRound || !currentMatch) return;
    const playerMatch = playerText.match(/Pingvinus|King|Gorilla|Kaninus|Kardinalus/);
    if (!playerMatch) return;
    saved.push({
      week:Number(currentWeek),
      round:currentRound,
      match:currentMatch,
      player:playerMatch[0],
      money:String(row[4] || '').trim(),
      result:String(row[8] || '').trim()
    });
  });
  return saved;
}

function doPost(e) {
  try {
    const payload = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (payload && payload.type === 'app_log') {
      logAppEvent_(payload);
      return json_({ok:true,status:'logged'});
    }
    const normalized = normalizePayload_(payload);
    const rows = buildRows_(normalized);
    const props = PropertiesService.getScriptProperties();
    const enabled = props.getProperty('WRITE_ENABLED') === 'true';

    if (!enabled) {
      return json_({ok:true,status:'dry-run',week:normalized.week,round:normalized.round,rowCount:rows.length,preview:rows});
    }

    const spreadsheetId = props.getProperty('SPREADSHEET_ID');
    if (!spreadsheetId) throw new Error('SPREADSHEET_ID mangler i Script Properties');
    const ss = SpreadsheetApp.openById(spreadsheetId);
    const sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) throw new Error('Fanen '+SHEET_NAME+' findes ikke');

    const lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try {
      const target = findTargetBlock_(sheet, normalized.week, normalized.round);
      if (target.existingCount && target.existingCount !== rows.length) {
        throw new Error('Eksisterende blok har '+target.existingCount+' rækker, men appen vil skrive '+rows.length+'. Manuel kontrol kræves.');
      }
      writeRows_(sheet, target.startRow, rows);
      SpreadsheetApp.flush();
      return json_({ok:true,status:'written',week:normalized.week,round:normalized.round,startRow:target.startRow,rowCount:rows.length});
    } finally {
      lock.releaseLock();
    }
  } catch (err) {
    return json_({ok:false,error:String(err && err.message || err)});
  }
}

function normalizePayload_(p) {
  if (!p || !Number.isInteger(Number(p.week))) throw new Error('Ugyldig uge');
  const week = Number(p.week);
  if (week < 1 || week > 53) throw new Error('Uge skal være 1-53');
  const round = String(p.round || '').trim();
  if (!round) throw new Error('Runde/aktivitet mangler');
  if (!Array.isArray(p.entries) || !p.entries.length) throw new Error('Ingen indtastninger');
  const allowed = ['Pingvinus','King','Gorilla','Kaninus','Kardinalus'];
  const entries = p.entries.map((x,i)=>{
    const player=String(x.player||'').trim(), match=String(x.match||'').trim();
    const money=Number(x.money);
    const result=String(x.result||'').trim().replace('–','-');
    if(!allowed.includes(player)) throw new Error('Ukendt spiller på linje '+(i+1));
    if(!match) throw new Error('Kamp mangler på linje '+(i+1));
    if(!Number.isFinite(money)||money<0) throw new Error('Ugyldigt Kr-beløb på linje '+(i+1));
    if(result && !/^\d+-\d+$/.test(result)) throw new Error('Ugyldigt resultat på linje '+(i+1));
    return {match:match,player:player,money:money,result:result};
  });
  return {week:week,round:round,entries:entries};
}

function buildRows_(p) {
  const emoji={Pingvinus:'🐧 Pingvinus',King:'👑 King',Gorilla:'🦍 Gorilla',Kaninus:'🐰 Kaninus',Kardinalus:'🙏 Kardinalus'};
  const rows=[];
  let previousMatch=null;
  p.entries.forEach((e,i)=>{
    const firstOfMatch=e.match!==previousMatch;
    rows.push([
      p.week,
      i===0?p.round:'',
      firstOfMatch?e.match:'',
      emoji[e.player],
      e.money,
      firstOfMatch?e.result:''
    ]);
    previousMatch=e.match;
  });
  return rows;
}

function findTargetBlock_(sheet, week, round) {
  const last=Math.max(FIRST_DATA_ROW,Math.min(sheet.getLastRow(),FIRST_DATA_ROW+MAX_SCAN_ROWS-1));
  const values=sheet.getRange(FIRST_DATA_ROW,1,last-FIRST_DATA_ROW+1,2).getDisplayValues();
  let firstBlank=null,start=null,count=0;
  for(let i=0;i<values.length;i++){
    const row=FIRST_DATA_ROW+i, w=String(values[i][0]).trim(), r=String(values[i][1]).trim();
    if(firstBlank===null && !w && !r) firstBlank=row;
    if(start===null && w===String(week) && r===round){start=row;count=1;continue}
    if(start!==null && row>start){
      if(w || r) break;
      count++;
    }
  }
  if(start!==null) return {startRow:start,existingCount:count};
  return {startRow:firstBlank || last+1,existingCount:0};
}

function writeRows_(sheet,startRow,rows) {
  // Never write formula/helper columns. Visible input columns are split deliberately.
  const left=rows.map(r=>r.slice(0,5));
  const results=rows.map(r=>[r[5]]);
  sheet.getRange(startRow,1,rows.length,5).setValues(left); // A:E
  sheet.getRange(startRow,9,rows.length,1).setValues(results); // I
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}


function logAppEvent_(payload) {
  var props = PropertiesService.getScriptProperties();
  var spreadsheetId = props.getProperty('SPREADSHEET_ID');
  var ss = spreadsheetId ? SpreadsheetApp.openById(spreadsheetId) : SpreadsheetApp.getActiveSpreadsheet();
  if (!ss) return;
  var sheet = ss.getSheetByName(APP_LOG_SHEET_NAME);
  if (!sheet) return;
  var eventName = String(payload.event || '').trim().slice(0,80);
  if (!eventName) return;
  var page = String(payload.page || '').trim().slice(0,80);
  var installation = String(payload.installation || '').trim().slice(0,100);
  var version = String(payload.version || '').trim().slice(0,40);
  var detail = String(payload.detail || '').trim().slice(0,250);
  sheet.appendRow([new Date(), eventName, page, installation, version, detail]);
}
