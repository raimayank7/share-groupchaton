"""share.groupchaton.com — builds the whole static site from the live WhatsApp group list.

   Every group or channel gets its own page (/g/<name>-<id>/) with real, useful content: facts we know (type,
   category, language, date), what happens when you join or follow, safety tips for its category, a 5-second join
   box, related listings and an FAQ. Community features (reports, suggested descriptions and categories) come from
   the share Apps Script (apps-script/Share.gs).

   Run:  python -X utf8 scripts/build.py            (reads the live lists, writes ./site)
         python -X utf8 scripts/build.py --offline  (uses data/cache/*.json from the last run)
   Photos: downloaded once into media/ as small WebP files (needs Pillow; skipped when it isn't installed).
   Designed & Developed by Nivesh Sahayak (https://www.niveshsahayak.in/)."""
import os, re, sys, json, html, shutil, hashlib, datetime, unicodedata, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(HERE, 'config.json'), encoding='utf-8'))
SITE = CFG['site']                       # https://share.groupchaton.com
# GitHub builds into ./site; on a PC the site goes outside OneDrive (thousands of pages would sync and lock on every build)
OUT = os.environ.get('SHARE_OUT') or (os.path.join(os.environ['LOCALAPPDATA'], 'share-groupchaton-site') if os.name == 'nt' else os.path.join(HERE, 'site'))
CACHE = os.path.join(HERE, 'data', 'cache')
MEDIA = os.path.join(HERE, 'media')
OFFLINE = '--offline' in sys.argv
E = lambda s: html.escape(str(s or ''), quote=True)
PER_PAGE = 48

# ------------------------------------------------------------------ data
def fetch_json(url, name):
    path = os.path.join(CACHE, name)
    if not OFFLINE and url:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'share.groupchaton.com builder'})
            data = json.load(urllib.request.urlopen(req, timeout=60))
            os.makedirs(CACHE, exist_ok=True)
            json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False)
            return data
        except Exception as e:
            print('  could not read %s (%s); using the last copy' % (name, e))
    return json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}

src = fetch_json(CFG['groups_url'], 'groups.json')
community = fetch_json(CFG.get('share_api') and CFG['share_api'] + '?action=export', 'community.json') or {}
community = community.get('groups', {}) if isinstance(community, dict) else {}
UPDATED = (src.get('updated') or datetime.datetime.utcnow().isoformat())[:10]
NOW_MS = datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000

CATS = {   # id: (name, icon, colour, intro, safety tips)
  'education': ('Education & Study', '📚', '#2563EB', 'Study groups and channels for school, college and competitive exams: notes, doubts, test series and class updates shared by students and teachers.',
                ['Never share your Aadhaar, marksheets or ID cards in a group; admins never need them.', 'Paid “leaked papers” or guaranteed-rank offers are scams.', 'Download notes only as PDF or images, never as APK apps.']),
  'jobs': ('Jobs & Careers', '💼', '#0EA5E9', 'Job alerts, vacancies, internships and career tips: from government exams to private and work-from-home openings.',
                ['Real employers never ask for a “registration fee” or deposit. If someone asks for money, it is a scam.', 'Check a job on the company’s own website before sharing documents.', 'Be careful with “earn daily from home” tasks that ask you to pay first.']),
  'stocks': ('Stocks & Trading', '📈', '#16A34A', 'Share market, trading and investing groups: market news, analysis and learning, from beginners to active traders.',
                ['Nobody can guarantee profits. “Sure-shot” tips and guaranteed returns are a common scam.', 'Never give your trading login, OTP or UPI PIN to anyone.', 'Check whether an adviser is SEBI-registered before paying for tips.']),
  'earning': ('Online Earning', '💰', '#CA8A04', 'Ideas and opportunities for earning online: freelancing, affiliate work, small tasks and side income.',
                ['If you must pay to start earning, it is almost always a scam.', 'Avoid “double your money” and task-based apps that ask for deposits.', 'Never share bank details, OTPs or card numbers in a group.']),
  'business': ('Business', '🏢', '#7C3AED', 'Groups for business owners, sellers and professionals: networking, promotions, wholesale deals and business advice.',
                ['Meet or verify sellers before paying large amounts.', 'Ask for a GST bill or invoice for business purchases.', 'Be wary of offers that look too cheap to be true.']),
  'shopping': ('Shopping & Deals', '🛍️', '#DB2777', 'Deals, discounts, loot offers and resellers: product links and price drops shared by members.',
                ['Buy through trusted stores or cash-on-delivery when you can.', 'Do not pay advance amounts to unknown sellers.', 'Shortened links can hide fake shops; check the website before paying.']),
  'tech': ('Technology', '💻', '#0891B2', 'Technology, phones, apps, AI tools and coding: news, tips and help from people who love tech.',
                ['Install apps only from the Play Store or App Store, never as APK files from a group.', 'Cheap “premium subscriptions” are often shared or stolen accounts.', 'Never share passwords or verification codes.']),
  'gaming': ('Gaming', '🎮', '#9333EA', 'Gaming communities: Free Fire, BGMI, Minecraft and more. Find squads, tournaments, tips and game news.',
                ['Never share your game account login or buy accounts from strangers.', '“Free diamonds” or UC generators are scams that steal accounts.', 'Tournament entry fees should go only to known organisers.']),
  'entertainment': ('Entertainment', '🎬', '#EA580C', 'Movies, web series, celebrities and pop culture: updates, discussions and recommendations.',
                ['Pirated movie links often carry malware or scam ads.', 'Do not install apps shared as APK files.', 'Report groups that share adult content.']),
  'music': ('Music', '🎵', '#E11D48', 'Music lovers, singers and musicians: songs, playlists, lyrics and learning instruments.',
                ['Share only music you have the right to share.', 'Be careful with links that ask you to log in to download songs.', 'Report spam and adult content to the admins.']),
  'fun': ('Fun & Memes', '😂', '#F59E0B', 'Jokes, memes, shayari and fun forwards for a good laugh.',
                ['Do not forward fake news or edited videos as real.', 'Leave groups that turn abusive; you can report them here.', 'Keep your profile photo private if strangers are in the group.']),
  'friendship': ('Friendship & Chat', '🤝', '#14B8A6', 'Groups for making friends and chatting with people who share your interests.',
                ['Keep personal details (address, school, workplace) private.', 'Never send money or photos to people you have only met online.', 'Paid “friendship clubs” are scams; report them.']),
  'love': ('Love & Relationships', '❤️', '#EF4444', 'Love quotes, relationship advice and romantic poetry.',
                ['Do not share private photos with anyone you met online.', 'Romance scams often end with a request for money; never send it.', 'Report anyone who threatens or blackmails you.']),
  'quotes': ('Quotes & Shayari', '✍️', '#8B5CF6', 'Daily quotes, shayari, status ideas and motivational lines in many languages.',
                ['Check before forwarding “facts” and health tips.', 'Avoid links that promise “status videos” as APK apps.', 'Report groups that spam ads or adult content.']),
  'news': ('News & Updates', '📰', '#475569', 'News channels and groups: local, national and world updates as they happen.',
                ['Check big news with a trusted news website before forwarding.', 'Edited videos and fake screenshots spread fast; think before you share.', 'Do not click “breaking news” links that ask you to log in.']),
  'sports': ('Sports', '⚽', '#22C55E', 'Cricket, football and every other sport: scores, match talk, fantasy teams and highlights.',
                ['Betting and “fixed match” tips are illegal in many places and often scams.', 'Do not pay for guaranteed fantasy-team wins.', 'Stream matches only from official apps.']),
  'religion': ('Religion & Spirituality', '🕉️', '#D97706', 'Devotional, spiritual and religious groups: prayers, teachings, festivals and community news.',
                ['Respect every faith; report hate and provocation.', 'Donate only through official trusts and receipts.', 'Do not forward unverified miracle or health claims.']),
  'travel': ('Travel', '✈️', '#06B6D4', 'Travel groups: trips, tour plans, travel buddies, tickets and destination tips.',
                ['Book tours and tickets through known agencies or official sites.', 'Never pay strangers in advance for “cheap tickets”.', 'Share live location only with people you trust.']),
  'health': ('Health & Fitness', '💪', '#10B981', 'Health, fitness, yoga and diet groups: workouts, healthy recipes and motivation.',
                ['Group advice is not medical advice; ask a doctor before changing medicines.', 'Avoid “miracle cure” products sold in groups.', 'Do not share your medical reports publicly.']),
  'food': ('Food & Recipes', '🍲', '#F97316', 'Recipes, home cooks, food business and restaurant recommendations.',
                ['Order from home kitchens with reviews or known contacts.', 'Pay on delivery when buying from new sellers.', 'Report groups that spam unrelated links.']),
  'others': ('Other Topics', '🧩', '#64748B', 'Groups and channels on many other topics that do not fit a single category.',
                ['Read the group description and rules before joining.', 'Never share OTPs, passwords or bank details.', 'Report spam, scams or adult content using the report button.']),
  'unknown': ('Waiting for a Category', '❔', '#94A3B8', 'Groups and channels whose topic we do not know yet. If you know one of them, open it and help categorise it with one tap.',
                ['We do not know this group’s topic yet, so read its messages before taking part.', 'Never share OTPs, passwords or bank details.', 'Report spam, scams or adult content using the report button.']),
}
CAT_ORDER = [c for c in CATS if c not in ('others', 'unknown')] + ['others', 'unknown']

