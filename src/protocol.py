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
    PROMOTION       -> Return promotion OK
    RESIGN              -> Return confirmation
"""


class Command:
    GET_AVAILABLE_MOVES = 10
    MAKE_MOVE = 11
    GET_BOARD = 12
    GET_STATUS = 13
    GET_WINNER = 14
    GET_MOVE_HISTORY = 15
    PROMOTION = 16
    RESIGN = 17


class Promotion:
    KNIGHT = 1
    BISHOP = 2
    ROCK = 3
    QUEEN = 4


def packet(cmd, payload=[]):

    size = 0
    for data in payload:
        if type(data) is float:
            size += 4
        else:
            size += 1

    pack = bytearray(1 + struct.calcsize('I') + size)
    struct.pack_into('B', pack, 0, cmd)
    struct.pack_into('I', pack, 1, size)

    i = 0
    for data in payload:
        data_type = type(data)
        fmt = 'B'

        if data_type is float:
            fmt = 'f'

        if data_type is str:
            data = ord(data)

        elif data_type is bool:
            data = 1 if data else 0

        struct.pack_into(fmt, pack, i+1+struct.calcsize('I'), data)

        if data_type is float:
            i += 4
        else:
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


def pkt_get_winner():
    return packet(Command.GET_WINNER)


def pkt_get_move_history():
    return packet(Command.GET_MOVE_HISTORY)


def pkt_promotion(promotion):
    return packet(Command.PROMOTION, promotion)


def pkt_resign():
    return packet(Command.RESIGN)


# --- Response packets for server --- #
def rsp_pkt_get_board(board):
    return packet(Command.GET_BOARD, board)


def rsp_pkt_move_result(move_result):
    return packet(Command.MAKE_MOVE, move_result.as_list())


def rsp_pkt_promotion(promote_ok):
    payload = [1] if promote_ok else [0]
    return packet(Command.PROMOTION, payload)


def rsp_pkt_get_status(status):
    return packet(Command.GET_STATUS, status)


def rsp_pkt_get_move_history(history):
    byte_history = bytearray()
    for move in history:
        byte_history.extend(move.as_bytes())
    return packet(Command.GET_MOVE_HISTORY, byte_history)


def rsp_pkt_get_winner(winner):
    winner = 0xff if winner is None else winner
    return packet(Command.GET_WINNER, [winner])


def rsp_pkt_resign(resign_ok):
    return packet(Command.RESIGN, [resign_ok])
