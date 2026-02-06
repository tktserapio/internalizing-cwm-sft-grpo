import random
from typing import Any, Dict, List, Optional, Tuple

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game Constants
CARDS = ["J", "Q", "K"]
RANKS = {"J": 0, "Q": 1, "K": 2}
CHANCE_ID = -1
TERMINAL_ID = -4

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "history": [],              # List of actions: [deal, action1, action2...]
        "cards": [],                # [P0_card, P1_card] populated by chance
        "current_player": CHANCE_ID,
        "is_terminal": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = state.copy()
    new_state["history"] = state["history"] + [action]

    # --- Chance Node ---
    if state["current_player"] == CHANCE_ID:
        new_state["cards"] = [action[0], action[1]]
        new_state["current_player"] = 0
        return new_state

    # --- Player Logic ---
    if action == "F":
        new_state["is_terminal"] = True
        new_state["current_player"] = TERMINAL_ID
        return new_state

    bets = new_state["history"][1:]
    n = len(bets)

    # State Transitions (Standard Kuhn)
    # 1. C -> P1
    # 2. R -> P1
    # 3. CC -> Showdown
    # 4. CR -> P0
    # 5. RC -> Showdown
    # 6. CRC -> Showdown
    
    if n == 1:
        new_state["current_player"] = 1
    elif n == 2:
        if bets == ["C", "R"]:
            new_state["current_player"] = 0
        else:
            new_state["is_terminal"] = True # CC or RC
            new_state["current_player"] = TERMINAL_ID
    elif n == 3:
        new_state["is_terminal"] = True # CRC
        new_state["current_player"] = TERMINAL_ID

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    mapping = {0: "Player 1", 1: "Player 2", CHANCE_ID: "Chance", TERMINAL_ID: "Terminal"}
    return mapping.get(player_id, "?")

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player from their last action."""
    if not state["is_terminal"]:
        return [0.0, 0.0]

    bets = state["history"][1:]
    
    # 1. Fold Scenario (+1 to winner)
    if bets[-1] == "F":
        loser = (len(bets) - 1) % 2
        winner = 1 - loser
        return [1.0 if i == winner else -1.0 for i in range(2)]

    # 2. Showdown Scenario
    # Payoff is 2 if there was a bet (R), else 1
    p0, p1 = state["cards"]
    winner = 0 if RANKS[p0] > RANKS[p1] else 1
    payoff = 2.0 if "R" in bets else 1.0
    
    return [payoff if i == winner else -payoff for i in range(2)]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions compatible with Standard Kuhn Poker (OpenSpiel)."""
    if state["is_terminal"]: return []
    if state["current_player"] == CHANCE_ID:
        return [p0 + p1 for p0 in CARDS for p1 in CARDS if p0 != p1]

    bets = state["history"][1:]
    n = len(bets)
    
    # Rule: Cannot Fold if you can Check.
    if n == 0: 
        return ["C", "R"] # P0 Start
    
    last_action = bets[-1]
    
    if n == 1:
        # P1 response to P0
        if last_action == "C": return ["C", "R"] # Check -> Check/Bet
        if last_action == "R": return ["F", "C"] # Bet -> Fold/Call
        
    if n == 2: 
        # P0 response to P1 Raise (history must be C, R)
        return ["F", "C"]
        
    return []

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observation for player."""
    if state["current_player"] == CHANCE_ID:
        return [{}, {}]
        
    history = state["history"][1:]
    cards = state["cards"]
    
    return [
        {"card": cards[0], "history": history},
        {"card": cards[1], "history": history}
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view."""
    if not obs_action_history: return []

    # Look at the MOST RECENT observation (index -1), not the first one.
    last_obs, last_action = obs_action_history[-1]
    
    my_card = last_obs.get("card")
    betting_history = last_obs.get("history", [])
    
    # Logic to sample a consistent opponent card
    possible_opp_cards = [c for c in CARDS if c != my_card]
    opp_card = random.choice(possible_opp_cards)
    
    deal_str = (my_card + opp_card) if player_id == 0 else (opp_card + my_card)
    
    # Base history derived from the observation
    full_history = [deal_str] + betting_history
    
    # Append the final action the player took at this step.
    # The 'betting_history' inside the observation only includes events UP TO this moment.
    # It does not include the action 'last_action' which matches this observation.
    if last_action is not None:
        full_history.append(last_action)
        
    return full_history