from typing import Any, Dict, List, Optional, Set, Tuple
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
BOARD_SIZE = 9
STONES = {P0: 'B', P1: 'W'}  # Black, White
KOMI = 6.5  # Compensation for white

def _neighbors(r: int, c: int) -> List[Tuple[int, int]]:
    """Get orthogonal neighbors on board."""
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
            result.append((nr, nc))
    return result

def _find_group(board: List[List[str]], r: int, c: int) -> Set[Tuple[int, int]]:
    """Find all stones connected to (r,c) of the same color."""
    color = board[r][c]
    if color == '':
        return set()

    group = set()
    stack = [(r, c)]

    while stack:
        cr, cc = stack.pop()
        if (cr, cc) in group:
            continue
        if board[cr][cc] != color:
            continue

        group.add((cr, cc))
        for nr, nc in _neighbors(cr, cc):
            if (nr, nc) not in group and board[nr][nc] == color:
                stack.append((nr, nc))

    return group

def _count_liberties(board: List[List[str]], group: Set[Tuple[int, int]]) -> int:
    """Count liberties (empty neighbors) of a group."""
    liberties = set()
    for r, c in group:
        for nr, nc in _neighbors(r, c):
            if board[nr][nc] == '':
                liberties.add((nr, nc))
    return len(liberties)

def _remove_group(board: List[List[str]], group: Set[Tuple[int, int]]) -> List[List[str]]:
    """Remove a group from the board."""
    new_board = [row[:] for row in board]
    for r, c in group:
        new_board[r][c] = ''
    return new_board

def _board_hash(board: List[List[str]]) -> str:
    """Create hash of board state for ko detection."""
    return ''.join(''.join(row) for row in board)

def _apply_move(board: List[List[str]], r: int, c: int, player: int) -> Optional[List[List[str]]]:
    """Apply a move and return new board, or None if illegal (suicide without capture)."""
    new_board = [row[:] for row in board]
    stone = STONES[player]
    opponent_stone = STONES[1 - player]

    new_board[r][c] = stone

    # First, check and remove any opponent groups with zero liberties
    captured = []
    for nr, nc in _neighbors(r, c):
        if new_board[nr][nc] == opponent_stone:
            group = _find_group(new_board, nr, nc)
            if _count_liberties(new_board, group) == 0:
                captured.extend(group)
                new_board = _remove_group(new_board, group)

    # Then, check if own group has liberties (suicide check)
    own_group = _find_group(new_board, r, c)
    if _count_liberties(new_board, own_group) == 0:
        # Suicide - illegal unless we captured something
        if not captured:
            return None

    return new_board

def _count_territory(board: List[List[str]], player: int) -> int:
    """Count territory controlled by player (area scoring)."""
    stone = STONES[player]
    visited = set()
    territory = 0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == stone:
                territory += 1  # Count own stones
            elif board[r][c] == '' and (r, c) not in visited:
                # Flood fill empty region
                region = set()
                borders_black = False
                borders_white = False
                stack = [(r, c)]

                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in region:
                        continue
                    if board[cr][cc] == 'B':
                        borders_black = True
                        continue
                    if board[cr][cc] == 'W':
                        borders_white = True
                        continue

                    region.add((cr, cc))
                    for nr, nc in _neighbors(cr, cc):
                        if (nr, nc) not in region:
                            stack.append((nr, nc))

                visited.update(region)

                # Region belongs to player if only bordered by their stones
                if player == P0 and borders_black and not borders_white:
                    territory += len(region)
                elif player == P1 and borders_white and not borders_black:
                    territory += len(region)

    return territory

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    return {
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'current_player': P0,
        'previous_board_hash': None,  # For ko detection
        'passes': 0,  # Consecutive passes
        'captures': {P0: 0, P1: 0},  # Captured stones
        'is_terminal': False
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = {
        'board': [row[:] for row in state['board']],
        'current_player': 1 - state['current_player'],
        'previous_board_hash': _board_hash(state['board']),
        'passes': state['passes'],
        'captures': state['captures'].copy(),
        'is_terminal': False
    }

    if action == 'pass':
        new_state['passes'] = state['passes'] + 1
        if new_state['passes'] >= 2:
            new_state['is_terminal'] = True
            new_state['current_player'] = TERMINAL
        return new_state

    # Reset pass counter on placement
    new_state['passes'] = 0

    # Parse placement
    _, r_str, c_str = action.split('_')
    r, c = int(r_str), int(c_str)
    player = state['current_player']

    # Count captures before move
    old_opponent_count = sum(
        1 for rr in range(BOARD_SIZE) for cc in range(BOARD_SIZE)
        if state['board'][rr][cc] == STONES[1 - player]
    )

    # Apply move
    new_board = _apply_move(state['board'], r, c, player)
    new_state['board'] = new_board

    # Count captures after move
    new_opponent_count = sum(
        1 for rr in range(BOARD_SIZE) for cc in range(BOARD_SIZE)
        if new_board[rr][cc] == STONES[1 - player]
    )
    captured = old_opponent_count - new_opponent_count
    new_state['captures'][player] = state['captures'][player] + captured

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0 (Black)"
    if player_id == P1: return "Player 1 (White)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    if not state['is_terminal']:
        return [0.0, 0.0]

    # Area scoring
    black_score = _count_territory(state['board'], P0)
    white_score = _count_territory(state['board'], P1) + KOMI

    if black_score > white_score:
        return [1.0, -1.0]
    else:
        return [-1.0, 1.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['is_terminal']:
        return []

    actions = ['pass']
    player = state['current_player']
    board = state['board']
    prev_hash = state['previous_board_hash']

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != '':
                continue

            # Try the move
            new_board = _apply_move(board, r, c, player)

            if new_board is None:
                continue  # Suicide

            # Check ko
            if prev_hash is not None and _board_hash(new_board) == prev_hash:
                continue  # Ko violation

            actions.append(f'place_{r}_{c}')

    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Go is perfect information."""
    obs = {
        'board': state['board'],
        'captures': state['captures'],
        'passes': state['passes']
    }
    return [obs, obs]