BLOCKED = ['porn', 'porno', 'xxx', 'sex', 'sexy', 'nude', 'nudes', 'erotic', 'adult', '18+', 'milf', 'blowjob', 'escort', 'escorts', 'call girl', 'call girls',
  'hot girl', 'hot girls', 'hot video', 'hot videos', 'bdsm', 'bokep', 'onlyfans', 'nangi', 'desi bhabhi', 'sex chat', 'video call girl',
  'chatting girl', 'chatting girls', 'chat girl', 'chat girls', 'girls chat', 'girl chat', 'hot chat', 'sexy chat', 'dirty chat',
  'video call', 'bhabhi', 'aunty', 'aunties', 'desi girl', 'desi girls', 'paid friendship', 'friendship club', 'night chat', 'lonely girl', 'single girls',
  'madarchod', 'behenchod', 'bhenchod', 'chutiya', 'randi', 'chut', 'gaand', 'gandu', 'bhosdike', 'bhosadike', 'lund', 'fucker', 'slut', 'whore',
  'nigger', 'faggot', 'kike', 'chink', 'raghead', 'pajeet', 'cocaine', 'heroin', 'meth', 'mdma', 'lsd', 'ganja', 'charas', 'brown sugar', 'chitta',
  'money doubling', 'double your money', 'guaranteed profit', '100% profit', 'free recharge', 'win iphone', 'lottery', 'jackpot',
  'otp', 'virtual number', 'virtual numbers', 'usa numbers', 'fake id', 'hacked', 'carding', 'bitcoin scam', 'crypto scam',
  'isis', 'daesh', 'al-qaeda', 'al qaeda', 'taliban', 'lashkar', 'jaish',
  # extra for share.groupchaton.com: betting and gambling ads are not allowed next to AdSense
  'betting', 'satta', 'matka', 'casino', 'gangster',
  # dating / escort-style wording
  'dating', 'hookup', 'hook up', 'real meet', 'meet available', 'meetup available']
BLOCKED_RE = re.compile(r'(?:^|[^\w])(?:' + '|'.join(re.escape(w) for w in BLOCKED) + r')(?=$|[^\w])', re.I)

def blocked(text):
    return bool(BLOCKED_RE.search(unicodedata.normalize('NFKC', text or '')))

SCRIPTS = [  # (first, last, language label)
  (0x0900, 0x097F, 'Hindi (Devanagari script)'), (0x0A00, 0x0A7F, 'Punjabi (Gurmukhi script)'), (0x0980, 0x09FF, 'Bengali'),
  (0x0A80, 0x0AFF, 'Gujarati'), (0x0B80, 0x0BFF, 'Tamil'), (0x0C00, 0x0C7F, 'Telugu'), (0x0C80, 0x0CFF, 'Kannada'), (0x0D00, 0x0D7F, 'Malayalam'),
  (0x0B00, 0x0B7F, 'Odia'), (0x0600, 0x06FF, 'Arabic script'), (0x0400, 0x04FF, 'Cyrillic script (Russian and others)'),
  (0x0E00, 0x0E7F, 'Thai'), (0x3040, 0x30FF, 'Japanese'), (0xAC00, 0xD7AF, 'Korean'), (0x4E00, 0x9FFF, 'Chinese characters'), (0x0590, 0x05FF, 'Hebrew')]
