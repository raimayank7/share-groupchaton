/* Share by GroupChatOn (share.groupchaton.com) — Designed & Developed by Nivesh Sahayak (https://www.niveshsahayak.in/)
   Theme, menu, instant search (hero, / and Ctrl K palette, search page), explore filters, save ★ and recently viewed,
   the 5-second link check (starts on page load), ads only after the listing's report check, report / describe / categorise / owner forms,
   copy / share / QR, add-your-group form, counters, progress bar, back to top, toasts, install, renamed-listing redirects. */
(function () {
  'use strict';
  var C = window.SHARE || {}, doc = document, root = doc.documentElement, body = doc.body;
  var CATS = C.cats || {};
  function $(s, r) { return (r || doc).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function jget(k, d) { try { return JSON.parse(store(k) || '') || d; } catch (e) { return d; } }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function norm(s) { return String(s).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, ''); }
  var ID = body.getAttribute('data-id'), isGroupPage = !!ID;
  var STAR = '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>';

  /* ---------- toasts ---------- */
  var toasts = $('.toasts');
  function toast(t) { if (!toasts) return; var d = doc.createElement('div'); d.className = 'toast'; d.textContent = t; toasts.appendChild(d); setTimeout(function () { d.remove(); }, 2600); }

  /* ---------- light / dark, menu ---------- */
  $$('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () { var t = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light'; root.setAttribute('data-theme', t); store('share-theme', t); });
  });
  var nav = $('#nav'), mb = $('.menu-btn');
  if (nav && mb) mb.addEventListener('click', function () { var o = nav.classList.toggle('is-open'); mb.setAttribute('aria-expanded', String(o)); });

  /* ---------- scroll progress + back to top ---------- */
  var bar = $('.progress i'), top = $('.totop');
  function onScroll() {
    var h = doc.documentElement.scrollHeight - innerHeight;
    if (bar) bar.style.width = (h > 0 ? (scrollY / h) * 100 : 0) + '%';
    if (top) top.hidden = scrollY < 900;
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (top) top.addEventListener('click', function () { scrollTo({ top: 0, behavior: 'smooth' }); });

  /* ---------- counters ---------- */
  var cnt = $$('[data-count-to]');
  if (cnt.length && 'IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; io.unobserve(e.target);
        var el = e.target, to = +el.getAttribute('data-count-to'), t0 = performance.now();
        (function step(t) { var k = Math.min(1, (t - t0) / 1200); el.textContent = Math.round(to * (1 - Math.pow(1 - k, 3))).toLocaleString('en-IN'); if (k < 1) requestAnimationFrame(step); })(t0);
      });
    });
    cnt.forEach(function (el) { io.observe(el); });
  }

  /* ---------- a random id for this browser: reports and votes count once per visitor ---------- */
  var visitor = store('share-visitor');
  if (!visitor) { visitor = 'v' + Math.random().toString(36).slice(2) + Date.now().toString(36); store('share-visitor', visitor); }
  function post(url, data) {
    return fetch(url, { method: 'POST', body: JSON.stringify(data), headers: { 'Content-Type': 'text/plain;charset=utf-8' } }).then(function (r) { return r.json(); });
  }

  /* ---------- Google Analytics + AdSense (ads only where allowed) ---------- */
  function loadScript(src, cors) { var s = doc.createElement('script'); s.async = true; s.src = src; if (cors) s.crossOrigin = 'anonymous'; doc.head.appendChild(s); return s; }   // only AdSense wants crossorigin
  if (C.analytics && location.protocol === 'https:') {
    window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date()); gtag('config', C.analytics); loadScript('https://www.googletagmanager.com/gtag/js?id=' + C.analytics);
  }
  var adsLoaded = false;
  function loadAds() {
    if (adsLoaded || !C.ads || body.getAttribute('data-ads') !== '1' || location.protocol !== 'https:') return;
    adsLoaded = true; loadScript('https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + C.ads, true);
  }
  function addNoindex() { if (!$('meta[name=robots][content^=noindex]')) { var m = doc.createElement('meta'); m.name = 'robots'; m.content = 'noindex,follow'; doc.head.appendChild(m); } }
  function showReported() { var n = $('[data-reported]'); if (n) n.hidden = false; addNoindex(); }
  function listingRemoved() {
    addNoindex();
    var j = $('[data-join]'); if (j) j.innerHTML = '<p class="muted" style="margin:0">This listing was reported by several people and is hidden while we review it.</p>';
    var n = $('[data-reported]'); if (n) n.hidden = true;
  }
  if (!isGroupPage || !C.api) loadAds();
  else {
    // one report is enough to stop ads: ask first, and show no ads if the answer doesn't come in time
    var late = false, timer = setTimeout(function () { late = true; }, 4000);
    fetch(C.api + '?action=status&id=' + encodeURIComponent(ID)).then(function (r) { return r.json(); }).then(function (s) {
      if (late) return; clearTimeout(timer);
      if (s && s.removed) return listingRemoved();
      if (s && s.adsOff) return showReported();
      if (s && s.ok) loadAds();
    }).catch(function () { clearTimeout(timer); });
  }

  /* ---------- listing index (search, explore, saved, recent) ---------- */
  var index = null;   // [slug, name, cat, ch, photo, lang, unix seconds]
  function getIndex() { return index || (index = fetch('/data/index.json').then(function (r) { return r.json(); })); }
  var saved = jget('share-saved', []);
  function isSaved(slug) { return saved.indexOf(slug) > -1; }
  function card(x) {
    var c = CATS[x[2]] || ['', '', '#25D366'], isNew = x[6] && (Date.now() / 1000 - x[6]) < 3 * 86400;
    var pic = x[4] ? '<img src="' + esc(x[4]) + '" alt="" loading="lazy" width="56" height="56">' : '<span>' + esc((x[1][0] || '?').toUpperCase()) + '</span>';
    return '<div class="card" style="--c:' + c[2] + '"><span class="av">' + pic + '</span><span class="ct"><span class="tags"><em class="ty ty-' + (x[3] ? 'channel">Channel' : 'group">Group') + '</em>' +
      (c[0] ? '<em>' + c[1] + ' ' + esc(c[0]) + '</em>' : '') + (isNew ? '<em class="new">NEW</em>' : '') + '</span><a class="cl" href="/g/' + esc(x[0]) + '/">' + esc(x[1]) + '</a>' +
      (x[5] ? '<small>' + esc(x[5]) + '</small>' : '') + '</span><button class="star" type="button" data-save="' + esc(x[0]) + '" aria-label="Save ' + esc(x[1]) + '" aria-pressed="' + isSaved(x[0]) + '">' + STAR + '</button></div>';
  }
  function match(list, q) {
    var words = norm(q).split(/\s+/).filter(Boolean);
    if (!words.length) return list;
    return list.filter(function (x) { var n = norm(x[1] + ' ' + ((CATS[x[2]] || [''])[0]) + ' ' + (x[5] || '') + ' ' + (x[3] ? 'channel' : 'group')); return words.every(function (w) { return n.indexOf(w) > -1; }); });
  }

  /* save ★ (works on cards drawn now and later) */
  function paintStars() { $$('[data-save]').forEach(function (b) { var on = isSaved(b.getAttribute('data-save')); b.setAttribute('aria-pressed', String(on)); var t = b.querySelector('span'); if (t) t.textContent = on ? 'Saved' : 'Save'; }); }
  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-save]'); if (!b) return;
    e.preventDefault(); var s = b.getAttribute('data-save'), i = saved.indexOf(s);
    if (i > -1) { saved.splice(i, 1); toast('Removed from Saved'); } else { saved.unshift(s); toast('★ Saved on this device'); }
    store('share-saved', JSON.stringify(saved.slice(0, 300))); paintStars();
  });
  paintStars();

  /* recently viewed: written on a listing page, shown in the corner panel above "back to top" */
  var viewed = $('[data-viewed]');
  if (viewed) { try { var v = JSON.parse(viewed.getAttribute('data-viewed')), r = jget('share-recent', []).filter(function (x) { return x[0] !== v[0]; }); r.unshift(v); store('share-recent', JSON.stringify(r.slice(0, 12))); } catch (e) {} }
  var rv = $('[data-rv]'), rvBtn = $('[data-rv-toggle]');
  function rvRow(x) {
    var pic = x[4] ? '<img src="' + esc(x[4]) + '" alt="" loading="lazy" width="36" height="36">' : '<span>' + esc((x[1][0] || '?').toUpperCase()) + '</span>';
    return '<a class="rv-i" href="/g/' + esc(x[0]) + '/"><span class="av">' + pic + '</span><span class="rv-t">' + esc(x[1]) + '<small>' + (x[3] ? 'Channel' : 'Group') + '</small></span></a>';
  }
  function rvPaint() {
    var rl = jget('share-recent', []), here = viewed ? (function () { try { return JSON.parse(viewed.getAttribute('data-viewed'))[0]; } catch (e) { return ''; } })() : '';
    rl = rl.filter(function (x) { return x[0] !== here; });
    if (!rvBtn) return;
    rvBtn.hidden = !rl.length; $('[data-rv-n]', rvBtn).textContent = rl.length || '';
    $('[data-rv-list]', rv).innerHTML = rl.map(rvRow).join('');
    if (!rl.length) rvOpen(false);
  }
  function rvOpen(o) { if (!rv) return; rv.hidden = !o; rvBtn.setAttribute('aria-expanded', String(o)); }
  if (rv && rvBtn) {
    rvBtn.addEventListener('click', function (e) { e.stopPropagation(); rvOpen(rv.hidden); });
    $('[data-rv-clear]', rv).addEventListener('click', function () { store('share-recent', '[]'); rvPaint(); });
    rv.addEventListener('click', function (e) { e.stopPropagation(); });
    doc.addEventListener('click', function () { rvOpen(false); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') rvOpen(false); });
    rvPaint();
  }
  if (location.pathname.indexOf('/submit/') === 0) { var fa = $('.fab-add'); if (fa) fa.hidden = true; }

  /* saved page */
  var sv = $('[data-saved]');
  if (sv) getIndex().then(function (list) {
    var by = {}; list.forEach(function (x) { by[x[0]] = x; });
    var items = saved.map(function (s) { return by[s]; }).filter(Boolean);
    sv.innerHTML = items.map(card).join(''); $('[data-saved-empty]').hidden = items.length > 0;
  });

  /* ---------- instant search: hero box, / or Ctrl K palette, search page ---------- */
  function wireSearch(box) {
    var input = $('input', box), res = $('.hs-res', box), on = -1, t = 0;
    function draw() {
      var q = input.value.trim();
      if (!q) { res.hidden = true; return; }
      getIndex().then(function (list) {
        var hits = match(list, q);
        res.innerHTML = hits.slice(0, 8).map(function (x) {
          var c = CATS[x[2]] || [''], pic = x[4] ? '<img src="' + esc(x[4]) + '" alt="" width="38" height="38">' : '<span>' + esc((x[1][0] || '?').toUpperCase()) + '</span>';
          return '<a href="/g/' + esc(x[0]) + '/"><span class="av">' + pic + '</span><span><b>' + esc(x[1]) + '</b><small>' + (x[3] ? 'Channel' : 'Group') + (c[0] ? ' · ' + esc(c[0]) : '') + (x[5] ? ' · ' + esc(x[5]) : '') + '</small></span></a>';
        }).join('') + '<a class="all" href="/search/?q=' + encodeURIComponent(q) + '">' + (hits.length ? 'See all ' + hits.length + ' results →' : 'No match. Try other words →') + '</a>';
        res.hidden = false; on = -1;
      });
    }
    input.addEventListener('input', function () { clearTimeout(t); t = setTimeout(draw, 90); });
    input.addEventListener('keydown', function (e) {
      var links = $$('a', res); if (!links.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); on = (on + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length; links.forEach(function (a, i) { a.classList.toggle('is-on', i === on); }); }
      if (e.key === 'Enter') { e.preventDefault(); location.href = (links[on] || links[links.length - 1]).href; }
    });
    doc.addEventListener('click', function (e) { if (!box.contains(e.target)) res.hidden = true; });
    return input;
  }
  var hero = $('[data-hero-search]'); if (hero) wireSearch(hero);
  var pal = null;
  function openPalette() {
    if (hero && hero.getBoundingClientRect().top > 0 && hero.getBoundingClientRect().bottom < innerHeight) { $('input', hero).focus(); return; }
    if (!pal) {
      pal = doc.createElement('dialog'); pal.className = 'pal';
      pal.innerHTML = '<div class="hs"><span class="hs-ic"><svg class="i" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></span><input type="search" placeholder="Search groups and channels…" aria-label="Search"><kbd>Esc</kbd><div class="hs-res" hidden></div></div>';
      body.appendChild(pal); wireSearch($('.hs', pal));
      pal.addEventListener('click', function (e) { if (e.target === pal) pal.close(); });
    }
    pal.showModal(); $('input', pal).focus();
  }
  $$('[data-palette]').forEach(function (a) { a.addEventListener('click', function (e) { if (pal !== false && 'HTMLDialogElement' in window) { e.preventDefault(); openPalette(); } }); });
  doc.addEventListener('keydown', function (e) {
    var typing = /input|textarea|select/i.test((e.target.tagName || '')) || e.target.isContentEditable;
    if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) { e.preventDefault(); openPalette(); }
    if (e.key === 'Escape' && nav) { nav.classList.remove('is-open'); if (mb) mb.setAttribute('aria-expanded', 'false'); }
  });
  var S = $('[data-search]');
  if (S) {
    var q = $('input', S), out = $('[data-results]', S), cntEl = $('[data-search-count]', S), st = 0;
    var init = new URLSearchParams(location.search).get('q'); if (init) q.value = init;
    function run() {
      getIndex().then(function (list) {
        var hits = q.value.trim() ? match(list, q.value) : list.slice(0, 24);
        cntEl.textContent = q.value.trim() ? hits.length + ' found' : 'Newest listings';
        out.innerHTML = hits.length ? hits.slice(0, 90).map(card).join('') : '<p class="muted">Nothing found. Try fewer words, or <a href="/categories/">browse categories</a>.</p>';
        paintStars();
      }).catch(function () { cntEl.textContent = 'Search needs an internet connection.'; });
    }
    q.addEventListener('input', function () { clearTimeout(st); st = setTimeout(run, 120); }); run();
  }

  /* ---------- explore: type, category, language, sort, load more ---------- */
  var X = $('[data-explore]');
  if (X) {
    var f = { type: 'all', cat: '', lang: '', sort: 'new' }, shown = 0, rows = [], list = $('[data-ex-list]', X), more = $('[data-ex-more]', X), info = $('[data-ex-count]', X);
    function apply(reset) {
      getIndex().then(function (all) {
        if (reset) {
          rows = all.filter(function (x) { return (f.type === 'all' || String(x[3]) === f.type) && (!f.cat || x[2] === f.cat) && (!f.lang || x[5] === f.lang); });
          if (f.sort === 'az') rows = rows.slice().sort(function (a, b) { return a[1].localeCompare(b[1]); });
          shown = 0; list.innerHTML = '';
        }
        var next = rows.slice(shown, shown + 24); shown += next.length;
        list.insertAdjacentHTML('beforeend', next.map(card).join(''));
        info.textContent = '> ' + rows.length.toLocaleString('en-IN') + ' match' + (rows.length === 1 ? '' : 'es') + ' · showing ' + shown;
        more.hidden = shown >= rows.length; paintStars();
      });
    }
    $$('[data-type]', X).forEach(function (b) { b.addEventListener('click', function () { $$('[data-type]', X).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); }); f.type = b.getAttribute('data-type'); apply(true); }); });
    $$('[data-f]', X).forEach(function (s) { s.addEventListener('change', function () { f[s.getAttribute('data-f')] = s.value; apply(true); }); });
    more.addEventListener('click', function () { apply(false); });
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { if (es[0].isIntersecting && !more.hidden && shown) apply(false); }, { rootMargin: '400px' }).observe(more);
    apply(true);
  }

  /* ---------- the 5-second join ring ---------- */
  $$('[data-join]').forEach(function (box) {
    var wait = $('.join-wait', box), go = $('[data-join-go]', box), ok = $('.join-ok', box), count = $('[data-count]', box);
    if (!wait || !go) return;
    /* the check starts on its own when the page opens */
    box.classList.add('is-waiting');
    var left = 5; count.textContent = left;
    var t = setInterval(function () {
      left -= 1; count.textContent = Math.max(left, 0);
      if (left <= 0) { clearInterval(t); wait.hidden = true; if (ok) ok.hidden = false; go.hidden = false; if (window.gtag) gtag('event', 'join_ready', { listing: ID }); }
    }, 1000);
    go.addEventListener('click', function () { if (window.gtag) gtag('event', 'join_open', { listing: ID }); });
  });

  /* ---------- copy, share, QR ---------- */
  var gTitle = ($('.gp h1') || {}).textContent || '', joinBox = $('[data-join]'), link = joinBox ? joinBox.getAttribute('data-link') : '';
  var kind = /\/channel\//.test(link) ? 'channel' : 'group';
  $$('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.getAttribute('data-copy');
      (navigator.clipboard ? navigator.clipboard.writeText(t) : Promise.reject()).then(function () { toast('Link copied'); }, function () { prompt('Copy this link:', t); });
    });
  });
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function () {
      var u = location.href.split('#')[0];
      if (navigator.share) navigator.share({ title: gTitle, text: gTitle + ' — WhatsApp ' + kind + ' on Share', url: u }).catch(function () {});
      else open('https://wa.me/?text=' + encodeURIComponent(gTitle + ' — ' + u), '_blank', 'noopener');
    });
  });
  var dlg = null;
  function dialog(html) {
    if (!dlg) { dlg = doc.createElement('dialog'); dlg.className = 'dlg'; body.appendChild(dlg); dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); }); }
    dlg.innerHTML = html; dlg.showModal ? dlg.showModal() : dlg.setAttribute('open', ''); return dlg;
  }
  $$('[data-qr]').forEach(function (b) {
    b.addEventListener('click', function () {
      var u = b.getAttribute('data-qr');
      var d = dialog('<form method="dialog"><h2>Scan to open</h2><p>Point a phone camera at this code to open the page.</p><div class="qr-box" data-qrbox><p class="muted">Making the code…</p></div><div class="row"><button class="btn">Close</button></div></form>');
      function draw() { var q = window.qrcode(0, 'M'); q.addData(u); q.make(); $('[data-qrbox]', d).innerHTML = q.createImgTag(6, 0) + '<small class="muted">' + esc(u) + '</small>'; }
      if (window.qrcode) draw();
      else { var s = loadScript('https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js'); s.onload = draw; s.onerror = function () { $('[data-qrbox]', d).innerHTML = '<p class="muted">Could not load the QR maker. Check your connection.</p>'; }; }
    });
  });

  /* ---------- report / describe / owner ---------- */
  var FORMS = {
    report: { h: 'Report this ' + kind, p: 'Tell us what’s wrong. Every report is reviewed, and a listing reported by several people is hidden until we check it.',
      html: '<div class="opts">' + [['spam', 'Spam or unrelated promotion'], ['adult', 'Adult or sexual content'], ['scam', 'Scam, fraud or asks for money'], ['hate', 'Hate, abuse or violence'], ['dead', 'Link not working']]
        .map(function (o, i) { return '<label><input type="radio" name="reason" value="' + o[0] + '"' + (i ? '' : ' required') + '> ' + o[1] + '</label>'; }).join('') + '</div>',
      send: 'Send report', data: function (f) { return { reason: (f.querySelector('input[name=reason]:checked') || {}).value }; } },
    describe: { h: 'Describe this ' + kind, p: 'In one or two sentences, what is this ' + kind + ' about? It appears after a quick review.',
      html: '<label>Description<textarea name="text" rows="3" minlength="10" maxlength="300" required placeholder="e.g. Daily job alerts for freshers in Punjab"></textarea></label><label>Your name (optional)<input name="by" maxlength="60"></label>',
      send: 'Send description', data: function (f) { return { text: f.text.value.trim(), by: f.by.value.trim() }; } },
    owner: { h: 'Is this your ' + kind + '?', p: 'Ask us to update the description or category, re-check a report, or remove the listing. We reply at the contact you give.',
      html: '<label>Your email or WhatsApp number<input name="contact" maxlength="120" required></label><label>What should we do?<textarea name="note" rows="3" maxlength="500" required></textarea></label>',
      send: 'Send request', data: function (f) { return { contact: f.contact.value.trim(), note: f.note.value.trim() }; } }
  };
  function openForm(key) {
    var F = FORMS[key]; if (!F) return;
    if (!C.api) { toast('This form opens very soon. Meanwhile write to help.groupchaton.com.'); return; }
    var d = dialog('<form method="dialog"><h2>' + F.h + '</h2><p>' + F.p + '</p>' + F.html + '<p class="msg" role="status"></p><div class="row"><button class="btn" type="button" data-close>Cancel</button><button class="btn btn-wa" type="submit">' + F.send + '</button></div></form>');
    var f = $('form', d), msg = $('.msg', f), btn = $('[type=submit]', f);
    $('[data-close]', f).onclick = function () { d.close(); };
    f.onsubmit = function (e) {
      e.preventDefault();
      var x = F.data(f); x.action = key; x.id = ID; x.link = link; x.name = gTitle; x.visitor = visitor;
      btn.disabled = true; msg.className = 'msg'; msg.textContent = 'Sending…';
      post(C.api, x).then(function (r) {
        msg.className = 'msg ' + (r && r.ok ? 'ok' : 'err'); msg.textContent = (r && r.message) || (r && r.ok ? 'Thanks! Sent.' : 'Could not send. Please try again.');
        if (r && r.ok) { setTimeout(function () { d.close(); }, 2200); if (key === 'report') { if (r.removed) listingRemoved(); else if (r.adsOff) showReported(); } }
        else btn.disabled = false;
      }).catch(function () { msg.className = 'msg err'; msg.textContent = 'Could not send. Check your connection and try again.'; btn.disabled = false; });
    };
  }
  $$('[data-open]').forEach(function (b) { b.addEventListener('click', function () { openForm(b.getAttribute('data-open')); }); });

  /* help categorise: one tap; 3 matching votes apply it */
  $$('[data-categorise]').forEach(function (box) {
    var msg = box.parentNode.querySelector('.msg'), key = 'share-cat-' + ID;
    if (store(key)) { msg.className = 'msg ok'; msg.textContent = 'Thanks, your choice is saved.'; }
    $$('.chip', box).forEach(function (c) {
      c.addEventListener('click', function () {
        if (!C.api) { msg.className = 'msg'; msg.textContent = 'Voting opens very soon.'; return; }
        $$('.chip', box).forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); c.setAttribute('aria-pressed', 'true');
        msg.className = 'msg'; msg.textContent = 'Sending…';
        post(C.api, { action: 'categorise', id: ID, cat: c.getAttribute('data-cat'), link: link, name: gTitle, visitor: visitor }).then(function (r) {
          msg.className = 'msg ' + (r && r.ok ? 'ok' : 'err'); msg.textContent = (r && r.message) || 'Thanks!'; if (r && r.ok) store(key, '1');
        }).catch(function () { msg.className = 'msg err'; msg.textContent = 'Could not send. Please try again.'; });
      });
    });
  });

  /* ---------- renamed listings: the 404 page finds the new address ---------- */
  if ($('[data-404]')) {
    var m = location.pathname.match(/^\/g\/[^/]*-([a-z0-9]{6})x*\/?$/);
    if (m) getIndex().then(function (list) { var hit = list.filter(function (x) { return x[0].replace(/x+$/, '').slice(-6) === m[1]; })[0]; if (hit) location.replace('/g/' + hit[0] + '/'); });
  }

  /* ---------- add your group (ShareYourGroup's form backend) ---------- */
  function bindSubmit(f) {
    var msg = $('.msg', f), btn = $('[type=submit]', f);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = f.group_link.value.trim().split('?')[0].replace(/\/$/, '');
      if (!/^https:\/\/(chat\.whatsapp\.com\/(invite\/)?|(www\.)?whatsapp\.com\/channel\/)[A-Za-z0-9]{15,40}$/.test(v)) {
        msg.className = 'msg err'; msg.textContent = 'Please paste a WhatsApp group link (chat.whatsapp.com/…) or channel link (whatsapp.com/channel/…).'; return;
      }
      btn.disabled = true; msg.className = 'msg'; msg.textContent = 'Checking your link with WhatsApp…';
      post(C.submit, { group_link: v, category: f.category.value, description: f.description.value.trim() }).then(function (r) {
        msg.className = 'msg ' + (r && r.ok ? 'ok' : 'err'); msg.textContent = (r && r.message) || 'Thanks!';
        if (r && r.ok && r.status !== 'rejected') { f.reset(); msg.textContent += ' Its page on Share appears within about 15 minutes.'; }
        btn.disabled = false;
      }).catch(function () { msg.className = 'msg err'; msg.textContent = 'Could not send. Check your connection and try again.'; btn.disabled = false; });
    });
  }
  $$('[data-submit]').forEach(bindSubmit);

  /* the hero "Add your group" button and the corner Submit button open the form in a popup (other links still go to /submit/) */
  $$('[data-add-popup]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button) return;
      e.preventDefault();
      var opts = Object.keys(CATS).filter(function (k) { return k !== 'unknown'; }).map(function (k) { return '<option value="' + esc(k) + '">' + esc(CATS[k][0]) + '</option>'; }).join('');
      var d = dialog('<form class="form add-pop" data-submit><h2>Add your group or channel</h2><p>Free. Paste the invite link and we create its own page. Only share groups you run or have the admin’s permission to share.</p>' +
        '<label>WhatsApp group or channel link<input name="group_link" type="url" required placeholder="https://chat.whatsapp.com/..."></label>' +
        '<label>Category<select name="category"><option value="">Choose a category (optional)</option>' + opts + '</select></label>' +
        '<label>Short description (optional)<textarea name="description" maxlength="200" rows="3"></textarea></label>' +
        '<p class="msg" role="status"></p><div class="row"><a class="btn" href="/submit/">Full guide</a><button class="btn" type="button" data-close>Cancel</button><button class="btn btn-wa" type="submit">Add my group</button></div></form>');
      var f = $('form', d); bindSubmit(f);
      $('[data-close]', f).addEventListener('click', function () { d.close(); });
      setTimeout(function () { f.group_link.focus(); }, 30);
    });
  });

  /* ---------- "Add as a preferred source on Google": Google's official button in the footer (plain link if it can't load) ---------- */
  var pref = $('[google-add-preferred-source-btn]');
  if (pref) {
    pref.setAttribute('data-theme', root.getAttribute('data-theme') === 'light' ? 'light' : 'dark');
    loadScript('https://news.google.com/swg/js/v1/publisher.js');
    setTimeout(function () {
      if (pref.childNodes.length) return;
      var g = $('.gsrc'), a = doc.createElement('a');
      a.className = 'pref-fallback'; a.href = g ? g.href : 'https://www.google.com/preferences/source?q=share.groupchaton.com'; a.target = '_blank'; a.rel = 'noopener';
      a.innerHTML = (g ? g.innerHTML : '') + 'Add Share as a preferred source on Google'; pref.appendChild(a);
    }, 6000);
  }

  /* ---------- install as an app ---------- */
  var deferred = null;
  addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); deferred = e; $$('[data-install]').forEach(function (b) { b.hidden = false; }); });
  $$('[data-install]').forEach(function (b) { b.addEventListener('click', function () { if (!deferred) return; deferred.prompt(); deferred.userChoice.then(function () { deferred = null; b.hidden = true; }); }); });
  // the "Install as an app" card: the browser's install prompt where it exists, otherwise simple steps
  $$('[data-install-card]').forEach(function (c) {
    c.addEventListener('click', function (e) {
      e.preventDefault();
      if (deferred) { deferred.prompt(); deferred.userChoice.then(function () { deferred = null; }); return; }
      if (matchMedia('(display-mode: standalone)').matches) { toast('You are already using the app'); return; }
      dialog('<form method="dialog"><h2>Install Share as an app</h2><ul class="list"><li><b>Android (Chrome):</b> tap ⋮ › <b>Add to Home screen</b> › Install.</li>' +
        '<li><b>iPhone (Safari):</b> tap Share <b>⎙</b> › <b>Add to Home Screen</b>.</li><li><b>Computer (Chrome or Edge):</b> click the install icon at the right of the address bar.</li></ul>' +
        '<div class="row"><button class="btn">OK</button></div></form>');
    });
  });
  if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('/sw.js').catch(function () {});
})();
