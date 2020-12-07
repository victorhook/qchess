from django.shortcuts import render
from django.http import HttpResponse

import sys
ENGINE_PATH = '/home/victor/coding/projects/qchess/src'
sys.path.append(ENGINE_PATH)


from engine_wrapper import EngineWrapper


def game(request):
    return render(request, 'game.html')


def test(request):
    class Command:
        NEW_GAME = 1

    if request.method == 'POST':
        command = request.POST.get('command', None)

        if command == Command.NEW_GAME:
            engine = EngineWrapper()



    return HttpResponse({'ok': 'hehe'})
