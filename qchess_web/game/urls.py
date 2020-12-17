from django.urls import path

from . import views

urlpatterns = [
    path('new_game/', views.new_game, name='new_game'),
    path('<int:game_id>/', views.game, name='game'),
    path('<int:game_id>/resign/', views.resign, name='resign'),
    path('<int:game_id>/promotion/', views.promotion, name='promotion'),
    path('<int:game_id>/get_board/', views.get_board, name='get_board'),
    path('<int:game_id>/make_move/', views.make_move, name='make_move'),
    path('<int:game_id>/get_moves/', views.get_moves, name='get_moves'),
    path('<int:game_id>/get_winner/', views.get_winner, name='get_winner'),
    path('<int:game_id>/get_status/', views.get_status, name='get_status'),
    path('<int:game_id>/get_move_history/', views.get_move_history,
         name='get_move_history'),
]
