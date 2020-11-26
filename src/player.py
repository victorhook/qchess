class Player:

    def __init__(self, color=None):
        self._score = 0
        self.color = color

    def make_move(self, move_ready):

        # A2 - A3
        move = input('>>> Move: ')
        move = move.split(' ')
        move_ready(move)
