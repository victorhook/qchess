from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from qchess_web import utils


import sys
ENGINE_PATH = '/home/victor/coding/projects/qchess/src'
sys.path.append(ENGINE_PATH)
from engine_loader import EngineLoader  # noqa



@utils.auth_active_game
def game(request, game_id):
    player = utils.get_player(request)
    color = utils.player_color(player, game_id)
    return render(request, 'game.html', {'color': color})


@utils.auth_active_game
def get_status(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    status = engine.get_status()
    status = {
        'is_checked': status[0],
        'is_check_mate': status[1],
        'is_draw': status[2],
        'enemy_resign': status[3],
        'player_color': status[4],
        'white_score': status[5],
        'black_score': status[6]
    }

    if status['is_check_mate'] or status['enemy_resign']:
        utils.game_over(game_id)

    return JsonResponse(status)


@utils.auth_active_game
def get_winner(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    color = engine.get_winner()
    winner = 'white' if color == utils.WHITE else 'black'
    return JsonResponse({'color': winner})

@utils.auth_active_game
def resign(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    resign_ok = engine.resign()
    return JsonResponse({'resign_ok': resign_ok})


@utils.auth_active_game
def get_move_history(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    history = [str(move) for move in engine.history]
    return JsonResponse({'moves': history})


@utils.auth_active_game
def get_moves(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    square = request.POST.get('square')
    moves = engine.get_available_moves(square)
    # Get the moveTo-squares from all of the moves.
    moves = [str(move)[2:] for move in moves]
    return JsonResponse({'moves': moves})


@utils.auth_active_game
def play_again(request, game_id):
    utils.game_over(game_id)
    pass
    """
    player = utils.get_player(request)
    if player_has_game(player, game_id):
        kill_engine(game_id)
        clear_active_game(game_id)
        return redirect('/game/new_game/')

    return redirect('/')
    """


@utils.auth_active_game
def get_board(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    board = engine.get_board_as_string()
    return JsonResponse({'board': board})


@utils.auth_active_game
def make_move(request, game_id):
    engine = EngineLoader.load_engine(game_id)
    move_from = request.POST.get('moveFrom')
    move_to = request.POST.get('moveTo')
    move_result = engine.make_move(move_from + ' ' + move_to)

    return JsonResponse({
        'isOk': move_result.is_ok,
        'capture': move_result.capture,
        'promotion': move_result.promotion})


@utils.auth_active_game
def promotion(request, game_id):
    engine = EngineLoader.load_engine(game_id)

    PIECE_TABLE = {
        'Bishop': 1,
        'Knight': 2,
        'Rock': 3,
        'Queen': 4
    }

    piece_type = request.POST.get('pieceType').title()
    promote_ok = engine.make_promotion(PIECE_TABLE[piece_type])
    return JsonResponse({'promoteOk': promote_ok})


@login_required
def new_game(request):
    player = utils.get_player(request)
    new_game = utils.create_new_game(player, white=True)
    utils.debug_to('Created new game with game_id: %s' % new_game.game_id)
    print('Created new game with game_id: %s' % new_game.game_id)

    return redirect('/game/%s' % new_game.game_id)
