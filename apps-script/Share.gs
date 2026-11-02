/**
 * Designed & Developed by Nivesh Sahayak (https://www.niveshsahayak.in/). All rights reserved: use or redistribution needs written permission and visible credit.
 * share.groupchaton.com — Google Apps Script backend (community features)
 *
 * This is a SEPARATE project with its own Google Sheet. It does not touch ShareYourGroup's sheet or script:
 * new group submissions still go to ShareYourGroup's own web app.
 *
 * Setup (once): open the Sheet › Extensions › Apps Script, paste this file, run setup(),
 * then Deploy › New deployment › Web app (Execute as: Me, Who has access: Anyone).
 * Full steps: "Share Backend - Setup Guide.html".
 *
 * API (the website calls exactly this)
 *   GET  ?action=status&id=…   → {ok, adsOff, removed}                        (cached 60 s per id)
 *   GET  ?action=export        → {ok, updated, groups:{id:{adsOff, removed, desc, cat}}}  (GitHub build, every 15 min)
 *   POST (JSON as text/plain)  → action report | describe | categorise | owner
 *
 * Sheets (made by setup):
 *   Reports      every report (time, id, link, name, reason, visitor)
 *   Suggestions  description suggestions; the owner types yes / no in "decision"
 *   Owners       group owners asking for a review or edit; decision: done / restore / remove
 *   Votes        category votes (3 different visitors picking the same category → applied automatically)
 *   State        one row per group with something on it; decision: restore / remove
 */

const CONFIG = {
  REMOVE_AT: 3,            // distinct reporters (since the last restore) before a page is hidden
  RATE_MAX: 20,            // posts per visitor per hour
  STATUS_TTL: 60,          // seconds a status answer is cached
  DESC_MIN: 10,
  DESC_MAX: 300,
  VOTES_TO_APPLY: 3        // distinct visitors picking the same category
};

const REASONS = ['spam', 'adult', 'scam', 'hate', 'dead'];
const CATS = ['education', 'jobs', 'stocks', 'earning', 'business', 'shopping', 'tech', 'gaming', 'entertainment', 'music', 'fun',
  'friendship', 'love', 'quotes', 'news', 'sports', 'religion', 'travel', 'health', 'food', 'others'];

const SHEETS = {
  Reports: ['time', 'id', 'link', 'name', 'reason', 'visitor'],
  Suggestions: ['time', 'id', 'link', 'name', 'text', 'by', 'visitor', 'decision'],
  Owners: ['time', 'id', 'link', 'name', 'contact', 'note', 'visitor', 'decision'],
  Votes: ['time', 'id', 'cat', 'visitor'],
  State: ['id', 'adsOff', 'removed', 'reports', 'restoredAt', 'cat', 'desc', 'decision', 'updated']
};
// State columns (0-based)
const ST = { ID: 0, ADS: 1, REM: 2, REP: 3, RESTORED: 4, CAT: 5, DESC: 6, DEC: 7, UPD: 8 };

