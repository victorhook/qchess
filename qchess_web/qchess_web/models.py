from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    date = models.DateTimeFieldField()
    opponent = models.OneToOneField(User, on_dlete=models.CASCADE)
    result = models.TextField()     # WIN / LOOOSE / DRAW
    points = models.IntegerField()
    pgn_file = models.FileField(blank=True)

class History(models.Model):
    games = models.ForeignKey(Game, blank=True)

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    history = models.OneToOneField(History, on_delete=models.CASCADE)
