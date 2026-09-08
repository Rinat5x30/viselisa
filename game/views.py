import json
import re

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import seo, services
from .serializers import GuessRequestSerializer, PlayerSerializer

LATIN_LETTER_REGEX = re.compile(r'^[a-z]$')

NO_PLAYERS_MESSAGE = 'Oyunçu tapılmadı.'
NO_GAME_MESSAGE = 'Oyun başlamayıb. "Yeni oyun" düyməsini basın.'
INVALID_LETTER_MESSAGE = 'Bir latın hərfi daxil edin (a-z).'


def home_view(request):
    context = {
        'faq_items': seo.FAQ_ITEMS,
        'structured_data': json.dumps(seo.build_home_json_ld(request), ensure_ascii=False),
    }
    return render(request, 'index.html', context)


def players_view(request):
    context = {
        'position_groups': services.get_players_grouped_by_position(),
        'structured_data': json.dumps(seo.build_players_json_ld(request), ensure_ascii=False),
    }
    return render(request, 'players.html', context)


def privacy_view(request):
    context = {
        'structured_data': json.dumps(
            seo.build_breadcrumb_json_ld(request, _('Məxfilik siyasəti')), ensure_ascii=False
        ),
    }
    return render(request, 'privacy.html', context)


def terms_view(request):
    context = {
        'structured_data': json.dumps(
            seo.build_breadcrumb_json_ld(request, _('İstifadə şərtləri')), ensure_ascii=False
        ),
    }
    return render(request, 'terms.html', context)


def robots_view(request):
    return HttpResponse(seo.robots_txt_content(), content_type='text/plain')


def sitemap_view(request):
    return HttpResponse(seo.sitemap_xml_content(), content_type='application/xml')


class RandomPlayerView(APIView):
    def get(self, request):
        player = services.pick_random_player()
        if not player:
            return Response({'detail': NO_PLAYERS_MESSAGE}, status=status.HTTP_404_NOT_FOUND)
        return Response(PlayerSerializer(player).data)


class NewGameView(APIView):
    def post(self, request):
        player = services.pick_random_player()
        if not player:
            return Response({'detail': NO_PLAYERS_MESSAGE}, status=status.HTTP_404_NOT_FOUND)

        state = services.build_game_state(player)
        request.session[services.SESSION_KEY] = state
        return Response(services.build_game_response(state))


class GuessLetterView(APIView):
    def post(self, request):
        serializer = GuessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        state = request.session.get(services.SESSION_KEY)
        if not state:
            return Response({'detail': NO_GAME_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        letter = serializer.validated_data['letter'].lower().strip()
        if not LATIN_LETTER_REGEX.match(letter):
            return Response({'detail': INVALID_LETTER_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        repeated = state['status'] == 'ongoing' and (
            letter in state['guessed_letters'] or letter in state['wrong_letters']
        )
        services.apply_guess(state, letter)
        request.session[services.SESSION_KEY] = state

        return Response(services.build_game_response(state, repeated=repeated))