// Copied from ShareYourGroup's apps-script/Code.gs (keep both in step by hand). Whole-word matches only.
// EDIT: add or remove words here.
const BLOCKED = [
  // adult
  'porn', 'porno', 'xxx', 'sex', 'sexy', 'nude', 'nudes', 'erotic', 'adult', '18+', 'milf', 'blowjob', 'escort', 'escorts', 'call girl', 'call girls',
  'hot girl', 'hot girls', 'hot video', 'hot videos', 'bdsm', 'bokep', 'onlyfans', 'nangi', 'desi bhabhi', 'sex chat', 'video call girl',
  'chatting girl', 'chatting girls', 'chat girl', 'chat girls', 'girls chat', 'girl chat', 'hot chat', 'sexy chat', 'dirty chat',
  'video call', 'bhabhi', 'aunty', 'aunties', 'desi girl', 'desi girls', 'paid friendship', 'friendship club', 'night chat', 'lonely girl', 'single girls',
  // abuse
  'madarchod', 'behenchod', 'bhenchod', 'chutiya', 'randi', 'chut', 'gaand', 'gandu', 'bhosdike', 'bhosadike', 'lund', 'fucker', 'slut', 'whore',
  // hate
  'nigger', 'faggot', 'kike', 'chink', 'raghead', 'pajeet',
  // drugs
  'cocaine', 'heroin', 'meth', 'mdma', 'lsd', 'ganja', 'charas', 'brown sugar', 'chitta',
  // scams
  'money doubling', 'double your money', 'guaranteed profit', '100% profit', 'free recharge', 'win iphone', 'lottery', 'jackpot',
  'otp', 'virtual number', 'virtual numbers', 'usa numbers', 'fake id', 'hacked', 'carding', 'bitcoin scam', 'crypto scam',
  // extremism
  'isis', 'daesh', 'al-qaeda', 'al qaeda', 'taliban', 'lashkar', 'jaish'
];
const BLOCKED_RE = new RegExp('(?:^|[^\\p{L}\\p{N}])(?:' + BLOCKED.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')(?=$|[^\\p{L}\\p{N}])', 'iu');
// Anything that looks like a link, a domain or a handle to another platform.
const LINK_RE = /(https?:|www\.|wa\.me|t\.me\/|chat\.whatsapp|whatsapp\.com|bit\.ly)/i;
const DOMAIN_RE = /\b[a-z0-9-]{2,}\.(com|in|net|org|me|io|co|xyz|link|ly|info|app|site|online|top)(\/|\b)/;   // lowercase only, so "group.In" is fine
const ID_RE = /^[A-Za-z0-9_-]{4,64}$/;
const VISITOR_RE = /^[A-Za-z0-9_-]{6,64}$/;

/* ------------------------------------------------------------------ web app */

function doGet(e) {
  const p = (e && e.parameter) || {};
  try {
    if (p.action === 'status') return json(status(p.id));
    if (p.action === 'export') return json(exportAll());
    return json({ ok: true, service: 'share.groupchaton.com' });
  } catch (err) {
    return json({ ok: false, message: 'Server error' });
  }
}

function doPost(e) {
  let d = {};
  try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return json({ ok: false, message: 'Bad request' }); }
  if (!d || typeof d !== 'object') return json({ ok: false, message: 'Bad request' });
  const fn = { report: report, describe: describe, categorise: categorise, owner: ownerRequest }[d.action];
  if (!fn) return json({ ok: false, message: 'Unknown action' });
  if (!ID_RE.test(String(d.id || ''))) return json({ ok: false, message: 'Unknown group' });
  if (!VISITOR_RE.test(String(d.visitor || ''))) return json({ ok: false, message: 'Please reload the page and try again.' });
  if (!rateOk(d.visitor)) return json({ ok: false, message: 'Too many requests. Please try again in an hour.' });
  const lock = LockService.getScriptLock();
  try { lock.waitLock(15000); } catch (err) { return json({ ok: false, message: 'Busy right now. Please try again.' }); }
  try {
    return json(fn(d));
  } catch (err) {
    return json({ ok: false, message: 'Something went wrong. Please try again.' });
  } finally {
    lock.releaseLock();
  }
}

/* ------------------------------------------------------------------ GET actions */

function status(id) {
  id = String(id || '');
  if (!ID_RE.test(id)) return { ok: false, message: 'Unknown group' };
  const cache = CacheService.getScriptCache();
  const hit = cache.get('st:' + id);
  if (hit) return JSON.parse(hit);
  const row = findState(id);
  const out = { ok: true, adsOff: !!(row && yes(row.v[ST.ADS])), removed: !!(row && yes(row.v[ST.REM])) };
  cache.put('st:' + id, JSON.stringify(out), CONFIG.STATUS_TTL);
  return out;
}

