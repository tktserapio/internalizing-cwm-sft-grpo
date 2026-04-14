from typing import Any, Dict, List, Set, Tuple

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
NUM_ROWS = 3  # Dots in each column (creates NUM_ROWS-1 box rows)
NUM_COLS = 3  # Dots in each row (creates NUM_COLS-1 box columns)

def _get_all_lines() -> List[Action]:
    """Get all possible line actions."""
    lines = []
    # Horizontal lines: between (r, c) and (r, c+1)
    for r in range(NUM_ROWS):
        for c in range(NUM_COLS - 1):
            lines.append(f"h_{r}_{c}")
    # Vertical lines: between (r, c) and (r+1, c)
    for r in range(NUM_ROWS - 1):
        for c in range(NUM_COLS):
            lines.append(f"v_{r}_{c}")
    return lines

def _check_box_completed(drawn_lines: Set[str], box_r: int, box_c: int) -> bool:
    """Check if a box at position (box_r, box_c) is completed.
    Box (r, c) has corners at dots (r,c), (r,c+1), (r+1,c), (r+1,c+1).
    """
    top = f"h_{box_r}_{box_c}"
    bottom = f"h_{box_r + 1}_{box_c}"
    left = f"v_{box_r}_{box_c}"
    right = f"v_{box_r}_{box_c + 1}"
    return all(line in drawn_lines for line in [top, bottom, left, right])

def _count_new_boxes(drawn_lines: Set[str], new_line: str) -> List[Tuple[int, int]]:
    """Return list of boxes completed by adding new_line."""
    new_drawn = drawn_lines | {new_line}
    completed = []

    # Check which boxes this line could complete
    parts = new_line.split("_")
    line_type = parts[0]
    r, c = int(parts[1]), int(parts[2])

    if line_type == "h":
        # Horizontal line at (r, c) to (r, c+1)
        # Could complete box above (r-1, c) or below (r, c)
        if r > 0:  # Box above
            if _check_box_completed(new_drawn, r - 1, c):
                completed.append((r - 1, c))
        if r < NUM_ROWS - 1:  # Box below
            if _check_box_completed(new_drawn, r, c):
                completed.append((r, c))
    else:
        # Vertical line at (r, c) to (r+1, c)
        # Could complete box to left (r, c-1) or right (r, c)
        if c > 0:  # Box to left
            if _check_box_completed(new_drawn, r, c - 1):
                completed.append((r, c - 1))
        if c < NUM_COLS - 1:  # Box to right
            if _check_box_completed(new_drawn, r, c):
                completed.append((r, c))

    return completed

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "drawn_lines": set(),
        "box_owners": {},  # {(r, c): player_id}
        "scores": [0, 0],
        "current_player": P0,
        "is_terminal": False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "drawn_lines": state["drawn_lines"].copy(),
        "box_owners": state["box_owners"].copy(),
        "scores": state["scores"].copy(),
        "current_player": state["current_player"],
        "is_terminal": False
    }

    current = state["current_player"]
    new_state["drawn_lines"].add(action)

    # Check for completed boxes
    new_boxes = _count_new_boxes(state["drawn_lines"], action)

    if new_boxes:
        # Player gets the boxes and another turn
        for box in new_boxes:
            new_state["box_owners"][box] = current
        new_state["scores"][current] += len(new_boxes)
        # Current player keeps their turn
    else:
        # Switch players
        new_state["current_player"] = 1 - current

    # Check if game is over (all lines drawn)
    total_boxes = (NUM_ROWS - 1) * (NUM_COLS - 1)
    if sum(new_state["scores"]) == total_boxes:
        new_state["is_terminal"] = True
        new_state["current_player"] = TERMINAL

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    names = {P0: "Player 0", P1: "Player 1", TERMINAL: "Terminal"}
    return names.get(player_id, "Unknown")

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    s0, s1 = state["scores"]
    if s0 > s1:
        return [1.0, -1.0]
    elif s1 > s0:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    all_lines = _get_all_lines()
    return [line for line in all_lines if line not in state["drawn_lines"]]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Dots and Boxes is perfect information."""
    obs = {
        "drawn_lines": list(state["drawn_lines"]),
        "box_owners": dict(state["box_owners"]),
        "scores": state["scores"]
    }
    return [obs, obs]
