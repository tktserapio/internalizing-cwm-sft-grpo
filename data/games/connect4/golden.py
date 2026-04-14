from typing import Any, Dict, List, Optional, Tuple

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game Constants
ROWS = 6
COLS = 7
EMPTY = '.'
MARKS = {0: 'x', 1: 'o'}
PLAYER_0 = 0
PLAYER_1 = 1
TERMINAL_PLAYER = -4

def get_initial_state() -> State:
    """Returns the initial game state with an empty board."""
    return {
        "board": [[EMPTY for _ in range(COLS)] for _ in range(ROWS)],
        "current_player": PLAYER_0,
        "is_terminal": False,
        "winner": None
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after a piece is dropped into a column."""
    if state["is_terminal"]:
        return state

    new_state = {k: v if k != "board" else [r[:] for r in v] for k, v in state.items()}
    board = new_state["board"]
    player = state["current_player"]
    
    # Parse action (e.g., "x3" -> col 3)
    col = int(action[1:])
    mark = MARKS[player]

    # Apply Gravity: Find the lowest empty row in the column
    row_idx = -1
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = mark
            row_idx = r
            break
            
    # Check for win or draw
    if _check_win(board, row_idx, col, mark):
        new_state["is_terminal"] = True
        new_state["winner"] = player
        new_state["current_player"] = TERMINAL_PLAYER
    elif all(board[0][c] != EMPTY for c in range(COLS)):
        # Board is full and no winner -> Draw
        new_state["is_terminal"] = True
        new_state["winner"] = None
        new_state["current_player"] = TERMINAL_PLAYER
    else:
        # Switch turns
        new_state["current_player"] = 1 - player

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, -4 for terminal."""
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == PLAYER_0: return "Player 0 (x)"
    if player_id == PLAYER_1: return "Player 1 (o)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player: +1 for win, -1 for loss, 0 otherwise."""
    winner = state["winner"]
    if winner is None:
        return [0.0, 0.0] # Draw
    
    rewards = [0.0, 0.0]
    rewards[winner] = 1.0
    rewards[1 - winner] = -1.0
    return rewards

def get_legal_actions(state: State) -> List[Action]:
    """Returns valid columns where the top row is empty."""
    if state["is_terminal"]:
        return []
    
    player_mark = MARKS[state["current_player"]]
    # A move is valid if the top row of the column is empty
    return [f"{player_mark}{c}" for c in range(COLS) if state["board"][0][c] == EMPTY]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the full board state as observation for both players (Perfect Information)."""
    obs = {"board": [row[:] for row in state["board"]], "current_player": state["current_player"]}
    return [obs, obs]

# --- Helper Functions ---

def _check_win(board: List[List[str]], r: int, c: int, mark: str) -> bool:
    """Checks for 4 connected marks starting from the last placed piece."""
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal (Top-Left to Bottom-Right)
        (1, -1)   # Diagonal (Bottom-Left to Top-Right)
    ]
    
    for dr, dc in directions:
        count = 1
        # Check positive direction
        for k in range(1, 4):
            nr, nc = r + dr * k, c + dc * k
            if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == mark:
                count += 1
            else:
                break
        # Check negative direction
        for k in range(1, 4):
            nr, nc = r - dr * k, c - dc * k
            if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == mark:
                count += 1
            else:
                break
        
        if count >= 4:
            return True
    return False