import random
import copy
from typing import Any, List, Dict, Optional, Tuple

# Type definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game Constants
RANKS = ['A', 'K', 'Q', 'J']
SUITS = ['s', 'h', 'd', 'c']
RANK_VAL = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}
FULL_DECK = [r + s for r in RANKS for s in SUITS]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == -1: return "Chance"
    if player_id == -4: return "Terminal"
    return f"Player {player_id}"

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "phase": "DEAL",           # phases: DEAL, PLAY, RESOLVE, TERMINAL
        "turn": -1,                # -1 (Chance), 0, 1
        "p0_hand": [],
        "p1_hand": [],
        "p0_draw": [],
        "p1_draw": [],
        "p0_win": [],
        "p1_win": [],
        "pot": [],                 # Cards currently at stake
        "staged": {},              # Cards selected by players this round {0: 'Ah', 1: 'Ks'}
        "history": [],             # List of actions taken
        "winner": None,
        "terminal": False
    }

def _get_deck_from_action(action: str) -> List[str]:
    """Parses 'deal:c1,c2...' into a list of cards."""
    return action.split(":")[1].split(",")

def _check_game_over_conditions(state: State) -> State:
    """Checks win conditions and updates terminal status."""
    # Condition 1: One player has all 16 cards (in hand + draw + win + pot + staged)
    # Simplified: If one player has 0 cards everywhere, the other wins. 
    # However, the rules specifically say "possesses all 16 cards". 
    # We check totals.
    
    def count_total(pid):
        h = state[f"p{pid}_hand"]
        d = state[f"p{pid}_draw"]
        w = state[f"p{pid}_win"]
        # Note: pot and staged are in limbo, effectively not possessed until won
        return len(h) + len(d) + len(w)

    p0_total = count_total(0)
    p1_total = count_total(1)
    
    # Check total possession (only valid if pot/staged is empty, otherwise game continues)
    if not state["pot"] and not state["staged"]:
        if p0_total == 16:
            state["winner"] = 0
            state["terminal"] = True
            return state
        if p1_total == 16:
            state["winner"] = 1
            state["terminal"] = True
            return state

    # Condition 2 is handled during gameplay (inability to draw/burn)
    return state

def _resolve_game_over_by_depletion(state: State) -> State:
    """Ends game by win pile count when draw pile is depleted and action fails."""
    state["terminal"] = True
    p0_score = len(state["p0_win"])
    p1_score = len(state["p1_win"])
    
    if p0_score > p1_score:
        state["winner"] = 0
    elif p1_score > p0_score:
        state["winner"] = 1
    else:
        state["winner"] = None # Draw
    return state

