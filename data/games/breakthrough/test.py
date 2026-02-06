"""Tests for Breakthrough game implementation."""
import unittest
import random
import copy
from golden import *


class TestBreakthrough(unittest.TestCase):

    def test_initial_state(self):
        """Verify the game starts correctly."""
        state = get_initial_state()
        self.assertFalse(state["terminal"])
        self.assertEqual(get_current_player(state), 0)  # White moves first
        self.assertEqual(get_rewards(state), [0.0, 0.0])

        # Check initial piece positions
        board = state["board"]
        # White on rows 0-1
        for r in range(2):
            for c in range(8):
                self.assertEqual(board[r][c], WHITE)
        # Black on rows 6-7
        for r in range(6, 8):
            for c in range(8):
                self.assertEqual(board[r][c], BLACK)
        # Middle rows empty
        for r in range(2, 6):
            for c in range(8):
                self.assertEqual(board[r][c], EMPTY)

    def test_no_chance_outcomes(self):
        """Breakthrough is deterministic - same action yields same result."""
        state = get_initial_state()
        action = get_legal_actions(state)[0]

        state1 = copy.deepcopy(state)
        state2 = copy.deepcopy(state)

        next1 = apply_action(state1, action)
        next2 = apply_action(state2, action)

        self.assertEqual(next1["board"], next2["board"])
        self.assertEqual(next1["current_player"], next2["current_player"])

    def test_legal_actions_format(self):
        """Test that legal actions have correct format."""
        state = get_initial_state()
        actions = get_legal_actions(state)

        # All actions should be moves (no captures at start)
        for action in actions:
            self.assertIn('-', action)
            self.assertNotIn('x', action)

        # Check some expected moves exist
        # White pieces on row 2 (index 1) can move to row 3 (index 2)
        # (Row 1 pieces are blocked by row 2 pieces at start)
        self.assertIn("a2-a3", actions)
        self.assertIn("a2-b3", actions)
        self.assertIn("b2-a3", actions)
        self.assertIn("b2-b3", actions)
        self.assertIn("b2-c3", actions)

    def test_random_simulation(self):
        """Run random games to check for crashes."""
        for _ in range(20):
            state = get_initial_state()
            moves = 0

            while not state["terminal"]:
                actions = get_legal_actions(state)
                self.assertTrue(len(actions) > 0, "Non-terminal must have actions")

                action = random.choice(actions)
                state = apply_action(state, action)
                moves += 1

                if moves > 500:
                    self.fail("Game exceeded maximum moves")

            rewards = get_rewards(state)
            self.assertEqual(sum(rewards), 0.0, "Zero-sum game")
            self.assertEqual(get_current_player(state), -4)

    def test_white_wins_by_reaching_back_row(self):
        """Test that White wins by reaching row 8."""
        state = get_initial_state()

        # Manually create a state where White is about to win
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        board[6][0] = WHITE  # White piece one step from victory
        board[7][1] = BLACK  # Black piece on back row

        state = {
            "board": board,
            "current_player": WHITE,
            "winner": None,
            "terminal": False
        }

        # White moves to row 7 (1-indexed row 8)
        new_state = apply_action(state, "a7-a8")

        self.assertTrue(new_state["terminal"])
        self.assertEqual(new_state["winner"], WHITE)
        self.assertEqual(get_rewards(new_state), [1.0, -1.0])

    def test_black_wins_by_reaching_back_row(self):
        """Test that Black wins by reaching row 1."""
        state = get_initial_state()

        # Manually create a state where Black is about to win
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        board[1][0] = BLACK  # Black piece one step from victory
        board[0][1] = WHITE  # White piece on back row

        state = {
            "board": board,
            "current_player": BLACK,
            "winner": None,
            "terminal": False
        }

        # Black moves to row 0 (1-indexed row 1)
        new_state = apply_action(state, "a2-a1")

        self.assertTrue(new_state["terminal"])
        self.assertEqual(new_state["winner"], BLACK)
        self.assertEqual(get_rewards(new_state), [-1.0, 1.0])

    def test_capture_diagonal_only(self):
        """Test that captures can only happen diagonally."""
        # Create state with adjacent pieces
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        board[3][3] = WHITE
        board[4][3] = BLACK  # Directly in front (straight)
        board[4][4] = BLACK  # Diagonal

        state = {
            "board": board,
            "current_player": WHITE,
            "winner": None,
            "terminal": False
        }

        actions = get_legal_actions(state)

        # Can capture diagonal
        self.assertIn("d4xe5", actions)
        # Cannot capture straight ahead (straight moves to occupied square not allowed)
        self.assertNotIn("d4-d5", actions)
        self.assertNotIn("d4xd5", actions)

    def test_state_immutability(self):
        """Test that apply_action doesn't mutate original state."""
        state = get_initial_state()
        original_board = copy.deepcopy(state["board"])

        action = get_legal_actions(state)[0]
        new_state = apply_action(state, action)

        self.assertEqual(state["board"], original_board)
        self.assertNotEqual(new_state["board"], original_board)


if __name__ == "__main__":
    unittest.main()
