from typing import Any, Dict, List, Optional, Tuple
import copy

# Type Definitions
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
P0, P1, TERMINAL = 0, 1, -4
BOARD_SIZE = 8
FILES = 'abcdefgh'
RANKS = '12345678'

# Piece characters (uppercase=White, lowercase=Black)
WHITE_PIECES = 'KQRBNP'
BLACK_PIECES = 'kqrbnp'

def _pos_to_algebraic(r: int, c: int) -> str:
    """Convert (row, col) to algebraic notation like 'e4'."""
    return FILES[c] + RANKS[r]

def _algebraic_to_pos(sq: str) -> Tuple[int, int]:
    """Convert 'e4' to (row, col)."""
    c = FILES.index(sq[0])
    r = RANKS.index(sq[1])
    return (r, c)

def _is_white(piece: str) -> bool:
    return piece in WHITE_PIECES

def _is_black(piece: str) -> bool:
    return piece in BLACK_PIECES

def _owner(piece: str) -> Optional[int]:
    if _is_white(piece): return P0
    if _is_black(piece): return P1
    return None

def _piece_type(piece: str) -> str:
    return piece.upper()

def _in_bounds(r: int, c: int) -> bool:
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def _find_king(board: List[List[str]], player: int) -> Optional[Tuple[int, int]]:
    """Find the king's position for a player."""
    king = 'K' if player == P0 else 'k'
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == king:
                return (r, c)
    return None

def _is_attacked(board: List[List[str]], r: int, c: int, by_player: int) -> bool:
    """Check if square (r,c) is attacked by by_player."""
    for rr in range(BOARD_SIZE):
        for cc in range(BOARD_SIZE):
            piece = board[rr][cc]
            if piece == '' or _owner(piece) != by_player:
                continue
            if _can_attack(board, rr, cc, r, c):
                return True
    return False

def _can_attack(board: List[List[str]], fr: int, fc: int, tr: int, tc: int) -> bool:
    """Check if piece at (fr,fc) can attack (tr,tc)."""
    piece = board[fr][fc]
    pt = _piece_type(piece)
    dr, dc = tr - fr, tc - fc

    if pt == 'P':
        direction = 1 if _is_white(piece) else -1
        return dr == direction and abs(dc) == 1

    if pt == 'N':
        return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]

    if pt == 'K':
        return abs(dr) <= 1 and abs(dc) <= 1 and (dr != 0 or dc != 0)

    if pt == 'R':
        if dr != 0 and dc != 0:
            return False
        return _path_clear(board, fr, fc, tr, tc)

    if pt == 'B':
        if abs(dr) != abs(dc) or dr == 0:
            return False
        return _path_clear(board, fr, fc, tr, tc)

    if pt == 'Q':
        if dr == 0 or dc == 0 or abs(dr) == abs(dc):
            return _path_clear(board, fr, fc, tr, tc)
        return False

    return False

def _path_clear(board: List[List[str]], fr: int, fc: int, tr: int, tc: int) -> bool:
    """Check if path between two squares is clear (exclusive of endpoints)."""
    dr = 0 if tr == fr else (1 if tr > fr else -1)
    dc = 0 if tc == fc else (1 if tc > fc else -1)

    r, c = fr + dr, fc + dc
    while (r, c) != (tr, tc):
        if board[r][c] != '':
            return False
        r, c = r + dr, c + dc
    return True

def _in_check(board: List[List[str]], player: int) -> bool:
    """Check if player's king is in check."""
    king_pos = _find_king(board, player)
    if king_pos is None:
        return True  # King captured (shouldn't happen in valid game)
    return _is_attacked(board, king_pos[0], king_pos[1], 1 - player)

def _generate_moves(state: State, only_legal: bool = True) -> List[Action]:
    """Generate all moves for current player."""
    board = state['board']
    player = state['current_player']
    moves = []

    for fr in range(BOARD_SIZE):
        for fc in range(BOARD_SIZE):
            piece = board[fr][fc]
            if piece == '' or _owner(piece) != player:
                continue

            pt = _piece_type(piece)
            piece_moves = _get_piece_moves(state, fr, fc)
            moves.extend(piece_moves)

    # Add castling
    moves.extend(_get_castling_moves(state))

    if only_legal:
        # Filter out moves that leave king in check
        legal_moves = []
        for move in moves:
            new_state = _apply_move_unchecked(state, move)
            if not _in_check(new_state['board'], player):
                legal_moves.append(move)
        return legal_moves

    return moves

