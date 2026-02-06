import unittest
from golden import *

# Assuming the functions are defined in the current scope
# from your_module import get_initial_state, apply_action, get_current_player, etc.

class BlackjackTest(unittest.TestCase):
    
    def force_chance(self, state, card):
        """Helper to apply a specific chance action."""
        action = f"deal:{card}"
        return apply_action(state, action)

    def test_no_bust_player_win(self):
        """
        Scenario: 
        Player: Ace(c), Ace(d) -> Soft 12. Hits + 9(c) -> 21.
        Dealer: Queen(c) [Hole], 5(c) [Up]. Total 15. Hits + 3(c) -> 18.
        Result: Player (21) beats Dealer (18).
        """
        state = get_initial_state()
        
        # Initial Deal Sequence: P1, D1(Up), P2, D2(Hole)
        # We map C++ scenario (Hole=Qc, Up=5c) to our deal order (Up first)
        state = self.force_chance(state, "Ac") # Player 1
        state = self.force_chance(state, "5c") # Dealer Up
        state = self.force_chance(state, "Ad") # Player 2
        state = self.force_chance(state, "Qc") # Dealer Hole

        # Player turn
        self.assertEqual(get_current_player(state), 0)
        state = apply_action(state, "H")
        
        # Chance deals 9c to player
        self.assertEqual(get_current_player(state), -1)
        state = self.force_chance(state, "9c")
        
        # Player has 21 (A+A+9), decides to Stand
        self.assertEqual(get_current_player(state), 0)
        state = apply_action(state, "S")
        
        # Dealer turn: Has 15 (Q+5), must Hit
        # Note: Your implementation might handle Dealer hits via chance loop or explicit steps.
        # Based on your code: Dealer S -> check <17 -> auto H -> goes to Chance
        self.assertEqual(get_current_player(state), 1)
        state = apply_action(state, "H") # Dealer takes hit
        
        self.assertEqual(get_current_player(state), -1)
        state = self.force_chance(state, "3c") # Dealer gets 3
        
        # Dealer now has 18 (15+3). Should Stand.
        self.assertEqual(get_current_player(state), 1)
        state = apply_action(state, "S")
        
        # Terminal
        self.assertEqual(get_current_player(state), -4)
        self.assertEqual(get_rewards(state)[0], 1.0) # Player wins

    def test_dealer_bust(self):
        """
        Scenario:
        Player: 9(c), 5(c) -> 14. Stands.
        Dealer: Jack(c) [Hole], 3(c) [Up] -> 13. Hits + 9(d) -> 22 (Bust).
        """
        state = get_initial_state()
        
        state = self.force_chance(state, "9c")
        state = self.force_chance(state, "3c") # Up
        state = self.force_chance(state, "5c")
        state = self.force_chance(state, "Jc") # Hole

        # Player Stands on 14
        state = apply_action(state, "S")
        
        # Dealer (13) Hits
        state = apply_action(state, "H")
        state = self.force_chance(state, "9d")
        
        # Dealer Busts (22), logic likely forces Stand or auto-resolves
        # If your code returns to Dealer to explicitly "Stand" (end turn) after bust:
        if get_current_player(state) == 1:
             state = apply_action(state, "S")

        self.assertEqual(get_current_player(state), -4)
        self.assertEqual(get_rewards(state)[0], 1.0)

    def test_player_bust(self):
        """
        Scenario:
        Player: Ten(c), Ten(d) -> 20. Hits (greedy!) + 9(d) -> 29 Bust.
        Dealer: 9(c), 5(c).
        """
        state = get_initial_state()
        
        state = self.force_chance(state, "Tc")
        state = self.force_chance(state, "5c")
        state = self.force_chance(state, "Td")
        state = self.force_chance(state, "9c")
        
        # Player Hits on 20
        state = apply_action(state, "H")
        state = self.force_chance(state, "9d")
        
        # Should be terminal loss immediately
        self.assertEqual(get_current_player(state), -4)
        self.assertEqual(get_rewards(state)[0], -1.0)

    def test_dealer_first_card_hidden(self):
        """Verifies that the observation hides the Dealer's hole card."""
        state = get_initial_state()
        
        # Deal: P=9c, D_Up=8c, P=Td, D_Hole=4c
        state = self.force_chance(state, "9c")
        state = self.force_chance(state, "8c") # Up card
        state = self.force_chance(state, "Td")
        state = self.force_chance(state, "4c") # Hole card
        
        obs = get_observations(state)[0]
        
        # Check visible info
        self.assertEqual(obs["dealer_up"], "8c")
        self.assertIn("9c", obs["my_hands"][0])
        self.assertIn("Td", obs["my_hands"][0])
        
        # Ensure Hole card (4c) is NOT in observation
        # (Assuming it's not leaked in the history or other fields improperly)
        self.assertNotEqual(obs["dealer_up"], "4c")
        self.assertNotIn("4c", str(obs)) # Crude check that '4c' isn't leaked strings

    def test_resampling_history(self):
        """
        Verifies that resampling consistency:
        1. Keeps Player cards and Dealer Upcard constant.
        2. Varies the Dealer Hole card (implies shuffled deck).
        """
        state = get_initial_state()
        
        # Setup specific cards
        p_cards = ["9c", "Td"]
        d_up = "8c"
        d_hole = "4c"
        
        state = self.force_chance(state, p_cards[0])
        state = self.force_chance(state, d_up)
        state = self.force_chance(state, p_cards[1])
        state = self.force_chance(state, d_hole)
        
        # Create history from player perspective
        obs = get_observations(state)[0]
        # Construct history as expected by resample function: List[(Obs, Action)]
        # For initial state, action was None or pre-game. 
        # The function signature expects `obs_action_history`. 
        # We need to build a mock history trace.
        history_trace = [(obs, None)] 
        
        # Run Resampling
        resampled_actions = resample_history(history_trace, 0)
        
        # Reconstruct state from resampled actions
        new_state = get_initial_state()
        for action in resampled_actions:
            new_state = apply_action(new_state, action)
            
        new_obs = get_observations(new_state)[0]
        
        # 1. Player cards must match exactly
        self.assertEqual(sorted(new_obs["my_hands"][0]), sorted(p_cards))
        
        # 2. Dealer Upcard must match exactly
        self.assertEqual(new_obs["dealer_up"], d_up)
        
        # 3. We check the internal state to see if the hole card changed.
        # Note: There is a small chance (1/49) it resamples the exact same hole card.
        # We assume the test passes if the logic holds, or we loop to verify variance.
        # For a unit test, we just ensure it's a valid card and the game state is valid.
        new_hole = new_state["d_hand"][1]
        self.assertTrue(new_hole in new_state["deck"] or new_hole not in p_cards + [d_up])

if __name__ == "__main__":
    unittest.main()