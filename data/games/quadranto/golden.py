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

def _cells_that_can_reach_quadrant(start_quadrant: int, target_quadrant: int) -> List[Tuple[int, int]]:
    """Returns cells in start_quadrant that can reach target_quadrant in one move."""
    result = []
    for cell in QUADRANTS[start_quadrant]:
        for name, (dr, dc) in MOVES.items():
            nr, nc = cell[0] + dr, cell[1] + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                if get_quadrant_id(nr, nc) == target_quadrant:
                    result.append(cell)
                    break
    return result if result else QUADRANTS[start_quadrant]  # Fallback to any cell


def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """
    Reconstructs a valid history of actions (including Chance and Opponent)
    that is consistent with the `player_id`'s observations.
    """
    if not obs_action_history:
        return []

    # 1. Parse Start Positions
    first_obs = obs_action_history[0][0]
    my_start = first_obs["loc"]

    # P0 always starts in quadrant 1 (top-left), P1 always starts in quadrant 4 (bottom-right)
    if player_id == 0:
        p0_start = my_start
        # For P0's first observation, opponent hasn't moved yet, so first_obs shows P1's starting quadrant
        # But P1 must start in quadrant 4, so just sample from there
        # However, we need P1 to potentially reach a different quadrant after moving
        # Look at the second observation (if exists) to see where P1 should be after their first move
        if len(obs_action_history) > 1:
            second_obs = obs_action_history[1][0]
            target_quad = second_obs["opponent_quadrant"]
            valid_starts = _cells_that_can_reach_quadrant(4, target_quad)
            p1_start = random.choice(valid_starts)
        else:
            p1_start = random.choice(QUADRANTS[4])
    else:
        # For player 1: the first observation is AFTER P0 has already moved once
        # P0 must start in quadrant 1
        # first_obs["opponent_quadrant"] shows where P0 is after their first move
        target_quad = first_obs["opponent_quadrant"]
        valid_starts = _cells_that_can_reach_quadrant(1, target_quad)
        p0_start = random.choice(valid_starts)
        p1_start = my_start

    history = [
        f"place_p0:{p0_start[0]},{p0_start[1]}",
        f"place_p1:{p1_start[0]},{p1_start[1]}"
    ]
    
    # 3. Initialize State
    state = get_initial_state()
    for act in history:
        state = apply_action(state, act)

    # 4. Decoupled Simulation Loop
    # We maintain an iterator for the evidence (observations)
    history_iter = iter(obs_action_history)
    
    # Grab the first piece of evidence to start
    try:
        current_obs, current_action = next(history_iter)
    except StopIteration:
        return history

    while state["current_player"] != -4:
        current_actor = get_current_player(state)

        # CASE A: It is OUR turn (Player ID)
        if current_actor == player_id:
            # We must take the action recorded in the history
            if current_action is None:
                # We reached the end of the recording, but the game expects a move.
                # Stop here.
                break
                
            chosen_action = current_action
            history.append(chosen_action)
            state = apply_action(state, chosen_action)
            
            # Advance the evidence iterator
            try:
                current_obs, current_action = next(history_iter)
            except StopIteration:
                # No more evidence left. 
                # If the game isn't over, we stop simulation here.
                current_action = None 
                # We continue the loop one last time if the opponent needs to move,
                # otherwise we break.
                if get_current_player(state) == player_id:
                    break

        # CASE B: It is the OPPONENT'S turn
        else:
            # We must hallucinate a move.
            # CONSTRAINT: The move must result in the state seen in 'current_obs'.
            # Note: 'current_obs' is the observation for the *upcoming* player turn.
            
            legal = get_legal_actions(state)
            valid_actions = []
            
            # If we have a future observation, use it to constrain the opponent
            # If current_action is None, it means we ran out of history, 
            # so we can't constrain the opponent (any move is fine).
            if current_action is not None:
                target_quad = current_obs["opponent_quadrant"]
                
                for act in legal:
                    # Tentatively apply opponent move
                    next_state = apply_action(state, act)
                    
                    # Check where the opponent ended up
                    if player_id == 0:
                        sim_opp_loc = next_state["p1_loc"]
                    else:
                        sim_opp_loc = next_state["p0_loc"]
                    
                    # Does this match what we see in the NEXT observation?
                    if get_quadrant_id(*sim_opp_loc) == target_quad:
                        valid_actions.append(act)
            
            # Fallback if no valid actions found (rare, implies inconsistent history) 
            # or if we are at the end of history (no constraint).
            if not valid_actions:
                valid_actions = legal

            chosen_action = random.choice(valid_actions)
            history.append(chosen_action)
            state = apply_action(state, chosen_action)

    return history