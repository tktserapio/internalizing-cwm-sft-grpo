from typing import Any, Dict, List, Optional, Tuple

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Board constants
ROWS = 8
COLS = 8
EMPTY = -1
WHITE = 0  # Player 0, moves up (toward row 8)
BLACK = 1  # Player 1, moves down (toward row 1)

def _pos_to_notation(row: int, col: int) -> str:
    """Convert 0-indexed (row, col) to chess notation like 'e2'."""
    return chr(ord('a') + col) + str(row + 1)

def _notation_to_pos(notation: str) -> Tuple[int, int]:
    """Convert chess notation 'e2' to 0-indexed (row, col)."""
    col = ord(notation[0]) - ord('a')
    row = int(notation[1]) - 1
    return row, col

def _create_initial_board() -> List[List[int]]:
    """Create starting board with pieces in first two rows for each player."""
    board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    # White pieces on rows 0 and 1 (rows 1-2 in notation)
    for r in range(2):
        for c in range(COLS):
            board[r][c] = WHITE
    # Black pieces on rows 6 and 7 (rows 7-8 in notation)
    for r in range(6, 8):
        for c in range(COLS):
            board[r][c] = BLACK
    return board

def get_initial_state() -> State:
    """Returns the initial game state."""
    return {
        "board": _create_initial_board(),
        "current_player": WHITE,
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
    if player_id == WHITE:
        return "White"
    elif player_id == BLACK:
        return "Black"
    return "Unknown"

def _count_pieces(board: List[List[int]], player: int) -> int:
    """Count pieces belonging to a player."""
    count = 0
    for row in board:
        for cell in row:
            if cell == player:
                count += 1
    return count

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current player."""
    if state["terminal"]:
        return []

    board = state["board"]
    player = state["current_player"]
    actions = []

    # Direction: White moves up (+1 row), Black moves down (-1 row)
    dr = 1 if player == WHITE else -1

    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != player:
                continue

            src = _pos_to_notation(r, c)
            new_r = r + dr

            if new_r < 0 or new_r >= ROWS:
                continue

            # Forward straight move (only if empty)
            if board[new_r][c] == EMPTY:
                dst = _pos_to_notation(new_r, c)
                actions.append(f"{src}-{dst}")

            # Forward diagonal moves (can move to empty or capture opponent)
            for dc in [-1, 1]:
                new_c = c + dc
                if new_c < 0 or new_c >= COLS:
                    continue

                target = board[new_r][new_c]
                dst = _pos_to_notation(new_r, new_c)

                if target == EMPTY:
                    # Regular diagonal move
                    actions.append(f"{src}-{dst}")
                elif target == 1 - player:
                    # Capture (diagonal only)
                    actions.append(f"{src}x{dst}")

    return sorted(actions)

def _check_winner(board: List[List[int]], player: int, new_r: int) -> Optional[int]:
    """Check if player has won by reaching back row or eliminating opponent."""
    # Win by reaching opponent's back row
    if player == WHITE and new_r == ROWS - 1:
        return WHITE
    if player == BLACK and new_r == 0:
        return BLACK

    # Win by eliminating all opponent pieces
    opponent = 1 - player
    if _count_pieces(board, opponent) == 0:
        return player

    return None

def apply_action(state: State, action: Action) -> State:
    """Apply action and return new state."""
    if state["terminal"]:
        return state

    player = state["current_player"]

    # Parse action: "e2-e3" or "e2xd3"
    is_capture = 'x' in action
    parts = action.split('x' if is_capture else '-')
    src_r, src_c = _notation_to_pos(parts[0])
    dst_r, dst_c = _notation_to_pos(parts[1])

    # Copy board
    new_board = [row[:] for row in state["board"]]

    # Move piece
    new_board[dst_r][dst_c] = player
    new_board[src_r][src_c] = EMPTY

    # Check for winner
    winner = _check_winner(new_board, player, dst_r)
    terminal = winner is not None

    # Also check if opponent has no pieces (already handled in _check_winner)
    # Or if opponent has no legal moves (stalemate = opponent loses)
    if not terminal:
        next_player = 1 - player
        # Quick check: does opponent have any pieces?
        if _count_pieces(new_board, next_player) == 0:
            winner = player
            terminal = True

    return {
        "board": new_board,
        "current_player": 1 - player if not terminal else -4,
        "winner": winner,
        "terminal": terminal
    }

def get_rewards(state: State) -> List[float]:
    """Returns rewards [white_reward, black_reward]."""
    winner = state["winner"]
    if winner == WHITE:
        return [1.0, -1.0]
    elif winner == BLACK:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observations. Perfect info game, both players see same state."""
    obs = {
        "board": [row[:] for row in state["board"]],
        "current_player": state["current_player"],
        "terminal": state["terminal"]
    }
    return [obs, obs]
