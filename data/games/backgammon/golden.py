from typing import Any, Dict, List, Optional, Tuple
from itertools import permutations
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, CHANCE, TERMINAL = 0, 1, -1, -4
NUM_POINTS = 24
NUM_CHECKERS = 15
DIE_SIDES = 6

# Initial positions: {point: (count, player)}
# Points are 1-indexed (1-24)
INITIAL_POSITION = {
    # Player 0 checkers
    24: (2, P0),
    13: (5, P0),
    8: (3, P0),
    6: (5, P0),
    # Player 1 checkers
    1: (2, P1),
    12: (5, P1),
    17: (3, P1),
    19: (5, P1),
}

def _get_direction(player: int) -> int:
    """P0 moves counterclockwise (decreasing), P1 moves clockwise (increasing)."""
    return -1 if player == P0 else 1

def _home_range(player: int) -> range:
    """Get home board range for player."""
    return range(1, 7) if player == P0 else range(19, 25)

def _bar_entry_range(player: int) -> range:
    """Get bar entry range (opponent's home board)."""
    return range(19, 25) if player == P0 else range(1, 7)

def _point_after_move(point: int, die: int, player: int) -> int:
    """Calculate destination point after moving die pips."""
    direction = _get_direction(player)
    return point + direction * die

def _can_bear_off(board: Dict[int, Tuple[int, int]], bar: Dict[int, int], player: int) -> bool:
    """Check if player can bear off (all checkers in home)."""
    if bar.get(player, 0) > 0:
        return False

    home = _home_range(player)
    for point in range(1, NUM_POINTS + 1):
        if point not in home:
            count, owner = board.get(point, (0, None))
            if owner == player and count > 0:
                return False
    return True

def _generate_moves_for_dice(board: Dict, bar: Dict, player: int, dice: List[int]) -> List[str]:
    """Generate all legal move combinations for given dice."""
    if not dice:
        return [""]

    moves = set()

    # Try using each die first (order matters for some positions)
    for perm in set(permutations(dice)):
        _find_move_sequences(board, bar, player, list(perm), [], moves)

    if not moves:
        return ["pass"]

    return list(moves)

def _find_move_sequences(board: Dict, bar: Dict, player: int,
                          remaining_dice: List[int], current_moves: List[str],
                          all_moves: set):
    """Recursively find all legal move sequences."""
    if not remaining_dice:
        if current_moves:
            all_moves.add(",".join(current_moves))
        return

    die = remaining_dice[0]
    rest = remaining_dice[1:]
    found_move = False

    # Must move from bar first
    if bar.get(player, 0) > 0:
        entry_point = die if player == P1 else (25 - die)
        if _can_move_to(board, entry_point, player):
            new_board, new_bar = _apply_single_move(board, bar, player, "bar", entry_point)
            move_str = f"bar/{entry_point}"
            _find_move_sequences(new_board, new_bar, player, rest,
                                current_moves + [move_str], all_moves)
            found_move = True
    else:
        # Try moving from each point
        for point in range(1, NUM_POINTS + 1):
            count, owner = board.get(point, (0, None))
            if owner != player or count == 0:
                continue

            dest = _point_after_move(point, die, player)

            # Bearing off
            if _can_bear_off(board, bar, player):
                home = _home_range(player)
                if player == P0:
                    if dest < 1:
                        # Exact or overshoot bearing off
                        if dest == 0 or _no_checkers_behind(board, player, point):
                            new_board, new_bar = _apply_single_move(board, bar, player, point, "off")
                            move_str = f"{point}/off"
                            _find_move_sequences(new_board, new_bar, player, rest,
                                                current_moves + [move_str], all_moves)
                            found_move = True
                            continue
                else:  # P1
                    if dest > 24:
                        if dest == 25 or _no_checkers_behind(board, player, point):
                            new_board, new_bar = _apply_single_move(board, bar, player, point, "off")
                            move_str = f"{point}/off"
                            _find_move_sequences(new_board, new_bar, player, rest,
                                                current_moves + [move_str], all_moves)
                            found_move = True
                            continue

            # Normal move
            if 1 <= dest <= 24 and _can_move_to(board, dest, player):
                new_board, new_bar = _apply_single_move(board, bar, player, point, dest)
                move_str = f"{point}/{dest}"
                _find_move_sequences(new_board, new_bar, player, rest,
                                    current_moves + [move_str], all_moves)
                found_move = True

    # If no move possible with this die, try skipping it
    if not found_move:
        _find_move_sequences(board, bar, player, rest, current_moves, all_moves)

