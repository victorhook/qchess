import threading

from piece import *
from player import Player


EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROCK = 4
KING = 5
QUEEN = 6

WHITE = 0
BLACK = 1


class ChessBoard:

    def __init__(self):
        self._board = [[EMPTY for i in range(8)] for i in range(8)]
        self.reset()

    def reset(self):
        # Pawns
        for i in range(8):
            self._board[1][i] = Pawn(1, i, WHITE, self)
            self._board[6][i] = Pawn(6, i, BLACK, self)

        # Rocks
        for row, col in [(0, 0), (0, 7)]:
            self._board[row][col] = Rock(row, col, WHITE, self)
        for row, col in [(7, 0), (7, 7)]:
            self._board[row][col] = Rock(row, col, BLACK, self)

        # Knights
        for row, col in [(0, 1), (0, 6)]:
            self._board[row][col] = Knight(row, col, WHITE, self)
        for row, col in [(7, 1), (7, 6)]:
            self._board[row][col] = Knight(row, col, BLACK, self)

        # Bishops
        for row, col in [(0, 2), (0, 5)]:
            self._board[row][col] = Bishop(row, col, WHITE, self)
        for row, col in [(7, 2), (7, 5)]:
            self._board[row][col] = Bishop(row, col, BLACK, self)

        # Queens
        self._board[0][3] = Queen(0, 3, WHITE, self)
        self._board[7][3] = Queen(7, 3, BLACK, self)

        # Kings
        self._board[0][4] = King(0, 4, WHITE, self)
        self._board[7][4] = King(7, 4, BLACK, self)


    def display(self):
        for row in self._board[::-1]:
            print(' '.join(['%s' % cell for cell in row]))

    def get(self, row, col):
        return self._board[row][col]

    def place(self, old, new):
        old_r, old_c = old
        new_r, new_c = new
        self._board[new_r][new_c] = self._board[old_r][old_c]

        piece = self._board[old_r][old_c]
        piece_t = type(piece)
        if piece_t == Pawn:
            piece.has_moved(True)
            if new_r == 7 or new_r == 0:
                self._promote(new_r, new_c, piece.color)
        if piece_t == King:
            piece.has_moved(True)

        self._board[old_r][old_c] = EMPTY

    def _promote(self, row, col, color):
        self._board[row][col] = Queen(row, col, color, self)


class ChessEngine:

    def __init__(self, board):
        self._board = board
        self._pwhite = None
        self._pblack = None
        self._next_move = None
        self._pflag = threading.Event()
        self._gflag = threading.Event()


    def play_game(self):
        self._board.reset()

        white = self._pwhite
        black = self._pblack
        pturn = self._pwhite

        # Main thread-flag
        self._gflag.set()

        while self._game_running() and self._gflag.is_set():

            valid_move = False
            while not valid_move and self._gflag.is_set():
                move = self._wait_for_player_move(pturn)
                move = self._parse_move(move)
                if self._valid_move(move, pturn.color):
                    print('Valied move')
                    valid_move = True
                print('Not valid move!')

            old, new = move
            print('Move: %s -> %s' % (old, new))
            self._board.place(old, new)
            self._board.display()


    def _game_running(self):
        return True

    def _valid_move(self, move, player_color):
        old, new = move
        old_r, old_c = old
        new_r, new_c = new

        if new_r > 7 or new_r < 0 or new_c > 7 or new_c < 0 or old == new:
            print('[1]')
            return False

        piece = self._board.get(old_r, old_c)
        if piece == EMPTY or piece.color != player_color:
            print('[2]')
            return

        dr = new_r - old_r
        dc = new_c - old_c

        target = self._board.get(new_r, new_c)

        if target != EMPTY and target.color == piece.color:
            print('[3] %s, %s' % (target, target.color))
            return False

        t_piece = type(piece)

        if piece != EMPTY:
            print('old_r %s, old_r %s, new_r %s, new_c %s, dr %s, dc %s, piece %s, t_piece %s, target %s, color: %s'
                  % (old_r, old_c, new_r, new_c, dr, dc, piece, t_piece, target, piece.color))

        if t_piece == Pawn:
            forward = 1 if piece.color == WHITE else -1
            # Check correct direction
            if (forward > 0 and dr < 0) or (forward < 0 and dr > 0):
                print('here %s' % forward)
                return False

            max_move = 1 if piece.has_moved() else 2
            if dr > max_move:
                print('here2')
                return False

            if target == EMPTY:
                if dc != 0:
                    print('here3')
                    return False
            else:
                if dc != 1 and dc != -1:
                    print('here4')
                    return False


        elif t_piece == Knight:
            dr = abs(dr)
            dc = abs(dc)
            if not ((dr == 1 and dc == 2) or (dr == 2 and dc == 1)):
                return False

        elif t_piece == Bishop:
            pass
        elif t_piece == Rock:
            pass
        elif t_piece == Queen:
            pass
        elif t_piece == King:
            pass

        else:
            return False

        return True

    def _wait_for_player_move(self, player):
        self._pflag.clear()
        player.make_move(self._player_callback)

        while not self._pflag.is_set():
            pass

        return self._next_move

    def _player_callback(self, move):
        self._pflag.set()
        self._next_move = move

    def _parse_move(self, move):
        old, new = move
        old = int(old[1]), ord(old[0].lower()) - ord('a')
        new = int(new[1]), ord(new[0].lower()) - ord('a')
        return (old, new)

    def set_white(self, player):
        self._pwhite = player

    def set_black(self, player):
        self._pblack = player


if __name__ == "__main__":
    board = ChessBoard()
    engine = ChessEngine(board)
    board.display()

    p1 = Player(WHITE)
    p2 = Player(BLACK)
    engine.set_white(p1)
    engine.set_black(p2)


    engine.play_game()