def _replenish_hands(state: State) -> State:
    """Draws cards from draw pile to hand until 3 cards or draw pile empty."""
    for pid in [0, 1]:
        while len(state[f"p{pid}_hand"]) < 3:
            if not state[f"p{pid}_draw"]:
                # Rule: If required to draw but cannot -> Game Over
                return _resolve_game_over_by_depletion(state)
            
            card = state[f"p{pid}_draw"].pop(0)
            state[f"p{pid}_hand"].append(card)
    return state

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if state["terminal"]:
        return state
        
    new_state = copy.deepcopy(state)
    new_state["history"].append(action)

    # --- CHANCE PHASE ---
    if new_state["turn"] == -1:
        deck = _get_deck_from_action(action)
        # Setup: Deal 8 to each
        new_state["p0_draw"] = deck[:8]
        new_state["p1_draw"] = deck[8:]
        
        # Form Hands (Draw top 3)
        # Note: We perform the initial draw manually to avoid depletion logic triggering early
        for _ in range(3):
            new_state["p0_hand"].append(new_state["p0_draw"].pop(0))
            new_state["p1_hand"].append(new_state["p1_draw"].pop(0))
            
        new_state["turn"] = 0 # Player 0 starts
        new_state["phase"] = "PLAY"
        return new_state

    # --- PLAYER PLAY PHASE ---
    player = new_state["turn"]
    card = action.replace("play:", "")
    
    # Remove from hand, add to staged
    new_state[f"p{player}_hand"].remove(card)
    new_state["staged"][player] = card

    if player == 0:
        new_state["turn"] = 1 # Wait for P1
    else:
        # Both players have selected. Proceed to Resolution.
        # We process resolution immediately here.
        c0 = new_state["staged"][0]
        c1 = new_state["staged"][1]
        
        # Move staged to pot temporarily for easier logic
        current_battle_cards = [c0, c1]
        
        r0 = RANK_VAL[c0[0]]
        r1 = RANK_VAL[c1[0]]
        
        if r0 > r1:
            # P0 Wins
            winnings = new_state["pot"] + current_battle_cards
            new_state["p0_win"].extend(winnings)
            new_state["pot"] = []
            new_state["staged"] = {}
            new_state = _replenish_hands(new_state)
            if not new_state["terminal"]: new_state["turn"] = 0
            
        elif r1 > r0:
            # P1 Wins
            winnings = new_state["pot"] + current_battle_cards
            new_state["p1_win"].extend(winnings)
            new_state["pot"] = []
            new_state["staged"] = {}
            new_state = _replenish_hands(new_state)
            if not new_state["terminal"]: new_state["turn"] = 0
            
        else:
            # Tie - Showdown
            new_state["pot"].extend(current_battle_cards)
            new_state["staged"] = {}
            
            # Burn Phase
            # Each player must burn 1 face down. If they can't -> Game Over
            for pid in [0, 1]:
                if not new_state[f"p{pid}_draw"]:
                     return _resolve_game_over_by_depletion(new_state)
                burn_card = new_state[f"p{pid}_draw"].pop(0)
                new_state["pot"].append(burn_card)
            
            # Note: Do NOT replenish hands during showdown steps.
            # Players play from remaining hand.
            # Repeat loop: Back to P0 input for battle card
            new_state["turn"] = 0
            
    return _check_game_over_conditions(new_state)

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    if state["terminal"]: return -4
    return state["turn"]

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player from their last action."""
    if not state["terminal"]:
        return [0.0, 0.0]
    if state["winner"] == 0:
        return [1.0, -1.0]
    elif state["winner"] == 1:
        return [-1.0, 1.0]
    return [0.0, 0.0] # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions that can be taken in current state."""
    if state["terminal"]:
        return []

    if state["turn"] == -1:
        # Return a deterministic sorted deck for the deal
        # Game variety comes from player card choices, not deal randomness
        deck = sorted(FULL_DECK)
        return [f"deal:{','.join(deck)}"]

    player = state["turn"]
    hand = state[f"p{player}_hand"]
    return [f"play:{c}" for c in hand]

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns the observation for player."""
    # Observations must exclude opponent's private info
    
    # Common public info
    public_obs = {
        "p0_draw_count": len(state["p0_draw"]),
        "p1_draw_count": len(state["p1_draw"]),
        "p0_win_count": len(state["p0_win"]),
        "p1_win_count": len(state["p1_win"]),
        "pot": state["pot"],
        "history": state["history"], # Full action history is public (moves are revealed eventually)
        "terminal": state["terminal"],
        "winner": state["winner"]
    }
    
    obs = []
    for pid in [0, 1]:
        p_obs = copy.deepcopy(public_obs)
        p_obs["my_hand"] = state[f"p{pid}_hand"]
        p_obs["my_id"] = pid
        
        # Handle hidden staged cards
        # If P0 has moved and it's P1's turn, P1 shouldn't know WHAT P0 played yet.
        # If P1 has moved (and we are resolving), cards are revealed.
        # In this implementation, apply_action resolves immediately after P1 moves,
        # so if we are in get_observations, it's either P0's turn (start of round)
        # or P1's turn (P0 has acted).
        
        if state["turn"] == 1:
            if pid == 1:
                # P1 is acting, P0 has acted. P1 sees P0 acted, but not the card?
                # The rules say "Simultaneously... place face down". 
                # So P1 knows P0 committed, but not the card.
                # Since 'history' contains "play:Card", we must mask the last element
                # if it belongs to P0 and we are P1.
                if p_obs["history"] and p_obs["history"][-1].startswith("play:"):
                    p_obs["history"][-1] = "play:?" 
            elif pid == 0:
                # P0 is waiting. Knows their own staged card.
                pass
                
        obs.append(p_obs)
    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's observation."""
    if not obs_action_history:
        return []

    last_obs, last_action = obs_action_history[-1]
    obs_history = last_obs.get("history", [])

    # Use the deterministic sorted deck (must match get_legal_actions)
    deck = sorted(FULL_DECK)
    deal_action = f"deal:{','.join(deck)}"

    # For play:? masked actions, we need to sample valid opponent cards
    # With sorted deck: P0 gets first 8, P1 gets last 8
    opp_id = 1 - player_id
    if opp_id == 0:
        opp_initial_cards = deck[:8]  # P0 gets first 8
    else:
        opp_initial_cards = deck[8:]  # P1 gets last 8

    # Track opponent's remaining cards (for sampling play:?)
    opp_remaining = list(opp_initial_cards)

    # Build the play action sequence, replacing play:? with sampled opponent actions
    play_actions = []
    for action in obs_history:
        if action.startswith("deal:"):
            continue  # Skip the deal, we'll add it at the start
        if action == "play:?":
            # Sample an opponent action from their remaining cards
            if opp_remaining:
                sampled_card = random.choice(opp_remaining)
                opp_remaining.remove(sampled_card)
                play_actions.append(f"play:{sampled_card}")
        elif action.startswith("play:"):
            play_actions.append(action)
            # Remove card from opponent's pool if it's theirs
            card = action.replace("play:", "")
            if card in opp_remaining:
                opp_remaining.remove(card)

    # Add the player's final action if not in history yet
    # (observation is captured BEFORE the action is taken)
    if last_action is not None:
        play_actions.append(last_action)

    return [deal_action] + play_actions