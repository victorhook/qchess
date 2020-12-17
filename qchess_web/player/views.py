from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from qchess_web import utils


@login_required
def profile(request):
    player = utils.get_player(request)
    history = utils.get_player_history(player)
    active_games = utils.get_active_games(player)
    return render(request, 'profile.html', {'history': history,
                                            'active_games': active_games})
