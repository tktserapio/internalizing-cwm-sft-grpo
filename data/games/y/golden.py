from typing import Any, Dict, List, Optional, Tuple

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Board size (cells per edge)
BOARD_SIZE = 5

# Players
BLACK = 0
WHITE = 1
EMPTY = -1

# Side flags (bitmask)
SIDE_LEFT = 1      # x == 0
SIDE_TOP = 2       # y == 0
SIDE_DIAGONAL = 4  # x + y == BOARD_SIZE - 1
ALL_SIDES = 7      # All three sides connected

# Hex neighbor offsets (6 directions)
NEIGHBOR_OFFSETS = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0)]


def _generate_cells() -> List[Tuple[int, int]]:
    """Generate all valid cell coordinates for the triangular board."""
    cells = []
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE - y):
            cells.append((x, y))
    return cells

def _cell_to_action(x: int, y: int) -> str:
    """Convert cell coordinates to action string."""
    return f"{x},{y}"

def _action_to_cell(action: str) -> Tuple[int, int]:
    """Convert action string to cell coordinates."""
    parts = action.split(',')
    return int(parts[0]), int(parts[1])

def _get_sides(x: int, y: int) -> int:
    """Return bitmask of which sides this cell touches."""
    sides = 0
    if x == 0:
        sides |= SIDE_LEFT
    if y == 0:
        sides |= SIDE_TOP
    if x + y == BOARD_SIZE - 1:
        sides |= SIDE_DIAGONAL
    return sides

def _is_valid(x: int, y: int) -> bool:
    """Check if coordinates are valid on the board."""
    return x >= 0 and y >= 0 and x + y < BOARD_SIZE

def _get_neighbors(x: int, y: int) -> List[Tuple[int, int]]:
    """Get valid neighboring cells."""
    neighbors = []
    for dx, dy in NEIGHBOR_OFFSETS:
        nx, ny = x + dx, y + dy
        if _is_valid(nx, ny):
            neighbors.append((nx, ny))
    return neighbors


# Union-Find helper functions
def _find(parent: Dict[Tuple, Tuple], cell: Tuple) -> Tuple:
    """Find root with path compression."""
    if parent[cell] != cell:
        parent[cell] = _find(parent, parent[cell])
    return parent[cell]

def _union(parent: Dict, rank: Dict, sides: Dict, a: Tuple, b: Tuple):
    """Union two groups, combining their side flags."""
    ra, rb = _find(parent, a), _find(parent, b)
    if ra == rb:
        return
    # Union by rank
    if rank[ra] < rank[rb]:
        ra, rb = rb, ra
    parent[rb] = ra
    if rank[ra] == rank[rb]:
        rank[ra] += 1
    # Combine sides
    sides[ra] |= sides[rb]


def get_initial_state() -> State:
    """Returns the initial game state."""
    return {
        "board": {},  # (x, y) -> player
        "current_player": BLACK,
        "winner": None,
        "terminal": False
    }

def get_current_player(state: State) -> int:
    """Returns current player (0 or 1), or -4 for terminal."""
    if state["terminal"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == BLACK:
        return "Black"
    elif player_id == WHITE:
        return "White"
    return "Unknown"

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions (empty cells)."""
    if state["terminal"]:
        return []

    board = state["board"]
    actions = []
    for x, y in _generate_cells():
        if (x, y) not in board:
            actions.append(_cell_to_action(x, y))
    return actions

def _check_winner(board: Dict[Tuple, int], player: int, last_move: Tuple) -> bool:
    """Check if player has won by connecting all three sides."""
    # Build union-find structure for this player's stones
    player_cells = [c for c, p in board.items() if p == player]
    if not player_cells:
        return False

    parent = {c: c for c in player_cells}
    rank = {c: 0 for c in player_cells}
    sides = {c: _get_sides(c[0], c[1]) for c in player_cells}

    # Union adjacent same-color stones
    for cell in player_cells:
        x, y = cell
        for nx, ny in _get_neighbors(x, y):
            if (nx, ny) in board and board[(nx, ny)] == player:
                _union(parent, rank, sides, cell, (nx, ny))

    # Check if any group has all three sides
    for cell in player_cells:
        root = _find(parent, cell)
        if sides[root] == ALL_SIDES:
            return True
    return False

def apply_action(state: State, action: Action) -> State:
    """Apply action (place stone) and return new state."""
    if state["terminal"]:
        return state

    player = state["current_player"]
    x, y = _action_to_cell(action)

    # Copy board and place stone
    new_board = dict(state["board"])
    new_board[(x, y)] = player

    # Check for winner
    winner = None
    if _check_winner(new_board, player, (x, y)):
        winner = player

    terminal = winner is not None or len(new_board) == len(_generate_cells())

    return {
        "board": new_board,
        "current_player": 1 - player if not terminal else -4,
        "winner": winner,
        "terminal": terminal
    }

def get_rewards(state: State) -> List[float]:
    """Returns rewards [black_reward, white_reward]."""
    winner = state["winner"]
    if winner == BLACK:
        return [1.0, -1.0]
    elif winner == WHITE:
        return [-1.0, 1.0]
    else:
        # Draw (shouldn't happen in Y, but handle it)
        return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observations. Perfect info game."""
    obs = {
        "board": dict(state["board"]),
        "current_player": state["current_player"],
        "terminal": state["terminal"]
    }
    return [obs, obs]
