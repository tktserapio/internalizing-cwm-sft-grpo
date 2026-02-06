from typing import Any, Dict, List, Optional

# --- Type Definitions ---
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# --- Constants ---
GRID_SIZE = 3
P0, P1, TERMINAL = 0, 1, -4
MARKS = {P0: 'x', P1: 'o'}

# --- Helper Functions ---

def _check_winner(board: List[List[str]]) -> Optional[str]:
    """Checks rows, columns, and diagonals for a winning mark."""
    # Generate all lines: 3 rows, 3 cols, 2 diagonals
    lines = (
        board + 
        [[board[r][c] for r in range(GRID_SIZE)] for c in range(GRID_SIZE)] +
        [[board[i][i] for i in range(GRID_SIZE)], [board[i][GRID_SIZE-1-i] for i in range(GRID_SIZE)]]
    )
    for line in lines:
        if line[0] != '' and all(cell == line[0] for cell in line):
            return line[0]
    return None

def _is_full(board: List[List[str]]) -> bool:
    """Returns True if no empty spaces remain."""
    return all(cell != '' for row in board for cell in row)

# --- Game Functions ---

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)],
        'current_player': P0,
        'status': 'ongoing' # ongoing, x_won, o_won, draw
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    # Parse action string 'mark(row,col)'
    content = action.split('(')[1].strip(')')
    r, c = map(int, content.split(','))
    
    # Create new board to preserve immutability
    new_board = [row[:] for row in state['board']]
    curr_p = state['current_player']
    new_board[r][c] = MARKS[curr_p]
    
    new_state = {
        'board': new_board,
        'current_player': 1 - curr_p, # Switch turns
        'status': 'ongoing'
    }

    # Check game over conditions
    winner = _check_winner(new_board)
    if winner:
        new_state['status'] = f'{winner}_won'
        new_state['current_player'] = TERMINAL
    elif _is_full(new_board):
        new_state['status'] = 'draw'
        new_state['current_player'] = TERMINAL
        
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0"
    if player_id == P1: return "Player 1"
    return "Terminal"

def get_rewards(state: State) -> list[float]:
    """Returns the rewards per player from their last action."""
    status = state['status']
    if status == 'x_won':
        return [1.0, -1.0]
    elif status == 'o_won':
        return [-1.0, 1.0]
    return [0.0, 0.0] # Draw or ongoing

def get_legal_actions(state: State) -> list[Action]:
    """Returns legal actions that can be taken in current state."""
    if state['current_player'] == TERMINAL:
        return []
    
    mark = MARKS[state['current_player']]
    actions = []
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if state['board'][r][c] == '':
                actions.append(f"{mark}({r},{c})")
    return actions

def get_observations(state: State) -> list[PlayerObservation]:
    """Returns the observation for player."""
    # Tic-Tac-Toe is a perfect information game; both see the full state.
    obs = {'board': state['board'], 'status': state['status']}
    return [obs, obs]