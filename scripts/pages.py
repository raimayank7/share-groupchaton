"""Static pages for share.groupchaton.com.

PAGES = {slug: (title, h1, meta_description, inner_html)}
build.py wraps each as <article class="prose"><h1>h1</h1>inner_html</article> at /<slug>/.
"""

UPDATED = '<p class="muted">Last updated: 2 November 2026</p>'
HELP = 'https://www.groupchaton.com/p/contact-us.html?from=share'
CONTACT_LINK = '<a href="%s">contact form</a>' % HELP

CATEGORIES = [
    ('education', 'Education &amp; Study'), ('jobs', 'Jobs &amp; Careers'), ('stocks', 'Stocks &amp; Trading'),
    ('earning', 'Online Earning'), ('business', 'Business'), ('shopping', 'Shopping &amp; Deals'),
    ('tech', 'Technology'), ('gaming', 'Gaming'), ('entertainment', 'Entertainment'), ('music', 'Music'),
    ('fun', 'Fun &amp; Memes'), ('friendship', 'Friendship &amp; Chat'), ('love', 'Love &amp; Relationships'),
    ('quotes', 'Quotes &amp; Shayari'), ('news', 'News &amp; Updates'), ('sports', 'Sports'),
    ('religion', 'Religion &amp; Spirituality'), ('travel', 'Travel'), ('health', 'Health &amp; Fitness'),
    ('food', 'Food &amp; Recipes'), ('others', 'Other Topics'),
]
OPTIONS = ''.join('<option value="%s">%s</option>' % c for c in CATEGORIES)

BANNED = '''<ul>
<li><b>Adult or sexual content</b>, including "dating" groups that are really adult groups, and anything involving minors.</li>
<li><b>Scams and fraud</b>: "double your money" schemes, fake jobs that ask for a fee, fake giveaways, phishing, selling accounts, hacking or cracked software.</li>
<li><b>Hate and harassment</b>: groups that attack people for religion, caste, race, gender, nationality or disability, or that target a person.</li>
<li><b>Drugs and weapons</b>: buying or selling drugs, medicines without prescription, weapons or explosives.</li>
<li><b>Betting and gambling</b>: satta, matka, betting tips, "fixed match" groups, casino and lottery promotion.</li>
<li><b>Violence and illegal activity</b>: threats, self-harm encouragement, pirated films or courses, leaked exam papers.</li>
</ul>'''

ABOUT = '''
<p><b>Share by GroupChatOn</b> is a free directory of WhatsApp group and channel links. People who run a group or channel add its invite link, and visitors browse by topic or search to find communities about study, jobs, business, gaming, news, music and much more. The site is simple on purpose: it loads fast on any phone, works in light and dark mode, and can be installed like an app from your browser.</p>

<h2>How listings work</h2>
<p>Every group or channel on Share gets <b>its own page</b> with its name, picture (when WhatsApp shows one), category, description and a join box. When you press <b>Join</b>, a short 5-second countdown appears with safety tips before WhatsApp opens. This pause is there so you see who you are about to join and what to watch out for, rather than jumping straight into an unknown chat.</p>
<p>The list comes from a shared group directory run by the same owner, so it stays current as new links are added. Listings are organised into categories, a latest list and a channels list, and each page links to similar groups in the same category.</p>
<ul>
<li><b>Community descriptions:</b> if a listing has a poor or missing description, any visitor can suggest a better one. Suggestions are reviewed before they appear.</li>
<li><b>Community categories:</b> if a group is in the wrong category, visitors can vote for the right one. When three different people agree, the category changes.</li>
</ul>

<h2>How we keep it safe</h2>
<p>We cannot check every chat ourselves, so Share is built to let the community flag problems quickly and to keep harmful links out from the start.</p>
<ul>
<li><b>Banned words:</b> links whose name or description contains adult, scam, hate, drug or betting terms are blocked automatically and never get a page.</li>
<li><b>Report button:</b> every listing has a Report button. Every report is reviewed, and a listing reported by <b>several different people</b> is hidden until we check it.</li>
<li><b>Dead-link checks:</b> invite links that WhatsApp has revoked or expired are checked regularly and taken off the site so you are not sent to broken invites.</li>
<li><b>Safety tips:</b> every join box reminds you never to pay money to join, never share OTPs or bank details, and to leave and report any group that makes you uncomfortable.</li>
</ul>

<h2>Add your own group or channel</h2>
<p>Run a WhatsApp group or channel? <a href="/submit/">Add it here</a> for free. Paste the invite link, choose a category and write a one-line description. There is no sign-up. Please read the <a href="/terms-of-use/">Terms of Use</a> first: you must have the right to share the link, and the content rules apply to every listing.</p>

<h2>Part of the GroupChatOn family</h2>
<p>Share is one of several free sites run under the GroupChatOn name:</p>
<ul>
<li><a href="https://www.groupchaton.com/">GroupChatOn</a> - free online novels and stories to read.</li>
<li><a href="https://infinity.groupchaton.com/">GroupChatOn Infinity</a> - hundreds of free tools that run in your browser, from calculators to text and image helpers.</li>
<li><a href="https://help.groupchaton.com/">GroupChatOn Help</a> - step-by-step guides for WhatsApp, our sites and everyday tech questions.</li>
<li><a href="https://app.groupchaton.com/">GroupChatOn App</a> - the installable reading app for our novels, with your library and reading place saved.</li>
</ul>

<h2>Who we are</h2>
<p>Share by GroupChatOn is built and maintained by <b>Nivesh Sahayak</b>. It is an independent project and is <b>not affiliated with, endorsed by or sponsored by WhatsApp or Meta</b>. "WhatsApp" is a trademark of its owner and is used here only to describe what the listed links are for. Questions or problems? See the <a href="/contact/">Contact page</a>.</p>
'''