def language(name):
    counts = {}
    for ch in name:
        o = ord(ch)
        for a, b, label in SCRIPTS:
            if a <= o <= b: counts[label] = counts.get(label, 0) + 1
    if counts:
        lab = max(counts, key=counts.get)
        if lab == 'Arabic script' and re.search('[ٹڈڑںےۓکگ]', name): lab = 'Urdu (Arabic script)'
        return lab
    if re.search('[ğşıİ]', name): return 'Turkish'
    if re.search('[ãõç]', name, re.I) and re.search(r'\b(de|do|da|para|com)\b', name, re.I): return 'Portuguese'
    if re.search('[ñ¿¡]', name): return 'Spanish'
    if re.search('[A-Za-z]', name): return 'English letters'
    return ''

def slugify(name, gid):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60].strip('-')
    return (s or 'whatsapp') + '-' + re.sub('[^a-z0-9]', '', gid.lower())[-6:]

def when(ms):
    try:
        if float(ms) < 1.3e12: raise ValueError('no real date')   # a few old rows have 1899/1970 dates
        d = datetime.datetime.fromtimestamp(float(ms) / 1000, datetime.timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError): d = datetime.datetime.fromisoformat(UPDATED)
    return d.strftime('%d %b %Y').lstrip('0'), d.strftime('%Y-%m-%d')

# ------------------------------------------------------------------ build the listing records
groups, seen_slugs = [], set()
for g in src.get('groups', []):
    gid, name = g.get('id'), (g.get('n') or '').strip()
    if not gid or not name: continue
    extra = community.get(gid, {})
    if extra.get('removed'): continue                                   # 3 reports or removed by the owner
    ch = bool(g.get('ch')) or '/channel/' in g.get('l', '')
    cat = extra.get('cat') or (g.get('c') if g.get('c') in CATS else '') or 'unknown'
    desc = (extra.get('desc') or g.get('d') or '').strip()
    slug = slugify(name, gid)
    while slug in seen_slugs: slug += 'x'
    seen_slugs.add(slug)
    shown, iso = when(g.get('t') or 0)
    flagged = blocked(name + ' ' + desc)
    groups.append({'id': gid, 'name': name, 'link': g['l'], 'ch': ch, 'cat': cat, 'desc': desc, 'slug': slug, 'img': g.get('i', ''),
                   'date': shown, 'iso': iso, 't': g.get('t') or 0, 'lang': language(name), 'flagged': flagged,
                   'adsoff': flagged or bool(extra.get('adsOff')), 'reported': bool(extra.get('adsOff')) and not flagged})
groups.sort(key=lambda x: -x['t'])
by_cat = {c: [g for g in groups if g['cat'] == c] for c in CATS}

