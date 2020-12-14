class History:
    def __init__(self):
        self.moves = []
        self._wking_has_moved = False
        self._bking_has_moved = False

    def add(self, move):
        self.moves.append(move)

    def peek(self):
        if self.moves:
            return self.moves[len(self.moves)-1]
        return None

    def get(self):
        return self.moves

    def get_recent(self):
        if self.moves:
            return self.moves[len(self.moves)-1]

    def __iter__(self):
        return iter(self.moves)

    def __repr__(self):
        return ', '.join([str(move) for move in self.moves])

