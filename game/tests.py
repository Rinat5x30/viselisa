import json

import defusedxml.ElementTree as ET
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import seo
from .models import Player


class HangmanApiTests(APITestCase):
    def setUp(self):
        self.player = Player.objects.create(
            name='totti',
            age=49,
            position='Forward',
            number=10,
            first_club='AS Roma',
            current_club='Retired',
        )
        self.new_game_url = reverse('new-game')
        self.guess_url = reverse('guess-letter')
        self.random_url = reverse('random-player')

    def test_random_player_returns_player_payload(self):
        response = self.client.get(self.random_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.player.id)
        self.assertEqual(response.data['name'], 'totti')

    def test_new_game_initial_state(self):
        response = self.client.post(self.new_game_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ongoing')
        self.assertEqual(response.data['mistakes'], 0)
        self.assertEqual(response.data['max_mistakes'], 6)
        self.assertEqual(response.data['hints'], [])
        self.assertEqual(response.data['masked_word'], '_ _ _ _ _')

    def test_wrong_guess_opens_first_hint(self):
        self.client.post(self.new_game_url)
        response = self.client.post(self.guess_url, {'letter': 'z'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mistakes'], 1)
        self.assertEqual(len(response.data['hints']), 1)
        self.assertEqual(response.data['hints'][0]['label'], 'Yaş')

    def test_repeated_guess_is_ignored(self):
        self.client.post(self.new_game_url)
        self.client.post(self.guess_url, {'letter': 'z'}, format='json')
        response = self.client.post(self.guess_url, {'letter': 'z'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mistakes'], 1)
        self.assertTrue(response.data['repeated'])

    def test_non_latin_letter_returns_error(self):
        self.client.post(self.new_game_url)
        response = self.client.post(self.guess_url, {'letter': 'я'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('latın', response.data['detail'])

    def test_game_can_be_won(self):
        self.client.post(self.new_game_url)
        for letter in ['t', 'o', 'i']:
            self.client.post(self.guess_url, {'letter': letter}, format='json')
        response = self.client.post(self.guess_url, {'letter': 'p'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'won')
        self.assertEqual(response.data['word'], 'totti')

    def test_game_has_extra_chance_after_fifth_hint(self):
        self.client.post(self.new_game_url)
        response = None
        for letter in ['a', 'b', 'c', 'd', 'e']:
            response = self.client.post(self.guess_url, {'letter': letter}, format='json')

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ongoing')
        self.assertEqual(response.data['mistakes'], 5)
        self.assertEqual(len(response.data['hints']), 5)

    def test_game_can_be_lost(self):
        self.client.post(self.new_game_url)
        response = None
        for letter in ['a', 'b', 'c', 'd', 'e', 'f']:
            response = self.client.post(self.guess_url, {'letter': letter}, format='json')

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'lost')
        self.assertEqual(response.data['mistakes'], 6)
        self.assertEqual(len(response.data['hints']), 5)


@override_settings(SITE_DOMAIN='example.test')
class SeoTests(TestCase):
    def setUp(self):
        self.player = Player.objects.create(
            name='totti',
            age=49,
            position='Forward',
            number=10,
            first_club='AS Roma',
            current_club='Retired',
        )

    def test_robots_txt_disallows_api_and_admin(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        content = response.content.decode()
        self.assertIn('Disallow: /api/', content)
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Sitemap: https://example.test/sitemap.xml', content)

    def test_sitemap_xml_is_well_formed_and_has_four_urls(self):
        response = self.client.get('/sitemap.xml')

        self.assertEqual(response.status_code, 200)
        namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        root = ET.fromstring(response.content)
        urls = root.findall('sm:url', namespace)

        self.assertEqual(len(urls), 4)
        for url in urls:
            loc = url.find('sm:loc', namespace).text
            self.assertTrue(loc.startswith('https://example.test'))

    def test_home_page_has_canonical_and_json_ld(self):
        response = self.client.get('/')

        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'application/ld+json')
        graph = self._extract_json_ld(response.content.decode())['@graph']
        types = {item['@type'] for item in graph}
        self.assertEqual(types, {'WebSite', 'WebApplication'})

    def test_home_page_renders_faq_content(self):
        response = self.client.get('/')

        content = response.content.decode()
        for item in seo.FAQ_ITEMS:
            self.assertIn(str(item['question']), content)

    def test_players_page_lists_roster_grouped_by_position(self):
        response = self.client.get('/futbolcular/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.name)
        self.assertContains(response, 'application/ld+json')
        json_ld = self._extract_json_ld(response.content.decode())
        types = {item['@type'] for item in json_ld}
        self.assertEqual(types, {'ItemList', 'BreadcrumbList'})
        item_list = next(item for item in json_ld if item['@type'] == 'ItemList')
        self.assertEqual(item_list['numberOfItems'], 1)

    def test_privacy_and_terms_have_distinct_meta_descriptions(self):
        home = self._extract_meta_description(self.client.get('/').content.decode())
        privacy = self._extract_meta_description(self.client.get('/privacy/').content.decode())
        terms = self._extract_meta_description(self.client.get('/terms/').content.decode())

        self.assertNotEqual(home, privacy)
        self.assertNotEqual(home, terms)
        self.assertNotEqual(privacy, terms)

    @staticmethod
    def _extract_json_ld(html: str) -> dict:
        marker = 'application/ld+json'
        tag_start = html.index(marker)
        start = html.index('>', tag_start) + 1
        end = html.index('</script>', start)
        return json.loads(html[start:end])

    @staticmethod
    def _extract_meta_description(html: str) -> str:
        marker = '<meta name="description" content="'
        start = html.index(marker) + len(marker)
        end = html.index('"', start)
        return html[start:end]
