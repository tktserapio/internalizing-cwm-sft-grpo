import unittest
from golden import *

class TestQuadranto(unittest.TestCase):
    
    def test_transition_mid_game(self):
        """
        Tests a specific mid-game state transition where:
        - P0 is at (1, 1) [Quadrant 1]
        - P1 is at (2, 2) [Quadrant 4]
        - It is Player 0's turn.
        """
        # Manually constructed state
        state = {
            "board_size": 4,
            "p0_loc": (1, 1),
            "p1_loc": (2, 2),
            "current_player": 0,
            "turn_count": 5,
            "status": "playing",
            "history": ["place_p0:1,1", "place_p1:2,2", "dummy_history"]
        }

        # 1. Check Current Player
        self.assertEqual(0, get_current_player(state))
        self.assertEqual("Player 0", get_player_name(0))

        # 2. Check Rewards (Ongoing game = 0.0)
        self.assertEqual([0.0, 0.0], get_rewards(state))

        # 3. Check Observations
        # P0 sees self at (1,1) and Opponent in Q4 (Quadrant of 2,2 is 4)
        # P1 sees self at (2,2) and Opponent in Q1 (Quadrant of 1,1 is 1)
        expected_obs = [
            {"loc": (1, 1), "opponent_quadrant": 4},
            {"loc": (2, 2), "opponent_quadrant": 1}
        ]
        self.assertEqual(expected_obs, get_observations(state))

        # 4. Check Legal Actions
        # At (1,1), P0 can move Up(0,1), Down(2,1), Left(1,0), Right(1,2), Stay(1,1)
        expected_actions = set(["Up", "Down", "Left", "Right", "Stay"])
        self.assertSetEqual(expected_actions, set(get_legal_actions(state)))

        # 5. Apply Action and Check Transition
        # P0 moves "Right" -> moves to (1, 2). (1,2) is in Quadrant 2.
        # Turn switches to P1.
        next_state = apply_action(state, "Right")
        
        self.assertEqual((1, 2), next_state["p0_loc"]) # P0 moved
        self.assertEqual((2, 2), next_state["p1_loc"]) # P1 stayed
        self.assertEqual(1, next_state["current_player"]) # Turn switched
        self.assertEqual("playing", next_state["status"])

    def test_resample_consistency(self):
        """
        Verifies that resample_history generates a valid sequence of actions
        that perfectly reproduces the player's sequence of observations.
        """
        # Scenario: 
        # P0 starts at (0,0) [Q1], P1 starts at (3,3) [Q4].
        # P0 moves "Right" -> (0,1).
        # P1 moves "Up" -> (2,3) (Hidden from P0, but affects P0's next obs of Q4).
        # P0 is now at (0,1), observing P1 still in Q4.
        
        player_id = 0
        
        # This is the history of what Player 0 SAW and DID.
        obs_action_history = [
            # Turn 1: P0 at (0,0), sees Opp in Q4. P0 acts "Right".
            ({"loc": (0, 0), "opponent_quadrant": 4}, "Right"),
            
            # Turn 2: P0 at (0,1), sees Opp in Q4. P0 has not acted yet (None).
            ({"loc": (0, 1), "opponent_quadrant": 4}, None)
        ]

        obs_and_action_iter = iter(obs_action_history)
        current_player_obs, current_player_action = next(obs_and_action_iter)
        
        # Start from a blank slate for the validation replay
        state = get_initial_state()
        
        # Get the full history (Chance + P0 + P1 actions) derived from P0's partial view
        resampled_actions = resample_history(obs_action_history, player_id)
        
        print(f"\nResampled Actions: {resampled_actions}")

        # --- User Provided Validation Loop ---
        for action in resampled_actions:
            # print(f"In state {state}") # Debug print
            
            if get_current_player(state) == player_id:
                # If it's our turn, the state must match our recorded observation
                print(f"Checking Observation match for P{player_id}...")
                self.assertEqual(current_player_obs, get_observations(state)[player_id])
                
                # The action the resampler chose for us must match what we actually did
                self.assertEqual(current_player_action, action)
                
                # Advance the iterator to the next observation we expect to see
                try:
                    current_player_obs, current_player_action = next(obs_and_action_iter)
                except StopIteration:
                    # If we ran out of observations but the loop continues, 
                    # it implies the resampler added extra actions for the player
                    # which shouldn't happen.
                    pass 

            print(f"Taking action {action}")
            state = apply_action(state, action)

        # Ensure we consumed all observations
        try:
            next(obs_and_action_iter)
            # If this succeeds, we had more observations than actions, which is a fail
            raise ValueError('Failed to iterate through all observations.')
        except StopIteration:
            pass
        
        # Verify final state ownership
        # Note: If the last entry in history has action=None, it means it's currently that player's turn
        self.assertEqual(player_id, get_current_player(state))

if __name__ == '__main__':
    unittest.main()