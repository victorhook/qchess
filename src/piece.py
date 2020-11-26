PIECES_WORTH = {
    'Pawn': 1,
    'Bishop': 3,
    'Knight': 3,
    'Rock': 5,
    'Queen': 8,
    'King': 99
}

PIECES_STR = {
    'Pawn': 'P',
    'Bishop': 'B',
    'Knight': 'K',
    'Rock': 'R',
    'Queen': 'Q',
    'King': 'Z'
}



class Piece:

    def __init__(self, row, col, color, board):
        self._row = row
        self._col = col
        self.color = color
        self._board = board
        self._worth = PIECES_WORTH[self.__class__.__name__]
        self._name = PIECES_STR[self.__class__.__name__]


    def get_valid_moves(self):
        pass

    def valid_move(self, old, new):
        pass

    def __repr__(self):
        return self._name


class Pawn(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)
        self._has_moved = False

    def has_moved(self, moved=None):
        if moved is None:
            return self._has_moved
        self._has_moved = moved

class Bishop(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)

class Knight(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)

class Rock(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)

class Queen(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)

class King(Piece):

    def __init__(self, row, col, color, board):
        super().__init__(row, col, color, board)
        self._has_moved = False

    def has_moved(self, moved=None):
        if moved is None:
            return self._has_moved
        self._has_moved = moved
