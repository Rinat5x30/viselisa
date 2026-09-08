"""Game-engine logic for the hangman game.

Keeps views thin per project conventions — all hangman rules live here.
"""

from .models import Player

MAX_MISTAKES = 6
HINT_ORDER = ['age', 'position', 'number', 'first_club', 'current_club']
HINT_LABELS = {
    'age': 'Yaş',
    'position': 'Mövqe',
    'number': 'Nömrə',
    'first_club': 'İlk peşəkar klub',
    'current_club': 'Hazırkı klub',
}

# Order reflects on-pitch formation order (GK -> DEF -> MID -> FWD), used for the
# roster page. Values match Player.position exactly as stored (see players.json).
POSITION_LABELS = {
    'Goalkeeper': 'Qapıçılar',
    'Defender': 'Müdafiəçilər',
    'Midfielder': 'Yarımmüdafiəçilər',
    'Forward': 'Hücumçular',
}

SESSION_KEY = 'game_state'


def pick_random_player() -> Player | None:
    return Player.objects.order_by('?').first()


def get_players_grouped_by_position() -> list[dict]:
    """Roster grouped for the public players page, in formation order."""
    players_by_position = {}
    for player in Player.objects.order_by('name'):
        players_by_position.setdefault(player.position, []).append(player)

    return [
        {'label': label, 'players': players_by_position[position]}
        for position, label in POSITION_LABELS.items()
        if position in players_by_position
    ]


def build_game_state(player: Player) -> dict:
    return {
        'word': player.name.lower(),
        'display_name': player.display_name or player.name.title(),
        'player': {
            'age': player.age,
            'position': player.position,
            'number': player.number,
            'first_club': player.first_club,
            'current_club': player.current_club,
        },
        'guessed_letters': [],
        'wrong_letters': [],
        'mistakes': 0,
        'status': 'ongoing',
    }


def build_masked_word(word: str, guessed_letters: list[str]) -> str:
    guessed_set = set(guessed_letters)
    return ' '.join(letter if letter in guessed_set else '_' for letter in word)


def build_hints(state: dict) -> list[dict]:
    player = state['player']
    hints_to_show = min(state['mistakes'], len(HINT_ORDER))
    return [
        {'label': HINT_LABELS[key], 'value': str(player[key])}
        for key in HINT_ORDER[:hints_to_show]
    ]


def build_game_response(state: dict, repeated: bool = False) -> dict:
    return {
        'masked_word': build_masked_word(state['word'], state['guessed_letters']),
        'mistakes': state['mistakes'],
        'max_mistakes': MAX_MISTAKES,
        'guessed_letters': state['guessed_letters'],
        'wrong_letters': state['wrong_letters'],
        'hints': build_hints(state),
        'status': state['status'],
        'repeated': repeated,
        'word': state['word'] if state['status'] != 'ongoing' else None,
        'display_name': state['display_name'] if state['status'] != 'ongoing' else None,
    }


def apply_guess(state: dict, letter: str) -> dict:
    """Mutates state in place, returns it. Caller must persist to session."""
    if state['status'] != 'ongoing':
        return state

    if letter in state['guessed_letters'] or letter in state['wrong_letters']:
        return state

    if letter in state['word']:
        state['guessed_letters'].append(letter)
    else:
        state['wrong_letters'].append(letter)
        state['mistakes'] += 1

    unique_letters = set(state['word'])
    if unique_letters.issubset(set(state['guessed_letters'])):
        state['status'] = 'won'
    elif state['mistakes'] >= MAX_MISTAKES:
        state['status'] = 'lost'

    return state