function exportAll() {
  const lock = LockService.getScriptLock();
  if (lock.tryLock(20000)) {
    try { applyDecisions(); } finally { lock.releaseLock(); }
  }
  const groups = {};
  sheetValues('State').forEach(r => {
    const id = String(r[ST.ID] || '').trim();
    if (!id) return;
    const g = { adsOff: yes(r[ST.ADS]), removed: yes(r[ST.REM]), desc: String(r[ST.DESC] || ''), cat: String(r[ST.CAT] || '') };
    if (g.adsOff || g.removed || g.desc || g.cat) groups[id] = g;
  });
  return { ok: true, updated: new Date().toISOString(), groups: groups };
}

/* ------------------------------------------------------------------ POST actions (run inside the lock) */

function report(d) {
  const reason = String(d.reason || '').toLowerCase();
  if (REASONS.indexOf(reason) < 0) return { ok: false, message: 'Please pick a reason.' };
  const id = String(d.id);
  sheet('Reports').appendRow(safeRow([new Date(), id, cleanLink(d.link), clean(d.name).slice(0, 120), reason, d.visitor]));
  const st = getState(id);
  if (reason === 'dead') {
    return { ok: true, adsOff: yes(st.v[ST.ADS]), removed: yes(st.v[ST.REM]), message: 'Thanks! We will check whether this link still works.' };
  }
  const n = countReporters(id, st.v[ST.RESTORED]);
  st.v[ST.REP] = n;
  if (n >= 1) st.v[ST.ADS] = true;
  if (n >= CONFIG.REMOVE_AT || decisionOf(st.v) === 'remove') { st.v[ST.REM] = true; st.v[ST.ADS] = true; }
  saveState(st);
  const removed = yes(st.v[ST.REM]);
  return {
    ok: true, adsOff: yes(st.v[ST.ADS]), removed: removed,
    message: removed ? 'Thanks for reporting. This group is now hidden until we review it.' : 'Thanks for reporting. We will review this group.'
  };
}

function describe(d) {
  const raw = String(d.text || '');
  const text = clean(raw);
  if (hasLink(raw) || hasLink(text)) return { ok: false, message: 'Please don\'t include links or website names.' };
  if (text.length < CONFIG.DESC_MIN) return { ok: false, message: 'Please write at least ' + CONFIG.DESC_MIN + ' characters.' };
  if (text.length > CONFIG.DESC_MAX) return { ok: false, message: 'Please keep it under ' + CONFIG.DESC_MAX + ' characters.' };
  const by = clean(d.by).slice(0, 40);
  if (isBlocked(text + ' ' + by) || hasLink(by)) return { ok: false, message: 'Sorry, this text can\'t be used.' };
  sheet('Suggestions').appendRow(safeRow([new Date(), String(d.id), cleanLink(d.link), clean(d.name).slice(0, 120), text, by, d.visitor, '']));
  return { ok: true, message: 'Thanks! It will appear after a quick review.' };
}

function categorise(d) {
  const cat = String(d.cat || '').toLowerCase();
  if (CATS.indexOf(cat) < 0) return { ok: false, message: 'Please pick a category.' };
  const id = String(d.id);
  sheet('Votes').appendRow(safeRow([new Date(), id, cat, d.visitor]));
  // each visitor's latest vote counts once
  const latest = {};
  rowsFor('Votes', 2, id).forEach(r => { latest[String(r[3])] = String(r[2]); });
  const tally = {};
  Object.keys(latest).forEach(v => { tally[latest[v]] = (tally[latest[v]] || 0) + 1; });
  let best = '', bestN = 0;
  Object.keys(tally).forEach(c => { if (tally[c] > bestN) { best = c; bestN = tally[c]; } });
  if (bestN >= CONFIG.VOTES_TO_APPLY) {
    const st = getState(id);
    if (String(st.v[ST.CAT]) !== best) { st.v[ST.CAT] = best; saveState(st); }
    if (best === cat) return { ok: true, applied: true, message: 'Thanks! The category is now "' + cat + '".' };
  }
  return { ok: true, applied: false, message: 'Thanks! Your vote is counted. The category changes when ' + CONFIG.VOTES_TO_APPLY + ' visitors agree.' };
}

