from typing import Any, List, Optional, Dict, Tuple
import copy

# Type Definitions
Action = str
State = dict[str, Any]
PlayerObservation = dict[str, Any]

# Game Constants
ROWS = 6
COLS = 6
WIN_LENGTH = 4
PLAYER_0 = 0
PLAYER_1 = 1
TERMINAL_PLAYER_ID = -4

def get_initial_state() -> State:
    """Returns the initial game state with an empty 6x6 board."""
    return {
        "board": [[None for _ in range(COLS)] for _ in range(ROWS)],
        "current_player": PLAYER_0,
        "status": "ongoing", # 'ongoing', 'win', 'draw'
        "winner": None
    }

def _check_win(board: List[List[Optional[int]]], player: int) -> bool:
    """Helper: Checks if the specified player has a winning line."""
    # Check horizontal, vertical, and both diagonals
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == player:
                # Horizontal
                if c + WIN_LENGTH <= COLS and all(board[r][c + k] == player for k in range(WIN_LENGTH)):
                    return True
                # Vertical
                if r + WIN_LENGTH <= ROWS and all(board[r + k][c] == player for k in range(WIN_LENGTH)):
                    return True
                # Diagonal (top-left to bottom-right)
                if r + WIN_LENGTH <= ROWS and c + WIN_LENGTH <= COLS and \
                   all(board[r + k][c + k] == player for k in range(WIN_LENGTH)):
                    return True
                # Diagonal (top-right to bottom-left)
                if r + WIN_LENGTH <= ROWS and c - WIN_LENGTH + 1 >= 0 and \
                   all(board[r + k][c - k] == player for k in range(WIN_LENGTH)):
                    return True
    return False

def _is_board_full(board: List[List[Optional[int]]]) -> bool:
    """Helper: Checks if there are no empty cells left."""
    return all(cell is not None for row in board for cell in row)

def apply_action(state: State, action: Action) -> State:
    """Applies an action to the state and transitions to the next turn."""
    if state["status"] != "ongoing":
        return copy.deepcopy(state)

    r, c = map(int, action.split(','))
    
    # Create a deep copy to avoid mutating the previous state
    new_state = copy.deepcopy(state)
    board = new_state["board"]
    current = new_state["current_player"]

    # Apply move
    board[r][c] = current

    # Check game termination conditions
    if _check_win(board, current):
        new_state["status"] = "win"
        new_state["winner"] = current
        new_state["current_player"] = TERMINAL_PLAYER_ID
    elif _is_board_full(board):
        new_state["status"] = "draw"
        new_state["current_player"] = TERMINAL_PLAYER_ID
    else:
        # Switch player
        new_state["current_player"] = 1 - current

    return new_state

def get_current_player(state: State) -> int:
    """Returns the ID of the player whose turn it is, or -4 if terminal."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns 'x' for player 0 and 'o' for player 1."""
    if player_id == PLAYER_0: return "x"
    if player_id == PLAYER_1: return "o"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns [1, -1] for win, [-1, 1] for loss, [0, 0] otherwise."""
    if state["status"] == "win":
        winner = state["winner"]
        return [1.0, -1.0] if winner == PLAYER_0 else [-1.0, 1.0]
    # Draw or ongoing
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns a list of 'row,col' strings for empty cells."""
    if state["status"] != "ongoing":
        return []
    
    actions = []
    for r in range(ROWS):
        for c in range(COLS):
            if state["board"][r][c] is None:
                actions.append(f"{r},{c}")
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns perfect information state for both players."""
    # Since it's a perfect information game, both see the full state
    obs = copy.deepcopy(state)
    return [obs, obs]