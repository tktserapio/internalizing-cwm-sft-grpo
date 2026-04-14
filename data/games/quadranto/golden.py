import random
from typing import Any, Dict, List, Optional, Tuple

# Type definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Game Constants
GRID_SIZE = 4
MAX_TURNS = 20
QUADRANTS = {
    1: [(r, c) for r in range(2) for c in range(2)],          # Top-Left
    2: [(r, c) for r in range(2) for c in range(2, 4)],       # Top-Right
    3: [(r, c) for r in range(2, 4) for c in range(2)],       # Bottom-Left
    4: [(r, c) for r in range(2, 4) for c in range(2, 4)]     # Bottom-Right
}
MOVES = {
    "Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1), "Stay": (0, 0)
}

def get_quadrant_id(r: int, c: int) -> int:
    """Returns the quadrant ID (1-4) for a given coordinate."""
    if r < 2:
        return 1 if c < 2 else 2
    else:
        return 3 if c < 2 else 4

def get_initial_state() -> State:
    """Returns the initial game state starting with chance actions."""
    return {
        "board_size": GRID_SIZE,
        "p0_loc": None,
        "p1_loc": None,
        "current_player": -1,  # Start with Chance
        "turn_count": 0,
        "status": "setup_p0",  # Phases: setup_p0 -> setup_p1 -> playing
        "history": []
    }

def get_player_name(player_id: int) -> str:
    if player_id == -1: return "Chance"
    if player_id == 0: return "Player 0"
    if player_id == 1: return "Player 1"
    return "Terminal"

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions. Handles chance setup and movement boundaries."""
    if state["current_player"] == -4:
        return []
    
    # Chance Logic for Setup
    if state["current_player"] == -1:
        if state["status"] == "setup_p0":
            return [f"place_p0:{r},{c}" for r, c in QUADRANTS[1]]
        elif state["status"] == "setup_p1":
            return [f"place_p1:{r},{c}" for r, c in QUADRANTS[4]]
        return []

    # Player Movement Logic
    p_loc = state["p0_loc"] if state["current_player"] == 0 else state["p1_loc"]
    actions = []
    r, c = p_loc
    
    for name, (dr, dc) in MOVES.items():
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            actions.append(name)
            
    return sorted(actions)

def apply_action(state: State, action: Action) -> State:
    """Applies an action and returns a new state."""
    new_state = state.copy()
    new_state["history"] = state["history"] + [action]
    
    # Handle Chance Actions
    if new_state["current_player"] == -1:
        if "place_p0" in action:
            _, coords = action.split(":")
            new_state["p0_loc"] = tuple(map(int, coords.split(",")))
            new_state["status"] = "setup_p1"
            # Current player remains -1 for second placement
        elif "place_p1" in action:
            _, coords = action.split(":")
            new_state["p1_loc"] = tuple(map(int, coords.split(",")))
            new_state["status"] = "playing"
            new_state["current_player"] = 0 # Game starts with P0
        return new_state

    # Handle Player Actions
    curr_p = new_state["current_player"]
    opp_p = 1 - curr_p
    
    # Update position
    dr, dc = MOVES[action]
    p_loc = new_state[f"p{curr_p}_loc"]
    new_loc = (p_loc[0] + dr, p_loc[1] + dc)
    new_state[f"p{curr_p}_loc"] = new_loc
    
    # Check Catch
    opp_loc = new_state[f"p{opp_p}_loc"]
    if new_loc == opp_loc:
        new_state["status"] = f"p{curr_p}_won"
        new_state["current_player"] = -4
        return new_state

    # Check Draw (Limit reached after update)
    # Increment turn count. We count individual moves. Draw happens at 20 total moves.
    new_state["turn_count"] += 1
    if new_state["turn_count"] >= MAX_TURNS:
        new_state["status"] = "draw"
        new_state["current_player"] = -4
        return new_state

    # Switch Turn
    new_state["current_player"] = opp_p
    return new_state

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_rewards(state: State) -> List[float]:
    """+1 for winner, -1 for loser, 0 for draw/ongoing."""
    status = state["status"]
    if status == "p0_won":
        return [1.0, -1.0]
    elif status == "p1_won":
        return [-1.0, 1.0]
    # Draw or ongoing
    return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observation: own exact loc, opponent's quadrant."""
    # If chance or terminal, return empty or status info
    if state["current_player"] == -1:
        return [{}, {}]
        
    def make_obs(my_loc, opp_loc):
        if my_loc is None or opp_loc is None: return {}
        return {
            "loc": my_loc,
            "opponent_quadrant": get_quadrant_id(*opp_loc)
        }

    return [
        make_obs(state["p0_loc"], state["p1_loc"]),
        make_obs(state["p1_loc"], state["p0_loc"])
    ]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Reconstruct a valid action history consistent with player_id's observations.

    Uses retry-based sampling: randomly picks opponent starting cell and
    opponent moves that satisfy quadrant constraints. Retries on dead ends.
    """
    if not obs_action_history:
        return []

    first_obs = obs_action_history[0][0]
    my_start = first_obs["loc"]
    opp_id = 1 - player_id
    opp_key = f"p{opp_id}_loc"

    n_obs = len(obs_action_history)

    for _attempt in range(1000):
        # Pick starting positions (P0 in Q1, P1 in Q4)
        if player_id == 0:
            p0_start, p1_start = my_start, random.choice(QUADRANTS[4])
        else:
            p0_start, p1_start = random.choice(QUADRANTS[1]), my_start

        history = [
            f"place_p0:{p0_start[0]},{p0_start[1]}",
            f"place_p1:{p1_start[0]},{p1_start[1]}"
        ]

        state = get_initial_state()
        for act in history:
            state = apply_action(state, act)

        obs_idx = 0
        current_obs, current_action = obs_action_history[0]
        dead_end = False

        while state["current_player"] != -4:
            cp = get_current_player(state)

            if cp == player_id:
                if current_action is None:
                    break
                history.append(current_action)
                state = apply_action(state, current_action)
                obs_idx += 1
                if obs_idx >= n_obs:
                    current_action = None
                    if get_current_player(state) == player_id:
                        break
                else:
                    current_obs, current_action = obs_action_history[obs_idx]
            else:
                # Opponent's turn — pick a move landing in the required quadrant
                legal = get_legal_actions(state)
                my_key = f"p{player_id}_loc"
                my_loc = state[my_key]

                if current_action is not None:
                    target_quad = current_obs["opponent_quadrant"]
                    candidates = [
                        a for a in legal
                        if get_quadrant_id(*apply_action(state, a)[opp_key]) == target_quad
                    ]
                    # Always prevent opponent from landing on player (opponent catch).
                    # Only prevent opponent from being at player's next position
                    # when there are more observations after the current one
                    # (at the last obs, player catching opponent is the expected ending).
                    avoid = {my_loc}
                    if obs_idx < n_obs - 1 and current_action in MOVES:
                        dr, dc = MOVES[current_action]
                        avoid.add((my_loc[0] + dr, my_loc[1] + dc))
                    safe = [a for a in candidates
                            if apply_action(state, a)[opp_key] not in avoid]
                    if safe:
                        candidates = safe
                    elif candidates:
                        dead_end = True
                        break
                else:
                    candidates = legal

                if not candidates:
                    dead_end = True
                    break

                history.append(random.choice(candidates))
                state = apply_action(state, history[-1])

        if not dead_end:
            return history

    return history  # best effort after retries