function ownerRequest(d) {
  const contact = clean(d.contact).slice(0, 100);
  const note = clean(d.note).slice(0, 500);
  if (contact.length < 5) return { ok: false, message: 'Please add an email or phone number so we can reply.' };
  if (note.length < 5) return { ok: false, message: 'Please tell us what you would like us to change.' };
  if (isBlocked(note)) return { ok: false, message: 'Sorry, this text can\'t be used.' };
  sheet('Owners').appendRow(safeRow([new Date(), String(d.id), cleanLink(d.link), clean(d.name).slice(0, 120), contact, note, d.visitor, '']));
  return { ok: true, message: 'Thanks! We will review your request and reply soon.' };
}

/* ------------------------------------------------------------------ owner decisions */

/**
 * Reads the owner's decisions and updates State:
 *   State.decision   restore → shows the page again, earlier reports no longer count (becomes "restored")
 *                    remove  → keeps the page hidden for good
 *   Suggestions      latest "yes" per group becomes that group's description; all "no" clears it
 *   Owners.decision  restore / remove → copied to State (then shows "done: restore" / "done: remove")
 * Runs from the Share menu, every 15 minutes, and before every export. Caller holds the lock (or none is needed).
 */
function applyDecisions() {
  const st = sheet('State');
  const rows = sheetValues('State');
  const byId = {};
  rows.forEach((r, i) => { const id = String(r[ST.ID] || '').trim(); if (id) byId[id] = { row: i + 2, v: r, dirty: false }; });
  const get = id => byId[id] || (byId[id] = { row: 0, v: ['' + id, false, false, 0, '', '', '', '', ''], dirty: true });

  // Owners: restore / remove requests the owner approved
  const ow = sheet('Owners');
  sheetValues('Owners').forEach((r, i) => {
    const dec = String(r[7] || '').trim().toLowerCase();
    if (dec !== 'restore' && dec !== 'remove') return;
    const s = get(String(r[1]).trim());
    s.v[ST.DEC] = dec; s.dirty = true;
    ow.getRange(i + 2, 8).setValue('done: ' + dec);
  });

  // Suggestions: latest yes per id; ids whose suggestions are all non-yes lose their description
  const desc = {}, seen = {};
  sheetValues('Suggestions').forEach(r => {
    const id = String(r[1] || '').trim();
    const dec = String(r[7] || '').trim().toLowerCase();
    if (!id || !dec) return;            // still waiting for review
    seen[id] = true;
    if (dec === 'yes' || dec === 'y') {
      const t = r[0] instanceof Date ? r[0].getTime() : 0;
      if (!desc[id] || t >= desc[id].t) desc[id] = { t: t, text: String(r[4] || '') };
    }
  });
  Object.keys(seen).forEach(id => {
    const want = desc[id] ? desc[id].text : '';
    if (!desc[id] && !byId[id]) return;
    const s = get(id);
    if (String(s.v[ST.DESC] || '') !== want) { s.v[ST.DESC] = want; s.dirty = true; }
  });

  // State decisions
  Object.keys(byId).forEach(id => {
    const s = byId[id];
    const dec = decisionOf(s.v);
    if (dec === 'restore') {
      s.v[ST.RESTORED] = new Date(); s.v[ST.ADS] = false; s.v[ST.REM] = false; s.v[ST.REP] = 0; s.v[ST.DEC] = 'restored'; s.dirty = true;
    } else if (dec === 'remove' && !(yes(s.v[ST.REM]) && yes(s.v[ST.ADS]))) {
      s.v[ST.REM] = true; s.v[ST.ADS] = true; s.dirty = true;
    }
  });

  const cache = CacheService.getScriptCache();
  const changed = [];
  Object.keys(byId).forEach(id => {
    const s = byId[id];
    if (!s.dirty) return;
    s.v[ST.UPD] = new Date();
    if (s.row) st.getRange(s.row, 1, 1, SHEETS.State.length).setValues([safeRow(s.v)]);
    else st.appendRow(safeRow(s.v));
    changed.push('st:' + id);
  });
  if (changed.length) cache.removeAll(changed);
  return changed.length;
}

