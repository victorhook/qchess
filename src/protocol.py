"""
    ---- REQUEST FORMATS  ----
        Types:
            1. MAKE_MOVE
            2. STATUS

        1. MAKE_MOVE
        BYTE |   1    |   2   |   3   |   4   |   5   |
        DATA |   1    | [a-h] | [1-8] | [a-h] | [1-8] |

        2. ASK_FOR_DRAW
        BYTE |   1    |  2-5  |
        DATA |   2    |  0000 |

        3. RESSIGN
        BYTE |   1    |  2-5  |
        DATA |   3    |  0000 |

        4. STATUS
        BYTE |   1    |  2-5  |
        DATA |   4    |  0000 |

    ---- REPLY FORMATS ----
    BYTE |       0      |
    DATA |      5/6     |

    BYTE |       1      |       2       |       3       |      4        |
    DATA |  valid_move  |   is_checked  | is_check_mate |   is_draw     |

    BYTE |       5        |       6       |    7-10       |      10-13   |
    DATA |  enemy_ressign |  player_turn  |  white_score  |  black_score |

    BYTE |                          14-77                                |
    DATA |                       chess board                             |


            # |  is_checked  | is_check_mate | is_draw | enemy_resign |
        #

"""
import struct


REQUEST_PACKET_SIZE = 5
REPLY_PACKET_SIZE = 79

"""
    GET_AVAILABLE_MOVES -> Return list of moves
    MAKE_MOVE           -> Return if move is OK
    GET_BOARD           -> Return current board
    GET_STATUS          -> Return list of status flags
    PROMOTE_PIECE       -> Return promotion OK
    RESIGN              -> Return confirmation
"""


class Command:
    GET_AVAILABLE_MOVES = 10
    MAKE_MOVE = 11
    GET_BOARD = 12
    GET_STATUS = 13
    PROMOTE_PIECE = 14
    RESIGN = 15


class Promotion:
    KNIGHT = 1
    BISHOP = 2
    ROCK = 3
    QUEEN = 4


def packet(cmd, payload=[]):
    size = len(payload) if payload else 0
    pack = bytearray(1 + struct.calcsize('I') + size)
    struct.pack_into('B', pack, 0, cmd)
    struct.pack_into('I', pack, 1, size)

    i = 0
    for data in payload:
        data_type = type(data)
        fmt = 'B'
        if data_type is str:
            data = ord(data)
        elif data_type is float:
            fmt = 'f'
            i += 3

        struct.pack_into(fmt, pack, i+1+struct.calcsize('I'), data)
        i += 1

    return pack


def pkt_get_available_moves(square):
    return packet(Command.GET_AVAILABLE_MOVES, square)


def pkt_make_move(move):
    return packet(Command.MAKE_MOVE, move)


def pkt_get_status():
    return packet(Command.GET_STATUS)


def pkt_get_board():
    return packet(Command.GET_BOARD)


def pkt_promote_piece(promotion):
    return packet(Command.GET_BOARD, promotion)


def pkt_resign():
    return packet(Command.RESIGN)


# --- Response packets for server --- #
def rsp_pkt_get_board(board):
    return packet(Command.GET_BOARD, board)


def rsp_pkt_move_result(move_result):
    return packet(Command.GET_BOARD, move_result.as_list())