PRIVACY = UPDATED + '''
<p>This Privacy Policy explains what information Share by GroupChatOn ("Share", "we", "us") at share.groupchaton.com collects, why, and the choices you have. We try to collect as little as possible: there are no user accounts, and you can browse the whole site without telling us who you are.</p>

<h2>1. Information you choose to give us</h2>
<ul>
<li><b>Group and channel submissions.</b> When you add a link, we store the invite link, the category and the description you write. These are <b>published publicly</b> on Share and in the shared group directory it is built from (run by the same owner), together with the group name and picture that WhatsApp shows for that invite. Do not put personal details such as your phone number in a description.</li>
<li><b>Reports and suggestions.</b> When you report a listing, suggest a description or vote for a category, we store the listing it is about, your reason or suggestion, the time, and a <b>random visitor id</b> created by your browser. The visitor id is a random string that does not contain your name, number or email; it only lets us count reports and votes from different people and stop one person voting many times. This data is kept in a private Google Sheet run through Google Apps Script.</li>
<li><b>Owner and support requests.</b> If you ask us to remove your group, correct a listing or answer a question, we store the contact details you give us (for example an email address) and your message, so we can reply.</li>
</ul>

<h2>2. Information collected automatically</h2>
<ul>
<li><b>Hosting logs.</b> The site is hosted on GitHub Pages. GitHub may record technical data such as your IP address, browser type and the pages requested, for security and to keep the service running. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's privacy statement</a>.</li>
<li><b>Google Analytics.</b> We use Google Analytics to understand which pages are used and how people find the site (for example pages viewed, approximate country, device type and referring site). We see these as totals and do not use them to identify you. You can install the <a href="https://tools.google.com/dlpage/gaoptout">Google Analytics opt-out browser add-on</a>.</li>
</ul>

<h2>3. Advertising and cookies</h2>
<p>Share is free because it shows ads from <b>Google AdSense</b>. Google and its partners use cookies and similar technology to show ads based on your visits to this and other websites, to limit how often you see an ad, and to measure results. Third-party vendors, including Google, use cookies to serve ads based on your prior visits.</p>
<ul>
<li>You can turn off personalised ads from Google at <a href="https://adssettings.google.com/">Google Ad Settings</a>.</li>
<li>You can opt out of personalised ads from many other vendors at <a href="https://www.aboutads.info/">www.aboutads.info</a>.</li>
<li>Learn how Google uses information from sites that use its services at <a href="https://policies.google.com/technologies/partner-sites">How Google uses data from partner sites</a>.</li>
</ul>
<p>Where the law requires it (for example in the European Economic Area, the United Kingdom and Switzerland), Google asks for consent before personalised ads are shown. Pages that have been reported are shown without ads until they are reviewed.</p>

<h2>4. Data stored in your browser</h2>
<p>Share uses your browser's local storage (not shared with other websites) to remember:</p>
<ul>
<li>your <b>light or dark theme</b> choice;</li>
<li>your <b>random visitor id</b> used for reports and votes, and which listings you have already reported or voted on;</li>
<li>if you install Share as an app, a <b>cached copy</b> of pages and files so it opens quickly and works with a weak connection.</li>
</ul>
<p>You can clear all of this at any time by clearing site data for share.groupchaton.com in your browser settings, or by uninstalling the app.</p>

<h2>5. How we use information</h2>
<p>We use the information above only to run the directory, publish listings, review reports and suggestions, prevent abuse and spam, reply to you, understand how the site is used, and show ads. We do not sell your personal information, and we do not use reports or suggestions to build profiles about you.</p>

<h2>6. Sharing</h2>
<p>Submitted listings are public by design. Apart from that, information is handled by the service providers named above (GitHub, Google) to run the site, and we may disclose information if the law requires it or to protect people from harm, for example when reporting a serious abuse to the authorities.</p>

<h2>7. How long we keep it</h2>
<ul>
<li>Listings stay until they are removed by the owner, removed after review, or their invite link stops working.</li>
<li>Reports, suggestions and votes are kept while the listing is on the site and for up to 12 months after a decision, so repeated abuse can be spotted, then deleted.</li>
<li>Support emails are kept for as long as needed to deal with your request and for up to 24 months afterwards.</li>
<li>Analytics and advertising data is kept according to Google's own retention settings.</li>
</ul>

<h2>8. Children</h2>
<p>Share is not meant for children under 13, and WhatsApp itself requires users to be at least 13 (older in some countries). We do not knowingly collect information from children under 13. If you believe a child has sent us personal information, contact us and we will delete it.</p>

<h2>9. Your rights</h2>
<p>Depending on where you live, laws such as the EU and UK <b>GDPR</b>, the California <b>CCPA/CPRA</b> and India's <b>Digital Personal Data Protection Act, 2023</b> give you rights over your personal data. These can include the right to know what we hold about you, to get a copy, to correct it, to delete it, to withdraw consent, and to complain to a data protection authority. We do not sell or "share" personal information for money as defined by the CCPA. Because we do not ask for names or accounts, tell us the listing link and the approximate date of your report or suggestion so we can find the right records.</p>

<h2>10. Changes to this policy</h2>
<p>If we change how we handle information, we will update this page and the date at the top.</p>

<h2>11. Contact</h2>
<p>For privacy questions or requests, use the ''' + CONTACT_LINK + ''' on GroupChatOn and start your message with "Privacy request". We aim to reply within 30 days.</p>
'''

