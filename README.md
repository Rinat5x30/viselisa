<div align="center">

# ⚽ toptop

**Futbolçunun adını hərflərlə tap — Azərbaycan dilində hangman.**

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red?style=flat-square)](https://www.django-rest-framework.org/)

</div>

---

## Overview

toptop is a hangman-style game where the hidden word is a famous footballer's name (any nationality, any era). Wrong guesses draw the gallows and unlock progressive hints (age, position, shirt number, clubs). The site is fully in Azerbaijani, player names are kept as their common Latin-script surname/nickname, and the whole UI follows a pixel-art design language (blocky borders, hard shadows, rainbow accents) — no real player photos or club crests are used, only original pixel-art placeholders.

A fresh random player is picked on every "Yeni oyun" — unlimited practice, no account required.

---

## Features

- **Session-based game engine** — state lives server-side (signed cookies), rules live in `game/services.py`
- **Progressive hint system** — each mistake reveals one more clue: age → position → shirt number → first club → current club
- **Pixel-art design system** — no external art assets, no real player photos/logos (avoids IP risk), mobile-first responsive layout
- **i18n-ready** — all UI strings wrapped in Django's `{% trans %}`/`gettext`; Azerbaijani (`az`) is the only active language today, more can be added later without touching code
- **Curated player database** — 139 players (legends + current stars) across dozens of nationalities, loaded from a JSON data file and editable via Django admin
- **Consent-gated Google Analytics (GA4) and AdSense** — third-party scripts only load after the visitor accepts the cookie banner
- **Static files via WhiteNoise** — single-process deployment, no Nginx required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web framework | Django 6.0 |
| REST API | Django REST Framework |
| Database | SQLite (committed to the repo — see [Database workflow](#database-workflow)) |
| Static files | WhiteNoise |
| Frontend | Vanilla HTML · CSS · JavaScript |
| WSGI server | Gunicorn |
| Hosting | Render |

---

## Project Structure

```
toptop/
├── backend_project/          # Django project package
│   ├── settings.py           # All config via environment variables
│   ├── urls.py
│   └── wsgi.py
├── game/                     # Core application
│   ├── models.py             # Player model (name, age, position, number, clubs)
│   ├── services.py           # Game-engine logic
│   ├── seo.py                # Canonical URLs, JSON-LD, robots.txt/sitemap.xml content
│   ├── views.py              # NewGameView · GuessLetterView · home/privacy/terms/robots/sitemap
│   ├── serializers.py
│   ├── context_processors.py # Exposes GA4/AdSense ids + canonical domain to templates
│   ├── data/players.json     # Player dataset (source of truth for seeding)
│   └── management/commands/
│       └── seed_players.py   # Loads game/data/players.json into the DB
├── frontend/                 # Static UI (served by WhiteNoise)
│   ├── base.html             # Shared layout: header, footer, cookie banner, SEO meta
│   ├── index.html            # Game page + how-to-play/FAQ content
│   ├── privacy.html / terms.html
│   ├── styles.css            # Pixel-art design system
│   ├── app.js                # Game logic
│   ├── consent.js            # Cookie banner + GA4/AdSense loader
│   ├── site.webmanifest      # PWA manifest
│   ├── favicon.svg / og-image.svg+.png / apple-touch-icon.png / android-chrome-*.png
│   └── (served at root) /robots.txt, /sitemap.xml
├── locale/                   # Django i18n catalogs (az is the source language)
├── render.yaml                # Render deploy config
├── .env.example
├── requirements.txt
└── manage.py
```

---

## API

Game state is persisted in the Django session.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/game/new/` | Starts a new game — picks a random player, resets session state |
| `POST` | `/api/game/guess/` | Submit a letter — body: `{"letter": "a"}` |
| `GET` | `/api/players/random/` | Fetch a random player record (utility) |

**Guess response shape:**

```json
{
  "masked_word":       "_ o r l a n",
  "mistakes":          1,
  "max_mistakes":      6,
  "guessed_letters":   ["o", "r", "l", "a", "n"],
  "wrong_letters":     ["q"],
  "hints":             [{"label": "Yaş", "value": "47"}],
  "status":            "ongoing",
  "repeated":          false,
  "word":              null
}
```

`status` is one of `ongoing` · `won` · `lost`. `word` is revealed only when the game ends.

---

## Getting Started

### Prerequisites

- Python 3.12+

### 1 — Clone & install

```bash
git clone <repo-url> toptop
cd toptop
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2 — Environment variables

```bash
cp .env.example .env
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`ADSENSE_CLIENT_ID` and `GA_MEASUREMENT_ID` can stay empty locally — ads/analytics simply won't load.

### 3 — Database & seed

```bash
python manage.py migrate
python manage.py seed_players
```

### 4 — Run

```bash
python manage.py runserver
```

Visit **http://localhost:8000**

---

## Database workflow

The project intentionally has **no managed Postgres**. `db.sqlite3` is committed to the repo, because Render's filesystem is reset on every deploy. To add or edit players:

1. Edit `game/data/players.json` (or use `/admin/` locally).
2. Run `python manage.py seed_players --reset` to rebuild the local `db.sqlite3` from the JSON file (or edit rows directly in `/admin/`).
3. Commit the updated `db.sqlite3` and push — Render serves whatever is committed.

Note: player `age` and `current_club` reflect the data as curated; both drift over time (birthdays, transfer windows) and should be reviewed periodically via `/admin/`.

---

## Deploying to Render

1. Push the repo to GitHub.
2. In Render, **New → Blueprint** and point it at the repo — `render.yaml` defines the service.
3. Once the custom domain is purchased, add it in Render's dashboard and set `ALLOWED_HOSTS` / `SITE_DOMAIN` / `CSRF_TRUSTED_ORIGINS` accordingly.
4. Set `ADSENSE_CLIENT_ID` and `GA_MEASUREMENT_ID` env vars once those accounts are approved.

Render automatically injects `RENDER_EXTERNAL_HOSTNAME` / `RENDER_EXTERNAL_URL` — picked up by `settings.py` automatically.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Django cryptographic secret |
| `DEBUG` | | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | | — | Comma-separated trusted origins (with scheme) |
| `SITE_DOMAIN` | | `toptop.az` | Canonical domain used in SEO tags |
| `ADSENSE_CLIENT_ID` | | — | Google AdSense publisher id — ads stay hidden until set |
| `GA_MEASUREMENT_ID` | | — | GA4 measurement id — analytics stay off until set |

---

## Testing

```bash
python manage.py test game
```

Covers the hangman rules: hints, win/lose, repeated guesses, invalid input.
