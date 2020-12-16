import argparse
import random
import os
import sys
import dill

#from engine_cli import parse_args
from history import History
from move import Move
from piece import Piece, Color, PieceType,  PIECE_SCORE
from piece import WHITE_PIECES_ASCII_TABLE, BLACK_PIECES_ASCII_TABLE


SAVE_PATH = 'saved_games'
SAVE_NAME = '_game_'
DEFAULT_PATH = os.path.join(SAVE_PATH, SAVE_NAME + str(os.getpid()))


class MoveResult:

    def __init__(self, is_ok=False, capture=False, promotion=False):
        self.is_ok = is_ok
        self.capture = capture
        self.promotion = promotion

    def as_list(self):
        return list(map(lambda val: 1 if val else 0,
                        [self.is_ok, self.capture, self.promotion]))

    def __repr__(self):
        return 'OK: %s, Capture: %s, Promotion: %s' % (
            self.is_ok, self.capture, self.promotion
        )


class Square:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class Engine:

    def __init__(self, id=os.getpid(), cli_display=False):

        self.id = id
        self._out = sys.stdout

        self._pwhite = None
        self._pblack = None

        self._w_king_moved = False
        self._b_king_moved = False

        self._w_en_passant = False
        self._b_en_passant = False

        self._w_ressign = False
        self._b_ressign = False

        self._promotion_sq = None

        self.history = History()

        self._board = [[None for i in range(8)] for i in range(8)]
        self._init_pieces()
        self._current_color = Color.WHITE

        self._cli_display = cli_display
        if self._cli_display:
            self._display()

        self._ensure_savepath_exists()

    def _ensure_savepath_exists(self):
        if not os.path.exists(SAVE_PATH):
            print('Failed to find path for saving the game: "'
                  f'{SAVE_PATH}".\n'
                  'Please make sure it exists!')
            sys.exit(1)

    """ Class methods """
    @staticmethod
    def load(filepath=None):
        if filepath is None:
            filepath = DEFAULT_PATH
        try:
            with open(filepath, 'rb') as f:
                engine = dill.load(f)
        except FileNotFoundError:
            print('No previous active game found, starting new')
            engine = Engine()
        return engine

    """ Public """

    def save(self, filepath=None):
        if filepath is None:
            filepath = DEFAULT_PATH

        with open(filepath, 'wb') as f:
            dill.dump(self, f)

        """ Probably not even needed, we can simply dill obj.
        state = {
            '_b_king_moved': self._w_king_moved,
            '_w_king_moved': self._b_king_moved,
            '_w_en_passant': self._w_en_passant,
            '_b_en_passant': self._b_en_passant,
            '_w_ressign': self._w_ressign,
            '_b_ressign': self._b_ressign,
            '_promotion_sq': self._promotion_sq,
            '_board': self.get_board_as_string(),
            '_current_color': self._current_color,
            'history': str(self.history),
        }
        """

    def get_status(self):
        # |  is_checked  | is_check_mate | is_draw | enemy_resign |
        # |  white score |  black score  | player turn |
        return [
            self.is_check(),
            self.is_check_mate(),
            self.is_draw(),
            self.enemy_resign(),
            self.player_color(),
            self.get_score(Color.WHITE),
            self.get_score(Color.BLACK)
            ]

    def get_move_history(self):
        return self.history.get()

    def get_score(self, color):
        START_SCORE = 40            # Standard points
        not_capured = 0
        for row in range(8):
            for col in range(8):
                piece = self._get(row, col)
                if (piece != PieceType.EMPTY and
                   piece.piece_type != PieceType.King):
                    if piece.color != color:
                        not_capured += PIECE_SCORE[piece.piece_type]

        return START_SCORE - not_capured

    def get_str(self, row, col):
        piece = self._get(row, col)
        string = ' ' if piece is None else piece.symbol()
        return string

    def get_all_available_moves(self):
        start_squares = self._get_squares_of_color(self._current_color)
        moves = []
        for move_from in start_squares:
            moves.extend(self.get_available_moves(move_from))
        return moves

    def get_available_moves(self, move_from):
        square = self._parse_square(move_from)
        moves = []
        for row in range(8):
            for col in range(8):
                move_to = (row, col)
                move = Move(square, move_to)
                if self.valid_move(move):
                    moves.append(move)

        return moves

    def get_winner(self):
        color = self._current_color
        self._current_color = Color.WHITE
        white_moves = len(self.get_all_available_moves())
        self._current_color = Color.BLACK
        black_moves = len(self.get_all_available_moves())
        self._current_color = color

        if white_moves == 0:
            winner = Color.BLACK
        elif black_moves == 0:
            winner = Color.WHITE
        else:
            winner = None

        print(white_moves, black_moves, winner)

        return winner

    def player_color(self):
        return self._current_color

    def enemy_resign(self):
        if self._current_color == Color.BLACK:
            resign = self._w_ressign
        else:
            resign = self._b_ressign
        return resign

    def is_resigned(self):
        return self._w_ressign or self._b_ressign

    def resign(self):
        if self._current_color == Color.WHITE:
            self._w_ressign = True
        else:
            self._b_ressign = True
        return True

    def is_checked(self):
        king_square = self._find_king()
        if king_square is None:
            raise Exception('Failed to find king!!!')
        king_color = self._current_color

        check = self._under_attack(king_square, king_color)

        return check

    def is_check(self):
        check = self.is_checked()
        self.swap_color()
        check |= self.is_checked()
        self.swap_color()
        return check

    def is_draw(self):
        return self.is_stale_mate() or self.is_dead_pos()

    def is_stale_mate(self):
        return self.is_dead_pos()

    def is_dead_pos(self):
        """
        1. king against king;
        2. king against king and bishop;
        3. king against king and knight;
        4. king and bishop against king and bishop, with both bishops on
            squares of the same color (see King and two bishops).
        """
        return (self._king_against_king() or
                self._king_against_king_and_bishop() or
                self._king_against_king_and_knight() or
                self._king_and_bishop_against_king_and_bishop())

    def clear(self):
        """ Clears the entire chess board. """
        for row in range(8):
            for col in range(8):
                self._put(row, col, PieceType.EMPTY)

    def set_board_from_string(self, string):
        self.clear()
        row, col = 0, 0
        for char in string:

            WHITE_PIECES_ASCII = ['P', 'B', 'N', 'R', 'Q', 'K']
            BLACK_PIECES_ASCII = ['p', 'b', 'n', 'r', 'q', 'k']
            if char == '.' or char == ' ':
                piece = PieceType.EMPTY

            elif char > 'Z':
                # Black pieces
                piece_type = BLACK_PIECES_ASCII_TABLE[char]
                piece = Piece(piece_type, Color.BLACK)
            else:
                # White pieces
                piece_type = WHITE_PIECES_ASCII_TABLE[char]
                piece = Piece(piece_type, Color.WHITE)

            self._put(row, col, piece)

            if col == 7:
                row += 1
                col = 0
            else:
                col += 1

    def get_board_as_string(self):
        return self._stringify()

    def is_check_mate(self):
        """ Must be check and no positions for one of the opponents. """
        check = self.is_checked()
        self.swap_color()
        check |= self.is_checked()
        self.swap_color()
        return check and self._no_moves_available()

    def make_move(self, move):
        """ Tries to make the given move.
            move: ((row_from, col_to), (row_to, col_to))
            returns: A MoveResult, containing information if the move
            was valid, if it caused a promotion and if it was a capture.
        """
        self.get_move_history()

        result = MoveResult()

        if (self.is_check_mate() or self.is_draw() or self.is_resigned() or
           self.is_promotion()):
            result.is_ok = False
        else:
            move = self._parse_move(move)
            valid = self.valid_move(move)

            if valid:
                result.capture = self.place(move)
                if self._cli_display:
                    self._display()
                result.is_ok = True
            else:
                result.is_ok = False

        result.promotion = self.is_promotion()
        return result

    def is_promotion(self):
        return self._promotion_sq is not None

    def make_promotion(self, piece_type):
        if piece_type in [PieceType.Bishop, PieceType.Rock, PieceType.Knight,
                          PieceType.Queen]:
            piece = Piece(piece_type, self._current_color)
            row, col = self._promotion_sq
            self._put(row, col, piece)
            self._promotion_sq = None
            return True
        return False

    def place(self, move):
        from_r, from_c = move.move_from
        to_r, to_c = move.move_to

        if self._king_move(move) or self._rock_move(move):
            self._update_castle_rules(move)

        if self._en_passant_move(move):
            self._take_en_passant(move)
            capture = True
        else:
            capture = self._is_capture(move)

        if self._is_promotion_move(move):
            self._promotion_sq = move.move_to

        elif self._castle_move(move):
            self._move_rocks(move)

        piece = self._get(from_r, from_c)
        self._put(to_r, to_c, piece)
        self._put(from_r, from_c, PieceType.EMPTY)
        self.history.add(move)
        return capture

    def run(self):
        while True:
            move = input('Move: ')
            res = self.make_move(move)

    def valid_move(self, move):
        valid = self._valid_move(move)
        return valid and not self._causes_check(move)

    def swap_color(self):
        if self._current_color == Color.WHITE:
            self._current_color = Color.BLACK
        else:
            self._current_color = Color.WHITE

    """ Private """

    def _init_pieces(self):
        # 'RNBQKBNR'
        # 'rnbqkbnr'
        self._board[0][0] = Piece(PieceType.Rock, Color.WHITE)
        self._board[0][1] = Piece(PieceType.Knight, Color.WHITE)
        self._board[0][2] = Piece(PieceType.Bishop, Color.WHITE)
        self._board[0][3] = Piece(PieceType.Queen, Color.WHITE)
        self._board[0][4] = Piece(PieceType.King, Color.WHITE)
        self._board[0][5] = Piece(PieceType.Bishop, Color.WHITE)
        self._board[0][6] = Piece(PieceType.Knight, Color.WHITE)
        self._board[0][7] = Piece(PieceType.Rock, Color.WHITE)

        self._board[7][0] = Piece(PieceType.Rock, Color.BLACK)
        self._board[7][1] = Piece(PieceType.Knight, Color.BLACK)
        self._board[7][2] = Piece(PieceType.Bishop, Color.BLACK)
        self._board[7][3] = Piece(PieceType.Queen, Color.BLACK)
        self._board[7][4] = Piece(PieceType.King, Color.BLACK)
        self._board[7][5] = Piece(PieceType.Bishop, Color.BLACK)
        self._board[7][6] = Piece(PieceType.Knight, Color.BLACK)
        self._board[7][7] = Piece(PieceType.Rock, Color.BLACK)

        for i in range(8):
            self._board[1][i] = Piece(PieceType.Pawn, Color.WHITE)
            self._board[6][i] = Piece(PieceType.Pawn, Color.BLACK)

    def _display(self):
        print()
        for row in self._board[::-1]:
            print('|', end='')
            for sq in row:
                sq = ' ' if sq is None else sq.symbol()
                print(' %s |' % sq, end='')
            print()

    def _parse_square(self, square):
        if type(square) is str:
            square = square.upper()
            square = (ord(square[1]) - 49, ord(square[0]) - 65)
        return square

    def _is_promotion_move(self, move):
        row = move.move_to[0]
        return (self._type(move.move_from) == PieceType.Pawn and
                (row == 0 or row == 7))

    def _is_capture(self, move):
        return self._piece_at(move.move_to)

    def _causes_check(self, move):
        """ Checks if the given move causes check by playing it on the board.
            check if checked, and then undo-ing the move again. """

        if self._type(move.move_to) == PieceType.King:
            return False

        piece_from = self._get(move.move_from)
        piece_to = self._get(move.move_to)

        self._put(move.move_from, PieceType.EMPTY)      # Clear old
        self._put(move.move_to, piece_from)             # Put piece to new sq
        checked = self.is_checked()

        self._put(move.move_from, piece_from)           # Reset moves
        self._put(move.move_to, piece_to)
        return checked

    def _rock_move(self, move):
        return self._type(move.move_from) == PieceType.Rock

    def _king_move(self, move):
        return self._type(move.move_from) == PieceType.King

    def _update_castle_rules(self, move):
        if self._color(move.move_from) == Color.WHITE:
            self._w_king_moved = True
        else:
            self._b_king_moved = True

    def _move_rocks(self, move):
        row, col = move.move_to[0], move.move_to[1]
        if col == 6:
            old_c, new_c = 7, 5
        else:
            old_c, new_c = 0, 3

        rock = self._get(row, old_c)
        self._put(row, old_c, PieceType.EMPTY)
        self._put(row, new_c, rock)

    def _castle_move(self, move):
        if (self._type(move.move_from) == PieceType.King and
            abs(self._dr_dc(move.move_from, move.move_to)[1]) > 1):
            return True

    def _take_en_passant(self, move):
        color = self._color(move.move_from)
        col = move.move_to[1]
        if color == Color.WHITE:
            row = move.move_to[0]-1
        else:
            row = move.move_to[0]+1
        self._put(row, col, PieceType.EMPTY)

    def _en_passant_move(self, move):
        dr, dc = self._dr_dc(move.move_from, move.move_to)
        if (self._type(move.move_from) == PieceType.Pawn and
           self._type(move.move_to) == PieceType.EMPTY and
           abs(dr) == 1 and abs(dc) == 1):
            return True
        return False

    def _stringify(self):
        board = ''
        for row in range(8):
            for col in range(8):
                piece = self._get(row, col)
                if piece != PieceType.EMPTY:
                    symbol = piece.ascii()
                else:
                    symbol = '.'
                board += symbol
        return board

    def _same_color(self, sq1, sq2):
        r1, c1 = sq1
        r2, c2 = sq2

        # Black
        if ((r1 % 2 == 0 and c1 % 2 == 0) or
           (r1 % 2 != 0 and c1 % 2 != 0)):
            return ((r2 % 2 == 0 and c2 % 2 == 0) or
                    (r2 % 2 != 0 and c2 % 2 != 0))
        # White
        elif ((r1 % 2 == 0 and c1 % 2 != 0) or
              (r1 % 2 != 0 and c1 % 2 == 0)):
            return ((r2 % 2 == 0 and c2 % 2 != 0) or
                    (r2 % 2 != 0 and c2 % 2 == 0))

    def _king_and_bishop_against_king_and_bishop(self):
        string = self._stringify().replace('.', '')

        if (string.count('b') == 1 and string.count('B') == 1 and
           ('k' in string) and ('K' in string)):

            b1_r, b1_c = 0, 0
            found = False
            for row in range(8):
                for col in range(8):
                    piece = self._get(row, col)
                    if (piece != PieceType.EMPTY and
                       piece.piece_type == PieceType.Bishop):
                        if found:
                            if self._same_color((b1_r, b1_c), (row, col)):
                                return True
                            return False
                        else:
                            found = True
                            b1_r, b1_c = row, col
        return False

    def _king_against_king_and_knight(self):
        string = self._stringify().replace('.', '').lower()

        for char in 'rbqp':
            if char in string:
                return False

        if string.count('n') == 1 and string.count('k') == 2:
            return True

        return False

    def _king_against_king_and_bishop(self):
        string = self._stringify().replace('.', '').lower()

        for char in 'rnqp':
            if char in string:
                return False

        if string.count('b') == 1 and string.count('k') == 2:
            return True

        return False

    def _king_against_king(self):
        return self._stringify().lower().replace('.', '') == 'kk'

    def _no_moves_available(self):
        m1 = self.get_all_available_moves()
        self.swap_color()
        m2 = self.get_all_available_moves()
        self.swap_color()
        return len(m1) == 0 or len(m2) == 0

    def _valid_move(self, move):
        color = self._current_color

        # Ensure square is not empty and that we're not trying to move
        # the opponents pieces.
        if (not self._piece_at(move.move_from) or
           self._color(move.move_from) != color):
            return False

        # Can't place out of bounds
        if self._out_of_bounds(move.move_from):
            return False

        piece_type = self._type(move.move_from)

        if piece_type == PieceType.Pawn:
            return self._valid_pawn(move, color)
        elif piece_type == PieceType.Knight:
            return self._valid_knight(move, color)
        elif piece_type == PieceType.Bishop:
            return self._valid_bishop(move, color)
        elif piece_type == PieceType.Rock:
            return self._valid_rock(move, color)
        elif piece_type == PieceType.Queen:
            return self._valid_queen(move, color)
        elif piece_type == PieceType.King:
            return self._valid_king(move, color)

    def _get_attackers(self, square, color):
        attackers = []
        self.swap_color()

        for row in range(8):
            for col in range(8):
                piece = self._get(row, col)
                if piece != PieceType.EMPTY and piece.color != color:
                    from_square = (row, col)
                    if self.valid_move(Move(from_square, square)):
                        attackers.append(from_square)

        self.swap_color()
        return attackers

    def _under_attack(self, square, color):
        return len(self._get_attackers(square, color)) > 0

    def _get_squares_of_color(self, color):
        squares = []
        for row in range(8):
            for col in range(8):
                if self._color((row, col)) == color:
                    squares.append((row, col))

        return squares

    def _find_king(self):
        for row in range(8):
            for col in range(8):
                square = (row, col)
                if (self._type(square) == PieceType.King
                   and self._color(square) == self._current_color):
                    return square
        return None

    def _pawn_max_moves(self, sq, color):
        row = sq[0]
        max_moves = 1
        if ((row == 1 and color == Color.WHITE) or
           (row == 6 and color == Color.BLACK)):
            max_moves = 2
        return max_moves

    def _valid_pawn(self, move, color):
        max_moves = self._pawn_max_moves(move.move_from, color)
        dr, dc = self._dr_dc(move.move_from, move.move_to)

        direction = 1 if self._color(move.move_from) == Color.WHITE else -1

        if ((abs(dr) > max_moves) or                # Max moves
           (abs(dc) > 1) or                         # Sideways cant be > 1
           (abs(dc) == 1 and dr == 0) or            # Cant move only sideways
           (self._color(move.move_to) == color)):   # Moving to same color
            return False

        if max_moves == 2 and direction*abs(dr) == dr and abs(dr) == 2:
            if (dc != 0 or
                self._in_the_way(move.move_from, move.move_to) or
                self._piece_at(move.move_to)):
                return False

        if abs(dr) == 1:
            if dc == 0:
                if self._piece_at(move.move_to) or direction != dr:
                    return False
            elif abs(dc) == 1:
                if direction*abs(dr) != dr:
                    return False
                if self._can_en_passant(move, color):
                    return True
                elif not self._piece_at(move.move_to):
                    return False

        return True

    def _valid_knight(self, move, color):
        if self._color(move.move_to) == color:       # Same color
            return False

        dr, dc = self._dr_dc(move.move_from, move.move_to)
        if ((abs(dr) == 2 and abs(dc) == 1) or
           (abs(dr) == 1 and abs(dc) == 2)):
            return True

        return False

    def _valid_bishop(self, move, color):
        dr, dc = self._dr_dc(move.move_from, move.move_to)

        if (abs(dr) != abs(dc) or       # Need to move only diagonally
           self._in_the_way(move.move_from, move.move_to) or
           self._color(move.move_to) == color):
            return False

        return True

    def _valid_rock(self, move, color):
        dr, dc = self._dr_dc(move.move_from, move.move_to)

        if ((dr != 0 and dc != 0) or
           self._color(move.move_to) == color or
           self._in_the_way(move.move_from, move.move_to)):
            return False

        return True

    def _valid_queen(self, move, color):
        dr, dc = self._dr_dc(move.move_from, move.move_to)
        if (self._color(move.move_to) == color or
           self._in_the_way(move.move_from, move.move_to)):
            return False

        diagonal = abs(dr) == abs(dc)
        straight = (dr != 0 and dc == 0) or (dr == 0 and dc != 0)

        return diagonal or straight

    def _valid_king(self, move, color):
        dr, dc = self._dr_dc(move.move_from, move.move_to)

        if dr == 0 and abs(dc) > 1:
            # Check for possible castle
            if self._can_castle(move, color):
                return True
            else:
                return False

        if ((abs(dc) > 1 or abs(dr) > 1) or
           self._color(move.move_to) == color):
            return False

        return True

    def _can_castle(self, move, color):
        col = move.move_to[1]
        row = move.move_to[0]

        if (self._under_attack(move.move_from, color) or
            self._piece_at(move.move_to)):
            return False

        if col != 2 and col != 6:
            return False

        if self._in_the_way(move.move_from, move.move_to):
            return False

        if col == 2:
            if self._piece_at(row, 1):      # Knight in the way
                return False
            sq1, sq2 = (row, 2), (row, 3)
        else:
            sq1, sq2 = (row, 5), (row, 6)

        if (self._under_attack(sq1, self._current_color) or
           self._under_attack(sq2, self._current_color)):
            return False

        if color == Color.WHITE:
            if self._w_king_moved:
                return False
        elif color == Color.BLACK:
            if self._b_king_moved:
                return False

        return True

    def _dr_dc(self, sq1, sq2):
        old_r, old_c = sq1
        new_r, new_c = sq2
        return new_r - old_r, new_c - old_c

    def _in_the_way(self, sq1, sq2):
        dr, dc = self._dr_dc(sq1, sq2)
        r, c = sq1
        if dc == 0:
            sign = 1 if dr > 0 else -1
            for i in range(abs(dr)-1):
                if self._piece_at(r+sign + sign*i, c):
                    return True
        elif dr == 0:
            sign = 1 if dc > 0 else -1
            for i in range(abs(dc)-1):
                if self._piece_at(r, c+sign + sign*i):
                    return True

        if abs(dr) == abs(dc):
            sign_r = 1 if dr > 0 else -1
            sign_c = 1 if dc > 0 else -1
            for i in range(abs(dr)-1):
                if self._piece_at(r+sign_r + sign_r*i, c+sign_c + sign_c*i):
                    return True

        return False

    def _out_of_bounds(self, sq):
        r, c = sq
        return r < 0 or r > 7 or c < 0 or c > 7

    def _can_en_passant(self, move, color):
        last = self.history.peek()
        if last is None:
            return False

        row = last.move_to[0]

        old_dr, _ = self._dr_dc(last.move_from, last.move_to)

        if (self._type(last.move_to) != PieceType.Pawn or
           (row != 4 and row != 3) or
           abs(old_dr) != 2):
            return False

        to_c, to_r = move.move_to[1], move.move_to[0]
        last_c, last_r = last.move_to[1], last.move_to[0]

        if to_c == last_c:
            if color == Color.WHITE:
                if last_r+1 == to_r:
                    return True
            else:
                if last_r-1 == to_r:
                    return True

        return False

    def _parse_move(self, move):
        move_t = type(move)
        if move_t is str:
            move = move.upper().split(' ')
            from_c = ord(move[0][0])-65
            from_r = ord(move[0][1])-49
            to_c = ord(move[1][0])-65
            to_r = ord(move[1][1])-49
            move = Move((from_r, from_c), (to_r, to_c))
        elif move_t is tuple:
            move = Move(move[0], move[1])

        return move

    def _get(self, row, *col):
        if type(row) is tuple:
            row, col = row[0], row[1]
        else:
            col = col[0]
        return self._board[row][col]

    def _put(self, row, col, *piece):
        if type(row) is tuple:
            piece = col
            row, col = row[0], row[1]
        else:
            piece = piece[0]
        self._board[row][col] = piece

    def _piece_at(self, sq, *sq2):
        if sq2:
            sq = (sq, sq2[0])
        return self._get(sq[0], sq[1]) != PieceType.EMPTY

    def _type(self, piece):
        if type(piece) is tuple:
            piece = self._get(piece[0], piece[1])
        if piece is None:
            piece_type = PieceType.EMPTY
        else:
            piece_type = piece.piece_type
        return piece_type

    def _color(self, piece):
        if type(piece) is tuple:
            piece = self._get(piece[0], piece[1])
        if piece is None:
            return -1

        return Color.WHITE if piece.color == Color.WHITE else Color.BLACK

    def do_random_move(self):
        moves = self.get_all_available_moves()
        if moves:
            move = random.choice(moves)
            self.make_move(move)
        else:
            pass


if __name__ == "__main__":
    engine = Engine.load('saved_games/dev')
