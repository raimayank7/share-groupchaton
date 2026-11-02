# Share by GroupChatOn — share.groupchaton.com

Find and share WhatsApp groups and channels. Every listing gets its own page with safety tips, a 5-second join box,
community descriptions and categories, and a strict report system.

- `scripts/build.py` builds the whole static site from the live group list (`config.json`), `scripts/pages.py` holds the info pages.
- `static/` is copied as-is (styles, script, icons, app manifest, offline worker); `media/` keeps small copies of group photos.
- `.github/workflows/build.yml` rebuilds and publishes every 15 minutes.
- `apps-script/Share.gs` is the backend for reports and suggestions (runs in Google Apps Script, not here).

Designed & Developed by Nivesh Sahayak (https://www.niveshsahayak.in/). All rights reserved.
