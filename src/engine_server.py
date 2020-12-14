import os
import socket
import struct
import sys
from threading import Thread, Event

sys.path.append('/home/victor/coding/projects/qchess/src')
import engine
import protocol


def debug_to(info, filepath='/home/victor/coding/projects/qchess/log/server.log'):
    with open(filepath, 'a') as f:
        f.write(info + ' \n')


class TCPServer:

    IP = ''
    PORT = os.getpid()
    #PORT = 9999

    def __init__(self):
        # Start chess engine
        self.engine = engine.Engine()
        self._sock = None
        self._flag = Event()
        debug_to('[%s] TCP Server started' % TCPServer.PORT)

    def run(self):
        # Start listening for connections
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((TCPServer.IP, TCPServer.PORT))
        self._sock.listen(0)

        # Start waiting for requests
        while not self._flag.is_set():
            client = self._sock.accept()[0]
            print('New request!')
            debug_to('[%s] New request' % TCPServer.PORT)
            self.RequestHandler(client, self.engine).start()

    def stop(self):
        self._flag.set()

    class RequestHandler(Thread):
        def __init__(self, sock, engine):
            super().__init__(daemon=True)
            self.sock = sock
            self.engine = engine

        def _read_packet(self):
            cmd = self.sock.recv(1)
            size = self.sock.recv(struct.calcsize('I'))
            size = struct.unpack('I', size)[0]

            if size > 0:
                data = self.sock.recv(size)
            else:
                data = None
            return self.Packet(cmd, data)

        def _get_moves(self, square):
            square = chr(square[0]) + chr(square[1])
            moves = self.engine.get_available_moves(square)
            return ' '.join([str(move)[2:] for move in moves])

        def run(self):
            packet = self._read_packet()
            print('PACKET -> %s, %s' % (packet.cmd, packet.data))

            if packet.cmd == protocol.Command.GET_AVAILABLE_MOVES:
                data = self._get_moves(packet.data)
                response = protocol.pkt_get_available_moves(data)

            elif packet.cmd == protocol.Command.MAKE_MOVE:
                move = packet.data.decode('utf-8')
                move_result = self.engine.make_move(move)
                response = protocol.rsp_pkt_move_result(move_result)

            elif packet.cmd == protocol.Command.GET_BOARD:
                board = self.engine.get_board_as_string()
                response = protocol.rsp_pkt_get_board(board)

            elif packet.cmd == protocol.Command.GET_STATUS:
                status = self.engine.get_status()
                response = protocol.rsp_pkt_get_status(status)

            elif packet.cmd == protocol.Command.GET_WINNER:
                winner = self.engine.get_winner()
                response = protocol.rsp_pkt_get_winner(winner)

            elif packet.cmd == protocol.Command.GET_MOVE_HISTORY:
                history = self.engine.get_move_history()
                print(history)
                response = protocol.rsp_pkt_get_move_history(history)

            elif packet.cmd == protocol.Command.PROMOTION:
                promote_ok = self.engine.make_promotion(ord(packet.data))
                response = protocol.rsp_pkt_promotion(promote_ok)

            elif packet.cmd == protocol.Command.RESIGN:
                resign_ok = self.engine.resign()
                response = protocol.rsp_pkt_resign(resign_ok)

            self.sock.send(response)

        def read_square(self):
            square = self.sock.recv(2)
            return chr(square[0]) + chr(square[1])

        class Packet:
            def __init__(self, cmd, data=None):
                self.cmd = ord(cmd)
                self.data = data






if __name__ == "__main__":
    server = TCPServer()
    server.run()
