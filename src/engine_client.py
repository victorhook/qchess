import socket
import struct

import protocol


IP = ''
DEBUG_PORT = 9999


"""
    GET_AVAILABLE_MOVES -> Return list of moves
    MAKE_MOVE           -> Return if move is OK
    GET_BOARD           -> Return current board
    GET_STATUS          -> Return list of status flags
    PROMOTION           -> Return promotion OK
    RESIGN              -> Return confirmation
"""


class TCPClient:

    GET_AVAILABLE_MOVES = protocol.Command.GET_AVAILABLE_MOVES
    MAKE_MOVE = protocol.Command.MAKE_MOVE
    GET_BOARD = protocol.Command.GET_BOARD
    GET_STATUS = protocol.Command.GET_STATUS
    GET_WINNER = protocol.Command.GET_WINNER
    GET_MOVE_HISTORY = protocol.Command.GET_MOVE_HISTORY
    PROMOTION = protocol.Command.PROMOTION
    RESIGN = protocol.Command.RESIGN

    def __init__(self, command, port=DEBUG_PORT, payload=None):
        self.sock = None
        self.cmd = command
        self.port = port
        self.payload = payload

    class Packet:
        def __init__(self, cmd, data=None):
            self.cmd = ord(cmd)
            self.data = data

    def _read_packet(self):
        cmd = self.sock.recv(1)
        size = self.sock.recv(struct.calcsize('I'))
        size = struct.unpack('I', size)[0]

        if size > 0:
            data = self.sock.recv(size)
        else:
            data = None
        return self.Packet(cmd, data)

    def send(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((IP, self.port))

        if self.cmd == protocol.Command.GET_AVAILABLE_MOVES:
            packet = protocol.pkt_get_available_moves(self.payload)

        elif self.cmd == protocol.Command.GET_BOARD:
            packet = protocol.pkt_get_board()

        elif self.cmd == protocol.Command.GET_STATUS:
            packet = protocol.pkt_get_status()

        elif self.cmd == protocol.Command.GET_WINNER:
            packet = protocol.pkt_get_winner()

        elif self.cmd == protocol.Command.GET_MOVE_HISTORY:
            packet = protocol.pkt_get_move_history()

        elif self.cmd == protocol.Command.MAKE_MOVE:
            packet = protocol.pkt_make_move(self.payload)

        elif self.cmd == protocol.Command.PROMOTION:
            packet = protocol.pkt_promotion([self.payload])

        elif self.cmd == protocol.Command.RESIGN:
            packet = protocol.pkt_resign()

        self.sock.send(packet)
        response = self._read_packet()
        response = self._decode_response(response)

        return response

    def _decode_response(self, response):
        if (self.cmd == protocol.Command.MAKE_MOVE or
           self.cmd == protocol.Command.PROMOTION):
            response = self._parse_booleans(response.data)
        elif self.cmd == protocol.Command.GET_STATUS:
            # Unfortunately, there seems to a bug with the struct package
            # so I have to do this hard-coded solution.
            rsp = [flag for flag in response.data[:5]]
            w_score = struct.unpack('f', response.data[5:9])[0]
            b_score = struct.unpack('f', response.data[9:])[0]
            rsp.extend([w_score, b_score])
            response = rsp
        elif self.cmd == protocol.Command.GET_WINNER:
            winner = ord(response.data)
            if winner == 0xff:
                response = None
            else:
                response = 'white' if winner == 0 else 'black'
        elif self.cmd == protocol.Command.RESIGN:
            response = ord(response.data) == 1
        elif self.cmd == protocol.Command.GET_MOVE_HISTORY:
            response = self._parse_move_history(response)
        else:
            response = response.data.decode('utf-8')

        return response

    def _parse_move_history(self, response):
        try:
            response = response.data.decode('utf-8')
            moves = []
            for i in range(0, len(response), 4):
                move = response[i:i+4]
                moves.append(move)
            response = moves
            print('Moves: %s' % moves)

        except AttributeError as e:
            print(e)
            response = None     # Response is empty.

        return response

    def _parse_booleans(self, data):
        return list(map(lambda val: True if val == 1 else False, data))


if __name__ == "__main__":
    client = TCPClient(protocol.Command.GET_WINNER)
    response = client.send()
    print(response)
