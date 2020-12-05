class Move:
    number = 0

    def __init__(self, move_from, move_to, increment=False, capture=False,
                 promotion=None):
        if increment:
            Move.number += 1
        self.move_from = move_from
        self.move_to = move_to
        self.capture = capture
        self.promotion = promotion

    def prettify(self, square):
        return chr(square[1] + 65) + chr(square[0] + 48)

    def __repr__(self):
        return '%s -> %s' % (self.prettify(self.move_from),
                                  self.prettify(self.move_to))
