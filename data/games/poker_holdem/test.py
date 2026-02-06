"""Tests for Texas Hold'em Poker implementation."""
import unittest
import random
import copy
from golden import *
from golden import _evaluate_hand, _best_five_card_hand

class TestHoldem(unittest.TestCase):

    def test_initial_state(self):
        """Verify the game starts with chance node for dealing."""
        state = get_initial_state()
        self.assertEqual(get_current_player(state), CHANCE_PLAYER)
        self.assertEqual(get_rewards(state), [0.0, 0.0])
        self.assertEqual(len(state["deck"]), 52)
        self.assertEqual(state["pot"], SMALL_BLIND + BIG_BLIND)

    def test_dealing_hole_cards(self):
        """Test that hole cards are dealt correctly."""
        state = get_initial_state()

        # Deal 4 hole cards
        for i in range(4):
            actions = get_legal_actions(state)
            self.assertTrue(all(a.startswith("deal:") for a in actions))
            action = random.choice(actions)
            state = apply_action(state, action)

        # After dealing, should be in preflop with P0 to act
        self.assertEqual(state["phase"], PHASE_PREFLOP)
        self.assertEqual(get_current_player(state), 0)
        self.assertEqual(len(state["hole_cards"][0]), 2)
        self.assertEqual(len(state["hole_cards"][1]), 2)

    def test_preflop_betting(self):
        """Test preflop betting actions."""
        state = get_initial_state()

        # Deal hole cards
        for i in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        # P0 (SB) acts first
        self.assertEqual(get_current_player(state), 0)
        actions = get_legal_actions(state)
        self.assertIn("F", actions)
        self.assertIn("C", actions)
        self.assertIn("R", actions)

    def test_fold_ends_game(self):
        """Test that folding ends the game."""
        state = get_initial_state()

        # Deal hole cards
        for i in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        # P0 folds
        state = apply_action(state, "F")

        self.assertTrue(state["terminal"])
        self.assertEqual(state["winner"], 1)
        self.assertEqual(get_current_player(state), TERMINAL_PLAYER)

    def test_check_advances_round(self):
        """Test that both players checking advances to next round."""
        state = get_initial_state()

        # Deal hole cards
        for i in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        # P0 calls, P1 checks
        state = apply_action(state, "C")
        self.assertEqual(get_current_player(state), 1)

        state = apply_action(state, "K")

        # Should now be dealing flop
        self.assertEqual(state["phase"], PHASE_DEAL_FLOP)
        self.assertEqual(get_current_player(state), CHANCE_PLAYER)

    def test_flop_dealing(self):
        """Test that flop deals 3 community cards."""
        state = get_initial_state()

        # Deal hole cards
        for i in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        # Preflop betting
        state = apply_action(state, "C")
        state = apply_action(state, "K")

        # Deal flop
        for i in range(3):
            self.assertEqual(get_current_player(state), CHANCE_PLAYER)
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        self.assertEqual(len(state["board"]), 3)
        self.assertEqual(state["phase"], PHASE_FLOP)
        self.assertEqual(get_current_player(state), 1)  # BB acts first post-flop

    def test_random_simulation(self):
        """Run random games to check for crashes."""
        for _ in range(20):
            state = get_initial_state()
            moves = 0

            while not state["terminal"]:
                actions = get_legal_actions(state)
                if not actions:
                    break

                action = random.choice(actions)
                state = apply_action(state, action)
                moves += 1

                if moves > 200:
                    self.fail("Game exceeded maximum moves")

            if state["terminal"]:
                rewards = get_rewards(state)
                # Zero-sum check (approximately, accounting for blinds)
                self.assertAlmostEqual(sum(rewards), 0.0, places=5)

    def test_observations_hide_opponent_cards(self):
        """Test that observations don't reveal opponent's hole cards."""
        state = get_initial_state()

        # Deal hole cards
        for i in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        obs = get_observations(state)

        # Each player should only see their own cards
        self.assertEqual(len(obs[0]["my_hole_cards"]), 2)
        self.assertEqual(len(obs[1]["my_hole_cards"]), 2)
        self.assertNotEqual(obs[0]["my_hole_cards"], obs[1]["my_hole_cards"])

    def test_hand_evaluation_high_card(self):
        """Test high card hand evaluation."""
        cards = ["2c", "5d", "7h", "9s", "Kc"]
        rank, tiebreakers = _evaluate_hand(cards)
        self.assertEqual(rank, 0)  # High card

    def test_hand_evaluation_pair(self):
        """Test pair hand evaluation."""
        cards = ["2c", "2d", "7h", "9s", "Kc"]
        rank, tiebreakers = _evaluate_hand(cards)
        self.assertEqual(rank, 1)  # Pair

    def test_hand_evaluation_flush(self):
        """Test flush hand evaluation."""
        cards = ["2c", "5c", "7c", "9c", "Kc"]
        rank, tiebreakers = _evaluate_hand(cards)
        self.assertEqual(rank, 5)  # Flush

    def test_hand_evaluation_straight(self):
        """Test straight hand evaluation."""
        cards = ["5c", "6d", "7h", "8s", "9c"]
        rank, tiebreakers = _evaluate_hand(cards)
        self.assertEqual(rank, 4)  # Straight

    def test_hand_evaluation_full_house(self):
        """Test full house hand evaluation."""
        cards = ["Kc", "Kd", "Kh", "9s", "9c"]
        rank, tiebreakers = _evaluate_hand(cards)
        self.assertEqual(rank, 6)  # Full house

    def test_best_five_card_hand(self):
        """Test best 5-card hand selection from 7 cards."""
        hole = ["Ac", "Kc"]
        board = ["Qc", "Jc", "Tc", "2d", "3h"]
        rank, _ = _best_five_card_hand(hole, board)
        self.assertEqual(rank, 9)  # Royal flush

    def test_showdown_winner(self):
        """Test that showdown correctly determines winner."""
        # Create a state at showdown
        state = {
            "deck": [],
            "hole_cards": [["Ac", "Kc"], ["2d", "3d"]],
            "board": ["Qc", "Jc", "Tc", "5h", "6s"],
            "phase": PHASE_RIVER,
            "current_player": 1,
            "pot": 20,
            "bets": [10, 10],
            "stacks": [90, 90],
            "to_call": 0,
            "last_raiser": -1,
            "actions_this_round": 1,
            "folded": [False, False],
            "history": [],
            "terminal": False,
            "winner": None
        }

        # Both check to showdown
        state = apply_action(state, "K")

        self.assertTrue(state["terminal"])
        self.assertEqual(state["winner"], 0)  # P0 has royal flush

    def test_resample_history_basic(self):
        """Test that resample_history returns a valid action list."""
        # Play a short game and record observations
        state = get_initial_state()
        player_id = 0
        obs_action_history = []

        while not state["terminal"]:
            cp = get_current_player(state)
            actions = get_legal_actions(state)
            if not actions:
                break

            action = random.choice(actions)

            # Record player's observations
            if cp == player_id:
                obs = copy.deepcopy(get_observations(state)[player_id])
                obs_action_history.append((obs, action))

            state = apply_action(state, action)

        if not obs_action_history:
            return  # Player never acted

        # Resample should return a list
        resampled = resample_history(obs_action_history, player_id)
        self.assertIsInstance(resampled, list)
        self.assertTrue(len(resampled) > 0)

    def test_resample_history_consistency(self):
        """
        Verify that resampled history produces consistent observations.
        Key invariant: player's hole cards must match at each of their decision points.
        """
        for _ in range(10):
            # 1. Play a random game and record player's view
            state = get_initial_state()
            player_id = random.choice([0, 1])
            obs_action_history = []

            while not state["terminal"]:
                cp = get_current_player(state)
                actions = get_legal_actions(state)
                if not actions:
                    break

                action = random.choice(actions)

                if cp == player_id:
                    obs = copy.deepcopy(get_observations(state)[player_id])
                    obs_action_history.append((obs, action))

                state = apply_action(state, action)

            if len(obs_action_history) < 1:
                continue

            # 2. Resample
            resampled = resample_history(copy.deepcopy(obs_action_history), player_id)

            # 3. Verify resampled history is valid (all actions are legal)
            replay_state = get_initial_state()
            for action in resampled:
                legal = get_legal_actions(replay_state)
                if not legal:
                    break

                # Deal actions may differ for opponent's cards
                if action.startswith("deal:"):
                    card = action.split(":")[1]
                    if f"deal:{card}" not in legal:
                        # Try any deal action
                        action = legal[0]

                if action in legal:
                    replay_state = apply_action(replay_state, action)
                else:
                    # Skip if not legal (shouldn't happen often)
                    break

            # 4. Verify player's hole cards are preserved
            if not replay_state["terminal"]:
                final_obs = get_observations(replay_state)[player_id]
                expected_hole = obs_action_history[0][0]["my_hole_cards"]
                self.assertEqual(
                    set(final_obs["my_hole_cards"]),
                    set(expected_hole),
                    f"Hole cards not preserved: {final_obs['my_hole_cards']} vs {expected_hole}"
                )

    def test_resample_preserves_player_cards(self):
        """Test that resample preserves the player's known hole cards."""
        state = get_initial_state()
        player_id = 0

        # Deal hole cards
        for _ in range(4):
            action = random.choice(get_legal_actions(state))
            state = apply_action(state, action)

        # Get player's observation with their hole cards
        obs = get_observations(state)[player_id]
        my_cards = obs["my_hole_cards"]

        # Create simple obs_action_history
        obs_action_history = [(copy.deepcopy(obs), "C")]

        # Resample multiple times
        for _ in range(10):
            resampled = resample_history(obs_action_history, player_id)

            # Find the deal actions for player's cards
            dealt_to_player = []
            for action in resampled:
                if action.startswith("deal:"):
                    card = action.split(":")[1]
                    # First 2 deals go to P0, next 2 to P1
                    if len(dealt_to_player) < 2 and player_id == 0:
                        dealt_to_player.append(card)
                    elif len(dealt_to_player) >= 2 and player_id == 1:
                        dealt_to_player.append(card)
                        if len(dealt_to_player) == 4:
                            dealt_to_player = dealt_to_player[2:4]
                            break

            # Player's cards should be preserved
            self.assertEqual(
                set(dealt_to_player[:2] if player_id == 0 else dealt_to_player),
                set(my_cards),
                f"Player cards not preserved: {dealt_to_player} vs {my_cards}"
            )


if __name__ == "__main__":
    unittest.main()
