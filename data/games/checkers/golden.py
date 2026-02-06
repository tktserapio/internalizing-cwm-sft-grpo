from typing import Any, Dict, List, Optional, Tuple
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
BOARD_SIZE = 8
PIECES = {P0: 'r', P1: 'b'}  # red, black
KINGS = {P0: 'R', P1: 'B'}
NO_CAPTURE_DRAW_LIMIT = 40

def _is_valid_square(r: int, c: int) -> bool:
    """Check if position is on board."""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def _is_dark_square(r: int, c: int) -> bool:
    """Dark squares are playable (where (r+c) is odd)."""
    return (r + c) % 2 == 1

def _get_piece_owner(piece: str) -> Optional[int]:
    """Return owner of piece, or None if empty."""
    if piece in ('r', 'R'): return P0
    if piece in ('b', 'B'): return P1
    return None

def _is_king(piece: str) -> bool:
    """Check if piece is a king."""
    return piece in ('R', 'B')

def _get_forward_dirs(player: int) -> List[int]:
    """Get forward row directions for player."""
    return [-1] if player == P0 else [1]

def _get_all_dirs(player: int, is_king: bool) -> List[int]:
    """Get all valid row directions for a piece."""
    if is_king:
        return [-1, 1]
    return _get_forward_dirs(player)

def _find_jumps(board: List[List[str]], r: int, c: int, player: int,
                path: List[Tuple[int, int]], captured: set) -> List[List[Tuple[int, int]]]:
    """Find all possible jump sequences from position."""
    piece = board[r][c]
    is_king = _is_king(piece)
    row_dirs = _get_all_dirs(player, is_king)

    jumps = []
    for dr in row_dirs:
        for dc in [-1, 1]:
            mr, mc = r + dr, c + dc  # middle (captured) position
            er, ec = r + 2*dr, c + 2*dc  # end position

            if not _is_valid_square(er, ec):
                continue
            if (mr, mc) in captured:
                continue

            middle_piece = board[mr][mc]
            end_piece = board[er][ec]

            if (middle_piece != '' and
                _get_piece_owner(middle_piece) != player and
                end_piece == ''):

                new_path = path + [(er, ec)]
                new_captured = captured | {(mr, mc)}

                # Recursively find more jumps
                more_jumps = _find_jumps(board, er, ec, player, new_path, new_captured)

                if more_jumps:
                    jumps.extend(more_jumps)
                else:
                    jumps.append(new_path)

    return jumps

def _get_all_jumps(board: List[List[str]], player: int) -> List[Action]:
    """Get all jump actions for player."""
    actions = []
    piece_chars = (PIECES[player], KINGS[player])

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] in piece_chars:
                jump_sequences = _find_jumps(board, r, c, player, [(r, c)], set())
                for seq in jump_sequences:
                    action = "jump_" + "_".join(f"{pr}_{pc}" for pr, pc in seq)
                    actions.append(action)

    return actions

def _get_all_moves(board: List[List[str]], player: int) -> List[Action]:
    """Get all simple move actions for player."""
    actions = []
    piece_chars = (PIECES[player], KINGS[player])

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            piece = board[r][c]
            if piece in piece_chars:
                is_king = _is_king(piece)
                row_dirs = _get_all_dirs(player, is_king)

                for dr in row_dirs:
                    for dc in [-1, 1]:
                        nr, nc = r + dr, c + dc
                        if _is_valid_square(nr, nc) and board[nr][nc] == '':
                            actions.append(f"move_{r}_{c}_{nr}_{nc}")

    return actions

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Place black pieces (rows 0-2)
    for r in range(3):
        for c in range(BOARD_SIZE):
            if _is_dark_square(r, c):
                board[r][c] = 'b'

    # Place red pieces (rows 5-7)
    for r in range(5, 8):
        for c in range(BOARD_SIZE):
            if _is_dark_square(r, c):
                board[r][c] = 'r'

    return {
        'board': board,
        'current_player': P0,
        'no_capture_count': 0,
        'status': 'ongoing'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_board = [row[:] for row in state['board']]
    current = state['current_player']
    no_capture_count = state['no_capture_count']

    parts = action.split('_')
    is_jump = (parts[0] == 'jump')

    if is_jump:
        # Parse jump path
        coords = []
        i = 1
        while i < len(parts):
            coords.append((int(parts[i]), int(parts[i+1])))
            i += 2

        piece = new_board[coords[0][0]][coords[0][1]]
        new_board[coords[0][0]][coords[0][1]] = ''

        # Process each jump in the chain
        for i in range(len(coords) - 1):
            sr, sc = coords[i]
            er, ec = coords[i + 1]
            # Remove captured piece
            mr, mc = (sr + er) // 2, (sc + ec) // 2
            new_board[mr][mc] = ''

        # Place piece at final position
        final_r, final_c = coords[-1]

        # Check for promotion
        if (current == P0 and final_r == 0) or (current == P1 and final_r == 7):
            piece = KINGS[current]

        new_board[final_r][final_c] = piece
        no_capture_count = 0  # Reset on capture

    else:
        # Simple move
        _, sr, sc, er, ec = parts
        sr, sc, er, ec = int(sr), int(sc), int(er), int(ec)

        piece = new_board[sr][sc]
        new_board[sr][sc] = ''

        # Check for promotion
        if (current == P0 and er == 0) or (current == P1 and er == 7):
            piece = KINGS[current]

        new_board[er][ec] = piece
        no_capture_count += 1

    new_state = {
        'board': new_board,
        'current_player': 1 - current,
        'no_capture_count': no_capture_count,
        'status': 'ongoing'
    }

    # Check game over conditions
    opponent = 1 - current
    opponent_pieces = (PIECES[opponent], KINGS[opponent])
    has_opponent_pieces = any(
        new_board[r][c] in opponent_pieces
        for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
    )

    if not has_opponent_pieces:
        # Current player wins - captured all pieces
        new_state['status'] = f'p{current}_won'
        new_state['current_player'] = TERMINAL
    elif no_capture_count >= NO_CAPTURE_DRAW_LIMIT:
        new_state['status'] = 'draw'
        new_state['current_player'] = TERMINAL
    else:
        # Check if opponent can move
        opponent_actions = get_legal_actions(new_state)
        if not opponent_actions:
            # Opponent blocked - current player wins
            new_state['status'] = f'p{current}_won'
            new_state['current_player'] = TERMINAL

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0 (Red)"
    if player_id == P1: return "Player 1 (Black)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player. Non-zero only at terminal states."""
    status = state['status']
    if status == 'p0_won':
        return [1.0, -1.0]
    elif status == 'p1_won':
        return [-1.0, 1.0]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['current_player'] == TERMINAL:
        return []

    player = state['current_player']
    board = state['board']

    # Jumps are mandatory if available
    jumps = _get_all_jumps(board, player)
    if jumps:
        return jumps

    # Otherwise, simple moves
    return _get_all_moves(board, player)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Checkers is perfect information."""
    obs = {
        'board': state['board'],
        'status': state['status'],
        'no_capture_count': state['no_capture_count']
    }
    return [obs, obs]
