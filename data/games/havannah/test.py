import unittest
import random
import copy
from golden import *

# Assuming the functions from the previous implementation are available.
# In a real project, these would be imported: 
# from havannah import get_initial_state, apply_action, get_legal_actions, ...

class TestHavannah(unittest.TestCase):
    
    def test_load_game_basic(self):
        """Adapts testing::LoadGameTest for the fixed board configuration."""
        state = get_initial_state()
        self.assertFalse(state["terminal"])
        self.assertEqual(state["current_player"], 0)
        self.assertEqual(get_rewards(state), [0.0, 0.0])
        # Verify board size implicitly by legal actions count
        # For a hex board of side 10, total cells = 3n(n-1) + 1 = 271
        legal_actions = get_legal_actions(state)
        self.assertEqual(len(legal_actions), 271)

    def test_no_chance_outcomes(self):
        """
        Adapts testing::NoChanceOutcomesTest.
        Havannah is a deterministic game (no dice rolls/chance nodes).
        This test verifies that the same action on the same state yields the same result.
        """
        state = get_initial_state()
        legal_actions = get_legal_actions(state)
        action = legal_actions[0]
        
        # Apply action twice independently
        state_copy_1 = copy.deepcopy(state)
        state_copy_2 = copy.deepcopy(state)
        
        next_state_1 = apply_action(state_copy_1, action)
        next_state_2 = apply_action(state_copy_2, action)
        
        self.assertEqual(next_state_1["board"], next_state_2["board"])
        self.assertEqual(next_state_1["current_player"], next_state_2["current_player"])

    def test_random_simulation(self):
        """
        Adapts testing::RandomSimTest.
        Runs complete game simulations to check for crashes and illegal states.
        """
        SIMULATIONS = 10 # Corresponds to the count in the C++ test
        
        for i in range(SIMULATIONS):
            state = get_initial_state()
            moves = 0
            
            while not state["terminal"]:
                legal_actions = get_legal_actions(state)
                
                # Verify we aren't stuck with no actions in a non-terminal state
                if not legal_actions:
                    self.fail(f"Game not terminal but no legal actions available at move {moves}")
                
                action = random.choice(legal_actions)
                state = apply_action(state, action)
                moves += 1
                
                # Safety break to prevent infinite loops if logic fails
                if moves > 300: 
                    print("Warning: Game exceeded expected length.")
                    break
            
            # Post-game checks
            rewards = get_rewards(state)
            self.assertTrue(sum(rewards) == 0.0 or sum(rewards) == 1.0 or sum(rewards) == -1.0,
                            f"Invalid rewards: {rewards}")
            
            # Verify terminal player logic (-4 indicates terminal)
            self.assertEqual(get_current_player(state), -4)

    def test_game_trajectory_consistency(self):
        """
        Additional verification ensuring the game state is consistent 
        through a known short trajectory.
        """
        state = get_initial_state()
        # Simulate a few moves to ensure history and player swapping work
        trajectory = ["J10", "K10", "I10"] # Arbitrary valid moves
        
        for idx, action in enumerate(trajectory):
            expected_player = idx % 2
            self.assertEqual(state["current_player"], expected_player)
            state = apply_action(state, action)
            
        self.assertEqual(len(state["history"]), 3)
        self.assertEqual(state["history"][-1], "I10")

if __name__ == "__main__":
    unittest.main()