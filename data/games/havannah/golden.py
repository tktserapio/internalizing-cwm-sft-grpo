import collections
from typing import Any, Dict, List, Set, Tuple

# --- Type Definitions ---
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Move limit to ensure termination
MAX_MOVES = 150

# --- Constants & Configuration ---
BOARD_SIZE = 10  # Hexes per side
MAX_COORD = BOARD_SIZE - 1
# Cube coordinates directions
DIRECTIONS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
]

# --- Coordinate System Helpers ---
def _generate_board_map() -> Tuple[Dict[str, Tuple[int, int, int]], Dict[Tuple[int, int, int], str], Set[Tuple[int, int, int]]]:
    """Generates the mapping between string actions (e.g., 'A1') and cube coordinates."""
    str_to_cube = {}
    cube_to_str = {}
    corners = set()
    
    # Generate hex grid with radius N-1
    # We map "visual" rows and cols to cube coords.
    # Notation logic: 'A1' is top-left valid hex.
    # We traverse top-to-bottom (r), then left-to-right (q).
    # This mapping is approximate to standard Havannah notation.
    valid_cubes = []
    for x in range(-MAX_COORD, MAX_COORD + 1):
        for y in range(-MAX_COORD, MAX_COORD + 1):
            z = -x - y
            if abs(z) <= MAX_COORD:
                valid_cubes.append((x, y, z))
    
    # Sort for consistent naming: Row primarily by y (desc), then x (asc)
    # Note: In cube coords, rows align with 'z' or 'y'. Let's align visually.
    # We'll assign standard "A1..T19" style labels based on a shifted grid.
    # Shift to positive integers for naming.
    # Map cube (x,y,z) to axial (q, r) for labeling.
    # We simply enumerate valid spots to match the prompt's implied bounds.
    
    # Identify corners
    for (x, y, z) in valid_cubes:
        # Corners are where two coordinates are at max absolute value
        coords = [abs(x), abs(y), abs(z)]
        if coords.count(MAX_COORD) >= 2:
            corners.add((x, y, z))

    # Naming strategy: Map (x, y, z) to "ColRow".
    # Col index: x + constant. Row index: z + constant.
    # Standard Havannah often uses a slanted coordinate view.
    # Implementation: 'A' starts at the left-most column. '1' at top row.
    for (x, y, z) in valid_cubes:
        # Axial q, r conversion for display text
        # Shift coords to be 1-based positive for A-T, 1-19
        # Col (letter) roughly corresponds to x
        # Row (number) roughly corresponds to z
        # This is a heuristic to fit the "A1" string requirement uniquely.
        col_idx = x + 9 # -9..9 -> 0..18 (A..S)
        # Adjusting specifically for a "flat topped" or "pointy topped" alignment
        # Let's use a standard mapping: column = x+z+offset, row = z+offset
        # Simple mapping: 
        # Col char: derived from (x + 10) -> 'A' is 0
        # Row num: derived from (z + 10)
        # However, to ensure uniqueness and coverage we use the canonical sort.
        pass

    # Simplified Direct Mapping for code compactness and reliability:
    # Use standard axial (q, r) logic where Strings are just IDs.
    # We will compute formatted names strictly based on bounding box.
    valid_cubes.sort(key=lambda c: (c[2], c[0])) # sort by Z then X
    
    # To strictly follow "A-T" and "1-19", we compute offsets
    # Row 1 is the top-most (min Z).
    min_z = min(c[2] for c in valid_cubes)
    min_x = min(c[0] for c in valid_cubes)
    
    for c in valid_cubes:
        x, y, z = c
        # Row number: 1 to 19 (based on Z)
        row_num = z - min_z + 1 
        # Column letter: Shifts based on row to maintain diagonal alignment
        # Standard offset: col = x + (z - min_z)//2? 
        # Let's use specific slanted column: col = x + 9 + (row_num+1)//2 is messy.
        # Let's use straight x-axis index for Column A..S
        # For a side-10 board, diagonal width is 19.
        # Let's map x directly.
        # x range is -9 to 9. +9 -> 0..18.
        # z range is -9 to 9.
        # We need a unique string.
        # Let's map: Col = (x + z) creates diagonal strips? 
        # Let's stick to: Col based on (x + offset), Row based on (z + offset).
        # We compensate for the hexagonal slant.
        col_id = x + 9 + (z + 9) // 2 # Attempt to straighten columns
        # Actually, let's just use (x, z) raw mapping for simplicity 
        # ensuring 1-1 mappings.
        # A simple visual mapping:
        col_char = chr(ord('A') + (x + 9 + (z+9)//2)) # Skewed column 
        # This might exceed T. Let's simplify:
        # Just use coordinate tuple string as internal ID if allowed, 
        # BUT prompt requires "C5".
        # Let's use the provided Example "J10" (Center).
        # If J10 is center (0,0,0), then J=9th index, 10=10th index.
        # x=0 -> J, z=0 -> 10.
        col_c = chr(ord('A') + (x + 9)) # x=-9 -> A, x=0 -> J
        row_n = z + 10                  # z=-9 -> 1, z=0 -> 10
        # Note: In hex grid x and z are not orthogonal, but this creates unique strings.
        key = f"{col_c}{row_n}"
        str_to_cube[key] = c
        cube_to_str[c] = key

    return str_to_cube, cube_to_str, corners

STR_TO_CUBE, CUBE_TO_STR, CORNER_COORDS = _generate_board_map()

# --- Game Logic ---

def get_initial_state() -> State:
    """Returns the initial game state."""
    return {
        "board": {},  # Dict[str, int] mapping action_str -> player_id
        "current_player": 0,
        "winner": None, # None, 0, 1, or -1 for draw
        "terminal": False,
        "history": []
    }

def get_current_player(state: State) -> int:
    """Returns current player (0 or 1), or -4 for terminal state."""
    if state["terminal"]:
        return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    return f"Player {player_id + 1}"

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state."""
    if state["terminal"]:
        return []
    occupied = set(state["board"].keys())
    all_actions = set(STR_TO_CUBE.keys())
    # Legal actions are all valid coords not in occupied list
    return sorted(list(all_actions - occupied), key=lambda x: (len(x), x))

def _get_neighbors(cube: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
    """Returns valid neighbor coordinates."""
    cx, cy, cz = cube
    neighbors = []
    for dx, dy, dz in DIRECTIONS:
        nx, ny, nz = cx + dx, cy + dy, cz + dz
        if (nx, ny, nz) in CUBE_TO_STR:
            neighbors.append((nx, ny, nz))
    return neighbors

def _find_group_and_corners(board_map: Dict[Tuple, int], start_node: Tuple, player: int) -> Tuple[Set[Tuple], Set[Tuple]]:
    """BFS to find connected component and the set of corners it touches."""
    queue = [start_node]
    group = {start_node}
    corners_touched = set()
    
    if start_node in CORNER_COORDS:
        corners_touched.add(start_node)
        
    idx = 0
    while idx < len(queue):
        curr = queue[idx]
        idx += 1
        for n in _get_neighbors(curr):
            if n in board_map and board_map[n] == player and n not in group:
                group.add(n)
                queue.append(n)
                if n in CORNER_COORDS:
                    corners_touched.add(n)
    return group, corners_touched

def _check_ring(board_map: Dict[Tuple, int], player: int) -> bool:
    """
    Checks for a Ring.
    Algorithm: 
    1. Identify all 'empty' or 'enemy' regions (connected components of non-player hexes).
    2. A region is 'enclosed' if it cannot reach the edge of the board.
    3. If an enclosed region exists, the boundary must be formed by the current player (implied by geometry).
    """
    # Create a set of all non-player hexes (empty or enemy)
    # We treat "off-board" as a special connected component.
    # We run Union-Find or BFS on the non-player hexes.
    
    all_hexes = set(CUBE_TO_STR.keys())
    player_hexes = {k for k, v in board_map.items() if v == player}
    non_player_hexes = all_hexes - player_hexes
    
    visited = set()
    
    for hex_pos in non_player_hexes:
        if hex_pos in visited:
            continue
            
        # Start BFS for this region
        region = set()
        stack = [hex_pos]
        visited.add(hex_pos)
        region.add(hex_pos)
        touches_edge = False
        
        while stack:
            curr = stack.pop()
            
            # Check if this hex is on the edge of the board
            cx, cy, cz = curr
            if abs(cx) == MAX_COORD or abs(cy) == MAX_COORD or abs(cz) == MAX_COORD:
                touches_edge = True
            
            for n in _get_neighbors(curr):
                if n in non_player_hexes and n not in visited:
                    visited.add(n)
                    region.add(n)
                    stack.append(n)
        
        # If a region of non-player hexes does NOT touch the edge, it is enclosed.
        # In Havannah, if P1 surrounds empty/P2 hexes, P1 wins.
        if not touches_edge:
            return True
            
    return False

def apply_action(state: State, action: Action) -> State:
    """Applies an action and checks for winning conditions."""
    if state["terminal"]:
        return state
    
    player = state["current_player"]
    new_board = state["board"].copy()
    new_board[action] = player
    
    # Convert string board to coordinate board for logic
    logic_board = {STR_TO_CUBE[k]: v for k, v in new_board.items()}
    last_move_cube = STR_TO_CUBE[action]
    
    winner = None
    
    # 1. Analyze connectivity for Bridge and Fork
    group, corners = _find_group_and_corners(logic_board, last_move_cube, player)
    
    # Bridge: Connects any 2 corners
    if len(corners) >= 2:
        winner = player
        
    # Fork: Connects any 3 corners
    # (Note: In standard rules, Bridge is 2 corners, Fork is 3. 
    # Usually completing a Fork also implies a Bridge, but Fork is distinct.
    # Any 3 corners wins.)
    if len(corners) >= 3:
        winner = player
        
    # 2. Analyze Ring (if not already won)
    if winner is None:
        if _check_ring(logic_board, player):
            winner = player

    # 3. Check Draw (full board or move limit)
    is_full = len(new_board) == len(STR_TO_CUBE)
    move_limit_reached = len(new_board) >= MAX_MOVES
    terminal = (winner is not None) or is_full or move_limit_reached
    
    next_player = 1 - player if not terminal else -4
    
    new_state = {
        "board": new_board,
        "current_player": next_player,
        "winner": winner if winner is not None else (-1 if (is_full or move_limit_reached) and winner is None else None),
        "terminal": terminal,
        "history": state["history"] + [action]
    }
    return new_state

def get_rewards(state: State) -> List[float]:
    """Returns rewards [p0_reward, p1_reward]. 1 for win, -1 for loss."""
    w = state["winner"]
    if w == 0:
        return [1.0, -1.0]
    elif w == 1:
        return [-1.0, 1.0]
    else:
        # Draw
        return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observations. Perfect information, so just the state copy."""
    # In a real RL setup, one might encode the board as a tensor.
    # Here we return the raw dictionary structure.
    obs = {
        "board": state["board"],
        "current_player": state["current_player"],
        "terminal": state["terminal"]
    }
    return [obs, obs]