from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('<int:pid>/', views.game, name='game'),
    path('<int:pid>/moves/', views.moves, name='moves'),
    path('new_game/', views.new_game, name='new_game')
]
