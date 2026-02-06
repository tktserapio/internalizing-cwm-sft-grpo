from typing import Any, Dict, List, Optional
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
BOARD_SIZE = 6
QUAD_SIZE = 3
MARKS = {P0: 'x', P1: 'o'}
WIN_LENGTH = 5

# Quadrant boundaries: (row_start, row_end, col_start, col_end)
QUADRANTS = {
    0: (0, 3, 0, 3),   # top-left
    1: (0, 3, 3, 6),   # top-right
    2: (3, 6, 0, 3),   # bottom-left
    3: (3, 6, 3, 6),   # bottom-right
}

def _rotate_quadrant(board: List[List[str]], quad: int, clockwise: bool) -> List[List[str]]:
    """Rotate a quadrant 90 degrees."""
    new_board = [row[:] for row in board]
    r_start, r_end, c_start, c_end = QUADRANTS[quad]

    # Extract quadrant
    quadrant = [[board[r][c] for c in range(c_start, c_end)]
                for r in range(r_start, r_end)]

    # Rotate
    if clockwise:
        rotated = [[quadrant[QUAD_SIZE-1-j][i] for j in range(QUAD_SIZE)]
                   for i in range(QUAD_SIZE)]
    else:
        rotated = [[quadrant[j][QUAD_SIZE-1-i] for j in range(QUAD_SIZE)]
                   for i in range(QUAD_SIZE)]

    # Place back
    for i in range(QUAD_SIZE):
        for j in range(QUAD_SIZE):
            new_board[r_start + i][c_start + j] = rotated[i][j]

    return new_board

def _check_five_in_row(board: List[List[str]], mark: str) -> bool:
    """Check if the given mark has 5 in a row."""
    # Check all rows
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE - WIN_LENGTH + 1):
            if all(board[r][c+i] == mark for i in range(WIN_LENGTH)):
                return True

    # Check all columns
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - WIN_LENGTH + 1):
            if all(board[r+i][c] == mark for i in range(WIN_LENGTH)):
                return True

    # Check diagonals (top-left to bottom-right)
    for r in range(BOARD_SIZE - WIN_LENGTH + 1):
        for c in range(BOARD_SIZE - WIN_LENGTH + 1):
            if all(board[r+i][c+i] == mark for i in range(WIN_LENGTH)):
                return True

    # Check anti-diagonals (top-right to bottom-left)
    for r in range(BOARD_SIZE - WIN_LENGTH + 1):
        for c in range(WIN_LENGTH - 1, BOARD_SIZE):
            if all(board[r+i][c-i] == mark for i in range(WIN_LENGTH)):
                return True

    return False

def _is_full(board: List[List[str]]) -> bool:
    """Check if board is full."""
    return all(board[r][c] != '' for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': P0,
        'status': 'ongoing'  # ongoing, x_won, o_won, draw
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    # Parse action: "mark(row,col)_rotate_Q_D"
    parts = action.split('_rotate_')
    place_part = parts[0]  # "mark(row,col)"
    rotate_part = parts[1]  # "Q_D"

    # Parse placement
    mark = place_part[0]
    coords = place_part[2:-1]  # "row,col"
    r, c = map(int, coords.split(','))

    # Parse rotation
    rot_parts = rotate_part.split('_')
    quad = int(rot_parts[0])
    direction = rot_parts[1]
    clockwise = (direction == "CW")

    # Create new board and place
    new_board = [row[:] for row in state['board']]
    new_board[r][c] = mark

    # Rotate
    new_board = _rotate_quadrant(new_board, quad, clockwise)

    new_state = {
        'board': new_board,
        'current_player': 1 - state['current_player'],
        'status': 'ongoing'
    }

    # Check win conditions
    x_wins = _check_five_in_row(new_board, 'x')
    o_wins = _check_five_in_row(new_board, 'o')

    if x_wins and o_wins:
        new_state['status'] = 'draw'
        new_state['current_player'] = TERMINAL
    elif x_wins:
        new_state['status'] = 'x_won'
        new_state['current_player'] = TERMINAL
    elif o_wins:
        new_state['status'] = 'o_won'
        new_state['current_player'] = TERMINAL
    elif _is_full(new_board):
        new_state['status'] = 'draw'
        new_state['current_player'] = TERMINAL

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0 (X)"
    if player_id == P1: return "Player 1 (O)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    status = state['status']
    if status == 'x_won':
        return [1.0, -1.0]
    elif status == 'o_won':
        return [-1.0, 1.0]
    return [0.0, 0.0]  # Draw or ongoing

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == TERMINAL:
        return []

    mark = MARKS[state['current_player']]
    actions = []

    # All combinations of: empty cell × quadrant × direction
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if state['board'][r][c] == '':
                for quad in range(4):
                    for direction in ['CW', 'CCW']:
                        actions.append(f"{mark}({r},{c})_rotate_{quad}_{direction}")

    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Pentago is perfect information."""
    obs = {'board': state['board'], 'status': state['status']}
    return [obs, obs]
