import unittest
import copy
import golden as converge

class TestConvergeGame(unittest.TestCase):
    """
    Tier 2 & 3 Verification Suite for 'Converge'.
    Tests: Runtime Robustness, State Immutability, Game Physics (Stuns), and Rewards.
    """

    def setUp(self):
        self.initial_state = converge.get_initial_state()

    def test_tier1_static_api(self):
        """Tier 1: Verify API structure and return types."""
        state = self.initial_state
        self.assertIsInstance(converge.get_legal_actions(state), list)
        self.assertIsInstance(converge.get_rewards(state), list)
        self.assertIsInstance(converge.get_current_player(state), int)
        # Check reward dimensions
        self.assertEqual(len(converge.get_rewards(state)), 2)

    def test_tier2_immutability(self):
        """Tier 2: Invariant - apply_action must NOT mutate the input state."""
        state = self.initial_state
        actions = converge.get_legal_actions(state)
        first_action = actions[0]
        
        # Deep copy for comparison
        original_state_snapshot = copy.deepcopy(state)
        
        # Apply action
        _ = converge.apply_action(state, first_action)
        
        # Assert the original state object is unchanged
        self.assertEqual(state, original_state_snapshot, 
                         "VIOLATION: apply_action mutated the input state in place.")

    def test_tier2_game_physics_movement(self):
        """Tier 2: Verify basic movement logic (occupancy and bounds)."""
        # Setup specific board: P0 at (0,0), P1 at (0,1) [Adjacent]
        state = self.initial_state
        state["board"] = {"0_0": 0, "0_1": 1}
        state["current_player"] = 0
        
        actions = converge.get_legal_actions(state)
        
        # P0 cannot move to (0,1) because it is occupied by P1
        self.assertNotIn("move (0,0) to (0,1)", actions)
        
        # P0 can move to (1,0) or (1,1)
        self.assertIn("move (0,0) to (1,0)", actions)

    def test_tier2_mechanic_stun_application(self):
        """Tier 2: Verify the 'Stun' mechanic triggers correctly."""
        # Setup: P0 at (1,0), P1 at (3,0). 
        # P0 moves to (2,0) -> Adjacent to P1 -> P1 should be stunned.
        state = self.initial_state
        state["board"] = {"1_0": 0, "3_0": 1}
        state["current_player"] = 0
        state["turn_count"] = 10
        
        action = "move (1,0) to (2,0)"
        next_state = converge.apply_action(state, action)
        
        # Check if P1's unit at (3,0) is recorded as stunned at turn 10
        self.assertIn("3_0", next_state["stunned_units"])
        self.assertEqual(next_state["stunned_units"]["3_0"], 10)

    def test_tier2_mechanic_stun_effect(self):
        """Tier 2: Verify a stunned unit cannot move."""
        # Setup: P1's turn. P1 at (3,0) was stunned on turn 10. Current turn is 11.
        state = self.initial_state
        state["board"] = {"2_0": 0, "3_0": 1}
        state["stunned_units"] = {"3_0": 10}
        state["current_player"] = 1
        state["turn_count"] = 11
        
        actions = converge.get_legal_actions(state)
        
        # Since P1 has only one unit and it is stunned, the ONLY legal action must be 'pass'
        self.assertEqual(actions, ["pass"], 
                         f"VIOLATION: Stunned unit was allowed to move. Actions: {actions}")

    def test_tier2_mechanic_stun_expiry(self):
        """Tier 2: Verify stun expires after one turn."""
        # Setup: P1's turn. P1 at (3,0) was stunned on turn 8. Current turn is 11 (Long past).
        state = self.initial_state
        state["board"] = {"2_0": 0, "3_0": 1}
        state["stunned_units"] = {"3_0": 8} # Expired stun
        state["current_player"] = 1
        state["turn_count"] = 11
        
        actions = converge.get_legal_actions(state)
        
        # Stun expired, should be able to move
        self.assertNotEqual(actions, ["pass"])
        self.assertTrue(any("move (3,0)" in a for a in actions))

    def test_tier3_win_condition_and_rewards(self):
        """Tier 3: Verify winning condition and zero-sum rewards."""
        # Setup: P0 at (1,1). Moves to (2,2) [Center/Win Pos]
        state = self.initial_state
        state["board"] = {"1_1": 0, "4_4": 1}
        state["current_player"] = 0
        
        action = "move (1,1) to (2,2)"
        next_state = converge.apply_action(state, action)
        
        # Check Terminal State
        self.assertEqual(next_state["status"], "won")
        self.assertEqual(next_state["winner"], 0)
        self.assertEqual(converge.get_current_player(next_state), -4) # Terminal
        
        # Check Zero-Sum Rewards
        rewards = converge.get_rewards(next_state)
        self.assertEqual(rewards, [1.0, -1.0])
        self.assertEqual(sum(rewards), 0.0)

    def test_tier3_draw_condition(self):
        """Tier 3: Verify draw condition at max turns."""
        state = self.initial_state
        state["turn_count"] = 49 # Max is 50
        state["board"] = {"0_0": 0, "4_4": 1}
        state["current_player"] = 0
        
        # Make a non-winning move
        action = "move (0,0) to (0,1)"
        next_state = converge.apply_action(state, action)
        
        # Should be turn 50 -> Draw
        self.assertEqual(next_state["status"], "draw")
        self.assertEqual(converge.get_current_player(next_state), -4)
        self.assertEqual(converge.get_rewards(next_state), [0.0, 0.0])

if __name__ == '__main__':
    unittest.main()