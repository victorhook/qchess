from datetime import datetime
from django.db.models import signals
from django.dispatch import receiver

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.utils import OperationalError

from player.models import Player
from game.models import ActiveGame, FinishedGame

import os
import sys
ENGINE_PATH = '/home/victor/coding/projects/qchess/src'
sys.path.append(ENGINE_PATH)
from engine_loader import EngineLoader  # noqa


WHITE = 0
BLACK = 1

GAME_RESULTS = {
    None: 'T',
    WHITE: 'W',
    BLACK: 'B'
}

GAME_MODES = {
    'N': 'Normal'
}

DATE_FMT = '%Y-%m-%d %H:%M:%S'


""" --- Decorators --- """


def auth_active_game(func):
    @login_required
    def wrapper(request, *args, **kwargs):
        game_id = kwargs.get('game_id', None)
        res = redirect('/')
        if game_id is not None:
            player = get_player(request)

            # Player does NOT have this game running. Eg, trying to access
            # someone else's game.
            if player is None:
                res = render(request, 'wrong_game.html')
            else:
                if player_has_game(player, game_id):
                    res = func(request, *args, **kwargs)
        return res

    return wrapper


def player_required(func):
    @login_required
    def wrapper(request, *args, **kwargs):

        from django.contrib import messages

        res = redirect('/')

        try:
            players = Player.objects.filter(user=request.user)

            if players:
                res = func(request, *args, **kwargs)
            else:
                messages.add_message(request, messages.INFO,
                                     'Failed to find player')
        except OperationalError:
            # No player found
            pass

        return res

    return wrapper


""" --- Signals --- """

"""
TODO: What to do here?
@receiver(signals.post_delete, sender=ActiveGame)
def signal_game_deletion(sender, *args, **kwargs):
    game = kwargs['instance']
    filepath = EngineLoader.get_filepath(game.game_id)
    try:
        os.remove(filepath)
    except Exception.FileNotFoundError:
        print('Failed to delete game from disk at %s' % filepath)
"""


def get_player(request):
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        player = None
    return player


def player_color(player, game_id):
    try:
        game = ActiveGame.objects.get(game_id=game_id)
    except ActiveGame.DoesNotExist:
        print('Failed to find game with game_id %s!' % game_id)
        return None

    color = 'white' if game.white == player else 'black'
    return color


def player_has_game(player, game_id):
    try:
        game = ActiveGame.objects.get(game_id=game_id)
    except ActiveGame.DoesNotExist:
        print('Failed to find game with game_id %s!' % game_id)
        return None
    return game.white == player or game.black == player


def create_new_game(player, white):
    game = ActiveGame()
    game.start = datetime.now()
    if white:
        game.white = player
    else:
        game.black = player

    engine = EngineLoader.new_game()
    game.game_id = engine.game_id
    game.save()
    return game


def game_over(game_id):
    engine = EngineLoader.load_engine(game_id)
    winner = engine.get_winner()

    game = ActiveGame.objects.get(game_id=game_id)

    finished = FinishedGame()
    finished.game = game
    finished.start = game.start
    finished.end = datetime.now()
    finished.result = GAME_RESULTS[winner]
    finished.save()
    # TODO: PGN File?


def dateify(date):
    return date.strftime(DATE_FMT)


def prettify(player, game):
    color = player_color(player, game.game_id)
    if game.result == 'T':
        game.result = 'Tie'
    elif ((game.result == 'W' and color == 'white') or
            (game.result == 'B' and color == 'black')):
        game.result = 'Win'
    else:
        game.result = 'Defeat'

    game.start = dateify(game.start)
    game.end = dateify(game.end)


def get_player_history(player):
    finished_games = FinishedGame.objects.all()
    history = list(filter(lambda g: (g.game.black == player or
                          g.game.white == player), finished_games))
    for game in history:
        prettify(player, game)

    return history


def get_active_games(player):
    blacks = list(ActiveGame.objects.filter(black=player))
    whites = list(ActiveGame.objects.filter(white=player))

    for game in blacks:
        game.start = dateify((game.start))
        game.mode = GAME_MODES.get(game.mode, '')
        game.color = 'Black'
        game.opponent = game.white

    for game in whites:
        game.start = dateify((game.start))
        game.mode = GAME_MODES.get(game.mode, '')
        game.color = 'White'
        game.opponent = game.black

    return whites + blacks


def debug_to(info, filepath='/home/victor/coding/projects/qchess/log/debug.log'):
    with open(filepath, 'a') as f:
        f.write(info + ' \n')
