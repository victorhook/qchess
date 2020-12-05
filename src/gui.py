import tkinter as tk
import threading

from engine import Engine


WHITE = 0
BLACK = 1

FONT = ("Times New Roman",  25)
LABEL_STYLE = {
    'bg': 'white',
    'relief': 'ridge',
    'height': 2,
    'width': 15
}

BEIGE = "#E9C998"
BROWN = "#9C4921"


class MainWindow(tk.Tk):

    def __init__(self, engine, player=None):
        tk.Tk.__init__(self)
        self.title('Chess')
        self.configure(background='white')

        self._engine = engine
        self._player = player

        self.info_frame = InfoFrame(self, engine)
        self.chess_frame = ChessFrame(self, engine, self.info_frame, player)

        self.chess_frame.pack(side='left')
        self.info_frame.pack(side='right')

        self._engine_thread_flag = threading.Event()
        #self._game_thread = threading.Thread(target=engine.play_game,
        #                                     daemon=True)
        #self._game_thread.start()

    def quit(self):
        self._engine.quit()
        self.root.destroy()


class InfoFrame(tk.Frame):

    def __init__(self, root, engine):
        tk.Frame.__init__(self, master=root, relief='ridge', bd=2, bg='white')

        self._engine = engine

        turn = tk.Label(self, text='Player turn: ', font=FONT, **LABEL_STYLE)
        w_score = tk.Label(self, text="White score: ", font=FONT, **LABEL_STYLE)
        b_score = tk.Label(self, text="Black score: ", font=FONT, **LABEL_STYLE)
        check = tk.Label(self, text="Check: ", font=FONT, **LABEL_STYLE)
        mate = tk.Label(self, text="Check mate: ", font=FONT, **LABEL_STYLE)

        self.turn = tk.Label(self, text="", font=FONT, **LABEL_STYLE)
        self.w_score = tk.Label(self, text="0", font=FONT, **LABEL_STYLE)
        self.b_score = tk.Label(self, text="0", font=FONT, **LABEL_STYLE)
        self.check = tk.Label(self, text="", font=FONT, **LABEL_STYLE)
        self.mate = tk.Label(self, text="", font=FONT, **LABEL_STYLE)

        turn.grid(row=0, column=0)
        w_score.grid(row=1, column=0)
        b_score.grid(row=2, column=0)
        check.grid(row=3, column=0)
        mate.grid(row=3, column=0)

        self.turn.grid(row=0, column=1)
        self.w_score.grid(row=1, column=1)
        self.b_score.grid(row=2, column=1)
        self.check.grid(row=3, column=1)
        self.mate.grid(row=3, column=1)

        automove = tk.Label(self, text='Automove: ', font=FONT, **LABEL_STYLE)
        self.automove = tk.Label(self, text='', font=FONT, **LABEL_STYLE)
        self.toggle_auto = tk.Button(self, text='Toggle', command=self._toggle_auto)

        self.toggle_color = tk.Button(self, text='Swap color', command=self._toggle_color)

        automove.grid(row=4, column=0)
        self.automove.grid(row=4, column=1)
        self.toggle_auto.grid(row=5, column=0, columnspan=2)
        self.toggle_color.grid(row=6, column=0, columnspan=2)

        self._automove = True

        self.update_ui()

    def _toggle_auto(self):
        self._automove = not self._automove
        self.update_ui()

    def _toggle_color(self):
        self._engine.swap_color()
        self.update_ui()

    def update_ui(self):
        status = self._engine.get_status()
        # Check mate | Check | White score | Black score | Player turn |
        turn = 'White' if status[4] == 0 else 'Black'
        self.turn.config(text=turn)
        self.w_score.config(text='%.2f' % status[3])
        self.b_score.config(text='%.2f' % status[2])
        self.check.config(text=str(status[1]))
        self.mate.config(text=str(status[0]))
        self.automove.config(text=str(self._automove))


class ChessFrame(tk.Frame):

    def __init__(self, root, engine, info_frame, player):
        tk.Frame.__init__(self, relief='ridge', bd=2, bg='white')
        self._info_frame = info_frame

        self._board = [[0 for i in range(8)] for i in range(8)]
        for row in range(8):
            for col in range(8):

                if ((row % 2 == 0) and (col % 2 != 0) or
                    (row % 2 != 0) and (col % 2 == 0)):
                    color = BEIGE
                else:
                    color = BROWN

                cell = self.Cell(self, row, col, color,
                                 text=engine.get_str(row, col))
                self._board[row][col] = cell
                cell.grid(row=7-row, column=col+1, ipady=5, ipadx=5)

        for i in reversed(range(1, 9)):

            border_numb = tk.Label(self, text=i, font=FONT, width=3, height=2,
                                   relief='ridge', bd=2, bg='brown')
            border_char = tk.Label(self, text=chr(i+64), font=FONT, width=5,
                                   height=1, relief='ridge', bd=2, bg='brown')
            border_numb.grid(row=i-1, column=0, ipady=5, ipadx=5)
            border_char.grid(row=8, column=i, ipady=5, ipadx=5)

        self._mark = None
        self._engine = engine
        self._player = player
        self._moves = []

    def _place(self, move_from, move_to):
        result = self._engine.make_move((move_from, move_to))
        if result:
            self._info_frame.update_ui()
            self._update_ui()
            if self._info_frame._automove:
                self._engine.swap_color()
                self._engine.do_random_move()
                self._engine.swap_color()
                self._info_frame.update_ui()
                self._update_ui()

    def select(self, row, col):
        for move in self._moves:
            self._unmark(move.move_to)

        if self._mark is not None:
            self._unmark(self._mark)
            #self._player.queue_move(self._mark, (row, col), self._update_ui)
            self._place(self._mark, (row, col))
            self._mark = None
        else:
            self._mark = (row, col)
            self._setmark(self._mark)
            self._moves = self._engine.get_available_moves(self._mark)
            for move in self._moves:
                row, col = move.move_to
                self._board[row][col].higlight()

    def _update_ui(self):
        self._info_frame.update()
        for row in range(8):
            for col in range(8):
                self._board[row][col].config(
                    text=self._engine.get_str(row, col))

    def _setmark(self, mark):
        row, col = self._mark
        self._board[row][col].mark()

    def _unmark(self, mark):
        row, col = mark
        self._board[row][col].un_mark()

    def deselect(self, ignore):
        if self._mark is not None:
            self._unmark(self._mark)
        self._mark = None


    class Cell(tk.Label):

        def __init__(self, parent, row, col, color, **kwargs):
            tk.Label.__init__(self, master=parent, width=5, height=2,
                              font=("Times New Roman", 25),
                              relief='ridge', bd=2, bg=color, **kwargs)
            self._color = color
            self._row = row
            self._col = col
            self.bind('<Button-1>',
                      lambda *args: parent.select(self._row, self._col))
            self.bind('<Button-3>', parent.deselect)

        def higlight(self):
            self.config(bg='#d3d3d3')

        def mark(self):
            self.config(bg='green')

        def un_mark(self):
            self.config(bg=self._color)




if __name__ == "__main__":
    engine = Engine()
    main = MainWindow(engine)
    main.geometry('+1800+200')
    main.mainloop()
