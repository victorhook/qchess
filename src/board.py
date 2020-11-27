import threading

from piece import *
from player import Player
from chess_signal import Signal


EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROCK = 4
KING = 5
QUEEN = 6

WHITE = 0
BLACK = 1

PAWN = 1
KNIGHT = 3
BISHOP = 3.5
ROCK = 5
QUEEN = 8
KING = 99

W_PAWN = 1
W_KNIGHT = 3
W_BISHOP = 3.5
W_ROCK = 5
W_QUEEN = 8
W_KING = 99

B_PAWN = -1
B_KNIGHT = -3
B_BISHOP = -3.5
B_ROCK = -5
B_QUEEN = -8
B_KING = -99

PIECES = {
    EMPTY: ' ',
    W_PAWN: '\u2659',
    W_KNIGHT: '\u2658',
    W_BISHOP: '\u2657',
    W_ROCK: '\u2656',
    W_QUEEN: '\u2655',
    W_KING: '\u2654',
    B_PAWN: '\u265F',
    B_KNIGHT: '\u265E',
    B_BISHOP: '\u265D',
    B_ROCK: '\u265C',
    B_QUEEN: '\u265B',
    B_KING: '\u265A',
}

class ChessBoard:

    def __init__(self):
        self._board = [[EMPTY for i in range(8)] for i in range(8)]
        self.reset()

    def reset(self):
        # Pawns
        for i in range(8):
            self._board[1][i] = W_PAWN
            self._board[6][i] = B_PAWN

        # Rocks
        for row, col in [(0, 0), (0, 7)]:
            self._board[row][col] = W_ROCK
        for row, col in [(7, 0), (7, 7)]:
            self._board[row][col] = B_ROCK

        # Knights
        for row, col in [(0, 1), (0, 6)]:
            self._board[row][col] = W_KNIGHT
        for row, col in [(7, 1), (7, 6)]:
            self._board[row][col] = B_KNIGHT

        # Bishops
        for row, col in [(0, 2), (0, 5)]:
            self._board[row][col] = W_BISHOP
        for row, col in [(7, 2), (7, 5)]:
            self._board[row][col] = B_BISHOP

        # Queens
        self._board[0][3] = W_QUEEN
        self._board[7][3] = B_QUEEN

        # Kings
        self._board[0][4] = W_KING
        self._board[7][4] = B_KING

    def cell_empty(self, row, col):
        return self._board[row][col] == EMPTY

    def display(self):
        for row in self._board[::-1]:
            print('| ', end='')
            print(' | '.join([PIECES[cell] for cell in row]), end='')
            print(' |')

    def get(self, row, col):
        return self._board[row][col]

    def place(self, old, new):
        old_r, old_c = old
        new_r, new_c = new
        self._board[new_r][new_c] = self._board[old_r][old_c]

        piece = self._board[old_r][old_c]
        piece_t = abs(piece)

        # ! TODO: PAWN and KING first move
        if piece_t == PAWN:
            if new_r == 7 or new_r == 0:
                self._promote(new_r, new_c)
                # ! TODO: PROMOTE
                pass
        elif piece_t == King:
            pass

        self._board[old_r][old_c] = EMPTY

    def _promote(self, row, col):
        self._board[row][col] = QUEEN


