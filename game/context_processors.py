from django.conf import settings

from . import seo


def site_settings(request):
    """Expose third-party integration ids and canonical domain to every template."""
    return {
        'ADSENSE_CLIENT_ID': settings.ADSENSE_CLIENT_ID,
        'GA_MEASUREMENT_ID': settings.GA_MEASUREMENT_ID,
        'SITE_DOMAIN': settings.SITE_DOMAIN,
        'CANONICAL_URL': seo.canonical_url(request.path),
    }
