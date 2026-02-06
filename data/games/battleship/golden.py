from typing import Any, Dict, List, Optional, Tuple
import random
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, CHANCE, TERMINAL = 0, 1, -1, -4
BOARD_SIZE = 4
SHIP_SIZES = [2, 1]  # One 2-cell ship, one 1-cell ship
TOTAL_SHIP_CELLS = sum(SHIP_SIZES)  # 3 cells per player

def _generate_ship_placements() -> List[List[Tuple[int, int]]]:
    """Generate a random valid ship placement. Returns list of ships, each ship is list of (r,c) tuples."""
    occupied = set()
    ships = []

    for size in SHIP_SIZES:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            attempts += 1
            # Random orientation
            horizontal = random.choice([True, False])
            if horizontal:
                r = random.randint(0, BOARD_SIZE - 1)
                c = random.randint(0, BOARD_SIZE - size)
                cells = [(r, c + i) for i in range(size)]
            else:
                r = random.randint(0, BOARD_SIZE - size)
                c = random.randint(0, BOARD_SIZE - 1)
                cells = [(r + i, c) for i in range(size)]

            # Check no overlap
            if all((r, c) not in occupied for r, c in cells):
                for cell in cells:
                    occupied.add(cell)
                ships.append(cells)
                placed = True

    return ships

def _encode_placement(ships: List[List[Tuple[int, int]]]) -> str:
    """Encode ship placement as string."""
    parts = []
    for ship in ships:
        cells = "_".join(f"{r}{c}" for r, c in ship)
        parts.append(cells)
    return "|".join(parts)

def _decode_placement(encoded: str) -> List[List[Tuple[int, int]]]:
    """Decode ship placement from string."""
    ships = []
    for ship_str in encoded.split("|"):
        cells = []
        for cell_str in ship_str.split("_"):
            r, c = int(cell_str[0]), int(cell_str[1])
            cells.append((r, c))
        ships.append(cells)
    return ships

def _get_all_ship_cells(ships: List[List[Tuple[int, int]]]) -> set:
    """Get all cells occupied by ships."""
    cells = set()
    for ship in ships:
        for cell in ship:
            cells.add(cell)
    return cells

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "ships": {},          # {"p0": [...], "p1": [...]}
        "shots": {"p0": [], "p1": []},  # Shots fired by each player
        "hits": {"p0": set(), "p1": set()},   # Hits landed by each player
        "current_player": CHANCE,
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "ships": copy.deepcopy(state["ships"]) if state["ships"] else {},
        "shots": {k: v.copy() for k, v in state["shots"].items()},
        "hits": {k: v.copy() for k, v in state["hits"].items()},
        "current_player": state["current_player"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }

    if state["current_player"] == CHANCE:
        # Parse setup action "p0_...|p1_..."
        parts = action.split("||")
        new_state["ships"]["p0"] = _decode_placement(parts[0])
        new_state["ships"]["p1"] = _decode_placement(parts[1])
        new_state["current_player"] = P0
        return new_state

    # Player fires
    current = state["current_player"]
    opponent = 1 - current

    # Parse "fire_R_C"
    _, r_str, c_str = action.split("_")
    r, c = int(r_str), int(c_str)
    shot = (r, c)

    player_key = f"p{current}"
    new_state["shots"][player_key].append(shot)

    # Check if hit
    opponent_cells = _get_all_ship_cells(new_state["ships"][f"p{opponent}"])
    if shot in opponent_cells:
        new_state["hits"][player_key].add(shot)

    # Check win condition
    if len(new_state["hits"][player_key]) >= TOTAL_SHIP_CELLS:
        new_state["is_terminal"] = True
        new_state["winner"] = current
        new_state["current_player"] = TERMINAL
    else:
        new_state["current_player"] = opponent

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

    if state["winner"] == P0:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    if state["current_player"] == CHANCE:
        # Generate deterministic placements for idempotency
        # Use fixed seed based on state to ensure same actions returned each call
        import random as rng
        rng.seed(42)  # Fixed seed for deterministic generation
        actions = set()
        for _ in range(10):  # Limit to 10 random setups
            p0_ships = _generate_ship_placements()
            p1_ships = _generate_ship_placements()
            action = f"{_encode_placement(p0_ships)}||{_encode_placement(p1_ships)}"
            actions.add(action)
        return sorted(actions)  # Sorted for consistent ordering

    # Player actions: fire at any unshot cell
    current = state["current_player"]
    player_key = f"p{current}"
    already_shot = set(state["shots"][player_key])

    actions = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) not in already_shot:
                actions.append(f"fire_{r}_{c}")

    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Each player sees their ships and shot results."""
    if state["current_player"] == CHANCE:
        return [{}, {}]

    obs = []
    for p in [P0, P1]:
        player_key = f"p{p}"
        opponent_key = f"p{1-p}"

        player_obs = {
            "my_ships": state["ships"].get(player_key, []),
            "my_shots": state["shots"][player_key],
            "my_hits": list(state["hits"][player_key]),
            "opponent_shots_at_me": state["shots"][opponent_key],
            "opponent_hits_on_me": list(state["hits"][opponent_key]),
        }

        if state["is_terminal"]:
            player_obs["opponent_ships"] = state["ships"].get(opponent_key, [])
            player_obs["winner"] = state["winner"]

        obs.append(player_obs)

    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """Stochastically sample a history consistent with player_id's view."""
    if not obs_action_history:
        return []

    last_obs, last_action = obs_action_history[-1]

    # Get my ships from observation
    my_ships = last_obs.get("my_ships", [])
    my_ships_encoded = _encode_placement(my_ships) if my_ships else ""

    # Get legal setup actions and find one that matches our ships
    initial_state = get_initial_state()
    legal_setups = get_legal_actions(initial_state)

    # Find a setup action where our ships match
    valid_setup = None
    for setup in legal_setups:
        parts = setup.split("||")
        if player_id == P0:
            if parts[0] == my_ships_encoded:
                valid_setup = setup
                break
        else:
            if parts[1] == my_ships_encoded:
                valid_setup = setup
                break

    # If no exact match (shouldn't happen in valid game), use first legal action
    if valid_setup is None:
        valid_setup = legal_setups[0] if legal_setups else ""

    history = [valid_setup]

    # Reconstruct the firing sequence from both players' shots
    # We need to interleave P0 and P1 shots correctly
    my_shots = last_obs.get("my_shots", [])
    opp_shots = last_obs.get("opponent_shots_at_me", [])

    # Interleave shots: P0 fires first, then P1, alternating
    max_shots = max(len(my_shots), len(opp_shots))
    for i in range(max_shots):
        if player_id == P0:
            # P0 fires first
            if i < len(my_shots):
                r, c = my_shots[i]
                history.append(f"fire_{r}_{c}")
            if i < len(opp_shots):
                r, c = opp_shots[i]
                history.append(f"fire_{r}_{c}")
        else:
            # P0 still fires first, but we're P1
            if i < len(opp_shots):
                r, c = opp_shots[i]
                history.append(f"fire_{r}_{c}")
            if i < len(my_shots):
                r, c = my_shots[i]
                history.append(f"fire_{r}_{c}")

    return history
