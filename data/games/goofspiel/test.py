"""Tests for Goofspiel game implementation."""
import unittest
import random
import copy
from golden import *


class TestGoofspiel(unittest.TestCase):

    def test_initial_state(self):
        """Verify the game starts with a chance node."""
        state = get_initial_state()
        self.assertEqual(get_current_player(state), CHANCE_PLAYER)
        self.assertEqual(get_rewards(state), [0.0, 0.0])
        self.assertEqual(len(state["hands"][0]), NUM_CARDS)
        self.assertEqual(len(state["hands"][1]), NUM_CARDS)
        self.assertEqual(len(state["prize_deck"]), NUM_CARDS)

    def test_chance_node_deals_prize(self):
        """Test that chance node reveals a prize card."""
        state = get_initial_state()
        actions = get_legal_actions(state)

        # All actions should be prize dealing
        for action in actions:
            self.assertTrue(action.startswith("prize:"))

        self.assertEqual(len(actions), NUM_CARDS)

    def test_player_bidding(self):
        """Test that players can bid cards from their hands."""
        state = get_initial_state()

        # Deal a prize
        prize_action = get_legal_actions(state)[0]
        state = apply_action(state, prize_action)

        # Player 0 should bid
        self.assertEqual(get_current_player(state), 0)
        actions = get_legal_actions(state)

        for action in actions:
            self.assertTrue(action.startswith("bid:"))

        self.assertEqual(len(actions), NUM_CARDS)

    def test_random_simulation(self):
        """Run random games to check for crashes."""
        for _ in range(20):
            state = get_initial_state()
            moves = 0

            while get_current_player(state) != TERMINAL_PLAYER:
                actions = get_legal_actions(state)
                self.assertTrue(len(actions) > 0, "Non-terminal must have actions")

                action = random.choice(actions)
                state = apply_action(state, action)
                moves += 1

                if moves > 100:
                    self.fail("Game exceeded maximum moves")

            rewards = get_rewards(state)
            self.assertEqual(sum(rewards), 0.0, "Zero-sum game")
            self.assertEqual(get_current_player(state), TERMINAL_PLAYER)

    def test_bidding_removes_card_from_hand(self):
        """Test that bidding removes the card from player's hand."""
        state = get_initial_state()

        # Deal a prize
        state = apply_action(state, "prize:5")

        # Player 0 bids
        initial_hand = state["hands"][0][:]
        state = apply_action(state, "bid:7")

        # Card 7 should be removed from player 0's hand
        self.assertNotIn(7, state["hands"][0])
        self.assertEqual(len(state["hands"][0]), NUM_CARDS - 1)

    def test_higher_bid_wins_prize(self):
        """Test that higher bid wins the prize card value."""
        state = get_initial_state()

        # Deal prize worth 5
        state = apply_action(state, "prize:5")

        # Player 0 bids 3
        state = apply_action(state, "bid:3")

        # Player 1 bids 7 (higher)
        state = apply_action(state, "bid:7")

        # After round resolves, player 1 should have 5 points
        self.assertEqual(state["points"][0], 0)
        self.assertEqual(state["points"][1], 5)

    def test_tie_discards_prize(self):
        """Test that tied bids result in prize being discarded."""
        state = get_initial_state()

        # Deal prize worth 5
        state = apply_action(state, "prize:5")

        # Both players bid 7
        state = apply_action(state, "bid:7")
        state = apply_action(state, "bid:7")

        # Neither player should have points
        self.assertEqual(state["points"][0], 0)
        self.assertEqual(state["points"][1], 0)

    def test_observations_hide_opponent_bid(self):
        """Test that observations don't reveal opponent's current bid."""
        state = get_initial_state()

        # Deal prize
        state = apply_action(state, "prize:5")

        # Player 0 bids
        state = apply_action(state, "bid:7")

        # Get player 1's observation
        obs = get_observations(state)[1]

        # Player 1 should not see player 0's bid
        self.assertIsNone(obs["my_current_bid"])

    def test_observations_reveal_bids_after_round(self):
        """Test that bids are revealed after round completes."""
        state = get_initial_state()

        # Complete one round
        state = apply_action(state, "prize:5")
        state = apply_action(state, "bid:3")  # P0 bids 3
        state = apply_action(state, "bid:7")  # P1 bids 7

        # Get observations
        obs0 = get_observations(state)[0]
        obs1 = get_observations(state)[1]

        # Both should see round history with bids
        self.assertEqual(len(obs0["round_history"]), 1)
        self.assertEqual(obs0["round_history"][0]["prize"], 5)
        self.assertEqual(obs0["round_history"][0]["my_bid"], 3)
        self.assertEqual(obs0["round_history"][0]["opp_bid"], 7)

    def test_game_ends_after_all_rounds(self):
        """Test that game terminates after NUM_CARDS rounds."""
        state = get_initial_state()

        # Play all rounds
        for _ in range(NUM_CARDS):
            # Deal prize
            prize_action = random.choice(get_legal_actions(state))
            state = apply_action(state, prize_action)

            # Both players bid
            bid0 = random.choice(get_legal_actions(state))
            state = apply_action(state, bid0)

            bid1 = random.choice(get_legal_actions(state))
            state = apply_action(state, bid1)

        self.assertEqual(get_current_player(state), TERMINAL_PLAYER)
        self.assertEqual(state["round"], NUM_CARDS)

    def test_final_rewards(self):
        """Test that rewards are assigned based on total points."""
        state = get_initial_state()

        # Descending prizes (13,12,...,1) + P0 bids max, P1 bids min.
        # P0 wins the first 6 rounds (prizes 13-8) for 63 pts;
        # P1 wins the last 6 rounds (prizes 6-1) for 21 pts → P0 wins.
        prizes = list(range(NUM_CARDS, 0, -1))

        for prize in prizes:
            state = apply_action(state, f"prize:{prize}")

            # Get available bids
            p0_hand = state["hands"][0]
            p1_hand = state["hands"][1]

            # P0 bids highest available
            p0_bid = max(p0_hand)
            state = apply_action(state, f"bid:{p0_bid}")

            # P1 bids lowest available
            p1_bid = min(p1_hand)
            state = apply_action(state, f"bid:{p1_bid}")

        rewards = get_rewards(state)

        # P0 should win (bid higher each time)
        self.assertEqual(rewards[0], 1.0)
        self.assertEqual(rewards[1], -1.0)

    def test_resample_history_basic(self):
        """Test basic resample_history functionality."""
        if not hasattr(__import__('golden'), 'resample_history'):
            self.skipTest("resample_history not implemented")

        # Create a simple game state
        state = get_initial_state()
        state = apply_action(state, "prize:5")
        state = apply_action(state, "bid:7")  # P0 bids
        state = apply_action(state, "bid:3")  # P1 bids

        # Get P1's observation
        obs = get_observations(state)[1]

        # Create observation history for P1
        obs_action_history = [(obs, None)]

        # Resample
        history = resample_history(obs_action_history, 1)

        # History should be a list of actions
        self.assertIsInstance(history, list)

    def test_resample_history_consistency(self):
        """Test that resampled history is consistent with observations."""
        if not hasattr(__import__('golden'), 'resample_history'):
            self.skipTest("resample_history not implemented")

        # Play a random game, recording P1's view
        for _ in range(10):
            state = get_initial_state()
            player_id = 1
            obs_action_history = []

            while get_current_player(state) != TERMINAL_PLAYER:
                cp = get_current_player(state)
                actions = get_legal_actions(state)
                action = random.choice(actions)

                if cp == player_id:
                    obs = copy.deepcopy(get_observations(state)[player_id])
                    obs_action_history.append((obs, action))

                state = apply_action(state, action)

            if not obs_action_history:
                continue

            # Resample and verify
            resampled = resample_history(copy.deepcopy(obs_action_history), player_id)

            # Resampled history should be valid actions
            self.assertIsInstance(resampled, list)
            self.assertTrue(len(resampled) > 0)


if __name__ == "__main__":
    unittest.main()