/* ------------------------------------------------------------------ menu, triggers, GitHub */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('Share')
    .addItem('Apply decisions now', 'menuApply')
    .addItem('Rebuild website now', 'menuRebuild')
    .addSeparator()
    .addItem('Run setup again', 'setup')
    .addToUi();
}

function menuApply() {
  const n = withLock(applyDecisions);
  SpreadsheetApp.getActive().toast(n + ' group(s) updated. The website shows the change after its next rebuild (within 15 minutes).', 'Share', 8);
}

function menuRebuild() {
  withLock(applyDecisions);
  const ok = kickGitHub();
  if (ok) SpreadsheetApp.getActive().toast('Website rebuild started. It is live in about 3 minutes.', 'Share', 8);
  else SpreadsheetApp.getUi().alert('Could not start the rebuild.\n\nAdd a GitHub key first: Extensions › Apps Script › Project Settings › Script properties › GITHUB_TOKEN (see the setup guide). The website still rebuilds by itself every 15 minutes.');
}

/** Time trigger (every 15 min, made by setup): apply decisions, then ask GitHub to rebuild. */
function every15() {
  withLock(applyDecisions);
  try { kickGitHub(); } catch (e) {}
}

/* Starts the website build on GitHub. Needs a fine-grained token saved under
   Project Settings → Script properties → GITHUB_TOKEN (only repo share-groupchaton, "Actions: Read and write"). */
const GH_REPO = 'raimayank7/share-groupchaton';
const GH_WORKFLOW = 'build.yml';

function kickGitHub() {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) { Logger.log('No GITHUB_TOKEN in Script properties yet.'); return false; }
  const res = UrlFetchApp.fetch('https://api.github.com/repos/' + GH_REPO + '/actions/workflows/' + GH_WORKFLOW + '/dispatches', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: { Authorization: 'Bearer ' + token.trim(), Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' },
    payload: JSON.stringify({ ref: 'main' })
  });
  const ok = res.getResponseCode() === 204;
  Logger.log(ok ? 'GitHub job started.' : 'GitHub said ' + res.getResponseCode() + ': ' + res.getContentText().slice(0, 300));
  return ok;
}

/** Run once (safe to run again): makes the sheets, review drop-downs and the 15-minute trigger. */
function setup() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  PropertiesService.getScriptProperties().setProperty('SHEET_ID', ss.getId());
  Object.keys(SHEETS).forEach(name => {
    const sh = ss.getSheetByName(name) || ss.insertSheet(name);
    const head = SHEETS[name];
    sh.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
    sh.setFrozenRows(1);
    sh.getRange('A:Z').setNumberFormat('@');                       // ids stay text (no 1E+21, no dropped zeros)
    (name === 'State' ? ['E2:E', 'I2:I'] : ['A2:A']).forEach(a1 => sh.getRange(a1).setNumberFormat('yyyy-mm-dd hh:mm'));
  });
  dropdown(ss.getSheetByName('Suggestions'), 'H2:H', ['yes', 'no'], 'Type yes to show this description, no to reject it.');
  dropdown(ss.getSheetByName('Owners'), 'H2:H', ['done', 'restore', 'remove'], 'done = handled; restore / remove = show or hide the page.');
  dropdown(ss.getSheetByName('State'), 'H2:H', ['restore', 'remove'], 'restore = show the page again; remove = hide it for good.');
  const first = ss.getSheetByName('Sheet1');
  if (first && first.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(first);

  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('every15').timeBased().everyMinutes(15).create();
  Logger.log('Setup done. Sheets: %s. Trigger: every15 every 15 minutes.', Object.keys(SHEETS).join(', '));
}