def _no_checkers_behind(board: Dict, player: int, point: int) -> bool:
    """Check if there are no checkers on higher points (for bearing off)."""
    if player == P0:
        for p in range(point + 1, 7):
            count, owner = board.get(p, (0, None))
            if owner == player and count > 0:
                return False
    else:
        for p in range(19, point):
            count, owner = board.get(p, (0, None))
            if owner == player and count > 0:
                return False
    return True

def _can_move_to(board: Dict, point: int, player: int) -> bool:
    """Check if player can move to a point."""
    count, owner = board.get(point, (0, None))
    return count < 2 or owner == player

def _apply_single_move(board: Dict, bar: Dict, player: int,
                        from_pos, to_pos) -> Tuple[Dict, Dict]:
    """Apply a single move and return new board and bar."""
    new_board = copy.deepcopy(board)
    new_bar = bar.copy()

    # Remove from source
    if from_pos == "bar":
        new_bar[player] = new_bar.get(player, 0) - 1
    else:
        count, owner = new_board.get(from_pos, (0, None))
        if count == 1:
            del new_board[from_pos]
        else:
            new_board[from_pos] = (count - 1, owner)

    # Add to destination
    if to_pos != "off":
        count, owner = new_board.get(to_pos, (0, None))
        if owner is not None and owner != player and count == 1:
            # Hit opponent's blot
            new_bar[1 - player] = new_bar.get(1 - player, 0) + 1
            new_board[to_pos] = (1, player)
        else:
            new_board[to_pos] = (count + 1, player)

    return new_board, new_bar

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        "board": copy.deepcopy(INITIAL_POSITION),
        "bar": {P0: 0, P1: 0},
        "borne_off": {P0: 0, P1: 0},
        "dice": [],
        "current_player": CHANCE,
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        "board": copy.deepcopy(state["board"]),
        "bar": state["bar"].copy(),
        "borne_off": state["borne_off"].copy(),
        "dice": state["dice"].copy(),
        "current_player": state["current_player"],
        "is_terminal": False,
        "winner": None
    }

    if state["current_player"] == CHANCE:
        # Parse dice roll "D_X_Y"
        parts = action.split("_")
        d1, d2 = int(parts[1]), int(parts[2])
        if d1 == d2:
            new_state["dice"] = [d1, d1, d1, d1]
        else:
            new_state["dice"] = [d1, d2]
        # Determine first player based on higher die if initial roll
        if sum(state["borne_off"].values()) == 0 and sum(state["bar"].values()) == 0:
            # Check if this is the very first roll
            p0_count = sum(c for p, (c, o) in state["board"].items() if o == P0)
            if p0_count == 15:  # Initial position
                new_state["current_player"] = P0 if d1 >= d2 else P1
            else:
                new_state["current_player"] = P0
        else:
            # Alternate players - find who just moved
            new_state["current_player"] = P0  # Will be set properly
        return new_state

    # Parse and apply moves
    player = state["current_player"]

    if action != "pass":
        moves = action.split(",")
        for move in moves:
            parts = move.split("/")
            from_pos = parts[0]
            to_pos = parts[1]

            if from_pos == "bar":
                from_pos = "bar"
            else:
                from_pos = int(from_pos)

            if to_pos == "off":
                to_pos = "off"
                new_state["borne_off"][player] += 1
            else:
                to_pos = int(to_pos)

            new_state["board"], new_state["bar"] = _apply_single_move(
                new_state["board"], new_state["bar"], player, from_pos, to_pos
            )

    # Check for win
    if new_state["borne_off"][player] >= NUM_CHECKERS:
        new_state["is_terminal"] = True
        new_state["winner"] = player
        new_state["current_player"] = TERMINAL
    else:
        # Next player rolls
        new_state["current_player"] = CHANCE
        new_state["dice"] = []

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
        # All possible dice rolls
        actions = []
        for d1 in range(1, DIE_SIDES + 1):
            for d2 in range(d1, DIE_SIDES + 1):
                actions.append(f"D_{d1}_{d2}")
        return actions

    player = state["current_player"]
    return _generate_moves_for_dice(state["board"], state["bar"], player, state["dice"])

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Backgammon is perfect information."""
    obs = {
        "board": state["board"],
        "bar": state["bar"],
        "borne_off": state["borne_off"],
        "dice": state["dice"]
    }
    return [obs, obs]