# ------------------------------------------------------------------ photos (small WebP copies; WhatsApp's photo links expire)
def photo(g):
    if not g['img']: return ''
    name = hashlib.sha1(g['id'].encode()).hexdigest()[:16] + '.webp'
    path = os.path.join(MEDIA, name)
    if not os.path.exists(path) and '--photos' in sys.argv:
        try:
            from PIL import Image
            import io
            raw = urllib.request.urlopen(urllib.request.Request(g['img'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=20).read()
            im = Image.open(io.BytesIO(raw)).convert('RGB'); im.thumbnail((256, 256))
            os.makedirs(MEDIA, exist_ok=True); im.save(path, 'WEBP', quality=72)
        except Exception:
            return ''
    return '/media/' + name if os.path.exists(path) else ''
for g in groups: g['photo'] = photo(g)

# ------------------------------------------------------------------ page shell
def kind(g, cap=False):
    w = 'channel' if g['ch'] else 'group'
    return w.capitalize() if cap else w

ICONS = {
  'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>', 'moon': '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>', 'plus': '<path d="M12 5v14M5 12h14"/>', 'flag': '<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>',
  'edit': '<path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>', 'users': '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0M16 3.5a4 4 0 0 1 0 7.5M22 21a7 7 0 0 0-5-6.7"/>',
  'radio': '<circle cx="12" cy="12" r="2"/><path d="M16.2 7.8a6 6 0 0 1 0 8.4M7.8 16.2a6 6 0 0 1 0-8.4M19.1 4.9a10 10 0 0 1 0 14.2M4.9 19.1a10 10 0 0 1 0-14.2"/>',
  'shield': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>', 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  'tag': '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
  'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  'check': '<path d="M20 6 9 17l-5-5"/>', 'help': '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
  'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>',
  'star': '<path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
  'copy': '<rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  'share': '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/>',
  'qr': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3h-3zM20 14v1M14 20h1M18 18h3v3h-3z"/>',
  'up': '<path d="M12 19V5M5 12l7-7 7 7"/>',
  'bolt': '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
}
def ic(k): return '<svg class="i" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[k] + '</svg>'
WA = ('<svg class="i wa" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" stroke="none" d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.27-.2-.57-.35m-5.42 7.4h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88m8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89a11.82 11.82 0 0 0-3.48-8.41z"/></svg>')

VER = hashlib.sha1((open(os.path.join(HERE, 'static', 'assets', 'share.css'), 'rb').read() + open(os.path.join(HERE, 'static', 'assets', 'share.js'), 'rb').read())).hexdigest()[:8]

def page(path, title, desc, body, *, noindex=False, ads=True, schema=None, og_image=None, gid=None, active='', crumbs_ld=None, kind_='WebPage'):
    canon = SITE + path
    img = og_image or SITE + '/brand/share-banner.png'
    if schema is None:   # every page gets WebPage + site + publisher (+ breadcrumbs)
        graph = [{'@type': kind_, '@id': canon + '#page', 'url': canon, 'name': title, 'description': desc, 'inLanguage': 'en',
                  'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#org'}, 'dateModified': UPDATED}, WEBSITE_LD, ORG_LD]
        if crumbs_ld: graph.append(crumbs_ld)
        schema = {'@context': 'https://schema.org', '@graph': graph}
    nav = ''.join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if active == k else '', t) for k, h, t in
                  (('home', '/', 'Home'), ('cats', '/categories/', 'Categories'), ('new', '/latest/', 'Latest'), ('saved', '/saved/', '★ Saved'), ('submit', '/submit/', 'Add your group'),
                   ('privacy-policy', '/privacy-policy/', 'Privacy Policy'), ('disclaimer', '/disclaimer/', 'Disclaimer'), ('terms-of-use', '/terms-of-use/', 'Terms of Use')))
    ld = ''
    if schema: ld = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('</', '<\\/') + '</script>'
    return f'''<!doctype html>
<html lang="en" data-theme="dark"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon)}">
{'<meta name="robots" content="noindex,follow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta property="og:type" content="website"><meta property="og:site_name" content="Share by GroupChatOn">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{E(canon)}">
<meta property="og:image" content="{E(img)}"><meta property="og:image:alt" content="{E(title)}"><meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{E(title)}"><meta name="twitter:description" content="{E(desc)}"><meta name="twitter:image" content="{E(img)}">
<meta name="author" content="Share by GroupChatOn"><meta name="application-name" content="Share"><meta name="apple-mobile-web-app-title" content="Share"><meta name="format-detection" content="telephone=no">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Unbounded:wght@500;600;700&display=swap">
<meta name="theme-color" content="#0B1210" media="(prefers-color-scheme: dark)"><meta name="theme-color" content="#F4FAF6" media="(prefers-color-scheme: light)">
<link rel="icon" href="/brand/favicon-32.png" sizes="32x32"><link rel="icon" href="/brand/favicon-192.png" sizes="192x192"><link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<script>try{{var t=localStorage.getItem('share-theme');if(t)document.documentElement.setAttribute('data-theme',t);else if(matchMedia('(prefers-color-scheme: light)').matches)document.documentElement.setAttribute('data-theme','light')}}catch(e){{}}</script>
<style>html{{background:#0B1210}}html[data-theme=light]{{background:#F4FAF6}}body{{margin:0}}</style>
<link rel="stylesheet" href="/assets/share.css?v={VER}">
{ld}
</head><body data-ads="{'1' if ads else '0'}"{(' data-id="%s"' % E(gid)) if gid else ''}>
<a class="skip" href="#main">Skip to content</a><div class="progress" aria-hidden="true"><i></i></div><div class="fx" aria-hidden="true"></div>
<header class="hd"><div class="wrap hd-in">
<a class="brand" href="/" aria-label="Share by GroupChatOn home"><img class="logo is-light" src="/brand/share-logo-light.png" alt="" width="520" height="100"><img class="logo is-dark" src="/brand/share-logo-dark.png" alt="" width="520" height="100"></a>
<nav class="nav" id="nav" aria-label="Main">{nav}</nav>
<div class="hd-act"><a class="ib kbd-hint" href="/search/" data-palette aria-label="Search (press /)">{ic('search')}<kbd>/</kbd></a><a class="ib gsrc" href="https://www.google.com/preferences/source?q=share.groupchaton.com" target="_blank" rel="noopener" title="Add Share as a preferred source on Google" aria-label="Add Share as a preferred source on Google"><svg class="g" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg></a><button class="ib" type="button" data-theme-toggle aria-label="Light or dark">{ic('moon')}</button><button class="ib menu-btn" type="button" aria-controls="nav" aria-expanded="false" aria-label="Menu">{ic('menu')}</button></div>
</div></header>
<main id="main" class="wrap">
{body}
</main>
<footer class="ft"><div class="wrap pref-band"><p class="mono">See Share first in Google results</p><div google-add-preferred-source-btn data-theme="dark"></div></div><div class="wrap ft-in">
<div><b>Share by GroupChatOn</b><p>Find and share WhatsApp groups and channels. Every listing has its own page, safety tips and a report button.</p></div>
<div><b>Explore</b><a href="/categories/">Categories</a><a href="/latest/">Latest listings</a><a href="/channels/">WhatsApp channels</a><a href="/submit/">Add your group</a></div>
<div><b>GroupChatOn</b><a href="https://www.groupchaton.com/">Novels</a><a href="https://infinity.groupchaton.com/">Free tools</a><a href="https://help.groupchaton.com/">Help</a><a href="https://app.groupchaton.com/">App</a></div>
<div><b>About</b><a href="/about/">About</a><a href="/privacy-policy/">Privacy policy</a><a href="/disclaimer/">Disclaimer</a><a href="/terms-of-use/">Terms of use</a><a href="/contact/">Contact</a></div>
</div><div class="wrap ft-bottom"><p>&#169; {datetime.date.today().year} <b>Share by GroupChatOn</b>. All rights reserved.</p><p>Not affiliated with WhatsApp or Meta. Listings are shared by users. Built by <a href="https://www.niveshsahayak.in/">Nivesh Sahayak</a>.</p></div></footer>
<div class="fab"><div class="rv" data-rv hidden><div class="rv-hd"><b>{ic('clock')} Recently viewed</b><button type="button" class="rv-x" data-rv-clear>Clear</button></div><div class="rv-list" data-rv-list></div></div>
<button class="fab-b" type="button" data-rv-toggle aria-label="Recently viewed" aria-expanded="false" hidden>{ic('clock')}<i data-rv-n></i></button>
<a class="fab-b fab-add" href="/submit/">{ic('plus')}<span>Submit</span></a>
<button class="fab-b totop" type="button" aria-label="Back to top" hidden>{ic('up')}</button></div><div class="toasts" role="status" aria-live="polite"></div>
<script>window.SHARE={json.dumps({'api': CFG.get('share_api', ''), 'submit': CFG['submit_api'], 'ads': CFG.get('adsense', ''), 'analytics': CFG.get('analytics', ''), 'cats': {c: list(CATS[c][:3]) for c in CATS}})}</script>
<script src="/assets/share.js?v={VER}" defer></script>
</body></html>
'''

WEBSITE_LD = {'@type': 'WebSite', '@id': SITE + '/#website', 'url': SITE + '/', 'name': 'Share by GroupChatOn', 'alternateName': 'Share', 'inLanguage': 'en',
              'publisher': {'@id': SITE + '/#org'},
              'potentialAction': {'@type': 'SearchAction', 'target': {'@type': 'EntryPoint', 'urlTemplate': SITE + '/search/?q={search_term_string}'}, 'query-input': 'required name=search_term_string'}}
