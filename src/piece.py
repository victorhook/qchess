class PieceType:
    EMPTY = None
    Pawn = 0
    Bishop = 1
    Knight = 2
    Rock = 3
    Queen = 4
    King = 5


class Color:
    WHITE = 0
    BLACK = 1


WHITE_PIECES_STR = ['\u2659', '\u2657', '\u2658', '\u2656', '\u2655', '\u2654']
BLACK_PIECES_STR = ['\u265F', '\u265D', '\u265E', '\u265C', '\u265B', '\u265A']
WHITE_PIECES_ASCII = ['P', 'B', 'N', 'R', 'Q', 'K']
BLACK_PIECES_ASCII = ['p', 'b', 'n', 'r', 'q', 'k']

WHITE_PIECES_ASCII_TABLE = {
    'P': PieceType.Pawn,
    'B': PieceType.Bishop,
    'N': PieceType.Knight,
    'R': PieceType.Rock,
    'Q': PieceType.Queen,
    'K': PieceType.King
}

BLACK_PIECES_ASCII_TABLE = {
    'p': PieceType.Pawn,
    'b': PieceType.Bishop,
    'n': PieceType.Knight,
    'r': PieceType.Rock,
    'q': PieceType.Queen,
    'k': PieceType.King
}

PIECE_SCORE = {
    PieceType.Pawn: 1,
    PieceType.Bishop: 3.5,
    PieceType.Knight: 3,
    PieceType.Rock: 5,
    PieceType.Queen: 9,
}


class Piece:
    def __init__(self, PieceType, color):
        self.piece_type = PieceType
        self.color = color

    def ascii(self):
        if self.color == Color.WHITE:
            return WHITE_PIECES_ASCII[self.piece_type]
        return BLACK_PIECES_ASCII[self.piece_type]

    def symbol(self):
        if self.color == Color.WHITE:
            return WHITE_PIECES_STR[self.piece_type]
        return BLACK_PIECES_STR[self.piece_type]