def _get_piece_moves(state: State, fr: int, fc: int) -> List[Action]:
    """Get moves for piece at (fr, fc)."""
    board = state['board']
    piece = board[fr][fc]
    player = _owner(piece)
    pt = _piece_type(piece)
    moves = []

    from_sq = _pos_to_algebraic(fr, fc)

    if pt == 'P':
        direction = 1 if player == P0 else -1
        start_rank = 1 if player == P0 else 6
        promo_rank = 7 if player == P0 else 0

        # Forward one
        nr = fr + direction
        if _in_bounds(nr, fc) and board[nr][fc] == '':
            if nr == promo_rank:
                for promo in 'QRBN':
                    moves.append(f"P_{from_sq}_{_pos_to_algebraic(nr, fc)}_{promo}")
            else:
                moves.append(f"P_{from_sq}_{_pos_to_algebraic(nr, fc)}")

            # Forward two from start
            if fr == start_rank:
                nr2 = fr + 2 * direction
                if board[nr2][fc] == '':
                    moves.append(f"P_{from_sq}_{_pos_to_algebraic(nr2, fc)}")

        # Captures
        for dc in [-1, 1]:
            nr, nc = fr + direction, fc + dc
            if not _in_bounds(nr, nc):
                continue

            target = board[nr][nc]
            # Regular capture or en passant
            ep = state.get('en_passant')
            if (target != '' and _owner(target) != player) or (ep and ep == (nr, nc)):
                if nr == promo_rank:
                    for promo in 'QRBN':
                        moves.append(f"P_{from_sq}_{_pos_to_algebraic(nr, nc)}_{promo}")
                else:
                    moves.append(f"P_{from_sq}_{_pos_to_algebraic(nr, nc)}")

    elif pt == 'N':
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = fr + dr, fc + dc
            if _in_bounds(nr, nc):
                target = board[nr][nc]
                if target == '' or _owner(target) != player:
                    moves.append(f"N_{from_sq}_{_pos_to_algebraic(nr, nc)}")

    elif pt == 'K':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = fr + dr, fc + dc
                if _in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target == '' or _owner(target) != player:
                        moves.append(f"K_{from_sq}_{_pos_to_algebraic(nr, nc)}")

    elif pt in 'RBQ':
        directions = []
        if pt in 'RQ':
            directions.extend([(0, 1), (0, -1), (1, 0), (-1, 0)])
        if pt in 'BQ':
            directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])

        for dr, dc in directions:
            nr, nc = fr + dr, fc + dc
            while _in_bounds(nr, nc):
                target = board[nr][nc]
                if target == '':
                    moves.append(f"{pt}_{from_sq}_{_pos_to_algebraic(nr, nc)}")
                elif _owner(target) != player:
                    moves.append(f"{pt}_{from_sq}_{_pos_to_algebraic(nr, nc)}")
                    break
                else:
                    break
                nr, nc = nr + dr, nc + dc

    return moves

def _get_castling_moves(state: State) -> List[Action]:
    """Get castling moves if legal."""
    moves = []
    board = state['board']
    player = state['current_player']
    rights = state['castling_rights']

    rank = 0 if player == P0 else 7
    king_file = 4

    # Check king hasn't moved and not in check
    if _in_check(board, player):
        return moves

    # Kingside
    if rights[player]['kingside']:
        if (board[rank][5] == '' and board[rank][6] == '' and
            not _is_attacked(board, rank, 5, 1 - player) and
            not _is_attacked(board, rank, 6, 1 - player)):
            moves.append('O-O')

    # Queenside
    if rights[player]['queenside']:
        if (board[rank][1] == '' and board[rank][2] == '' and board[rank][3] == '' and
            not _is_attacked(board, rank, 2, 1 - player) and
            not _is_attacked(board, rank, 3, 1 - player)):
            moves.append('O-O-O')

    return moves

