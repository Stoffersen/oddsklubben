/**
 * Oddsklubben mobile app – Google Apps Script backend skeleton.
 * NOT DEPLOYED. Configure SCRIPT_PROPERTY SPREADSHEET_ID before use.
 * Do not put credentials in the browser app.
 */
const SHEET_NAME = '📲 Rundeindtastning';

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    validatePayload_(payload);
    // Writing is deliberately disabled until the new-season sheet migration is approved.
    return json_({ ok: false, status: 'dry-run', message: 'Backend is ready, but Sheet writes are disabled.' });
  } catch (err) {
    return json_({ ok: false, error: String(err.message || err) });
  }
}

function validatePayload_(p) {
  if (!p || !p.week || !p.round || !Array.isArray(p.entries)) throw new Error('Ugyldig payload');
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
