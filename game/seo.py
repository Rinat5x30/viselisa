"""SEO helpers: canonical URLs, structured data, robots.txt and sitemap.xml content.

Kept separate from views.py/context_processors.py so the same FAQ copy and the
same canonical-URL logic are never duplicated across templates and views.
"""

from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import Player

STATIC_URLS = [
    ('home', 'daily', '1.0'),
    ('players', 'weekly', '0.7'),
    ('privacy', 'yearly', '0.3'),
    ('terms', 'yearly', '0.3'),
]

FAQ_ITEMS = [
    {
        'question': _('toptop necə oynanılır?'),
        'answer': _(
            'Gizli söz məşhur bir futbolçunun soyadı və ya ləqəbidir. Hərfləri bir-bir '
            'təxmin edin: doğru hərf sözdə görünəcək, səhv hərf isə asma adam şəklini '
            'tamamlayacaq.'
        ),
    },
    {
        'question': _('Neçə səhv etmək olar?'),
        'answer': _(
            'Maksimum 6 səhv hərfə icazə verilir. Hər səhvdən sonra bir yeni ipucu '
            'açılır — yaş, mövqe, forma nömrəsi, ilk peşəkar klub, hazırkı klub.'
        ),
    },
    {
        'question': _('Qeydiyyat və ya ödəniş tələb olunurmu?'),
        'answer': _(
            'Xeyr. toptop tamamilə pulsuzdur və heç bir qeydiyyat tələb etmir — oyun '
            'vəziyyəti yalnız brauzerinizin sessiyasında saxlanılır.'
        ),
    },
    {
        'question': _('Futbolçu məlumatları nə qədər dəqiqdir?'),
        'answer': _(
            'Yaş və hazırkı klub kimi məlumatlar ictimai mənbələrə əsaslanır və vaxtaşırı '
            'yenilənir, lakin tam dəqiqliyə zəmanət vermirik.'
        ),
    },
    {
        'question': _('Neçə futbolçu arasından seçilir?'),
        'answer': _(
            'Yüzlərlə əfsanə və müasir ulduz futbolçu arasından təsadüfi seçim edilir, '
            'kolleksiya davamlı olaraq genişlənir.'
        ),
    },
]


def canonical_url(path: str) -> str:
    return f'https://{settings.SITE_DOMAIN}{path}'


def build_home_json_ld(request: HttpRequest) -> dict:
    home_url = canonical_url(reverse('home'))
    return {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'WebSite',
                '@id': f'{home_url}#website',
                'name': 'toptop',
                'url': home_url,
                'inLanguage': 'az',
            },
            {
                '@type': 'WebApplication',
                '@id': f'{home_url}#webapp',
                'name': 'toptop',
                'url': home_url,
                'applicationCategory': 'GameApplication',
                'operatingSystem': 'Any (web browser)',
                'isAccessibleForFree': True,
                'inLanguage': 'az',
            },
        ],
    }


def build_players_json_ld(request: HttpRequest) -> dict:
    players_url = canonical_url(reverse('players'))
    return {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        '@id': f'{players_url}#players',
        'name': 'toptop futbolçular kolleksiyası',
        'url': players_url,
        'numberOfItems': Player.objects.count(),
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': index,
                'item': {'@type': 'Person', 'name': player.name},
            }
            for index, player in enumerate(Player.objects.order_by('name'), start=1)
        ],
    }


def build_breadcrumb_json_ld(request: HttpRequest, page_name: str) -> dict:
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {
                '@type': 'ListItem',
                'position': 1,
                'name': str(_('Ana səhifə')),
                'item': canonical_url(reverse('home')),
            },
            {
                '@type': 'ListItem',
                'position': 2,
                'name': page_name,
                'item': canonical_url(request.path),
            },
        ],
    }


def robots_txt_content() -> str:
    sitemap_url = canonical_url(reverse('sitemap'))
    return (
        'User-agent: *\n'
        'Disallow: /api/\n'
        'Disallow: /admin/\n'
        'Allow: /\n'
        '\n'
        f'Sitemap: {sitemap_url}\n'
    )


def sitemap_xml_content() -> str:
    entries = []
    for url_name, changefreq, priority in STATIC_URLS:
        loc = escape(canonical_url(reverse(url_name)))
        entries.append(
            f'  <url>\n'
            f'    <loc>{loc}</loc>\n'
            f'    <changefreq>{changefreq}</changefreq>\n'
            f'    <priority>{priority}</priority>\n'
            f'  </url>'
        )
    body = '\n'.join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{body}\n'
        '</urlset>\n'
    )
