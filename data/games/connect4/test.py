"""Tests for Connect Four, adapted from OpenSpiel's connect_four_test.cc."""
import unittest
import random
from golden import *


class TestConnectFour(unittest.TestCase):

    def test_no_chance_outcomes(self):
        """Adapted from BasicConnectFourTests: no chance node at start."""
        state = get_initial_state()
        self.assertNotEqual(get_current_player(state), -1)
        self.assertEqual(get_current_player(state), 0)

    def test_random_simulation(self):
        """Adapted from BasicConnectFourTests -> RandomSimTest (100 games)."""
        for _ in range(100):
            state = get_initial_state()
            moves = 0
            while get_current_player(state) != TERMINAL_PLAYER:
                actions = get_legal_actions(state)
                self.assertTrue(len(actions) > 0)
                state = apply_action(state, random.choice(actions))
                moves += 1
                self.assertLessEqual(moves, ROWS * COLS + 1)

            self.assertTrue(state["is_terminal"])
            self.assertEqual(get_legal_actions(state), [])
            rewards = get_rewards(state)
            self.assertEqual(len(rewards), 2)
            self.assertAlmostEqual(sum(rewards), 0.0)  # zero-sum or draw

    def test_fast_loss(self):
        """
        Adapted from FastLoss in connect_four_test.cc.
        P0 wins horizontally in columns 1-4 of the bottom row.

        OpenSpiel action sequence: 3,3,4,4,2,2,1
        Mapped to our strings:     x3,o3,x4,o4,x2,o2,x1

        Expected board:
          .......
          .......
          .......
          .......
          ..ooo..
          .xxxx..
        """
        state = get_initial_state()
        for action in ["x3", "o3", "x4", "o4", "x2", "o2"]:
            state = apply_action(state, action)
        self.assertFalse(state["is_terminal"])

        state = apply_action(state, "x1")
        self.assertTrue(state["is_terminal"])
        self.assertEqual(get_current_player(state), TERMINAL_PLAYER)
        self.assertEqual(get_rewards(state), [1.0, -1.0])
        self.assertEqual(state["winner"], 0)

        expected_board = [
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', 'o', 'o', 'o', '.', '.'],
            ['.', 'x', 'x', 'x', 'x', '.', '.'],
        ]
        self.assertEqual(state["board"], expected_board)

    def test_vertical_win(self):
        """
        Adapted from ArbitrarySizeTests vertical win.
        P0 wins vertically in column 0: x0,o1,x0,o1,x0,o1,x0
        """
        state = get_initial_state()
        for action in ["x0", "o1", "x0", "o1", "x0", "o1"]:
            state = apply_action(state, action)
        self.assertFalse(state["is_terminal"])

        state = apply_action(state, "x0")
        self.assertTrue(state["is_terminal"])
        self.assertEqual(get_rewards(state), [1.0, -1.0])
        self.assertEqual(state["winner"], 0)

    def test_p1_wins(self):
        """P1 wins horizontally in columns 0-3; rewards are [-1, +1]."""
        state = get_initial_state()
        # P0 spreads across cols 4,5,6 (no 4-in-a-row); P1 builds cols 0-3
        for action in ["x4", "o0", "x5", "o1", "x6", "o2"]:
            state = apply_action(state, action)
        self.assertFalse(state["is_terminal"])

        state = apply_action(state, "x4")   # P0: 2nd piece in col 4 (no win)
        state = apply_action(state, "o3")   # P1 completes 4-in-a-row cols 0-3
        self.assertTrue(state["is_terminal"])
        self.assertEqual(get_rewards(state), [-1.0, 1.0])
        self.assertEqual(state["winner"], 1)

    def test_check_full_board_draw(self):
        """
        Adapted from CheckFullBoardDraw.
        A full board with no winner yields rewards [0.0, 0.0].
        Board pattern (no 4-in-a-row): ooxxxoo / xxoooxx alternating rows.
        """
        board = [
            ['o', 'o', 'x', 'x', 'x', 'o', 'o'],
            ['x', 'x', 'o', 'o', 'o', 'x', 'x'],
            ['o', 'o', 'x', 'x', 'x', 'o', 'o'],
            ['x', 'x', 'o', 'o', 'o', 'x', 'x'],
            ['o', 'o', 'x', 'x', 'x', 'o', 'o'],
            ['x', 'x', 'o', 'o', 'o', 'x', 'x'],
        ]
        state = {
            "board": board,
            "current_player": TERMINAL_PLAYER,
            "is_terminal": True,
            "winner": None,
        }
        self.assertTrue(state["is_terminal"])
        self.assertEqual(get_current_player(state), TERMINAL_PLAYER)
        self.assertEqual(get_rewards(state), [0.0, 0.0])
        self.assertEqual(get_legal_actions(state), [])

    def test_column_fills_and_legal_actions_shrink(self):
        """Filling a column removes it from legal actions."""
        state = get_initial_state()
        # Fill column 0 (ROWS moves, alternating players)
        for _ in range(ROWS // 2):
            state = apply_action(state, f"{MARKS[get_current_player(state)]}0")
            state = apply_action(state, f"{MARKS[get_current_player(state)]}0")

        # Column 0 top row is now occupied
        self.assertNotEqual(state["board"][0][0], EMPTY)

        actions = get_legal_actions(state)
        player_mark = MARKS[get_current_player(state)]
        self.assertNotIn(f"{player_mark}0", actions)
        self.assertEqual(len(actions), COLS - 1)

    def test_gravity(self):
        """Pieces fall to the lowest available row in a column."""
        state = get_initial_state()
        state = apply_action(state, "x3")
        self.assertEqual(state["board"][ROWS - 1][3], 'x')  # bottom row
        state = apply_action(state, "o3")
        self.assertEqual(state["board"][ROWS - 2][3], 'o')  # stacks above

    def test_observations_perfect_info(self):
        """Both players see the full board (perfect information)."""
        state = get_initial_state()
        state = apply_action(state, "x3")
        state = apply_action(state, "o4")

        obs = get_observations(state)
        self.assertEqual(len(obs), 2)
        self.assertEqual(obs[0]["board"], obs[1]["board"])
        self.assertEqual(obs[0]["board"][ROWS - 1][3], 'x')
        self.assertEqual(obs[0]["board"][ROWS - 1][4], 'o')

    def test_rewards_zero_mid_game(self):
        """Rewards are [0.0, 0.0] for a non-terminal state."""
        state = get_initial_state()
        state = apply_action(state, "x3")
        self.assertEqual(get_rewards(state), [0.0, 0.0])

    def test_player_names(self):
        self.assertEqual(get_player_name(0), "Player 0 (x)")
        self.assertEqual(get_player_name(1), "Player 1 (o)")


if __name__ == '__main__':
    unittest.main()
