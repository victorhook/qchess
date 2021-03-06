import os
import sys
import unittest

ABS_PATH = '/home/victor/coding/projects/chess/src'
BASE = os.path.dirname(os.path.dirname(__file__))
SOURCE_PATH = os.path.join(BASE, 'src')


class TestEngine(unittest.TestCase):

    def setUp(self):
        sys.path.extend([SOURCE_PATH, ABS_PATH])
        from engine import Engine
        self.engine = Engine()

    def test_pawn(self):
        self.assertTrue(self.engine.make_move('a2 a3').is_ok)     # Single step
        self.assertFalse(self.engine.make_move('a3 b3').is_ok)    # Sideways
        self.assertTrue(self.engine.make_move('b2 b4').is_ok)     # Two steps
        self.assertFalse(self.engine.make_move('c2 c5').is_ok)    # Three step
        self.assertFalse(self.engine.make_move('d2 e3').is_ok)    # Diagonal

        # Capture
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('e7 e5').is_ok)
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('d2 d4').is_ok)
        self.assertTrue(self.engine.make_move('d4 e5').is_ok)

        # En passant
        self.assertTrue(self.engine.make_move('h2 h4').is_ok)
        self.assertTrue(self.engine.make_move('h4 h5').is_ok)
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('g7 g5').is_ok)
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('h5 g6').is_ok)

    def test_bishop(self):
        self.assertTrue(self.engine.make_move('d2 d4').is_ok)
        self.assertTrue(self.engine.make_move('c1 f4').is_ok)

        # Put pawn in the way
        self.assertTrue(self.engine.make_move('e2 e4').is_ok)
        self.assertTrue(self.engine.make_move('e4 e5').is_ok)
        self.assertFalse(self.engine.make_move('f4 d6').is_ok)

        # Capture
        self.assertTrue(self.engine.make_move('e5 e6').is_ok)
        self.assertTrue(self.engine.make_move('f4 c7').is_ok)

        # Can't place on own pieces
        self.assertTrue(self.engine.make_move('c7 g3').is_ok)
        self.assertFalse(self.engine.make_move('g3 f2').is_ok)

    def test_knight(self):
        self.assertTrue(self.engine.make_move('b1 c3').is_ok)
        self.assertTrue(self.engine.make_move('c3 e4').is_ok)

        # Can't place on own pieces
        self.assertFalse(self.engine.make_move('e4 f2').is_ok)

        # Test check
        self.assertTrue(self.engine.make_move('e4 d6').is_ok)
        self.assert_check()

        # Capture
        self.assertTrue(self.engine.make_move('d6 c8').is_ok)

    def test_rock(self):
        self.assertTrue(self.engine.make_move('a2 a4').is_ok)
        self.assertTrue(self.engine.make_move('a1 a3').is_ok)
        self.assertTrue(self.engine.make_move('a3 c3').is_ok)

        # Can't place on own pieces
        self.assertFalse(self.engine.make_move('c3 c2').is_ok)

        self.assertTrue(self.engine.make_move('c3 c7').is_ok)
        self.assertTrue(self.engine.make_move('c7 d7').is_ok)
        self.assertTrue(self.engine.make_move('d7 e7').is_ok)

        # Test check
        self.assert_check()

    def test_queen(self):
        self.assertTrue(self.engine.make_move('d2 d4').is_ok)

        # Can't place on own pieces
        self.assertFalse(self.engine.make_move('d1 c1').is_ok)

        # Pieces in the way
        self.assertFalse(self.engine.make_move('d1 d5').is_ok)
        self.assertFalse(self.engine.make_move('d1 h4').is_ok)
        self.assertTrue(self.engine.make_move('d1 d3').is_ok)

        # Test check
        self.assertTrue(self.engine.make_move('d3 f5').is_ok)
        self.assertTrue(self.engine.make_move('f5 d7').is_ok)
        self.assert_check()

    def test_king(self):
        self.assertTrue(self.engine.make_move('e2 e4').is_ok)
        self.assertTrue(self.engine.make_move('e1 e2').is_ok)
        self.assertTrue(self.engine.make_move('e2 d3').is_ok)
        self.assertTrue(self.engine.make_move('d3 e2').is_ok)
        self.assertTrue(self.engine.make_move('e2 e1').is_ok)
        self.assertFalse(self.engine.make_move('e1 d1').is_ok)

        # Move pieces to prepare for castle, should fail because
        # king has already moved.
        self.assertTrue(self.engine.make_move('g2 g3').is_ok)
        self.assertTrue(self.engine.make_move('f1 h3').is_ok)
        self.assertTrue(self.engine.make_move('g1 f3').is_ok)

        self.assertFalse(self.engine.make_move('e1 g1').is_ok)

    def test_castle_right(self):
        self.assertTrue(self.engine.make_move('g2 g3').is_ok)
        self.assertTrue(self.engine.make_move('f1 h3').is_ok)
        self.assertTrue(self.engine.make_move('g1 f3').is_ok)
        self.assertTrue(self.engine.make_move('e1 g1').is_ok)

    def test_castle_left(self):
        self.assertTrue(self.engine.make_move('b2 b4').is_ok)
        self.assertTrue(self.engine.make_move('c2 c4').is_ok)
        self.assertTrue(self.engine.make_move('c1 a3').is_ok)
        self.assertTrue(self.engine.make_move('b1 c3').is_ok)
        self.assertTrue(self.engine.make_move('d1 c2').is_ok)
        self.assertTrue(self.engine.make_move('e1 c1').is_ok)

    def test_castle_under_check(self):
        self.assertTrue(self.engine.make_move('g2 g3').is_ok)
        self.assertTrue(self.engine.make_move('f1 h3').is_ok)
        self.assertTrue(self.engine.make_move('g1 f3').is_ok)

        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('g8 h6').is_ok)
        self.assertTrue(self.engine.make_move('h6 g4').is_ok)
        self.assertTrue(self.engine.make_move('g4 h2').is_ok)
        self.engine.swap_color()

        # Knight holds check on f1, castle should not be possible to castle
        self.assertFalse(self.engine.make_move('e1 g1').is_ok)

        # Move knight to check the king
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('h2 f3').is_ok)
        self.engine.swap_color()

        # Can't castle under check
        self.assertFalse(self.engine.make_move('e1 g1').is_ok)

        # Move the knight away form any checking
        self.engine.swap_color()
        self.assertTrue(self.engine.make_move('f3 g5').is_ok)
        self.engine.swap_color()

        # Knight has moved, should be able to castle
        self.assertTrue(self.engine.make_move('e1 g1').is_ok)

    def test_check_mate(self):
        self.assertTrue(self.engine.make_move('e2 e4').is_ok)
        self.assertTrue(self.engine.make_move('f1 c4').is_ok)
        self.assertTrue(self.engine.make_move('d1 f3').is_ok)
        self.assertFalse(self.engine.is_check_mate())
        self.assertTrue(self.engine.make_move('f3 f7').is_ok)
        self.assertTrue(self.engine.is_check_mate())

    def test_dead_position(self):
        # All should be false in beginning
        self.assertFalse(self.engine.is_dead_pos())

        # King against king
        self.engine.set_board_from_string('kk')
        self.assertTrue(self.engine.is_dead_pos())
        self.engine.set_board_from_string('kkbpp')
        self.assertFalse(self.engine.is_dead_pos())

        # King against king and bishop
        self.engine.set_board_from_string('kkb')
        self.assertTrue(self.engine.is_dead_pos())

        self.engine.set_board_from_string('kkBB')
        self.assertFalse(self.engine.is_dead_pos())

        # King against king and knight
        self.engine.set_board_from_string('kkn')
        self.assertTrue(self.engine.is_dead_pos())

        # King against king and bishop vs king against king and bishop.
        # They bishops must be on same colors.
        self.engine.set_board_from_string('kKb B')
        self.assertTrue(self.engine.is_dead_pos())

        self.engine.set_board_from_string('kKb......B')
        self.assertTrue(self.engine.is_dead_pos())

    """ Helper method """
    def assert_check(self):
        self.engine.swap_color()
        self.assertTrue(self.engine.is_checked())
        self.engine.swap_color()


if __name__ == "__main__":
    unittest.main()
