from typing import Any, Dict, List, Optional, Tuple
import random

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, CHANCE, TERMINAL = 0, 1, -1, -4
ITEM_COUNTS = {"books": 2, "hats": 2, "balls": 2}
VALUE_RANGE = [0, 1, 2, 3]
MAX_ROUNDS = 10  # Prevent infinite negotiation

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "valuations": {},     # {"p0": [b,h,l], "p1": [b,h,l]}
        "current_proposal": None,  # {"proposer": 0/1, "division": [b,h,l]}
        "proposer": None,     # Who made the current proposal
        "current_player": CHANCE,
        "round": 0,
        "outcome": None,      # "accepted", "rejected", or None
        "is_terminal": False
    }

def _parse_valuation_action(action: str) -> Dict:
    """Parse 'v0_A_B_C_v1_D_E_F' into valuations dict."""
    parts = action.split("_")
    return {
        "p0": [int(parts[1]), int(parts[2]), int(parts[3])],
        "p1": [int(parts[5]), int(parts[6]), int(parts[7])]
    }

def _parse_proposal(action: str) -> List[int]:
    """Parse 'propose_X_Y_Z' into [books, hats, balls] for proposer."""
    parts = action.split("_")
    return [int(parts[1]), int(parts[2]), int(parts[3])]

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "valuations": state["valuations"].copy() if state["valuations"] else {},
        "current_proposal": state["current_proposal"],
        "proposer": state["proposer"],
        "current_player": state["current_player"],
        "round": state["round"],
        "outcome": state["outcome"],
        "is_terminal": state["is_terminal"]
    }

    if state["current_player"] == CHANCE:
        new_state["valuations"] = _parse_valuation_action(action)
        new_state["current_player"] = P0
        return new_state

    current = state["current_player"]

    if action == "accept":
        new_state["outcome"] = "accepted"
        new_state["is_terminal"] = True
        new_state["current_player"] = TERMINAL
    elif action == "reject":
        new_state["outcome"] = "rejected"
        new_state["is_terminal"] = True
        new_state["current_player"] = TERMINAL
    elif action.startswith("propose_"):
        division = _parse_proposal(action)
        new_state["current_proposal"] = division
        new_state["proposer"] = current
        new_state["current_player"] = 1 - current
        new_state["round"] = state["round"] + 1

        # Force end if max rounds reached
        if new_state["round"] >= MAX_ROUNDS:
            new_state["outcome"] = "rejected"
            new_state["is_terminal"] = True
            new_state["current_player"] = TERMINAL

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

    if state["outcome"] == "rejected":
        return [0.0, 0.0]

    # Accepted proposal
    proposal = state["current_proposal"]
    proposer = state["proposer"]
    vals = state["valuations"]

    # Proposer gets proposal amounts, other gets remainder
    proposer_items = proposal
    other_items = [
        ITEM_COUNTS["books"] - proposal[0],
        ITEM_COUNTS["hats"] - proposal[1],
        ITEM_COUNTS["balls"] - proposal[2]
    ]

    if proposer == P0:
        p0_items, p1_items = proposer_items, other_items
    else:
        p0_items, p1_items = other_items, proposer_items

    p0_reward = sum(p0_items[i] * vals["p0"][i] for i in range(3))
    p1_reward = sum(p1_items[i] * vals["p1"][i] for i in range(3))

    # Normalize to zero-sum by subtracting mean
    mean_reward = (p0_reward + p1_reward) / 2
    return [float(p0_reward - mean_reward), float(p1_reward - mean_reward)]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    if state["current_player"] == CHANCE:
        # Generate all valuation combinations (simplified: just a subset)
        actions = []
        for v0b in VALUE_RANGE:
            for v0h in VALUE_RANGE:
                for v0l in VALUE_RANGE:
                    for v1b in VALUE_RANGE:
                        for v1h in VALUE_RANGE:
                            for v1l in VALUE_RANGE:
                                actions.append(f"v0_{v0b}_{v0h}_{v0l}_v1_{v1b}_{v1h}_{v1l}")
        return actions

    actions = []

    # Can always reject
    actions.append("reject")

    # Can accept if there's a proposal from opponent
    if state["current_proposal"] is not None and state["proposer"] != state["current_player"]:
        actions.append("accept")

    # Can make any valid proposal
    for b in range(ITEM_COUNTS["books"] + 1):
        for h in range(ITEM_COUNTS["hats"] + 1):
            for l in range(ITEM_COUNTS["balls"] + 1):
                actions.append(f"propose_{b}_{h}_{l}")

    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Players see their own values and proposals."""
    if state["current_player"] == CHANCE:
        return [{}, {}]

    vals = state["valuations"]

    base_obs = {
        "current_proposal": state["current_proposal"],
        "proposer": state["proposer"],
        "round": state["round"]
    }

    p0_obs = {**base_obs, "my_values": vals["p0"]}
    p1_obs = {**base_obs, "my_values": vals["p1"]}

    if state["is_terminal"]:
        p0_obs["opponent_values"] = vals["p1"]
        p1_obs["opponent_values"] = vals["p0"]
        p0_obs["outcome"] = state["outcome"]
        p1_obs["outcome"] = state["outcome"]

    return [p0_obs, p1_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view."""
    if not obs_action_history:
        return []

    last_obs, last_action = obs_action_history[-1]
    my_values = last_obs.get("my_values", [0, 0, 0])

    # Sample opponent's values
    opp_values = [random.choice(VALUE_RANGE) for _ in range(3)]

    if player_id == P0:
        deal = f"v0_{my_values[0]}_{my_values[1]}_{my_values[2]}_v1_{opp_values[0]}_{opp_values[1]}_{opp_values[2]}"
    else:
        deal = f"v0_{opp_values[0]}_{opp_values[1]}_{opp_values[2]}_v1_{my_values[0]}_{my_values[1]}_{my_values[2]}"

    history = [deal]

    # Reconstruct the full action history
    # obs_action_history contains (obs, action) only for our turns
    # The observation shows the state BEFORE we act
    # current_proposal/proposer shows opponent's last proposal (if they made one)

    # Track what proposal we last made (to infer opponent responses)
    last_our_proposal = None

    for i, (obs, act) in enumerate(obs_action_history):
        curr_proposal = obs.get("current_proposal")
        curr_proposer = obs.get("proposer")

        # If there's a proposal from opponent visible in our observation,
        # it means opponent made a proposal between our last turn and now
        if curr_proposal is not None and curr_proposer == (1 - player_id):
            # Only add if this is a new opponent proposal
            opp_action = f"propose_{curr_proposal[0]}_{curr_proposal[1]}_{curr_proposal[2]}"
            history.append(opp_action)

        # Add our action
        if act is not None:
            history.append(act)
            # Track if we made a proposal
            if act.startswith("propose_"):
                parts = act.split("_")
                last_our_proposal = [int(parts[1]), int(parts[2]), int(parts[3])]

    return history