DISCLAIMER = UPDATED + '''
<p>Please read this disclaimer before joining any group or channel through Share by GroupChatOn (share.groupchaton.com).</p>

<h2>Listings are added by users</h2>
<p>Every group and channel on Share is added by members of the public. We do not create, own, run or moderate these groups or channels, and we have no control over who is in them, what is posted there, or whether the admin changes the group's topic after it is listed. The name, picture and description you see come from WhatsApp and from the person who submitted the link, and may not be accurate.</p>

<h2>Not affiliated with WhatsApp or Meta</h2>
<p>Share by GroupChatOn is an independent website built by Nivesh Sahayak. It is <b>not affiliated with, endorsed by or sponsored by WhatsApp LLC or Meta Platforms, Inc.</b> WhatsApp is their trademark and is mentioned only to describe the links listed here. Problems inside a WhatsApp chat should also be reported in the WhatsApp app itself.</p>

<h2>Join at your own risk</h2>
<p>When you join a group, other members and admins can see your phone number and profile, and you will see theirs. Joining any group or channel is your own decision and your own responsibility. We cannot guarantee that a group is safe, active, friendly or what it claims to be.</p>

<h2>No endorsement</h2>
<p>A listing on Share does not mean we recommend, check or approve the group, its admins or anything sold or advertised there. The order of listings, categories and "similar groups" are generated automatically and are not a ranking of quality or trust.</p>

<h2>Watch out for scams</h2>
<ul>
<li>Never pay money to join a group or to "unlock" a job, prize, loan or investment.</li>
<li>Never share OTPs, UPI PINs, passwords, bank or card details with anyone in a group.</li>
<li>Be careful with links and APK files sent in groups; they may contain malware.</li>
<li>Ignore promises of guaranteed profits, stock tips, "work from home" tasks that ask for a deposit, or betting tips.</li>
<li>If something feels wrong, leave the group, report it in WhatsApp and press <b>Report</b> on its page here.</li>
</ul>
<p>If you have lost money to fraud in India, call the cyber crime helpline <b>1930</b> or report at <a href="https://cybercrime.gov.in/">cybercrime.gov.in</a> as soon as possible.</p>

<h2>Information on this site</h2>
<p>Safety tips and other text on Share are general information, not legal, financial or professional advice. We try to keep everything correct and up to date but make no promise that it is complete or error-free.</p>

<h2>External links and ads</h2>
<p>Share links to WhatsApp, to our other sites and to third-party websites, and shows ads served by Google AdSense. We are not responsible for the content, products, privacy practices or offers of external websites or advertisers. An ad appearing next to a listing does not mean the advertiser is connected with that group.</p>

<h2>Limitation of liability</h2>
<p>To the fullest extent allowed by law, Share by GroupChatOn and Nivesh Sahayak are not liable for any loss or harm arising from joining, using or relying on any group, channel, link or advertisement found through this site. See also our <a href="/terms-of-use/">Terms of Use</a> and <a href="/privacy-policy/">Privacy Policy</a>.</p>
'''

