from chess_signal import Signal

import threading


class Player:

    def __init__(self, color=None):
        self._score = 0
        self.color = color

    def signal(self, action, callback=None):
        if action == Signal.MAKE_MOVE:
            self._make_move(callback)
        elif action == Signal.INVALID_MOVE:
            self._invalid_move()
        elif action == Signal.UPDATE:
            self._update()
        elif action == Signal.WIN:
            self._win()
        elif action == Signal.LOOSE:
            self._loose()

    def _win(self):
        pass

    def _loose(self):
        pass

    def _invalid_move(sefl):
        print('Invalid move')

    def _update(self):
        pass

    def _make_move(self, move_ready):
        move = input('>>> Move: ')
        move = move.split(' ')
        move_ready(move)


class PlayerSocket(Player):

    def __init__(self, con, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.con = con


class GuiPlayer(Player):

    def __init__(self, ui, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flag = threading.Event()
        self._next_move = None
        self._ui_callback = None

    def queue_move(self, old_sq, new_sq, *ui_callback):
        self._next_move = (old_sq, new_sq)
        self._flag.set()
        if ui_callback:
            self._ui_callback = ui_callback[0]

    # Override
    def _update(self):
        if self._ui_callback is not None:
            self._ui_callback()

    # Override
    def _make_move(self, callback):
        print('Waiting for move...')
        self._flag.clear()
        while not self._flag.is_set():
            pass

        callback(self._next_move)
        self._next_move = None

    def _win():
        pass

    def _loose():
        pass
