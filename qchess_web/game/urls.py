from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.game, name='game'),
    path('test/', views.test, name='test'),
]