TERMS = UPDATED + '''
<p>These Terms of Use apply to everyone who visits or adds content to Share by GroupChatOn at share.groupchaton.com ("Share", "we", "us"). By using the site you agree to them. If you do not agree, please do not use the site.</p>

<h2>1. Using the site</h2>
<p>You may browse, search and join listed groups for personal, lawful purposes. You must be at least 13 years old, and old enough under the laws of your country to use WhatsApp. Do not try to break, overload or scrape the site in a way that harms it, and do not use automated tools to submit links, reports or votes.</p>

<h2>2. Submitting a group or channel</h2>
<p>When you add a link, you confirm that:</p>
<ul>
<li>you are an admin or owner of the group or channel, or have the admin's permission to share its invite link publicly;</li>
<li>the name, picture, category and description are honest and describe what the group is really about;</li>
<li>the group follows WhatsApp's own Terms of Service and the law of your country;</li>
<li>you understand the link, name, picture and description will be <b>public</b> on Share and in the shared group directory it is built from (run by the same owner), and may appear in search engines.</li>
</ul>
<p>You keep any rights you have in your description, and you give us a free, worldwide permission to publish, edit for length or clarity, translate, categorise and display it on our sites for as long as the listing is live.</p>

<h2>3. Content that is not allowed</h2>
<p>The following are not allowed on Share and are blocked or removed:</p>
''' + BANNED + '''
<p>Also not allowed: spam (adding the same link many times), misleading names or categories, links that are not WhatsApp group or channel invites, and personal information about other people. Some of these are blocked automatically by our banned-words filter; the rest are handled through reports.</p>

<h2>4. Reporting abuse</h2>
<p>Every listing has a <b>Report</b> button. Please use it honestly. Every report is reviewed, and a listing reported by several different people is hidden until we check it. Making false reports, or reporting many listings to harm a competitor, is misuse of the site. Community description suggestions and category votes must also be genuine.</p>

<h2>5. Our right to remove content</h2>
<p>We may edit, re-categorise, hide or remove any listing, suggestion or vote at any time, with or without notice, if we believe it breaks these terms, is reported, is no longer working, or could harm visitors or the site. We may block links, words or visitors that are used for abuse. We are not obliged to keep any listing online, and removal does not entitle anyone to compensation.</p>

<h2>6. Ads</h2>
<p>Share is supported by ads from Google AdSense. Ads are chosen by Google, not by us, and an ad next to a listing is not connected with that group. Do not click ads to earn money for anyone or ask others to do so; this breaks Google's rules. Paid placement of listings is not offered.</p>

<h2>7. No warranty and limitation of liability</h2>
<p>The site is provided "as is" and "as available". We do not run the listed groups and do not guarantee that any listing is accurate, safe, active or lawful, or that the site will always be available. To the fullest extent allowed by law, Share by GroupChatOn and Nivesh Sahayak are not liable for any direct or indirect loss arising from use of the site, from any group or channel you join, or from dealings with other users or advertisers. Please read the <a href="/disclaimer/">Disclaimer</a>.</p>

<h2>8. Trademarks</h2>
<p>WhatsApp is a trademark of WhatsApp LLC / Meta Platforms, Inc. Share is not affiliated with them. Group names and pictures belong to their owners and are shown only to identify the listing.</p>

<h2>9. Governing law</h2>
<p>These terms are governed by the laws of <b>India</b>. Any dispute will first be discussed in good faith; if it cannot be settled, it will be subject to the jurisdiction of the courts in India. Nothing here removes rights you have under the consumer laws of the country where you live.</p>

<h2>10. Changes</h2>
<p>We may update these terms from time to time. The date at the top shows the latest version. Continuing to use the site after a change means you accept the updated terms.</p>

<h2>11. Contact</h2>
<p>Questions about these terms? Use the ''' + CONTACT_LINK + ''' on GroupChatOn, or see the <a href="/contact/">Contact page</a>.</p>
'''

