from django.db import models


class GameMode(models.Model):
    MODES = [
        ('N', 'Normal')
    ]


class ActiveGame(models.Model):
    date_time = models.DateTimeField()
    pid = models.IntegerField()
    mode = models.CharField(max_length=50, choices=[('N', 'Normal')])
    white = models.ForeignKey('player.Player', related_name='white',
                              on_delete=models.CASCADE, blank=True, null=True)
    black = models.ForeignKey('player.Player', related_name='black',
                              on_delete=models.CASCADE, blank=True, null=True)

    def __eq__(self, other):
        return self.pid == other


class FinishedGame(models.Model):
    game = models.ForeignKey(ActiveGame, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    result = models.TextField()     # WIN / LOOOSE / DRAW
    pgn_file = models.FileField(blank=True)


class History(models.Model):
    games = models.ForeignKey(FinishedGame, on_delete=models.CASCADE,
                              blank=True)
