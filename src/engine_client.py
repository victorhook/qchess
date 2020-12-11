import socket
import struct

import protocol


IP = ''
PORT = 9999


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
    PROMOTION = protocol.Command.PROMOTION
    RESIGN = protocol.Command.RESIGN

    def __init__(self, command, payload=None):
        self.sock = None
        self.cmd = command
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
        self.sock.connect((IP, PORT))

        if self.cmd == protocol.Command.GET_AVAILABLE_MOVES:
            packet = protocol.pkt_get_available_moves(self.payload)

        elif self.cmd == protocol.Command.MAKE_MOVE:
            packet = protocol.pkt_make_move(self.payload)

        elif self.cmd == protocol.Command.GET_BOARD:
            packet = protocol.pkt_get_board()

        elif self.cmd == protocol.Command.GET_STATUS:
            packet = protocol.pkt_get_status()

        elif self.cmd == protocol.Command.PROMOTION:
            packet = protocol.pkt_PROMOTION([self.payload])

        elif self.cmd == protocol.Command.RESIGN:
            packet = protocol.pkt_resign()

        self.sock.send(packet)
        response = self._read_packet()

        if (self.cmd == protocol.Command.MAKE_MOVE or
           self.cmd == protocol.Command.PROMOTION):
            response = self._parse_booleans(response.data)
        else:
            response = response.data.decode('utf-8')

        return response

    def _parse_booleans(self, data):
        return list(map(lambda val: True if val == 1 else False, data))


if __name__ == "__main__":
    client = TCPClient(protocol.Command.MAKE_MOVE, 'a2 a3')
    response = client.send()
    print(response)
