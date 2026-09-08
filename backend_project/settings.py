"""Django settings for the toptop project."""

import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv

from django.utils.csp import CSP

# Some hosts' system mimetypes DB lacks these — WhiteNoise falls back to
# application/octet-stream otherwise, which breaks the <link rel="preload" type="font/woff2">
# match and can trigger browser console warnings for the self-hosted fonts.
mimetypes.add_type('font/woff2', '.woff2')
mimetypes.add_type('font/woff', '.woff')

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Render injects RENDER_EXTERNAL_HOSTNAME/RENDER_EXTERNAL_URL automatically
_render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if _render_hostname:
    ALLOWED_HOSTS.append(_render_hostname)

# Required for HTTPS POST requests (Django 4+) — covers Render's proxy
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o]
_render_url = os.environ.get('RENDER_EXTERNAL_URL')
if _render_url:
    CSRF_TRUSTED_ORIGINS.append(_render_url)

# Tell Django it's behind an HTTPS reverse proxy (Render, nginx, etc.)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    # SESSION_ENGINE is signed_cookies — the entire game state lives in this cookie
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # playtoptop.onrender.com is a specific FQDN (not the shared onrender.com apex),
    # so includeSubDomains only affects subdomains of this app, not other Render customers.
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    # Not enabling preload: this is a temporary Render subdomain until the real
    # custom domain is bought — preload entries are very slow/hard to remove later.

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'game',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'frontend'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.csp',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'game.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_project.wsgi.application'

# Store sessions in signed cookies — no DB table required, works on ephemeral filesystems
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'az'
TIME_ZONE = 'Asia/Baku'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'frontend']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    # Manifest storage hashes filenames (styles.a1b2c3.css) so WhiteNoise can send
    # far-future immutable cache headers safely. Skipped in DEBUG so `{% static %}`
    # doesn't require running collectstatic locally.
    'staticfiles': {
        'BACKEND': (
            'whitenoise.storage.CompressedStaticFilesStorage'
            if DEBUG
            else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        )
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Content-Security-Policy ---------------------------------------------
# Inline scripts (JSON-LD, the GA/AdSense id bootstrap in base.html) use
# {{ csp_nonce }} instead of 'unsafe-inline'. The googlesyndication.com/
# doubleclick.net/google-analytics.com entries are only exercised once
# ADSENSE_CLIENT_ID / GA_MEASUREMENT_ID are set (see consent.js) — kept here
# now so turning those on later doesn't silently break under CSP.
SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [
        CSP.SELF,
        CSP.NONCE,
        'https://www.googletagmanager.com',
        'https://pagead2.googlesyndication.com',
        'https://googleads.g.doubleclick.net',
    ],
    'style-src': [CSP.SELF],
    'font-src': [CSP.SELF],
    'img-src': [
        CSP.SELF,
        'https://www.google-analytics.com',
        'https://*.googlesyndication.com',
        'https://*.doubleclick.net',
    ],
    'connect-src': [
        CSP.SELF,
        'https://www.google-analytics.com',
        'https://analytics.google.com',
        'https://www.googletagmanager.com',
    ],
    'frame-src': [
        'https://googleads.g.doubleclick.net',
        'https://tpc.googlesyndication.com',
        'https://www.google.com',
    ],
    'object-src': [CSP.NONE],
    'base-uri': [CSP.SELF],
    'form-action': [CSP.SELF],
    'frame-ancestors': [CSP.NONE],
}

# --- toptop: third-party integrations (all optional, off until configured) ---
# Google AdSense publisher id, e.g. "ca-pub-1234567890123456"
ADSENSE_CLIENT_ID = os.environ.get('ADSENSE_CLIENT_ID', '')
# GA4 measurement id, e.g. "G-XXXXXXXXXX"
GA_MEASUREMENT_ID = os.environ.get('GA_MEASUREMENT_ID', '')
# Canonical public domain used for SEO tags (og:url, canonical link, sitemap)
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'toptop.az')
