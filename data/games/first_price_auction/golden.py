from typing import Any, Dict, List, Optional, Tuple
import random

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, CHANCE, TERMINAL = 0, 1, -1, -4
VALUATIONS = [1, 2, 3, 4, 5]
BID_RANGE = [0, 1, 2, 3, 4, 5]

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "valuations": [],  # [P0_valuation, P1_valuation]
        "bids": [],        # [P0_bid, P1_bid]
        "current_player": CHANCE,
        "is_terminal": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "valuations": state["valuations"].copy() if state["valuations"] else [],
        "bids": state["bids"].copy() if state["bids"] else [],
        "current_player": state["current_player"],
        "is_terminal": state["is_terminal"]
    }

    if state["current_player"] == CHANCE:
        # Parse valuation deal "VxVy"
        v0, v1 = int(action[0]), int(action[1])
        new_state["valuations"] = [v0, v1]
        new_state["current_player"] = P0
    elif state["current_player"] == P0:
        # Parse bid "bid_N"
        bid = int(action.split("_")[1])
        new_state["bids"] = [bid]
        new_state["current_player"] = P1
    elif state["current_player"] == P1:
        bid = int(action.split("_")[1])
        new_state["bids"] = state["bids"] + [bid]
        new_state["current_player"] = TERMINAL
        new_state["is_terminal"] = True

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    names = {P0: "Player 0", P1: "Player 1", CHANCE: "Chance", TERMINAL: "Terminal"}
    return names.get(player_id, "Unknown")

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    if not state["is_terminal"]:
        return [0.0, 0.0]

    v0, v1 = state["valuations"]
    b0, b1 = state["bids"]

    # Determine winner (P0 wins ties)
    if b0 >= b1:
        winner = P0
        winning_bid = b0
        winner_valuation = v0
    else:
        winner = P1
        winning_bid = b1
        winner_valuation = v1

    # Winner gets valuation - bid, loser gets negative of that (zero-sum normalization)
    winner_utility = float(winner_valuation - winning_bid)
    rewards = [0.0, 0.0]
    rewards[winner] = winner_utility / 2
    rewards[1 - winner] = -winner_utility / 2
    return rewards

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    if state["current_player"] == CHANCE:
        # All possible valuation pairs
        return [f"{v0}{v1}" for v0 in VALUATIONS for v1 in VALUATIONS]

    # Player bids
    return [f"bid_{b}" for b in BID_RANGE]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Players see only their own valuation and bid."""
    if state["current_player"] == CHANCE:
        return [{}, {}]

    valuations = state["valuations"]
    bids = state["bids"]

    if state["is_terminal"]:
        # At terminal, reveal all information
        return [
            {"my_valuation": valuations[0], "my_bid": bids[0],
             "opponent_valuation": valuations[1], "opponent_bid": bids[1]},
            {"my_valuation": valuations[1], "my_bid": bids[1],
             "opponent_valuation": valuations[0], "opponent_bid": bids[0]}
        ]

    # During play, players only see their valuation and their own bid
    p0_obs = {"my_valuation": valuations[0]}
    p1_obs = {"my_valuation": valuations[1]}

    if len(bids) >= 1:
        p0_obs["my_bid"] = bids[0]
    if len(bids) >= 2:
        p1_obs["my_bid"] = bids[1]

    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view."""
    if not obs_action_history:
        return []

    last_obs, last_action = obs_action_history[-1]
    my_valuation = last_obs.get("my_valuation")

    # Sample opponent's valuation uniformly
    opponent_valuation = random.choice(VALUATIONS)

    # Construct deal action
    if player_id == P0:
        deal = f"{my_valuation}{opponent_valuation}"
    else:
        deal = f"{opponent_valuation}{my_valuation}"

    history = [deal]

    # Add bids
    my_bid = last_obs.get("my_bid")
    opponent_bid = last_obs.get("opponent_bid")

    if player_id == P0:
        if my_bid is not None:
            history.append(f"bid_{my_bid}")
        if opponent_bid is not None:
            history.append(f"bid_{opponent_bid}")
        elif my_bid is not None:
            # Opponent has bid but we don't know it yet - sample
            history.append(f"bid_{random.choice(BID_RANGE)}")
    else:
        if opponent_bid is not None:
            history.append(f"bid_{opponent_bid}")
        else:
            # P0 has bid but we don't know it
            history.append(f"bid_{random.choice(BID_RANGE)}")
        if my_bid is not None:
            history.append(f"bid_{my_bid}")

    if last_action is not None and (not history or history[-1] != last_action):
        history.append(last_action)

    return history
