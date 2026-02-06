import unittest
import random
from golden import *

class TestLiarsDice(unittest.TestCase):

    def test_transition_mid_game(self):
        # Construct a specific mid-game state
        # P0 has [1, 1, 1], P1 has [2, 2, 2]
        # P0 just bid "5 Fours" (bid:5:4). It is P1's turn.
        state = {
            "dice": [[1, 1, 1], [2, 2, 2]],
            "history": ["roll:1", "roll:1", "roll:1", "roll:2", "roll:2", "roll:2", "bid:5:4"],
            "current_player": 1,  # P1's turn
            "dice_queue": [],
            "last_bid": (5, 4),
            "terminal": False,
            "winner": None
        }

        # 1. Check Current Player
        self.assertEqual(1, get_current_player(state))
        self.assertEqual("Player_1", get_player_name(1))

        # 2. Check Rewards (Game not over)
        self.assertEqual([0.0, 0.0], get_rewards(state))

        # 3. Check Observations
        # P1 sees their own dice [2, 2, 2] and public history
        observations = get_observations(state)
        p1_obs = observations[1]
        self.assertEqual(p1_obs['my_dice'], [2, 2, 2])
        self.assertEqual(p1_obs['last_bid'], (5, 4))
        self.assertEqual(p1_obs['player_id'], 1)
        # P0 should see their own dice [1, 1, 1]
        self.assertEqual(observations[0]['my_dice'], [1, 1, 1])

        # 4. Check Legal Actions
        # Last bid was 5:4. Max Quantity is 6 (2 players * 3 dice).
        # Valid: Liar, Same Q Higher F (5:5, 5:6), Higher Q Any F (6:1...6:6)
        expected_actions = {"liar", "bid:5:5", "bid:5:6"}
        for f in range(1, 7):
            expected_actions.add(f"bid:6:{f}")
        
        self.assertSetEqual(expected_actions, set(get_legal_actions(state)))

        # 5. Apply Action (Transition)
        # P1 calls Liar.
        # P0 bid 5 Fours.
        # Dice: P0=[1,1,1] (Wilds count as Fours), P1=[2,2,2].
        # Total Fours = 3 (from P0) + 0 (from P1) = 3.
        # Bid (5) > Actual (3). Bidder (P0) loses. Challenger (P1) wins.
        next_state = apply_action(state, "liar")
        
        self.assertTrue(next_state["terminal"])
        self.assertEqual(next_state["winner"], 1) # P1 wins
        self.assertEqual(get_rewards(next_state), [-1.0, 1.0]) # P0 loses, P1 wins

    def test_resample_history_consistency(self):
        """
        Adapts the provided loop to verify that resampled history
        recreates the exact same sequence of observations for the player.
        """
        # 1. Generate a valid history by playing a short random game
        full_history_state = get_initial_state()
        history_log = [] # List of (State, Action)
        
        # Play until game ends
        while not full_history_state["terminal"]:
            actions = get_legal_actions(full_history_state)
            # Pick a deterministic action for reproducibility or random
            # Prefer 'liar' early to keep history short for test
            if "liar" in actions and random.random() < 0.5:
                action = "liar"
            else:
                action = random.choice(actions)
            
            # Store observation before action
            obs = get_observations(full_history_state)
            history_log.append((obs, action))
            full_history_state = apply_action(full_history_state, action)

        # 2. Select a player to test (e.g., Player 0)
        player_id = 0
        
        # Prepare the input for resample_history: List[Tuple[PlayerObs, Action]]
        obs_action_history = []
        for obs_pair, act in history_log:
            obs_action_history.append((obs_pair[player_id], act))

        # 3. Run the verification loop provided in the prompt
        state = get_initial_state()
        obs_and_action_iter = iter(obs_action_history)
        
        # Get first observation/action from the original log
        try:
            current_player_obs, current_player_action = next(obs_and_action_iter)
        except StopIteration:
            return # Short game, nothing to test

        print(f"Testing Resample for Player {player_id}")
        
        resampled_actions = resample_history(obs_action_history, player_id)
        
        for action in resampled_actions:
            # Current player check (-1 is chance)
            curr_p = get_current_player(state)
            
            # Verify Observation Consistency
            # If it is this player's turn (or they receive info), their observation MUST match
            if curr_p == player_id or curr_p == -1: 
                # Note: Chance nodes (-1) generate obs updates (dealing cards/dice)
                # We check if the state generates the expected obs for player_id
                generated_obs = get_observations(state)[player_id]
                
                # We remove 'history' from comparison because resampled history strings 
                # for opponent rolls will differ (e.g. "roll:3" vs "roll:5"), 
                # but private info (my_dice) and public bids must match.
                # In a real rigorous test, we would mask the hidden parts of the history string.
                self.assertEqual(generated_obs['my_dice'], current_player_obs['my_dice'])
                self.assertEqual(generated_obs['last_bid'], current_player_obs['last_bid'])
                self.assertEqual(generated_obs['terminal'], current_player_obs['terminal'])
                
            # Verify Action Consistency
            # We can only assert equality for:
            # 1. The player's OWN actions
            # 2. Public actions (bids)
            # We CANNOT assert equality for Opponent's Chance Actions (they are re-randomized)
            is_opponent_chance = (curr_p == -1 and "roll" in action and 
                                  len(state["dice"][player_id]) == 3) # Simple heuristic for opponent roll phase
            
            if not is_opponent_chance:
                self.assertEqual(current_player_action, action)

            # Step forward in the original log
            try:
                current_player_obs, current_player_action = next(obs_and_action_iter)
            except StopIteration:
                # End of original history
                pass

            # Apply the resampled action
            state = apply_action(state, action)

        # Ensure we reached the end of the history
        self.assertRaises(StopIteration, next, obs_and_action_iter)

if __name__ == '__main__':
    unittest.main()