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


def _all_placements() -> List[List[List[Tuple[int, int]]]]:
    """Generate all valid ship placements for one player."""
    two_cell = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - 1):
            two_cell.append([(r, c), (r, c + 1)])
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE):
            two_cell.append([(r, c), (r + 1, c)])

    placements = []
    for ship2 in two_cell:
        occupied = set(tuple(cell) for cell in ship2)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r, c) not in occupied:
                    placements.append([ship2, [(r, c)]])
    return placements


# Precompute all valid placements and their encodings
_ALL_PLACEMENTS = _all_placements()
_ALL_ENCODED = sorted(set(_encode_placement(p) for p in _ALL_PLACEMENTS))


def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "ships": {},
        "shots": {"p0": [], "p1": []},
        "hits": {"p0": set(), "p1": set()},
        "current_player": CHANCE,
        "phase": "setup_p0",
        "is_terminal": False,
        "winner": None
    }


def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "ships": copy.deepcopy(state["ships"]),
        "shots": {k: v.copy() for k, v in state["shots"].items()},
        "hits": {k: v.copy() for k, v in state["hits"].items()},
        "current_player": state["current_player"],
        "phase": state["phase"],
        "is_terminal": state["is_terminal"],
        "winner": state["winner"]
    }

    if state["current_player"] == CHANCE:
        if state["phase"] == "setup_p0":
            encoded = action.split(":", 1)[1]
            new_state["ships"]["p0"] = _decode_placement(encoded)
            new_state["phase"] = "setup_p1"
        elif state["phase"] == "setup_p1":
            encoded = action.split(":", 1)[1]
            new_state["ships"]["p1"] = _decode_placement(encoded)
            new_state["phase"] = "playing"
            new_state["current_player"] = P0
        return new_state

    # Player fires
    current = state["current_player"]
    opponent = 1 - current

    _, r_str, c_str = action.split("_")
    r, c = int(r_str), int(c_str)
    shot = (r, c)

    player_key = f"p{current}"
    new_state["shots"][player_key].append(shot)

    opponent_cells = _get_all_ship_cells(new_state["ships"][f"p{opponent}"])
    if shot in opponent_cells:
        new_state["hits"][player_key].add(shot)

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
    """Returns the rewards per player."""
    if state["winner"] == P0:
        return [1.0, -1.0]
    elif state["winner"] == P1:
        return [-1.0, 1.0]
    return [0.0, 0.0]


def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state["is_terminal"]:
        return []

    if state["current_player"] == CHANCE:
        if state["phase"] == "setup_p0":
            return [f"place_p0:{e}" for e in _ALL_ENCODED]
        elif state["phase"] == "setup_p1":
            return [f"place_p1:{e}" for e in _ALL_ENCODED]
        return []

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
    """Returns [player_0_obs, player_1_obs]."""
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

    last_obs = obs_action_history[-1][0]
    my_ships = last_obs.get("my_ships", [])
    my_ships_encoded = _encode_placement(my_ships) if my_ships else ""

    # Determine opponent ships: known from terminal obs, or sample
    opp_ships_encoded = None
    if "opponent_ships" in last_obs:
        opp_ships_encoded = _encode_placement(last_obs["opponent_ships"])
    else:
        # Sample opponent placement consistent with hits/misses
        my_hits = set(tuple(h) for h in last_obs.get("my_hits", []))
        my_shots = set(tuple(s) for s in last_obs.get("my_shots", []))
        my_misses = my_shots - my_hits

        candidates = []
        for placement in _ALL_PLACEMENTS:
            cells = _get_all_ship_cells(placement)
            if my_hits <= cells and not (my_misses & cells):
                candidates.append(placement)
        if candidates:
            opp_ships_encoded = _encode_placement(random.choice(candidates))
        else:
            opp_ships_encoded = _ALL_ENCODED[0]

    # Build chance actions
    if player_id == P0:
        history = [f"place_p0:{my_ships_encoded}", f"place_p1:{opp_ships_encoded}"]
    else:
        history = [f"place_p0:{opp_ships_encoded}", f"place_p1:{my_ships_encoded}"]

    # Reconstruct fire actions from obs_action_history
    # Player's actions come from history; opponent's from observation
    opp_shots = last_obs.get("opponent_shots_at_me", [])

    # Collect player's fire actions in order
    my_fires = [act for _, act in obs_action_history if act is not None]

    # Interleave: P0 fires first, then P1, alternating
    max_shots = max(len(my_fires), len(opp_shots))
    for i in range(max_shots):
        if player_id == P0:
            if i < len(my_fires):
                history.append(my_fires[i])
            if i < len(opp_shots):
                r, c = opp_shots[i]
                history.append(f"fire_{r}_{c}")
        else:
            if i < len(opp_shots):
                r, c = opp_shots[i]
                history.append(f"fire_{r}_{c}")
            if i < len(my_fires):
                history.append(my_fires[i])

    return history
