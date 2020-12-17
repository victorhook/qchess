from django.db import models

DATE_FMT = '%Y-%m-%d %H:%M:%S'


class ActiveGame(models.Model):
    start = models.DateTimeField()
    game_id = models.IntegerField()
    mode = models.CharField(max_length=50, choices=[('N', 'Normal')])
    white = models.ForeignKey('player.Player', related_name='white',
                              on_delete=models.CASCADE, blank=True, null=True)
    black = models.ForeignKey('player.Player', related_name='black',
                              on_delete=models.CASCADE, blank=True, null=True)

    def __eq__(self, other):
        return self.game_id == other

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return str(self.game_id)


class FinishedGame(models.Model):
    game = models.ForeignKey(ActiveGame, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()
    result = models.CharField(max_length=50, choices=[('T', 'Tie'),
                                                      ('W', 'White win'),
                                                      ('B', 'Black win')])
    pgn_file = models.FileField(blank=True)

    def __str__(self):
        return '[%s]  Result: %s  Start: %s   End: %s  ' % (
                        self.game.game_id,
                        self.result,
                        self.start.strftime(DATE_FMT),
                        self.end.strftime(DATE_FMT),
                         )
