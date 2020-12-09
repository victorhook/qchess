from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from datetime import datetime

from player.models import Player
from game.models import ActiveGame


import sys
ENGINE_PATH = '/home/victor/coding/projects/qchess/src'
sys.path.append(ENGINE_PATH)
from engine_server import TCPServer


@login_required
def game(request, pid):
    player = get_player(request)
    if player_has_game(player, pid):
        color = player_color(player, pid)
        return render(request, 'game.html', {'color': color})
    else:
        return redirect('/')


def moves(request, pid):
    print(pid)
    return render(request, 'game.html', {'color': "white"})


@login_required
def new_game(request):
    class Command:
        NEW_GAME = '1'

    if request.method == 'POST':
        player = get_player(request)

            #new_game = create_new_game(player, white=True)
            #print('Created new game with pid: %s' % new_game.pid)

        return redirect("/game/9999")
        #return render(request, 'game.html', response)


def player_color(player, pid):
    games = player.active_game.all()
    for game in games.all():
        if game.pid == pid:
            if game.white == player:
                return "white"
            else:
                return "black"


def get_player(request):
    player = Player.objects.get(user=request.user)
    return player


def player_has_game(player, pid):
    games = player.active_game
    if games:
        for game in games.all():
            if game.pid == pid:
                return True
    return False


def create_new_game(player, white):
    game = ActiveGame()
    game.date_time = datetime.now()
    if white:
        game.white = player
    else:
        game.black = player
    game.pid = invoke_engine()
    return game


def invoke_engine():
    import subprocess
    import os

    PYTHON_PATH = '/home/victor/coding/projects/qchess/env/bin/python'
    SOURCE = '/home/victor/coding/projects/qchess/src'
    EXE = os.path.join(SOURCE, 'engine_server.py')

    proc = subprocess.Popen([PYTHON_PATH, EXE], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #return proc.pid
    return 9999