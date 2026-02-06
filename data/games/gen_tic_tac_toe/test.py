import unittest
from typing import List, Optional
from golden import *

class TestGeneralTicTacToe(unittest.TestCase):

    def setUp(self):
        """Runs before every test to get a fresh empty state."""
        self.initial_state = get_initial_state()

    def _manual_setup(self, moves: List[tuple[int, int, int]]):
        """Helper to force-set board state for testing specific patterns.
        moves: List of (row, col, player_id)
        """
        state = get_initial_state()
        for r, c, p in moves:
            state["board"][r][c] = p
        return state

    def test_initialization(self):
        """Test the board starts empty and correct player starts."""
        state = self.initial_state
        self.assertEqual(state["current_player"], 0)
        self.assertEqual(state["status"], "ongoing")
        self.assertIsNone(state["winner"])
        # Check board is 6x6 and empty
        self.assertEqual(len(state["board"]), 6)
        self.assertEqual(len(state["board"][0]), 6)
        self.assertTrue(all(cell is None for row in state["board"] for cell in row))

    def test_apply_action_logic_and_immutability(self):
        """Test taking a turn updates state correctly and does not mutate old state."""
        state_v0 = self.initial_state
        action = "3,3"
        
        state_v1 = apply_action(state_v0, action)

        # Check v1 updates
        self.assertEqual(state_v1["board"][3][3], 0)
        self.assertEqual(state_v1["current_player"], 1)
        
        # Check v0 remains unchanged (immutability)
        self.assertIsNone(state_v0["board"][3][3])
        self.assertEqual(state_v0["current_player"], 0)

    def test_horizontal_win(self):
        """Test a row of 4 triggers a win."""
        # Player 0 has 3 marks, is about to place the 4th at (0,3)
        state = self._manual_setup([(0,0,0), (0,1,0), (0,2,0)])
        
        # Apply winning move
        new_state = apply_action(state, "0,3")
        
        self.assertEqual(new_state["status"], "win")
        self.assertEqual(new_state["winner"], 0)
        self.assertEqual(new_state["current_player"], -4) # Terminal
        self.assertEqual(get_rewards(new_state), [1.0, -1.0])

    def test_vertical_win(self):
        """Test a column of 4 triggers a win."""
        # Player 1 setup at column 5
        state = self._manual_setup([(0,5,1), (1,5,1), (2,5,1)])
        state["current_player"] = 1 # Set turn to player 1
        
        new_state = apply_action(state, "3,5")

        self.assertEqual(new_state["status"], "win")
        self.assertEqual(new_state["winner"], 1)
        self.assertEqual(get_rewards(new_state), [-1.0, 1.0])

    def test_diagonal_win_main(self):
        """Test Top-Left to Bottom-Right diagonal win."""
        # P0 at (1,1), (2,2), (3,3), placing (4,4)
        state = self._manual_setup([(1,1,0), (2,2,0), (3,3,0)])
        
        new_state = apply_action(state, "4,4")
        self.assertEqual(new_state["status"], "win")
        self.assertEqual(new_state["winner"], 0)

    def test_diagonal_win_anti(self):
        """Test Top-Right to Bottom-Left diagonal win."""
        # P1 at (0,3), (1,2), (2,1), placing (3,0)
        state = self._manual_setup([(0,3,1), (1,2,1), (2,1,1)])
        state["current_player"] = 1
        
        new_state = apply_action(state, "3,0")
        self.assertEqual(new_state["status"], "win")
        self.assertEqual(new_state["winner"], 1)

    def test_draw_condition(self):
        """Test that a full board with no winner results in a draw."""
        # Use a pattern that fills the board without creating a line of 4.
        # Pattern: Alternating pairs "0 0 1 1 0 0" and "1 1 0 0 1 1"
        # This breaks all vertical, horizontal, and diagonal lines > 2.
        state = get_initial_state()
        
        for r in range(6):
            for c in range(6):
                # Even rows: 0 0 1 1 0 0
                if r % 2 == 0:
                    val = 0 if (c % 6) in [0, 1, 4, 5] else 1
                # Odd rows: 1 1 0 0 1 1
                else:
                    val = 1 if (c % 6) in [0, 1, 4, 5] else 0
                state["board"][r][c] = val

        # We leave the last spot (5,5) open to simulate the final move.
        # In our pattern (Odd row), (5,5) should be 1.
        state["board"][5][5] = None
        state["current_player"] = 1 # Player 1's turn to fill the last spot
        
        # Verify it's ongoing before the last move
        self.assertEqual(state["status"], "ongoing")
        
        # Apply the final move
        new_state = apply_action(state, "5,5")

        self.assertEqual(new_state["status"], "draw")
        self.assertIsNone(new_state["winner"])
        self.assertEqual(new_state["current_player"], -4)
        self.assertEqual(get_rewards(new_state), [0.0, 0.0])

    def test_legal_actions(self):
        """Test that get_legal_actions only returns empty cells."""
        state = self._manual_setup([(0,0,0), (5,5,1)])
        actions = get_legal_actions(state)
        
        self.assertNotIn("0,0", actions)
        self.assertNotIn("5,5", actions)
        self.assertIn("0,1", actions)
        self.assertEqual(len(actions), 34) # 36 total - 2 occupied

        # Test terminal state has no actions
        state["status"] = "win"
        self.assertEqual(get_legal_actions(state), [])

if __name__ == '__main__':
    unittest.main()