ORG_LD = {'@type': 'Organization', '@id': SITE + '/#org', 'name': 'GroupChatOn', 'url': 'https://www.groupchaton.com/',
          'logo': {'@type': 'ImageObject', 'url': SITE + '/brand/favicon-512.png', 'width': 512, 'height': 512},
          'sameAs': ['https://www.groupchaton.com/', 'https://infinity.groupchaton.com/', 'https://help.groupchaton.com/', 'https://www.shareyourgroup.com/']}

def card(g):
    cname, cicon, ccol = CATS[g['cat']][:3]
    pic = ('<img src="%s" alt="" loading="lazy" width="56" height="56">' % E(g['photo'])) if g['photo'] else '<span>%s</span>' % E((g['name'][:1] or '?').upper())
    d = g['desc'] or ('No description yet. Know this %s? Help describe it.' % kind(g))
    new = '<em class="new">NEW</em>' if g['t'] and (NOW_MS - g['t']) < 3 * 86400e3 else ''
    return (f'<div class="card" style="--c:{ccol}"><span class="av">{pic}</span><span class="ct">'
            f'<span class="tags"><em class="ty ty-{kind(g)}">{kind(g, True)}</em><em>{cicon} {E(cname)}</em>{new}</span>'
            f'<a class="cl" href="/g/{g["slug"]}/">{E(g["name"])}</a><small>{E(d)}</small></span>'
            f'<button class="star" type="button" data-save="{g["slug"]}" aria-label="Save {E(g["name"])}" aria-pressed="false">{ic("star")}</button></div>')

def grid(items): return '<div class="grid">' + ''.join(card(g) for g in items) + '</div>'

