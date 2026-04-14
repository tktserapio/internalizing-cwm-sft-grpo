import unittest
import random
from collections import deque
import golden as kuhn_poker  # Assuming your implementation is in kuhn_poker.py
import copy

class TestKuhnPoker(unittest.TestCase):

    def test_initial_state(self):
        """Verify the game starts correctly (Chance node)."""
        state = kuhn_poker.get_initial_state()
        self.assertEqual(kuhn_poker.get_current_player(state), -1)
        self.assertFalse(state["is_terminal"])
        self.assertEqual(len(state["history"]), 0)

    def test_random_simulation(self):
        """Simulate random games to check for crashes and valid transitions."""
        for _ in range(100):
            state = kuhn_poker.get_initial_state()
            while not state["is_terminal"]:
                legal = kuhn_poker.get_legal_actions(state)
                self.assertTrue(len(legal) > 0, "Non-terminal state must have actions")
                
                # Verify chance actions format
                if kuhn_poker.get_current_player(state) == -1:
                    for action in legal:
                        self.assertIn(action, ["JK", "JQ", "KJ", "KQ", "QJ", "QK"])
                
                action = random.choice(legal)
                state = kuhn_poker.apply_action(state, action)
            
            # Verify terminal state properties
            rewards = kuhn_poker.get_rewards(state)
            self.assertEqual(sum(rewards), 0.0, "Zero-sum game check")
            self.assertIn(abs(rewards[0]), [1.0, 2.0], "Valid payoffs are 1 or 2")

    def test_count_states(self):
        """
        Equivalent to OpenSpiel's CountStates().
        BFS to traverse the entire game tree and count non-chance states.
        Expected: 6 deals * 9 betting sequences = 54 states.
        """
        queue = deque([kuhn_poker.get_initial_state()])
        count = 0
        seen_histories = set()

        while queue:
            state = queue.popleft()
            
            # Use tuple history as unique key
            hist_key = tuple(state["history"])
            if hist_key in seen_histories:
                continue
            seen_histories.add(hist_key)

            if not state["is_terminal"]:
                # Count if it's a Player node (not Chance)
                if kuhn_poker.get_current_player(state) >= 0:
                    count += 1
                
                for action in kuhn_poker.get_legal_actions(state):
                    queue.append(kuhn_poker.apply_action(state, action))
        
        # OpenSpiel counts 54 states. 
        # Logic: 6 possible deals.
        # Betting Tree per deal:
        # 1. Root (P0)
        # 2. P0 Check -> P1
        # 3. P0 Bet -> P1
        # 4. P0 Check, P1 Bet -> P0
        # Terminal nodes are NOT included in this specific count in OpenSpiel usually,
        # but let's check your implementation's tree structure.
        # Your tree for one deal (e.g., JK):
        # [] (P0)
        # [C] (P1)
        # [R] (P1)
        # [C, R] (P0)
        # Terminals: [C, C], [C, R, C], [C, R, F], [R, C], [R, F], [F]
        # Total player nodes per deal = 4.
        # Total deals = 6.
        # Total player nodes = 24.
        
        # WAIT: The C++ test says 54. Let's look at the comment:
        # "6 deals * 9 betting sequences (-, p, b, pp, pb, bp, bb, pbp, pbb)"
        # Note: p=pass(check), b=bet.
        # - (Root)
        # p (Check)
        # b (Bet)
        # pp (Check, Check - Terminal)
        # pb (Check, Bet)
        # bp (Bet, Call - Terminal)
        # bb (Bet, Raise? Kuhn doesn't allow re-raise. 'bb' likely means Bet/Call?) 
        # Actually Kuhn has: 
        # 1. Root
        # 2. C
        # 3. R
        # 4. CC (T)
        # 5. CR
        # 6. RF (T)
        # 7. RC (T)
        # 8. CRC (T)
        # 9. CRF (T)
        
        # If we include terminals in the count:
        # 1(Root) + 1(C) + 1(R) + 1(CR) = 4 decision nodes per deal.
        # Terminals: CC, RF, RC, CRC, CRF = 5 terminals per deal.
        # Total = 9 states per deal.
        # 9 * 6 = 54. 
        # So we must count ALL nodes (Decision + Terminal) excluding Chance.
        
        # Reset count to verify exact 54
        queue = deque([kuhn_poker.get_initial_state()])
        count = 0
        seen_histories = set()

        while queue:
            state = queue.popleft()
            hist_key = tuple(state["history"])
            if hist_key in seen_histories: continue
            seen_histories.add(hist_key)

            if kuhn_poker.get_current_player(state) != -1:
                count += 1 # Count Decision AND Terminal nodes

            if not state["is_terminal"]:
                for action in kuhn_poker.get_legal_actions(state):
                    queue.append(kuhn_poker.apply_action(state, action))

        print(f"Total non-chance states found: {count}")
        self.assertEqual(count, 54)

    def test_specific_trajectory(self):
        """Test the specific example from the prompt description."""
        # Step 0: Chance
        s = kuhn_poker.get_initial_state()
        s = kuhn_poker.apply_action(s, "KJ") # Deal K to P0, J to P1
        
        # Step 1: P0 acts
        self.assertEqual(kuhn_poker.get_current_player(s), 0)
        s = kuhn_poker.apply_action(s, "Call") # Check

        # Step 2: P1 acts
        self.assertEqual(kuhn_poker.get_current_player(s), 1)
        s = kuhn_poker.apply_action(s, "Raise") # Bet

        # Step 3: P0 acts (facing bet)
        self.assertEqual(kuhn_poker.get_current_player(s), 0)
        legal = kuhn_poker.get_legal_actions(s)
        self.assertEqual(set(legal), {"Fold", "Call"})
        s = kuhn_poker.apply_action(s, "Call") # Call
        
        # Step 4: Terminal
        self.assertTrue(s["is_terminal"])
        rewards = kuhn_poker.get_rewards(s)
        # Pot: Ante(1+1) + Bet(1+1) = 4. Winner gets +2 profit.
        # P0 (K) vs P1 (J) -> P0 wins.
        self.assertEqual(rewards[0], 2.0)
        self.assertEqual(rewards[1], -2.0)

    def test_resample_history(self):
        """Test the imperfect information resampling."""
        # Create a state: P0 has J, P1 has K. P0 Checks.
        # P1 observes: Own card K, History [C].
        # P1 doesn't know P0 has J. Could be Q.
        
        # 1. Setup the true state
        s = kuhn_poker.get_initial_state()
        s = kuhn_poker.apply_action(s, "JK") # Deal J, K
        s = kuhn_poker.apply_action(s, "Call")  # P0 Checks
        
        # 2. Get P1 observation
        obs = kuhn_poker.get_observations(s)[1] # P1 index 1
        
        # 3. Create observation history for resampling
        # (Obs, Action) tuples. 
        # Start of game: (Obs_start, "C") -> This is tricky in the compact API.
        # Usually resampling takes a list of (Obs, Action) pairs experienced by the player.
        # P1 experienced: 
        #   t=0: (Card:K, Hist:[]), Action=None (It was P0's turn)
        #   t=1: (Card:K, Hist:[C]), Action=Current (No action taken yet)
        
        # Let's mock the input for resample_history based on the function sig:
        # obs_action_history: list[tuple[PlayerObservation, Action | None]]
        
        # P1's view of the history:
        # At start, P1 saw their card. P0 acted "C".
        history_input = [
            ({"card": "K", "history": []}, None) # P1 didn't act here
        ]
        
        # Resample
        possible_histories = []
        for _ in range(50):
            h = kuhn_poker.resample_history(history_input, 1)
            possible_histories.append(h)
            
        # P1 holds K. P0 must hold J or Q.
        # So "deal" action in history must be "JK" (if P0=J) or "QK" (if P0=Q).
        deals = [h[0] for h in possible_histories]
        self.assertTrue(all(d in ["JK", "QK"] for d in deals))
        self.assertIn("JK", deals)
        self.assertIn("QK", deals)

    def test_resample_consistency(self):
        """
        Verifies resample_history using the strict replay consistency check.
        """
        # 1. CHECK AVAILABILITY
        if not hasattr(kuhn_poker, 'resample_history'):
            print("\n[Skip] resample_history not implemented.")
            return

        # 2. GENERATE GROUND TRUTH TRAJECTORY
        # We play a random game to get a valid (Observations, Actions) sequence.
        state = kuhn_poker.get_initial_state()
        player_id = 1  # Testing Player 1's perspective
        
        obs_action_history = []
        true_history = [] # For debugging
        
        # Run the simulation
        while True:
            cp = kuhn_poker.get_current_player(state)
            if cp == -4: break # Terminal
            
            legal = kuhn_poker.get_legal_actions(state)
            action = random.choice(legal)
            
            # If it's our target player, record what they saw and did.
            if cp == player_id:
                raw_obs = kuhn_poker.get_observations(state)[player_id]
                # --- THE FIX: DEEPCOPY TO PREVENT MUTATION BUGS ---
                obs = copy.deepcopy(raw_obs) 
                obs_action_history.append((obs, action))
            
            state = kuhn_poker.apply_action(state, action)
            true_history.append(action)

        # Edge Case: If P1 never acted in this random seed, skip.
        if not obs_action_history:
            return

        # 3. RUN THE VERIFICATION LOGIC
        print(f"Verifying P{player_id} consistency on history: {true_history}")
        
        # Reset State for Replay
        state = kuhn_poker.get_initial_state()
        
        # Create an iterator for our expectations
        obs_iter = iter(obs_action_history)
        
        # Safely get the first expectation
        try:
            expected_obs, expected_action = next(obs_iter)
            has_expectations = True
        except StopIteration:
            has_expectations = False

        # Run the function under test
        # Note: We pass a deepcopy of the history to ensure the function doesn't mutate our test data
        resampled_actions = kuhn_poker.resample_history(copy.deepcopy(obs_action_history), player_id)

        # REPLAY LOOP
        for action in resampled_actions:
            
            # Check if we are at a step where the Target Player acts
            if kuhn_poker.get_current_player(state) == player_id:
                
                # Failure 1: Resampler generated extra moves for the player
                if not has_expectations:
                    self.fail(f"Resampled history contains extra moves for P{player_id}. Action: {action}")
                
                # Check A: Does the Replayed Observation match the Recorded Observation?
                actual_obs = kuhn_poker.get_observations(state)[player_id]
                self.assertEqual(actual_obs, expected_obs, 
                                f"Observation Mismatch!\nExpected: {expected_obs}\nActual:   {actual_obs}")
                
                # Check B: Does the Resampled Action match the Recorded Action?
                self.assertEqual(action, expected_action,
                                f"Action Mismatch!\nExpected: {expected_action}\nResampled: {action}")
                
                # Advance to the next expectation
                try:
                    expected_obs, expected_action = next(obs_iter)
                except StopIteration:
                    has_expectations = False

            # Apply the action to move the state forward
            state = kuhn_poker.apply_action(state, action)

        # Failure 2: Resampler generated too few moves (missed observations)
        if has_expectations:
            self.fail("Resampled history ended too early! It did not cover all recorded observations.")

if __name__ == '__main__':
    unittest.main()