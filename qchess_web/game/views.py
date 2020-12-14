from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from player.models import Player
from game.models import ActiveGame

from datetime import datetime

import sys
ENGINE_PATH = '/home/victor/coding/projects/qchess/src'
sys.path.append(ENGINE_PATH)
from engine_client import TCPClient


@login_required
def game(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        color = player_color(player, pid)
        return render(request, 'game.html', {'color': color})
    else:
        return redirect('/')

@login_required
def get_status(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        client = TCPClient(command=TCPClient.GET_STATUS, port=pid)
        status = client.send()
        status = {
            'is_checked': status[0],
            'is_check_mate': status[1],
            'is_draw': status[2],
            'enemy_resign': status[3],
            'player_color': status[4],
            'white_score': status[5],
            'black_score': status[6]
        }

        return JsonResponse(status)

@login_required
def get_winner(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        client = TCPClient(command=TCPClient.GET_WINNER, port=pid)
        winner = client.send()
        print('winner: %s' % winner)

        return JsonResponse({'color': winner})


@login_required
def resign(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        client = TCPClient(command=TCPClient.RESIGN, port=pid)
        resign_ok = client.send()

        return JsonResponse({'resign_ok': resign_ok})


@login_required
def get_move_history(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        client = TCPClient(command=TCPClient.GET_MOVE_HISTORY, port=pid)
        moves = client.send()

        return JsonResponse({'moves': moves})


@login_required
def get_moves(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        square = request.POST.get('square')
        client = TCPClient(command=TCPClient.GET_AVAILABLE_MOVES, port=pid,
                           payload=square)
        response = client.send()
        response = b'' if response is None else response

        return JsonResponse({'moves': response})

    return render(request, 'game.html', {'color': "white"})

@login_required
def play_again(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        kill_engine(pid)
        clear_active_game(pid)
        return redirect('/game/new_game/')

    return redirect('/')



@login_required
def get_board(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        client = TCPClient(command=TCPClient.GET_BOARD, port=pid)
        response = client.send()
        return JsonResponse({'board': response})


@login_required
def make_move(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        move_from = request.POST.get('moveFrom')
        move_to = request.POST.get('moveTo')
        move = '%s %s' % (move_from, move_to)
        client = TCPClient(command=TCPClient.MAKE_MOVE, port=pid,
                           payload=move)
        response = client.send()

        return JsonResponse({
            'isOk': response[0],
            'capture': response[1],
            'promotion': response[2]})

    return render(request, 'game.html', {'color': "white"})


@login_required
def promotion(request, pid):
    player = get_player(request)

    if player_has_game(player, pid):

        PIECE_TABLE = {
            'Bishop': 1,
            'Knight': 2,
            'Rock': 3,
            'Queen': 4
        }

        piece_type = request.POST.get('pieceType').title()
        client = TCPClient(command=TCPClient.PROMOTION, port=pid,
                           payload=PIECE_TABLE[piece_type])
        response = client.send()

        return JsonResponse({'promoteOk': response[0]})


@login_required
def new_game(request):
    class Command:
        NEW_GAME = '1'

    if request.method == 'POST':
        player = get_player(request)

        new_game = create_new_game(player, white=True)
        debug_to('Created new game with pid: %s' % new_game.pid)
        print('Created new game with pid: %s' % new_game.pid)

        return redirect('/game/%s' % new_game.pid)


def player_color(player, pid):
    try:
        game = ActiveGame.objects.get(pid=pid)
    except ActiveGame.DoesNotExist:
        print('Failed to find game with pid %s!' % pid)
        return None

    color = 'white' if game.white == player else 'black'
    return color


def get_player(request):
    player = Player.objects.get(user=request.user)
    return player


def player_has_game(player, pid):
    try:
        game = ActiveGame.objects.get(pid=pid)
    except ActiveGame.DoesNotExist:
        print('Failed to find game with pid %s!' % pid)
        return None
    return game.white == player or game.black == player


def create_new_game(player, white):
    game = ActiveGame()
    game.date_time = datetime.now()
    if white:
        game.white = player
    else:
        game.black = player
    game.pid = invoke_engine()
    game.save()
    player.active_game = game
    return game


def kill_engine(pid):
    import psutil
    try:
        psutil.Process(pid).terminate()
    except psutil.NoSuchProcess:
        pass


def invoke_engine():
    import subprocess
    import os

    PYTHON_PATH = '/home/victor/coding/projects/qchess/env/bin/python'
    SOURCE = '/home/victor/coding/projects/qchess/src'
    EXE = os.path.join(SOURCE, 'engine_server.py')

    proc = subprocess.Popen([PYTHON_PATH, EXE], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.pid


def debug_to(info, filepath='/home/victor/coding/projects/qchess/log/debug.log'):
    with open(filepath, 'a') as f:
        f.write(info + ' \n')