def _apply_move_unchecked(state: State, action: Action) -> State:
    """Apply move without checking legality."""
    new_board = [row[:] for row in state['board']]
    player = state['current_player']
    new_rights = copy.deepcopy(state['castling_rights'])
    new_ep = None
    new_halfmove = state['halfmove_clock'] + 1

    if action == 'O-O':
        rank = 0 if player == P0 else 7
        king = 'K' if player == P0 else 'k'
        rook = 'R' if player == P0 else 'r'
        new_board[rank][4] = ''
        new_board[rank][7] = ''
        new_board[rank][6] = king
        new_board[rank][5] = rook
        new_rights[player] = {'kingside': False, 'queenside': False}
        new_halfmove = state['halfmove_clock'] + 1

    elif action == 'O-O-O':
        rank = 0 if player == P0 else 7
        king = 'K' if player == P0 else 'k'
        rook = 'R' if player == P0 else 'r'
        new_board[rank][4] = ''
        new_board[rank][0] = ''
        new_board[rank][2] = king
        new_board[rank][3] = rook
        new_rights[player] = {'kingside': False, 'queenside': False}

    else:
        parts = action.split('_')
        piece_char = parts[0]
        from_sq = parts[1]
        to_sq = parts[2]
        promo = parts[3] if len(parts) > 3 else None

        fr, fc = _algebraic_to_pos(from_sq)
        tr, tc = _algebraic_to_pos(to_sq)

        piece = new_board[fr][fc]
        captured = new_board[tr][tc]

        # Handle en passant capture
        if piece_char == 'P' and state.get('en_passant') == (tr, tc):
            ep_capture_r = fr  # Pawn being captured is on same rank as moving pawn
            new_board[ep_capture_r][tc] = ''
            new_halfmove = 0

        new_board[fr][fc] = ''

        # Promotion
        if promo:
            piece = promo if player == P0 else promo.lower()
            new_halfmove = 0

        new_board[tr][tc] = piece

        # Reset halfmove on pawn move or capture
        if piece_char == 'P' or captured != '':
            new_halfmove = 0

        # Set en passant square
        if piece_char == 'P' and abs(tr - fr) == 2:
            new_ep = ((fr + tr) // 2, fc)

        # Update castling rights
        if piece_char == 'K':
            new_rights[player] = {'kingside': False, 'queenside': False}
        if piece_char == 'R':
            if fc == 0:
                new_rights[player]['queenside'] = False
            elif fc == 7:
                new_rights[player]['kingside'] = False

        # If rook captured
        if captured != '' and _piece_type(captured) == 'R':
            opp = 1 - player
            if tr == (0 if opp == P0 else 7):
                if tc == 0:
                    new_rights[opp]['queenside'] = False
                elif tc == 7:
                    new_rights[opp]['kingside'] = False

    return {
        'board': new_board,
        'current_player': 1 - player,
        'castling_rights': new_rights,
        'en_passant': new_ep,
        'halfmove_clock': new_halfmove,
        'is_terminal': False,
        'result': None
    }

def _insufficient_material(board: List[List[str]]) -> bool:
    """Check for insufficient material draw."""
    pieces = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p != '':
                pieces.append(p.upper())

    pieces.sort()

    # K vs K
    if pieces == ['K', 'K']:
        return True
    # K+B vs K or K+N vs K
    if pieces in [['B', 'K', 'K'], ['K', 'K', 'N']]:
        return True

    return False

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # Set up initial position
    back_rank_white = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    back_rank_black = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']

    board[0] = back_rank_white[:]
    board[1] = ['P'] * 8
    board[6] = ['p'] * 8
    board[7] = back_rank_black[:]

    return {
        'board': board,
        'current_player': P0,
        'castling_rights': {
            P0: {'kingside': True, 'queenside': True},
            P1: {'kingside': True, 'queenside': True}
        },
        'en_passant': None,
        'halfmove_clock': 0,
        'is_terminal': False,
        'result': None  # 'white', 'black', 'draw'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = _apply_move_unchecked(state, action)

    # Check for game end
    opponent = new_state['current_player']
    legal_moves = _generate_moves(new_state, only_legal=True)

    if len(legal_moves) == 0:
        new_state['is_terminal'] = True
        new_state['current_player'] = TERMINAL
        if _in_check(new_state['board'], opponent):
            # Checkmate
            new_state['result'] = 'white' if opponent == P1 else 'black'
        else:
            # Stalemate
            new_state['result'] = 'draw'
    elif new_state['halfmove_clock'] >= 50:  # 25-move rule (stricter for training)
        new_state['is_terminal'] = True
        new_state['current_player'] = TERMINAL
        new_state['result'] = 'draw'
    elif _insufficient_material(new_state['board']):
        new_state['is_terminal'] = True
        new_state['current_player'] = TERMINAL
        new_state['result'] = 'draw'

    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, or -4 for terminal state."""
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == P0: return "Player 0 (White)"
    if player_id == P1: return "Player 1 (Black)"
    return "Terminal"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player."""
    result = state['result']
    if result == 'white':
        return [1.0, -1.0]
    elif result == 'black':
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]  # Draw

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current state. Empty list if terminal."""
    if state['is_terminal']:
        return []
    return _generate_moves(state, only_legal=True)

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns [player_0_obs, player_1_obs]. Chess is perfect information."""
    obs = {
        'board': state['board'],
        'castling_rights': state['castling_rights'],
        'en_passant': state['en_passant'],
        'halfmove_clock': state['halfmove_clock']
    }
    return [obs, obs]