def crumbs(*parts):
    items = [('Home', SITE + '/')] + list(parts)
    html_ = '<nav class="crumbs" aria-label="Breadcrumb">' + ' › '.join('<a href="%s">%s</a>' % (E(u), E(n)) for n, u in items) + '</nav>'
    ld = {'@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)]}
    return html_, ld

def write(path, content):
    full = os.path.join(OUT, path.strip('/'), 'index.html') if not path.endswith('.html') else os.path.join(OUT, path.strip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8', newline='\n').write(content)

def pager(base, n, total):
    if total <= 1: return ''
    link = lambda k: base if k == 1 else '%spage/%d/' % (base, k)
    parts = []
    if n > 1: parts.append('<a class="btn" href="%s">← Newer</a>' % link(n - 1))
    parts.append('<span>Page %d of %d</span>' % (n, total))
    if n < total: parts.append('<a class="btn" href="%s">Older →</a>' % link(n + 1))
    return '<div class="pager">' + ''.join(parts) + '</div>'

# ------------------------------------------------------------------ group pages
def related(g):
    pool = [x for x in by_cat[g['cat']] if x['id'] != g['id'] and not x['flagged']] if g['cat'] != 'unknown' else []
    if len(pool) < 6 and g['lang']: pool += [x for x in groups if x['lang'] == g['lang'] and x['id'] != g['id'] and not x['flagged'] and x not in pool]
    newest = [x for x in groups if x['id'] != g['id'] and not x['flagged'] and x not in pool[:6]][:3]
    return pool[:6], newest

def group_page(g):
    k, K = kind(g), kind(g, True)
    verb, Verb = ('follow', 'Follow') if g['ch'] else ('join', 'Join')
    cname, cicon, ccol, cintro, tips = CATS[g['cat']]
    title = '%s: WhatsApp %s Link (%s)' % (g['name'], K, Verb)
    if g['desc']:
        meta = '%s. %s this WhatsApp %s with one tap, plus safety tips and similar %ss.' % (g['desc'].rstrip('.'), Verb, k, k)
    else:
        meta = '%s the “%s” WhatsApp %s%s. See what happens when you %s, safety tips and similar %ss.' % (
            Verb, g['name'], k, (' (' + cname + ')') if g['cat'] != 'unknown' else '', verb, k)
    meta = meta[:300]
    facts = ['WhatsApp %s' % k, 'Listed on %s' % g['date']]
    gen = '“%s” is a WhatsApp %s%s, listed on %s.' % (g['name'], k, (' about ' + cname.lower()) if g['cat'] not in ('unknown', 'others') else '', g['date'])
    if g['lang']: gen += ' Its name is written in %s.' % g['lang']
    if g['desc']:
        about = '<p class="lead">%s</p><p class="muted">%s</p>' % (E(g['desc']), E(gen))
    else:
        about = (f'<div class="note warn"><b>No description yet.</b> The person who shared this {k} didn’t add a description, so be careful before '
                 f'{"following it" if g["ch"] else "joining"}. {"Do you follow this channel, or know it?" if g["ch"] else "Are you a member, or do you know this group?"} '
                 f'<button class="link" type="button" data-open="describe">Add a short description</button> to help others.</div><p class="muted">{E(gen)}</p>')
    if g['ch']:
        what = ('<li><b>Admins can’t see your phone number</b> or profile photo. Other followers can’t see you either.</li>'
                '<li>You only <b>receive updates</b>; you can react to posts but not reply in the channel.</li>'
                '<li>Find it in the <b>Updates</b> tab. Unfollow any time: open the channel › ⋮ › Unfollow.</li>'
                '<li>You can mute it so updates don’t notify you.</li>')
    else:
        what = ('<li><b>Every member can see your phone number</b> and profile photo (unless you hide them in Privacy settings).</li>'
                '<li>You can read and send messages; admins can remove members and change who can post.</li>'
                '<li>Leave any time: open the group › ⋮ › More › Exit group. You can also mute it.</li>'
                '<li>Tip: Settings › Privacy › Groups lets you choose who can add you to groups.</li>')
    cat_block = ''
    if g['cat'] == 'unknown':
        chips = ''.join('<button type="button" class="chip" data-cat="%s">%s %s</button>' % (c, CATS[c][1], E(CATS[c][0])) for c in CAT_ORDER if c != 'unknown')
        cat_block = (f'<section class="box"><h2>{ic("tag")} Help categorise this {k}</h2><p>We don’t know this {k}’s topic yet. If you know it, pick one; '
                     f'when 3 people choose the same category it’s applied.</p><div class="chips" data-categorise>{chips}</div><p class="msg" role="status"></p></section>')
    rel, newest = related(g)
    faq = [
        ('How do I %s %s?' % (verb, g['name']), 'Tap “%s %s” on this page, wait 5 seconds while you check the details, then tap “Open in WhatsApp”. WhatsApp opens and asks you to confirm.' % (Verb, k)),
        ('Is %s a WhatsApp group or a channel?' % g['name'], 'It is a WhatsApp %s. %s' % (k, 'Admins and other followers cannot see your phone number.' if g['ch'] else 'Members can see your phone number and profile photo.')),
        ('Is it free to %s?' % verb, 'Yes. %sing a WhatsApp %s is free. Be careful if anyone inside asks you to pay.' % (Verb, k)),
        ('What if the link doesn’t work?', 'The admin may have reset the link, or the %s may be full. Tap “Report” and choose “Link not working”, and we re-check it.' % k),
    ]
    faq_html = ''.join('<details><summary>%s</summary><p>%s</p></details>' % (E(q), E(a)) for q, a in faq)
    bc, bcld = crumbs((cname, SITE + '/category/%s/' % g['cat']), (g['name'], SITE + '/g/%s/' % g['slug']))
    pic = ('<img src="%s" alt="%s" width="112" height="112">' % (E(g['photo']), E(g['name'] + ' WhatsApp ' + k + ' photo'))) if g['photo'] else '<span>%s</span>' % E((g['name'][:1] or '?').upper())
    reported = '<div class="note warn" data-reported %s>%s This %s was reported and is being reviewed.</div>' % ('' if g['reported'] else 'hidden', ic('flag'), k)
    body = f'''{bc}
<article class="gp" style="--c:{ccol}">
<header class="gp-hd">
<span class="av big">{pic}</span>
<div><div class="tags"><em class="ty ty-{k}">{K}</em><a href="/category/{g['cat']}/"><em>{cicon} {E(cname)}</em></a>{('<em>' + ic('globe') + E(g['lang']) + '</em>') if g['lang'] else ''}</div>
<h1>{E(g['name'])}</h1>
<div class="gp-acts"><button class="pill" type="button" data-save="{g['slug']}" aria-pressed="false">{ic('star')} <span>Save</span></button><button class="pill" type="button" data-copy="{E(SITE + '/g/' + g['slug'] + '/')}">{ic('copy')} Copy link</button><button class="pill" type="button" data-share>{ic('share')} Share</button><button class="pill" type="button" data-qr="{E(SITE + '/g/' + g['slug'] + '/')}">{ic('qr')} QR code</button></div>
<p class="facts">{ic('clock')} Listed on {g['date']} · {ic('check')} On our live list as of {datetime.date.fromisoformat(UPDATED).strftime('%d %b %Y').lstrip('0')}</p></div>
</header>
{reported}
<div class="join" data-join data-link="{E(g['link'])}" data-verb="{Verb}">
<div class="join-wait"><div class="ring"><svg viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="19"/><circle class="ring-p" cx="22" cy="22" r="19"/></svg><b data-count>5</b></div><p><span class="mono">&gt; getting things ready…</span><br>While you wait, take a moment to read the details and safety tips below.</p></div>
<p class="join-ok mono" hidden>&gt; all set. Tap below to open WhatsApp.</p>
<a class="btn btn-wa" data-join-go hidden rel="nofollow noopener" target="_blank" href="{E(g['link'])}">{WA} {Verb} {k}</a>
<noscript><a class="btn btn-wa" rel="nofollow noopener" target="_blank" href="{E(g['link'])}">{WA} {Verb} {k}</a></noscript>
<p class="join-note">Opens WhatsApp. {('Admins won’t see your number.' if g['ch'] else 'Members will see your number.')}</p>
</div>
<section class="box"><h2>{ic('help')} About this {k}</h2>{about}</section>
<section class="box"><h2>{ic('users') if not g['ch'] else ic('radio')} What happens when you {verb}</h2><ul class="list">{what}</ul></section>
<section class="box"><h2>{ic('shield')} Safety tips{'' if g['cat'] == 'unknown' else ' for ' + E(cname.lower()) + ' ' + k + 's'}</h2><ul class="list">{''.join('<li>' + E(t) + '</li>' for t in tips)}<li>Report this {k} below if it shares spam, scams or adult content.</li></ul></section>
{cat_block}
<section class="box"><h2>{ic('flag')} Link not working or something wrong?</h2>
<ul class="list"><li>Update WhatsApp, then try again.</li><li>The {k} may be full, or the admin may have reset the link.</li><li>On a computer, WhatsApp Web or the desktop app must be signed in.</li></ul>
<div class="acts"><button class="btn" type="button" data-open="report">{ic('flag')} Report this {k}</button>{'' if g['desc'] else '<button class="btn" type="button" data-open="describe">' + ic('edit') + ' Add a description</button>'}<button class="btn" type="button" data-open="owner">{ic('users')} Is this your {k}?</button></div>
</section>
<section class="box faq"><h2>{ic('help')} Questions</h2>{faq_html}</section>
</article>
{('<h2 class="sec">More ' + E(cname.lower()) + ' and similar</h2>' + grid(rel)) if rel else ''}
{('<h2 class="sec">Newest listings</h2>' + grid(newest)) if newest else ''}
<span hidden data-viewed='{json.dumps([g["slug"], g["name"], g["cat"], int(g["ch"]), g["photo"]], ensure_ascii=False).replace("'", "&#39;")}'></span>'''
    schema = {'@context': 'https://schema.org', '@graph': [
        dict({'@type': 'WebPage', '@id': SITE + '/g/%s/#page' % g['slug'], 'name': title, 'description': meta, 'url': SITE + '/g/%s/' % g['slug'],
              'datePublished': g['iso'], 'dateModified': UPDATED, 'inLanguage': 'en', 'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#org'},
              'breadcrumb': {'@id': SITE + '/g/%s/#crumbs' % g['slug']}, 'about': {'@type': 'Thing', 'name': g['name'], 'description': g['desc'] or gen, 'url': g['link']}},
             **({'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + g['photo']}} if g['photo'] else {})),
        dict(bcld, **{'@id': SITE + '/g/%s/#crumbs' % g['slug']}), WEBSITE_LD, ORG_LD, {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]}
    og = SITE + g['photo'] if g['photo'] else None
    return page('/g/%s/' % g['slug'], title, meta, body, noindex=g['flagged'] or g['reported'], ads=not g['adsoff'], schema=schema, og_image=og, gid=g['id'])

# ------------------------------------------------------------------ list pages
def list_pages(base, items, title, h1, intro, desc, active='', extra=''):
    total = max(1, (len(items) + PER_PAGE - 1) // PER_PAGE)
    for n in range(1, total + 1):
        chunk = items[(n - 1) * PER_PAGE:n * PER_PAGE]
        path = base if n == 1 else '%spage/%d/' % (base, n)
        t = title if n == 1 else '%s (page %d)' % (title, n)
        body = f'<div class="ph"><h1>{E(h1)}</h1><p>{intro}</p>{extra if n == 1 else ""}</div>{grid(chunk) if chunk else "<p class=muted>Nothing here yet.</p>"}{pager(base, n, total)}'
        _, bl = crumbs((h1.split(' ', 1)[-1] if h1[:1] > '~' else h1, SITE + base))
        ld = {'@context': 'https://schema.org', '@graph': [
            {'@type': 'CollectionPage', '@id': SITE + path + '#page', 'url': SITE + path, 'name': t, 'description': desc, 'inLanguage': 'en', 'dateModified': UPDATED,
             'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#org'},
             'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(items), 'itemListElement': [
                 {'@type': 'ListItem', 'position': (n - 1) * PER_PAGE + i + 1, 'url': SITE + '/g/%s/' % g['slug'], 'name': g['name']} for i, g in enumerate(chunk)]}},
            bl, WEBSITE_LD, ORG_LD]}
        desc_n = desc if n == 1 else '%s Page %d of %d.' % (desc.rstrip('.') + '.', n, total)
        write(path, page(path, t, desc_n, body, active=active, schema=ld))

def build():
    if os.path.exists(OUT):
        def force(fn, path, exc):   # Windows: clear read-only flags and retry
            import stat, time
            try: os.chmod(path, stat.S_IWRITE); time.sleep(0.05); fn(path)
            except Exception: pass
        shutil.rmtree(OUT, onerror=force)
    shutil.copytree(os.path.join(HERE, 'static'), OUT, dirs_exist_ok=True)
    if os.path.exists(MEDIA): shutil.copytree(MEDIA, os.path.join(OUT, 'media'), dirs_exist_ok=True)
    clean = [g for g in groups if not g['flagged']]
    for g in groups: write('/g/%s/' % g['slug'], group_page(g))

    # home
    cats = ''.join('<a class="cat" href="/category/%s/" style="--c:%s"><span>%s</span><b>%s</b><small>%d listing%s</small></a>' % (c, CATS[c][2], CATS[c][1], E(CATS[c][0]), len(by_cat[c]), '' if len(by_cat[c]) == 1 else 's')
                   for c in CAT_ORDER if by_cat[c])
    n_ch = sum(g['ch'] for g in groups)
    n_cats = sum(1 for c in CATS if by_cat[c])
    home = f'''<section class="hero">
<div class="eyebrows"><p class="eyebrow mono"><span class="dot"></span>live · {len(groups):,} listings<span class="hide-sm"> · synced {UPDATED}</span><span class="caret"></span></p>
<p class="counts mono"><span><b data-count-to="{len(groups) - n_ch}">{len(groups) - n_ch:,}</b> groups</span> · <span><b data-count-to="{n_ch}">{n_ch:,}</b> channels</span> · <span><b data-count-to="{n_cats}">{n_cats}</b> categories</span></p></div>
<h1>Find WhatsApp groups and channels worth joining</h1>
<p>Every listing has its own page: what it’s about, what happens when you join, safety tips for its topic and a report button. Add your own group in seconds.</p>
<div class="hs" data-hero-search><span class="hs-ic">{ic('search')}</span><input type="search" placeholder="Search groups and channels…" aria-label="Search groups and channels" autocomplete="off"><kbd>/</kbd><div class="hs-res" hidden></div></div>
<div class="acts center"><a class="btn btn-wa" href="/submit/">{ic('plus')} Add your group</a><a class="btn" href="/categories/">Browse categories</a><button class="btn" type="button" data-install hidden>{ic('download')} Install app</button></div>
<ul class="feats">
<li><span class="fi">{ic('shield')}</span><b>Safe listings</b><span>Spam, scams and dead links are reported and removed fast.</span></li>
<li><span class="fi">{ic('users')}</span><b>No sign-up</b><span>Browse, join and save groups without an account.</span></li>
<li><a href="/?install=1" data-install-card><span class="fi">{ic('download')}</span><b>Install as an app →</b><span>On your phone or PC. Opens like an app.</span></a></li>
<li><a href="/submit/"><span class="fi">{ic('plus')}</span><b>Add your group →</b><span>Free. Your group gets its own page in minutes.</span></a></li>
</ul>
</section>
<div class="ticker" aria-label="Just added"><span class="tk-label mono">{ic('bolt')} just added</span><div class="tk"><div class="tk-in">{''.join('<a href="/g/%s/">%s <em>%s</em></a>' % (g['slug'], E(g['name'][:48]), kind(g)) for g in clean[:16]) * 2}</div></div></div>
<section class="explore" data-explore>
<div class="ex-hd"><h2 class="sec">Explore</h2><div class="seg" role="group" aria-label="Type"><button type="button" aria-pressed="true" data-type="all">All</button><button type="button" aria-pressed="false" data-type="0">Groups</button><button type="button" aria-pressed="false" data-type="1">Channels</button></div></div>
<div class="filters"><select data-f="cat" aria-label="Category"><option value="">All categories</option>{''.join('<option value="%s">%s %s</option>' % (c, CATS[c][1], E(CATS[c][0])) for c in CAT_ORDER if by_cat[c])}</select><select data-f="lang" aria-label="Language"><option value="">Any language</option>{''.join('<option>%s</option>' % E(l) for l in sorted({g['lang'] for g in clean if g['lang']}))}</select><select data-f="sort" aria-label="Sort"><option value="new">Newest first</option><option value="az">A to Z</option></select></div>
<p class="muted mono ex-count" data-ex-count></p>
<div class="grid" data-ex-list>{grid(clean[:12])[len('<div class="grid">'):-len('</div>')]}</div>
<div class="ex-more"><button class="btn" type="button" data-ex-more hidden>Load more</button></div>
</section>
<h2 class="sec">Browse by category</h2><div class="cats">{cats}</div>
<section class="box why"><h2>{ic('shield')} How we keep listings safe</h2><ul class="list">
<li><b>Report any listing</b> that looks like spam, a scam or adult content. Every report is reviewed.</li>
<li><b>Listings reported by several people</b> are hidden until we check them.</li>
<li><b>Banned words</b> (adult, scams, hate, drugs) are blocked when a group is shared.</li>
<li><b>Dead links</b> are checked automatically and removed.</li></ul></section>
<section class="box"><h2>{ic('radio')} WhatsApp channels</h2><p>{n_ch} channels are listed. Following a channel is private: admins can’t see your number. <a href="/channels/">See all channels →</a></p></section>'''
    write('/', page('/', 'Share by GroupChatOn: WhatsApp Group and Channel Links', 'Find and share WhatsApp group and channel links by topic: jobs, study, business, gaming and more. Every listing has safety tips and a report button.',
                    home, active='home', schema={'@context': 'https://schema.org', '@graph': [
                        {'@type': 'WebPage', '@id': SITE + '/#page', 'url': SITE + '/', 'name': 'Share by GroupChatOn: WhatsApp Group and Channel Links', 'inLanguage': 'en',
                         'isPartOf': {'@id': SITE + '/#website'}, 'publisher': {'@id': SITE + '/#org'}, 'dateModified': UPDATED,
                         'mainEntity': {'@type': 'ItemList', 'name': 'Newest listings', 'itemListElement': [
                             {'@type': 'ListItem', 'position': i + 1, 'url': SITE + '/g/%s/' % g['slug'], 'name': g['name']} for i, g in enumerate(clean[:12])]}},
                        WEBSITE_LD, ORG_LD]}))

    # categories
    write('/categories/', page('/categories/', 'WhatsApp Group Categories | Share by GroupChatOn', 'Browse WhatsApp groups and channels by category: education, jobs, stocks, gaming, business, news and more.',
                               '<div class="ph"><h1>Categories</h1><p>Pick a topic. Groups whose topic we don’t know yet are in “Waiting for a category”, and you can help sort them.</p></div><div class="cats">' + cats + '</div>', active='cats',
                               kind_='CollectionPage', crumbs_ld=crumbs(('Categories', SITE + '/categories/'))[1]))
    for c in CAT_ORDER:
        name, icon, col, intro, tips = CATS[c]
        tip = '<div class="note">' + ic('shield') + ' <b>Safety:</b> ' + E(tips[0]) + '</div>'
        items = [g for g in by_cat[c] if not g['flagged']]
        list_pages('/category/%s/' % c, items, '%s WhatsApp Groups and Channels | Share by GroupChatOn' % name, '%s %s' % (icon, name), E(intro),
                   ('%s WhatsApp group and channel links. ' % name) + intro[:200], active='cats', extra=tip)
    list_pages('/latest/', clean, 'Latest WhatsApp Group Links | Share by GroupChatOn', 'Latest listings', 'The newest WhatsApp groups and channels shared on Share, newest first.',
               'The newest WhatsApp group and channel links, updated every few minutes.', active='new')
    list_pages('/channels/', [g for g in clean if g['ch']], 'WhatsApp Channel Links | Share by GroupChatOn', 'WhatsApp channels',
               'Channels are one-way: you get updates from the admins, and nobody can see your phone number.', 'WhatsApp channel links on every topic. Following a channel is private.')

    # static pages
    for slug, (title, h1, desc, html_) in PAGES.items():
        kd = {'about': 'AboutPage', 'contact': 'ContactPage', 'search': 'SearchResultsPage'}.get(slug, 'WebPage')
        write('/%s/' % slug, page('/%s/' % slug, title, desc, '<article class="prose"><h1>%s</h1>%s</article>' % (E(h1), html_), active=slug,
                                  kind_=kd, crumbs_ld=crumbs((h1, SITE + '/%s/' % slug))[1], noindex=slug == 'search'))

    # search index, 404, sitemap, robots
    idx = [[g['slug'], g['name'], g['cat'], int(g['ch']), g['photo'], g['lang'], int(g['t'] // 1000)] for g in clean]
    os.makedirs(os.path.join(OUT, 'data'), exist_ok=True)
    json.dump(idx, open(os.path.join(OUT, 'data', 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    write('/saved/', page('/saved/', 'Saved groups | Share by GroupChatOn', 'Groups and channels you saved on this device.',
          '<div class="ph"><h1>★ Saved</h1><p>Groups and channels you saved with the ★ button. They are kept on this device only, no account needed.</p></div><div class="grid" data-saved></div><p class="muted" data-saved-empty hidden>Nothing saved yet. Tap ★ on any listing to keep it here.</p>', noindex=True, active='saved'))
    write('/404.html', page('/404.html', 'Page not found | Share by GroupChatOn', 'This page could not be found.',
          '<div class="ph" data-404><h1>Page not found</h1><p>This listing may have been renamed or removed. <a href="/search/">Search all groups</a> or <a href="/">go home</a>.</p></div>', noindex=True))
    urls = ['/', '/categories/', '/latest/', '/channels/', '/submit/', '/about/'] + ['/category/%s/' % c for c in CAT_ORDER] + \
           ['/g/%s/' % g['slug'] for g in groups if not (g['flagged'] or g['reported'])]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lastmod = {('/g/%s/' % g['slug']): g['iso'] for g in groups}
    for u in urls: sm.append('<url><loc>%s%s</loc>%s</url>' % (SITE, u, ('<lastmod>%s</lastmod>' % lastmod[u]) if u in lastmod else ''))
    sm.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(sm))
    open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' % SITE)
    open(os.path.join(OUT, 'CNAME'), 'w').write(SITE.split('//')[1] + '\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').write('')
    print('built %d listing pages (%d flagged, %d reported), %d categories, %d photos; data from %s' % (
        len(groups), sum(g['flagged'] for g in groups), sum(g['reported'] for g in groups), len(CAT_ORDER), sum(1 for g in groups if g['photo']), UPDATED))

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pages import PAGES   # about, privacy, disclaimer, terms, contact, submit, search
except ImportError:
    print('  scripts/pages.py not found yet: info pages skipped'); PAGES = {}
build()
