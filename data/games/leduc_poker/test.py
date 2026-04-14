import unittest
import random
from typing import List, Dict, Any

# Assuming the game implementation is in a module named leduc_poker
from golden import *

# For the purpose of this snippet, I assume the functions 
# defined in your previous prompt are available in the local namespace.

class TestLeducPoker(unittest.TestCase):

    def _play_random_game(self):
        """Helper to play a full game with random valid actions."""
        state = get_initial_state()
        while get_current_player(state) != -4:
            legal_actions = get_legal_actions(state)
            action = random.choice(legal_actions)
            state = apply_action(state, action)
        return state

    def test_random_simulation(self):
        """
        Adaptation of BasicLeducTests -> RandomSimTest.
        Runs 100 random games to ensure no crashes and valid terminal states.
        """
        for _ in range(100):
            final_state = self._play_random_game()
            
            # Check basic terminal properties
            self.assertEqual(get_current_player(final_state), -4)
            rewards = get_rewards(final_state)
            self.assertEqual(len(rewards), 2)
            # Zero-sum check
            self.assertAlmostEqual(sum(rewards), 0.0)

    def test_chance_outcomes(self):
        """
        Adaptation of BasicLeducTests -> ChanceOutcomesTest.
        Verifies that the deck behaves correctly (max 2 of each rank).
        """
        state = get_initial_state()
        # In this implementation, chance actions are strings like "deal:J"
        # We can simulate dealing all cards to ensure the deck composition is correct
        
        # Override deck to force all deals
        full_deck_deals = []
        while state['deck']:
            card = state['deck'][0]
            action = f"deal:{card}"
            full_deck_deals.append(card)
            # We manually manipulate state here just to check deck logic 
            # or simply rely on get_legal_actions for chance
            actions = get_legal_actions(state)
            if not actions: break
            # Pick the first available deal action
            state = apply_action(state, actions[0])

        # Count ranks
        counts = {'J': 0, 'Q': 0, 'K': 0}
        # We can inspect the history or the state's used cards
        # Since the state tracks the deck, let's verify the initial deck composition
        initial = get_initial_state()
        for card in initial['deck']:
            counts[card] += 1
            
        self.assertEqual(counts['J'], 2)
        self.assertEqual(counts['Q'], 2)
        self.assertEqual(counts['K'], 2)

    def test_resample_infostate(self):
        """
        Adaptation of BasicLeducTests -> ResampleInfostateTest.
        Ensures that resampling history produces a state consistent with the
        player's current observation.
        """
        for _ in range(10): # Run 10 times
            # 1. Play a random game until end
            state = get_initial_state()
            history_w_obs = [] # Store tuple of (Observation, Action)
            
            while get_current_player(state) != -4:
                cp = get_current_player(state)
                
                # Store observation before action if it's a player
                if cp >= 0:
                    obs = get_observations(state)[cp]
                    # We need the full history of (Obs, Action) for the resample function
                    # But the signature asks for a list of (Obs, Action|None)
                    # We will reconstruct this for the specific test player below
                    pass
                
                legal = get_legal_actions(state)
                action = random.choice(legal)
                state = apply_action(state, action)
            
            # 2. Pick a player to test (e.g., Player 0)
            player_id = 0
            
            # Reconstruct the (Observation, Action) history for Player 0
            # We must replay the game to capture observations at every step
            replay_state = get_initial_state()
            obs_history = []
            
            # Extract actions from the final state history
            # Filter out chance actions for the replay loop logic if necessary,
            # but apply_action handles them.
            full_action_history = [x[1] for x in state['history']]
            
            # Note: The state['history'] might not store chance actions in the same list 
            # depending on implementation details. The provided implementation 
            # stores (player, action) in history. Chance is -1.
            
            # Re-running to build the specific input format for resample_history
            for player, action in state['history']:
                if player == player_id:
                    # Capture obs before acting
                    obs = get_observations(replay_state)[player_id]
                    obs_history.append((obs, action))
                elif player != -1:
                    # Opponent action: we see the state before they act (waiting)
                    # But the resample signature usually implies "My Obs" + "My Action"
                    # or "My Obs" + "Incoming Action"?
                    # The prompt signature says: list[tuple[PlayerObservation, Action | None]]
                    # Usually this means: "At this observation, I took this action."
                    pass
                    
                replay_state = apply_action(replay_state, action)

            # If the player never acted, skip
            if not obs_history:
                continue
                
            # 3. Resample
            new_history_actions = resample_history(obs_history, player_id)
            
            # 4. Verify the new history results in the same private card for Player 0
            #    and matches public information.
            check_state = get_initial_state()
            for action in new_history_actions:
                check_state = apply_action(check_state, action)
                
            final_obs = get_observations(check_state)[player_id]
            original_last_obs = obs_history[-1][0]
            
            self.assertEqual(final_obs['private_card'], original_last_obs['private_card'])
            self.assertEqual(final_obs['public_card'], original_last_obs['public_card'])
            # Note: pot comparison omitted — original_last_obs captures state BEFORE
            # the last action, but resampled history includes the last action applied.

    def test_policies(self):
        """
        Adaptation of PolicyTest.
        Tests specific policies (Always Fold, Call, Raise) against each other.
        """
        policies = {
            "Fold": lambda s: "Fold",
            "Call": lambda s: "Call" if "Call" in get_legal_actions(s) else "Fold",
            "Raise": lambda s: "Raise" if "Raise" in get_legal_actions(s) else "Call"
        }

        # Matrix of policies to test
        for p1_name, p1_pol in policies.items():
            for p2_name, p2_pol in policies.items():
                state = get_initial_state()
                while get_current_player(state) != -4:
                    cp = get_current_player(state)
                    if cp == -1: # Chance
                        action = random.choice(get_legal_actions(state))
                    elif cp == 0:
                        action = p1_pol(state)
                    else:
                        action = p2_pol(state)
                    
                    # Safety fallback if policy returns illegal action (e.g. Raise when capped)
                    if action not in get_legal_actions(state):
                        action = "Call" if "Call" in get_legal_actions(state) else "Fold"
                        
                    state = apply_action(state, action)
                
                # Check for clean finish
                self.assertEqual(get_current_player(state), -4)

    def test_game_flow_fixed_scenario(self):
        """
        Adaptation of StartingPlayerTest.
        Since we cannot change the starting player (always P1/SB), we test
        a specific 'Happy Path' to ensure state transitions are correct.
        
        Trajectory:
        1. Deal P1: J, P2: K
        2. P1 Calls (Preflop)
        3. P2 Raises
        4. P1 Calls
        5. Flop Deal: Q
        6. P1 Checks (Call)
        7. P2 Checks (Call) -> Showdown
        """
        state = get_initial_state()
        
        # 1. Deals
        state = apply_action(state, "deal:J") # P1
        state = apply_action(state, "deal:K") # P2
        self.assertEqual(get_current_player(state), 0) # P1 acts first
        self.assertEqual(state['pot'], 3) # SB(1) + BB(2)

        # 2. P1 Calls
        state = apply_action(state, "Call") 
        self.assertEqual(state['pot'], 4) # 1+1 + 2
        self.assertEqual(get_current_player(state), 1) # P2 Turn

        # 3. P2 Raises
        # P2 is currently at 2. Raise adds 2 more (total 4).
        state = apply_action(state, "Raise")
        self.assertEqual(state['pot'], 6) # 2 + 4
        self.assertEqual(get_current_player(state), 0) # Back to P1

        # 4. P1 Calls
        # P1 is at 2. Must match 4. Adds 2.
        state = apply_action(state, "Call")
        self.assertEqual(state['pot'], 8) # 4 + 4
        
        # End of Round 1. 
        self.assertEqual(get_current_player(state), -1) # Chance node for Flop

        # 5. Flop Deal
        state = apply_action(state, "deal:Q")
        self.assertEqual(state['round'], 2)
        self.assertEqual(get_current_player(state), 0) # P1 starts Post-flop

        # 6. P1 Checks (Call 0)
        state = apply_action(state, "Call")
        self.assertEqual(get_current_player(state), 1)

        # 7. P2 Checks (Call 0) -> Showdown
        state = apply_action(state, "Call")
        self.assertEqual(get_current_player(state), -4) # Terminal

        # Check Winner
        # P1: J + Q (Public) -> High Card Q
        # P2: K + Q (Public) -> High Card K
        # P2 wins. 
        # P2 invested 4. Won 8. Net +4.
        # P1 invested 4. Lost. Net -4.
        rewards = get_rewards(state)
        self.assertEqual(rewards, [-4.0, 4.0])

if __name__ == '__main__':
    unittest.main()