CONTACT = '''
<p>Share by GroupChatOn is run by a small team, so most help is handled through our Help site. Pick the option below that matches what you need; it is the fastest way to get a reply.</p>

<h2>Get help or send a question</h2>
<p>Use the ''' + CONTACT_LINK + ''' on GroupChatOn. Tell us which page your question is about (copy its address from your browser) and what went wrong. We usually reply within a few working days. You can also browse <a href="https://help.groupchaton.com/">GroupChatOn Help</a> for step-by-step guides about WhatsApp groups, channels and invite links.</p>

<h2>Report a group or channel</h2>
<p>The quickest way is the <b>Report</b> button on the listing's own page. Choose a reason (for example scam, adult content, hate, wrong category or broken link) and send it. You do not need to give your name.</p>
<ul>
<li>Every report is <b>reviewed</b>, usually within a day.</li>
<li>A listing reported by <b>several different people</b> is hidden while we check it.</li>
</ul>
<p>Please also report the group inside WhatsApp (open the group, tap its name, then <b>Report group</b>) so WhatsApp can act on the chat itself. If someone is in immediate danger, contact local emergency services first. In India, report online fraud on <b>1930</b> or at <a href="https://cybercrime.gov.in/">cybercrime.gov.in</a>.</p>

<h2>Remove or change your own group</h2>
<p>The simplest way to take your group off Share is to <b>reset its invite link</b> in WhatsApp (group info › Invite via link › Reset link). The old link stops working and our dead-link check removes the listing automatically. To fix a description, use "Suggest a better description" on your listing's page. If you need something else, for example a faster removal or a category change, send a request through the ''' + CONTACT_LINK + ''' with the link to your listing and proof you are an admin (such as a screenshot of the group info screen).</p>

<h2>Privacy requests</h2>
<p>To ask what information we hold, or to have reports, suggestions or support messages deleted, use the ''' + CONTACT_LINK + ''' and start your message with "Privacy request". Our <a href="/privacy-policy/">Privacy Policy</a> explains what we store and for how long.</p>

<h2>Before you write</h2>
<details><summary>Can you get me into a full or private group?</summary><p>No. We do not run any of the listed groups. Only that group's admins can add you, approve your request or share a new link.</p></details>
<details><summary>Someone in a group asked me for money. Is that you?</summary><p>No. Share never asks for money and never contacts you on WhatsApp. Leave the group, report it, and never pay to join anything.</p></details>
<details><summary>Can I pay to put my group at the top?</summary><p>No. Listings are free and there is no paid placement.</p></details>
<div class="note">Share by GroupChatOn is not affiliated with WhatsApp or Meta. For problems with your WhatsApp account, contact WhatsApp support from the app (Settings › Help).</div>
'''

