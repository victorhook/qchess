from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_game = models.ManyToManyField('game.ActiveGame', blank=True)
    history = models.OneToOneField('game.History', on_delete=models.CASCADE,
                                   null=True, blank=True)

    def __str__(self):
        return self.user.username
