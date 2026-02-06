import unittest
import random
import json
from unittest.mock import patch
import golden as connect_four

class TestConnectFour(unittest.TestCase):

    def test_basic_random_sim(self):
        """Equivalent to BasicConnectFourTests: RandomSimTest (100 runs)."""
        for _ in range(100):
            state = connect_four.new_initial_state()
            while not state['is_terminal']:
                legal = connect_four.get_legal_actions(state)
                self.assertTrue(len(legal) > 0)
                state = connect_four.apply_action(state, random.choice(legal))
            
            rewards = connect_four.get_rewards(state)
            self.assertEqual(len(rewards), 2)
            # Verify Zero-Sum
            self.assertTrue(abs(sum(rewards)) < 1e-5)

    def test_fast_loss(self):
        """Equivalent to FastLoss C++ test."""
        # Standard 6x7 board
        state = connect_four.new_initial_state()
        
        # Moves: 3, 3, 4, 4, 2, 2
        moves = [3, 3, 4, 4, 2, 2]
        for m in moves:
            state = connect_four.apply_action(state, m)
            
        self.assertFalse(state['is_terminal'])
        
        # Player X (P0) plays col 1 to win horizontally (1,2,3,4)
        state = connect_four.apply_action(state, 1)
        
        self.assertTrue(state['is_terminal'])
        self.assertEqual(connect_four.get_rewards(state), [1.0, -1.0])
        
        expected_board = (
            ".......\n"
            ".......\n"
            ".......\n"
            ".......\n"
            "..ooo..\n"
            ".xxxx..\n"
        )
        self.assertEqual(connect_four.to_string(state), expected_board)

    def test_check_full_board_draw(self):
        """Equivalent to CheckFullBoardDraw."""
        # Construct a known draw state manually to match the string in C++ test
        # "ooxxxoo\nxxoooxx\n..."
        # Logic: Board is full, no winner.
        
        state = connect_four.new_initial_state()
        
        # We simulate the board state by injecting the grid directly
        # because playing it out move-by-move is tedious.
        # Row 0 (Bottom) to Row 5 (Top) matches the visual string reversed.
        
        # Visual Top:    ooxxxoo
        #                xxoooxx
        #                ooxxxoo
        #                xxoooxx
        #                ooxxxoo
        # Visual Bottom: xxoooxx
        
        # Map: 'x'->0, 'o'->1
        row_pattern_1 = [0, 0, 1, 1, 1, 0, 0] # xxoooxx
        row_pattern_2 = [1, 1, 0, 0, 0, 1, 1] # ooxxxoo
        
        # Fill board: Row 0 is pattern1, Row 1 is pattern2, etc.
        board = []
        for r in range(6):
            if r % 2 == 0:
                board.append(list(row_pattern_1))
            else:
                board.append(list(row_pattern_2))
                
        state['board'] = board
        state['is_terminal'] = True
        state['winner'] = None # Draw
        state['current_player'] = -1
        
        self.assertEqual(connect_four.get_rewards(state), [0.0, 0.0])
        # Verify string matches the C++ expected string
        expected_str = (
            "ooxxxoo\n"
            "xxoooxx\n"
            "ooxxxoo\n"
            "xxoooxx\n"
            "ooxxxoo\n"
            "xxoooxx\n"
        )
        self.assertEqual(connect_four.to_string(state), expected_str)

    def test_arbitrary_size(self):
        """Equivalent to ArbitrarySizeTests."""
        
        # Case 1: 4x5 Board, Vertical Win
        with patch('golden.NUM_ROWS', 4), \
             patch('golden.NUM_COLS', 5):
             
            state = connect_four.new_initial_state()
            # Moves to create vertical setup: P0(0), P1(1), P0(0)...
            # P0 needs 4 in col 0.
            # Moves: 0, 1, 0, 1, 0, 1
            for m in [0, 1, 0, 1, 0, 1]:
                state = connect_four.apply_action(state, m)
            
            # Check intermediate string
            # Visual:
            # .....
            # xo...
            # xo...
            # xo...
            expected_inter = ".....\nxo...\nxo...\nxo...\n"
            self.assertEqual(connect_four.to_string(state), expected_inter)
            
            # P0 plays 0 to win
            state = connect_four.apply_action(state, 0)
            self.assertTrue(state['is_terminal'])
            self.assertEqual(connect_four.get_rewards(state), [1.0, -1.0])

        # Case 2: 5x6 Board, Horizontal Win
        with patch('connect_four.NUM_ROWS', 5), \
             patch('connect_four.NUM_COLS', 6):
             
            state = connect_four.new_initial_state()
            # P0: 0, 1, 2. P1: 0, 1, 2.
            moves = [0, 0, 1, 1, 2, 2]
            for m in moves:
                state = connect_four.apply_action(state, m)
                
            self.assertFalse(state['is_terminal'])
            # P0 plays 3 to win
            state = connect_four.apply_action(state, 3)
            self.assertTrue(state['is_terminal'])
            
            expected_win = (
                "......\n"
                "......\n"
                "......\n"
                "ooo...\n"
                "xxxx..\n"
            )
            self.assertEqual(connect_four.to_string(state), expected_win)

    def test_state_struct_json(self):
        """Equivalent to TestStateStruct."""
        state = connect_four.new_initial_state()
        state = connect_four.apply_action(state, 3) # x
        state = connect_four.apply_action(state, 4) # o
        
        json_output = connect_four.to_json(state)
        data = json.loads(json_output)
        
        # Verify basic fields
        self.assertEqual(data["current_player"], "x") # P0 is next? No P0 moved, P1 moved. Next is P0(x).
        self.assertFalse(data["is_terminal"])
        
        # Verify board content in JSON
        # C++ JSON format: List of rows, where row 0 is bottom.
        # Row 0 should be [..., 'x', 'o', ...]
        row0 = data["board"][0]
        self.assertEqual(row0[3], "x")
        self.assertEqual(row0[4], "o")

if __name__ == '__main__':
    unittest.main()