function dropdown(sh, a1, list, help) {
  const rule = SpreadsheetApp.newDataValidation().requireValueInList(list, true).setAllowInvalid(true).setHelpText(help).build();
  sh.getRange(a1).setDataValidation(rule);
}

/* ------------------------------------------------------------------ helpers */

function book() {
  const id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

function sheet(name) { return book().getSheetByName(name); }

function sheetValues(name) {
  const sh = sheet(name);
  const n = sh.getLastRow() - 1;
  return n > 0 ? sh.getRange(2, 1, n, SHEETS[name].length).getValues() : [];
}

/** Rows of a sheet whose column `col` (1-based) equals `id` exactly. */
function rowsFor(name, col, id) {
  const sh = sheet(name);
  const n = sh.getLastRow() - 1;
  if (n <= 0) return [];
  const width = SHEETS[name].length;
  return sh.getRange(2, col, n, 1).createTextFinder(id).matchEntireCell(true).matchCase(true).findAll()
    .map(c => sh.getRange(c.getRow(), 1, 1, width).getValues()[0]);
}

function findState(id) {
  const sh = sheet('State');
  const n = sh.getLastRow() - 1;
  if (n <= 0) return null;
  const c = sh.getRange(2, 1, n, 1).createTextFinder(id).matchEntireCell(true).matchCase(true).findNext();
  return c ? { row: c.getRow(), v: sh.getRange(c.getRow(), 1, 1, SHEETS.State.length).getValues()[0] } : null;
}

function getState(id) {
  return findState(id) || { row: 0, v: [id, false, false, 0, '', '', '', '', ''] };
}

function saveState(s) {
  s.v[ST.UPD] = new Date();
  const sh = sheet('State');
  if (s.row) sh.getRange(s.row, 1, 1, SHEETS.State.length).setValues([safeRow(s.v)]);
  else { sh.appendRow(safeRow(s.v)); s.row = sh.getLastRow(); }
  CacheService.getScriptCache().remove('st:' + s.v[ST.ID]);
}

/** Distinct visitors who reported `id` (not "dead") after the last restore. */
function countReporters(id, restoredAt) {
  const since = restoredAt instanceof Date ? restoredAt.getTime() : (restoredAt ? new Date(restoredAt).getTime() || 0 : 0);
  const who = {};
  rowsFor('Reports', 2, id).forEach(r => {
    const t = r[0] instanceof Date ? r[0].getTime() : 0;
    if (String(r[4]) !== 'dead' && t >= since) who[String(r[5])] = true;
  });
  return Object.keys(who).length;
}

function decisionOf(v) { return String(v[ST.DEC] || '').trim().toLowerCase(); }

function yes(v) { return v === true || /^(true|yes|y|1)$/i.test(String(v || '').trim()); }

function withLock(fn) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try { return fn(); } finally { lock.releaseLock(); }
}

/** Max CONFIG.RATE_MAX posts per visitor per hour. */
function rateOk(visitor) {
  const cache = CacheService.getScriptCache();
  const key = 'rl:' + visitor;
  const n = Number(cache.get(key) || 0);
  if (n >= CONFIG.RATE_MAX) return false;
  cache.put(key, String(n + 1), 3600);
  return true;
}

/** Stops text that starts with = + - @ from running as a spreadsheet formula. */
function safeRow(arr) {
  return arr.map(v => (typeof v === 'string' && /^[=+\-@]/.test(v)) ? "'" + v : v);
}

function cleanLink(s) {
  s = String(s || '').trim();
  return /^https:\/\/(chat\.whatsapp\.com|(www\.)?whatsapp\.com)\//.test(s) ? s.slice(0, 200) : '';
}

function clean(s) {
  return String(s || '').replace(/<[^>]*>/g, ' ').replace(/[<>]/g, '').replace(/\s+/g, ' ').trim();
}

function hasLink(s) {
  return LINK_RE.test(s) || DOMAIN_RE.test(s);
}

function isBlocked(text) {
  return BLOCKED_RE.test(String(text || '').normalize('NFKC'));
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