SUBMIT = '''
<p>Add your WhatsApp group or channel to Share for free. It gets its own page, appears in its category and the latest list. No sign-up is needed.</p>

<h2>Before you add a link</h2>
<ul>
<li>You must be an admin of the group or channel, or have the admin's permission to share it publicly.</li>
<li>Choose the category that really fits and write an honest one-line description.</li>
<li>Do not put phone numbers or other personal details in the description.</li>
<li>Adult, scam, hate, drugs and betting groups are blocked. See the full list in the <a href="/terms-of-use/">Terms of Use</a>.</li>
</ul>

<form class="form" data-submit><label>WhatsApp group or channel link<input name="group_link" type="url" required placeholder="https://chat.whatsapp.com/..."></label><label>Category<select name="category"><option value="">Choose a category (optional)</option>''' + OPTIONS + '''</select></label><label>Short description (optional)<textarea name="description" maxlength="200" rows="3"></textarea></label><button class="btn btn-wa" type="submit">Submit</button><p class="msg" role="status"></p></form>

<h2>How to copy your invite link</h2>
<details open><summary>For a WhatsApp group</summary>
<ol>
<li>Open the group in WhatsApp and tap the <b>group name</b> at the top.</li>
<li>Tap <b>Invite to group via link</b> (on some phones: <b>Invite via link</b>). Only admins see this option.</li>
<li>Tap <b>Copy link</b>. It starts with <b>https://chat.whatsapp.com/</b>.</li>
<li>Come back here, paste it in the first box, and press <b>Submit</b>.</li>
</ol></details>
<details><summary>For a WhatsApp channel</summary>
<ol>
<li>Open the <b>Updates</b> tab in WhatsApp and open your channel.</li>
<li>Tap the <b>channel name</b> to open channel info.</li>
<li>Tap <b>Share</b> or <b>Channel link</b>, then <b>Copy link</b>. It starts with <b>https://whatsapp.com/channel/</b>.</li>
<li>Paste it in the first box above and press <b>Submit</b>.</li>
</ol></details>

<h2>What happens next</h2>
<ul>
<li>Your link is checked against our banned-words list. If it passes, it is added to the shared list straight away.</li>
<li>Share's pages are rebuilt regularly, so your group's own page appears soon after, usually within a day or two.</li>
<li>Visitors can suggest a better description or vote for a different category; suggestions are reviewed and a category changes after three votes.</li>
<li>If the invite link is reset or stops working, the listing is removed automatically.</li>
<li>If the group is reported, it may be hidden or removed while we review it.</li>
</ul>
<div class="note">Adding the same link many times does not move it up and may get it blocked. To remove your group later, just reset its invite link in WhatsApp.</div>
'''

SEARCH = '''
<p>Search all WhatsApp groups and channels listed on Share by name, description or category. Results appear as you type.</p>
<div class="search" data-search><input type="search" name="q" placeholder="Search groups and channels…" aria-label="Search" autofocus><p class="muted" data-search-count></p><div class="grid" data-results></div></div>
<h2>Search tips</h2>
<p>Use one or two simple words such as <b>jobs</b>, <b>class 10</b>, <b>stock market</b> or <b>cricket</b>; you can also search in Hindi or Hinglish words that groups use in their names. If you find nothing, try a shorter word or browse the <a href="/categories/">categories</a> and the <a href="/latest/">latest listings</a>. Open a listing to read its safety tips before you join, and use its Report button if something looks wrong. Can't find a group for your topic? <a href="/submit/">Add your own</a>.</p>
'''

S = ' | Share by GroupChatOn'
PAGES = {
    'about': ('About Share' + S, 'About Share by GroupChatOn',
              'What Share by GroupChatOn is: a free directory of WhatsApp group and channel links, with a page, safety tips and a report button for every listing.',
              ABOUT),
    'privacy-policy': ('Privacy Policy' + S, 'Privacy Policy',
                       'How Share by GroupChatOn handles submissions, reports, analytics, Google AdSense cookies and browser storage, and the privacy rights you have.',
                       PRIVACY),
    'disclaimer': ('Disclaimer' + S, 'Disclaimer',
                   'Listings on Share are added by users. We do not run any group and are not affiliated with WhatsApp or Meta. Join at your own risk and avoid scams.',
                   DISCLAIMER),
    'terms-of-use': ('Terms of Use' + S, 'Terms of Use',
                     'Rules for using Share by GroupChatOn: what you may submit, banned content, reporting abuse, removal of listings, ads, liability and governing law.',
                     TERMS),
    'contact': ('Contact' + S, 'Contact and help',
                'Get help with Share by GroupChatOn: ask a question, report a WhatsApp group, remove or update your own listing, or send a privacy request.',
                CONTACT),
    'submit': ('Add your WhatsApp group or channel' + S, 'Add your WhatsApp group or channel',
               'Add your WhatsApp group or channel link to Share for free. Choose a category, write a short description and get your own listing page with safety tips.',
               SUBMIT),
    'search': ('Search WhatsApp groups and channels' + S, 'Search groups and channels',
               'Search WhatsApp group and channel links on Share by name, topic or category. Every result has its own page with safety tips and a report button.',
               SEARCH),
}