class ChessEngine:

    def __init__(self, board=None, thread_flag=None):
        self._board = ChessBoard() if board is None else board
        self._pwhite = None
        self._pblack = None
        self._pturn = None
        self._next_move = None
        self._pflag = threading.Event()
        self._gflag = threading.Event() if thread_flag is None else thread_flag

        self._pwhite_score = 0
        self._pblack_score = 0

        self._board.display()

    def quit(self):
        self._gflag.set()

    def play_game(self, thread_flag=None):
        if thread_flag is not None:
            self._gflag = thread_flag

        self._board.reset()

        white = self._pwhite
        black = self._pblack
        self._pturn = self._pwhite

        # Main thread-flag
        self._gflag.set()

        while self._game_running() and self._gflag.is_set():

            valid_move = False
            while not valid_move and self._gflag.is_set():
                move = self._wait_for_player_move(self._pturn)
                move = self._parse_move(move)
                if self._valid_move(move, self._pturn.color):
                    valid_move = True
                else:
                    self._pturn.signal(Signal.INVALID_MOVE)

                if self._castling:
                    print('Castle')

            old, new = move
            self._update_score(new, self._pturn)

            self._board.place(old, new)
            self._board.display()
            self._pturn.signal(Signal.UPDATE)

            # Change turns
            #pturn = black if pturn.color == WHITE else white

    def _update_score(self, new, pturn):
        target = abs(self._board.get(*new))
        if target != EMPTY:
            if target == KING:
                self._gameover(pturn)
            else:
                if pturn == WHITE:
                    self._pwhite_score += abs(target)
                else:
                    self._pblack_score += abs(target)

    def get_player_score(self, player):
        if player == WHITE:
            return self._pwhite_score
        else:
            return self._pblack_score

    def get_player_turn(self):
        return self._pturn

    def _gameover(self, pturn):
        winner = pturn
        if winner == WHITE:
            looser = self._pblack
        else:
            looser = self._pwhite

        print('Gameover!')
        winner.signal(Signal.WIN)
        looser.signal(Signal.LOOSE)
        self._gflag.is_set().clear()

    def _game_running(self):
        return True

    def _valid_move(self, move, player_color):
        old, new = move
        old_r, old_c = old
        new_r, new_c = new

        # Out of bounds
        if new_r > 7 or new_r < 0 or new_c > 7 or new_c < 0 or old == new:
            return False

        piece = self._board.get(old_r, old_c)

        # Can't move opponents pieces
        if (piece < 0 and player_color == WHITE or
            piece > 0 and player_color == BLACK):
            return False

        # Difference in rows / cols
        dr = new_r - old_r
        dc = new_c - old_c

        target = self._board.get(new_r, new_c)

        # Can't place piece on same color
        if (piece > 0 and target > 0) or (piece < 0 and target < 0):
            return False

        t_piece = abs(piece)

        self._castling = False

        if t_piece == PAWN:
            # White pieces increase, black decrease
            forward = 1 if piece > 0 else -1

            # Check correct direction
            if (forward > 0 and dr < 0) or (forward < 0 and dr > 0):
                return False

            # Can't go sideways
            if abs(dc) > 0 and dr == 0:
                return False

            # If the pawn hasn't moved before, we can moove 2 spots.
            if old_r == 1 and piece > 0 or old_r == 6 and piece < 0:
                max_move = 2
            else:
                max_move = 1

            if dr > max_move:
                return False

            if dr == 2:
                if dc == 0 and not self._board.cell_empty(old_r+forward, old_c):
                    return False

            if target == EMPTY:
                if dc != 0:
                    return False
            else:
                if abs(dc) != 1:
                    return False

        elif t_piece == KNIGHT:
            dr = abs(dr)
            dc = abs(dc)
            if not ((dr == 1 and dc == 2) or (dr == 2 and dc == 1)):
                return False

        elif t_piece == BISHOP:
            if abs(dr) != abs(dc):
                return False

            sign_r = 1 if dr > 0 else -1
            sign_c = 1 if dc > 0 else -1

            for i in range(abs(dr)-1):
                r = old_r+sign_r + sign_r*i
                c = old_c+sign_c + sign_c*i
                if not self._board.cell_empty(r, c):
                    return False

        elif t_piece == ROCK:
            if dr != 0 and dc != 0:
                return False

            if dr > 0:
                sign = 1 if dr > 0 else -1
                for i in range(abs(dr)-1):
                    row = old_r+sign + i*sign
                    if not self._board.cell_empty(row, old_c):
                        return False
            else:
                sign = 1 if dc > 0 else -1
                for i in range(abs(dc)-1):
                    col = old_c+sign + i*sign
                    if not self._board.cell_empty(old_r, col):
                        return False

        elif t_piece == QUEEN:

            # Needs to be diagonal or straight line
            if abs(dr) != abs(dc) and dr != 0 and dc != 0:
                return False

            sign_r = 1 if dr > 0 else -1
            sign_c = 1 if dc > 0 else -1

            # Diagonality
            if abs(dr) == abs(dc):
                for i in range(abs(dr)-1):
                    row = old_r+sign_r + i*sign_r
                    col = old_c+sign_c + i*sign_c

                    # Something is in the way!
                    if not self._board.cell_empty(row, col):
                        return False

            elif dr == 0:
                for i in range(abs(dc)-1):
                    col = old_c+sign_c + i*sign_c
                    if not self._board.cell_empty(old_r, col):
                        return False
            elif dc == 0:
                for i in range(abs(dr)-1):
                    row = old_r+sign_r + i*sign_r
                    if not self._board.cell_empty(row, old_c):
                        return False

        elif t_piece == KING:

            if abs(dr) > 1 or abs(dc) > 1:
                return False

        else:
            return False

        return True

    def get_available_moves(self, cell):
        moves = []
        for row in range(8):
            for col in range(8):
                if self._valid_move((cell, (row, col)), WHITE):
                    moves.append((row, col))
        return moves

    def _wait_for_player_move(self, player):
        self._pflag.clear()
        player.signal(Signal.MAKE_MOVE, self._player_move)

        while not self._pflag.is_set():
            pass

        return self._next_move

    def _player_move(self, move):
        self._pflag.set()
        self._next_move = move

    def _parse_move(self, move):
        old, new = move

            # ( (ROW, COL), (ROW, COL) )
        if type(old[0]) == int:
            old = int(old[0]), int(old[1])
            new = int(new[0]), int(new[1])
        else:
            # ( E1, E2 )
            old = int(old[1])-1, ord(old[0].lower()) - ord('a')
            new = int(new[1])-1, ord(new[0].lower()) - ord('a')

        return (old, new)

    def set_white(self, player):
        self._pwhite = player

    def set_black(self, player):
        self._pblack = player

    def get(self, row, col):
        return self._board.get(row, col)

    def get_str(self, row, col):
        return PIECES[self._board.get(row, col)]

from player import GuiPlayer

if __name__ == "__main__":
    engine = ChessEngine()

    p1 = Player(WHITE)
    p2 = Player(BLACK)
    engine.set_white(p1)
    engine.set_black(p2)

    engine.play_game()
