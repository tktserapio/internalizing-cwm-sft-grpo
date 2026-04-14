import random
from typing import Any, List, Dict, Optional, Tuple

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game Constants
NUM_DICE = 3
SIDES = 6
WILD = 1  # 1s are wild

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "dice": [[], []],           # [P0_dice, P1_dice]
        "history": [],              # List of actions taken
        "current_player": -1,       # Starts with Chance to roll dice
        "dice_queue": [0]*NUM_DICE + [1]*NUM_DICE, # Who needs to roll next
        "last_bid": None,           # (quantity, face)
        "terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    if state["terminal"]:
        raise ValueError("Action taken in terminal state")

    # Create deep copy for new state
    new_state = {
        "dice": [list(d) for d in state["dice"]],
        "history": state["history"] + [action],
        "current_player": state["current_player"],
        "dice_queue": list(state["dice_queue"]),
        "last_bid": state["last_bid"],
        "terminal": False,
        "winner": None
    }

    # Handle CHANCE Actions (Rolling)
    if action.startswith("roll:"):
        val = int(action.split(":")[1])
        player_idx = new_state["dice_queue"].pop(0)
        new_state["dice"][player_idx].append(val)
        
        # Determine next player
        if new_state["dice_queue"]:
            new_state["current_player"] = -1
        else:
            new_state["current_player"] = 0 # Betting starts with P0
        return new_state

    # Handle PLAYER Actions
    player = state["current_player"]
    
    if action == "liar":
        # Resolution Phase
        last_q, last_f = state["last_bid"]
        
        # Count dice (including wilds)
        all_dice = new_state["dice"][0] + new_state["dice"][1]
        count = sum(1 for d in all_dice if d == last_f or d == WILD)
        
        # Determine winner
        # If actual count < bid, Bidder (prev player) loses -> Challenger (current) wins
        # If actual count >= bid, Bidder wins -> Challenger loses
        bidder = 1 - player
        if count < last_q:
            new_state["winner"] = player # Challenger wins
        else:
            new_state["winner"] = bidder # Bidder wins
            
        new_state["terminal"] = True
        new_state["current_player"] = -4
        return new_state

    # Handle Bid Actions "bid:Q:F"
    parts = action.split(":")
    q, f = int(parts[1]), int(parts[2])
    new_state["last_bid"] = (q, f)
    new_state["current_player"] = 1 - player # Switch turn
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == -1: return "Chance"
    if player_id == -4: return "Terminal"
    return f"Player_{player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player from their last action."""
    if state["winner"] == 0:
        return [1.0, -1.0]
    elif state["winner"] == 1:
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions that can be taken in current state."""
    if state["terminal"]:
        return []

    # Chance Actions
    if state["current_player"] == -1:
        # Chance can roll any face 1-6
        return [f"roll:{i}" for i in range(1, SIDES + 1)]

    # Player Actions
    last_bid = state["last_bid"]
    actions = []

    # Can challenge if there is a previous bid
    if last_bid is not None:
        actions.append("liar")
    
    # Generate valid bids
    # Minimal logic: Q must increase OR Same Q + Higher Face
    # Cap Q at 2 * NUM_DICE to keep action space finite/compact
    current_q = 0 if last_bid is None else last_bid[0]
    current_f = 0 if last_bid is None else last_bid[1]
    
    max_q = NUM_DICE * 2
    
    for q in range(current_q, max_q + 1):
        start_f = (current_f + 1) if q == current_q else 1
        # Skip q=0 cases
        if q == 0: continue
        
        for f in range(start_f, SIDES + 1):
            actions.append(f"bid:{q}:{f}")
            
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observation for player."""
    # Filter history to only include publicly observable actions (bids, liar)
    # Dice rolls are hidden information
    public_history = [a for a in state["history"] if not a.startswith("roll:")]

    # Common public info
    public_info = {
        "history": public_history,
        "last_bid": state["last_bid"],
        "num_dice": [len(state["dice"][0]), len(state["dice"][1])],
        "terminal": state["terminal"]
    }

    obs = []
    for p in [0, 1]:
        p_obs = public_info.copy()
        p_obs["my_dice"] = list(state["dice"][p])  # Can only see own dice
        p_obs["player_id"] = p
        obs.append(p_obs)

    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """
    Reconstructs a history consistent with player_id's observations.
    Opponent's chance outcomes are randomized; Player's chance outcomes are fixed from obs.
    """
    if not obs_action_history:
        return []

    # Get the player's dice from the last observation that has all dice rolled
    my_dice = []
    for obs, _ in reversed(obs_action_history):
        candidate = obs.get("my_dice", [])
        if candidate:
            my_dice = list(candidate)
            break

    if not my_dice:
        return []

    # Get the public action history from the last observation
    # This contains only bids and liar calls (rolls are hidden)
    # Note: obs["history"] is captured BEFORE the action, so we need to add
    # the final action from obs_action_history
    public_history = []
    last_action = None
    for obs, action in reversed(obs_action_history):
        if obs.get("history") is not None:
            public_history = list(obs["history"])
            last_action = action
            break

    # Add the final action if it exists (it's not in obs["history"] yet)
    if last_action is not None:
        public_history.append(last_action)

    # Generate the dice roll actions first
    # Dice queue is [0, 0, 0, 1, 1, 1] - P0 rolls first, then P1
    generated_actions = []

    num_my_dice = len(my_dice)
    num_opp_dice = obs_action_history[-1][0].get("num_dice", [NUM_DICE, NUM_DICE])[1 - player_id]

    # P0's dice rolls
    p0_count = num_my_dice if player_id == 0 else num_opp_dice
    for i in range(p0_count):
        if player_id == 0:
            generated_actions.append(f"roll:{my_dice[i]}")
        else:
            generated_actions.append(f"roll:{random.randint(1, SIDES)}")

    # P1's dice rolls
    p1_count = num_my_dice if player_id == 1 else num_opp_dice
    for i in range(p1_count):
        if player_id == 1:
            generated_actions.append(f"roll:{my_dice[i]}")
        else:
            generated_actions.append(f"roll:{random.randint(1, SIDES)}")

    # Append the public actions (bids, liar)
    generated_actions.extend(public_history)

    return generated_actions