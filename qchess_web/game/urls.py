from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('<int:pid>/', views.game, name='game'),
    path('<int:pid>/promotion/', views.promotion, name='promotion'),
    path('<int:pid>/get_board/', views.get_board, name='get_board'),
    path('<int:pid>/make_move/', views.make_move, name='make_move'),
    path('<int:pid>/get_moves/', views.get_moves, name='get_moves'),
    path('<int:pid>/get_status/', views.get_status, name='get_status'),
    path('new_game/', views.new_game, name='new_game')
]
