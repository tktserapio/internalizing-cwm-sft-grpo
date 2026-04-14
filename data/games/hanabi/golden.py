import copy
import random
from collections import Counter
from typing import Any, List, Tuple, Dict, Optional

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
COLORS = ['R', 'Y', 'G', 'B', 'W']
RANKS = [1, 2, 3, 4, 5]
DECK_COMPOSITION = {1: 3, 2: 2, 3: 2, 4: 2, 5: 1}
MAX_CLUES = 8
MAX_LIVES = 3
HAND_SIZE = 5


def _full_deck() -> Counter:
    deck = Counter()
    for c in COLORS:
        for r, count in DECK_COMPOSITION.items():
            deck[(c, r)] = count
    return deck


def _deck_size(deck: Counter) -> int:
    return sum(deck.values())


def _distinct_cards(deck: Counter) -> List[str]:
    """Return sorted deal actions for distinct cards in deck."""
    return sorted(f"deal:{c},{r}" for (c, r) in deck if deck[(c, r)] > 0)


def get_initial_state() -> State:
    """Returns the initial game state. Cards are dealt via chance actions."""
    return {
        'deck': _full_deck(),
        'p0_hand': [],
        'p1_hand': [],
        'board': {c: 0 for c in COLORS},
        'discard': [],
        'clues': MAX_CLUES,
        'lives': MAX_LIVES,
        'current_player': -1,  # Chance deals first
        'phase': 'deal_p0',    # deal_p0, deal_p1, play, draw_p0, draw_p1
        'turn': 0,
        'game_over': False,
        'final_round': False,
        'final_round_turns': 0,
    }


def _check_game_over(state: State) -> bool:
    if state['lives'] < 0:
        return True
    if all(state['board'][c] == 5 for c in COLORS):
        return True
    if state['final_round'] and state['final_round_turns'] >= 2:
        return True
    return False


def _finish_turn(state: State, acting_player: int, deck_empty_draw: bool = False):
    """Transition after a player's action (and possible draw) is complete."""
    if deck_empty_draw and not state['final_round']:
        state['final_round'] = True
        state['final_round_turns'] = 0

    state['phase'] = 'play'
    next_player = 1 - acting_player
    state['current_player'] = next_player

    if acting_player == 1:
        state['turn'] += 1

    if state['final_round']:
        state['final_round_turns'] += 1

    if _check_game_over(state):
        state['game_over'] = True
        state['current_player'] = -4


def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new = copy.deepcopy(state)

    if new['game_over']:
        return new

    # === CHANCE ACTIONS (deals and draws) ===
    if new['current_player'] == -1:
        _, card_str = action.split(":", 1)
        c, r_str = card_str.split(",")
        r = int(r_str)
        card = (c, r)

        new['deck'][card] -= 1
        if new['deck'][card] == 0:
            del new['deck'][card]

        if new['phase'] == 'deal_p0':
            new['p0_hand'].append(card)
            if len(new['p0_hand']) >= HAND_SIZE:
                new['phase'] = 'deal_p1'

        elif new['phase'] == 'deal_p1':
            new['p1_hand'].append(card)
            if len(new['p1_hand']) >= HAND_SIZE:
                new['phase'] = 'play'
                new['current_player'] = 0

        elif new['phase'].startswith('draw_'):
            drawing_player = int(new['phase'][-1])
            new[f'p{drawing_player}_hand'].append(card)
            _finish_turn(new, drawing_player)

        return new

    # === PLAYER ACTIONS ===
    player = new['current_player']
    hand = new[f'p{player}_hand']
    needs_draw = False
    parts = action.split()

    if parts[0] == "Play":
        idx = int(parts[1])
        if idx >= len(hand):
            return new
        card = hand[idx]
        color, rank = card
        if new['board'][color] == rank - 1:
            new['board'][color] = rank
        else:
            new['lives'] -= 1
            new['discard'].append(card)
        hand.pop(idx)
        needs_draw = True

    elif parts[0] == "Discard":
        idx = int(parts[1])
        if idx >= len(hand):
            return new
        card = hand[idx]
        new['discard'].append(card)
        new['clues'] = min(MAX_CLUES, new['clues'] + 1)
        hand.pop(idx)
        needs_draw = True

    elif parts[0] == "Reveal":
        if new['clues'] <= 0:
            return new
        new['clues'] -= 1

    # Check immediate end (lives lost or perfect score)
    if _check_game_over(new):
        new['game_over'] = True
        new['current_player'] = -4
        return new

    if needs_draw and new['deck']:
        new['phase'] = f'draw_p{player}'
        new['current_player'] = -1
    else:
        _finish_turn(new, player, deck_empty_draw=(needs_draw and not new['deck']))

    return new


def get_current_player(state: State) -> int:
    if state['game_over']:
        return -4
    return state['current_player']


def get_player_name(player_id: int) -> str:
    if player_id == -1:
        return "Chance"
    elif player_id == -4:
        return "Terminal"
    return f"Player {player_id}"


def get_rewards(state: State) -> List[float]:
    if state['lives'] < 0:
        return [0.0, 0.0]
    score = float(sum(state['board'].values()))
    return [score, score]


def get_legal_actions(state: State) -> List[Action]:
    if state['game_over']:
        return []

    if state['current_player'] == -1:
        return _distinct_cards(state['deck'])

    player = state['current_player']
    hand = state[f'p{player}_hand']
    actions = []

    for i in range(len(hand)):
        actions.append(f"Play {i}")

    if state['clues'] < MAX_CLUES:
        for i in range(len(hand)):
            actions.append(f"Discard {i}")

    if state['clues'] > 0:
        other = 1 - player
        other_hand = state[f'p{other}_hand']
        for c in COLORS:
            if any(card[0] == c for card in other_hand):
                actions.append(f"Reveal color {other} {c}")
        for r in RANKS:
            if any(card[1] == r for card in other_hand):
                actions.append(f"Reveal rank {other} {r}")

    return actions


def get_observations(state: State) -> List[PlayerObservation]:
    obs = []
    for player in [0, 1]:
        other = 1 - player
        observation = {
            'board': copy.deepcopy(state['board']),
            'discard': copy.deepcopy(state['discard']),
            'clues': state['clues'],
            'lives': state['lives'],
            'partner_hand': copy.deepcopy(state[f'p{other}_hand']),
            'deck_size': _deck_size(state['deck']),
            'game_over': state['game_over'],
            'current_player': state['current_player'],
        }
        observation['my_hand'] = [None] * len(state[f'p{player}_hand'])
        obs.append(observation)
    return obs


def _find_partner_hand_diff(ph_before, ph_after):
    """Find the removed card and drawn card from partner hand change.
    Returns (removed_card, drawn_card) or (None, None) if hands are equal.
    """
    if ph_before == ph_after:
        return None, None

    for j in range(len(ph_before)):
        remaining = ph_before[:j] + ph_before[j+1:]
        if len(ph_after) > len(remaining) and ph_after[:len(remaining)] == remaining:
            return ph_before[j], ph_after[-1]
        if ph_after == remaining:
            return ph_before[j], None

    return None, None


def _infer_my_card(obs_before, obs_after, player_action, partner_removed):
    """Infer the card the player held at the played/discarded index.
    Uses discard pile ordering (player acts before partner) and board changes.
    """
    parts = player_action.split()
    if parts[0] not in ('Play', 'Discard'):
        return None

    discard_before = [tuple(c) for c in obs_before['discard']]
    discard_after = [tuple(c) for c in obs_after['discard']]
    new_discards = discard_after[len(discard_before):]

    if parts[0] == 'Discard':
        # Player's discard is the FIRST new entry (player acts before partner)
        if new_discards:
            return new_discards[0]
        return None

    # Play action — check for successful play via board change
    board_before = obs_before['board']
    board_after = obs_after['board']

    # Find board advances and attribute to player vs partner
    for c in COLORS:
        diff = board_after[c] - board_before[c]
        if diff == 0:
            continue
        partner_played_c = (partner_removed is not None and partner_removed[0] == c
                            and partner_removed not in new_discards)
        if diff >= 1 and not partner_played_c:
            return (c, board_before[c] + 1)
        if diff == 2 and partner_played_c:
            # Both played same color: player first
            return (c, board_before[c] + 1)

    # Failed play — card went to discard (first new entry)
    if new_discards:
        return new_discards[0]

    return None


def resample_history(
    obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]],
    player_id: int,
) -> List[Action]:
    """Stochastically sample a valid action sequence consistent with player_id's observations."""
    if not obs_action_history:
        return []

    partner_id = 1 - player_id
    n_obs = len(obs_action_history)

    # === Phase 1: Infer player's cards from observation diffs ===
    # Track partner hand diffs and inferred player cards
    partner_removed_cards = []  # per gap: (removed, drawn) or (None, None)
    inferred_cards = {}  # obs_idx -> card at the played/discarded index

    for i in range(n_obs - 1):
        obs_now = obs_action_history[i][0]
        obs_next = obs_action_history[i + 1][0]
        action = obs_action_history[i][1]

        ph_before = [tuple(c) for c in obs_now['partner_hand']]
        ph_after = [tuple(c) for c in obs_next['partner_hand']]
        p_removed, p_drawn = _find_partner_hand_diff(ph_before, ph_after)
        partner_removed_cards.append((p_removed, p_drawn))

        if action and action.split()[0] in ('Play', 'Discard'):
            card = _infer_my_card(obs_now, obs_next, action, p_removed)
            if card:
                inferred_cards[i] = tuple(card)

    # === Phase 2: Build player's initial hand using index tracking ===
    first_obs = obs_action_history[0][0]
    partner_obs_hand = [tuple(c) for c in first_obs['partner_hand']]
    partner_first_draw = None

    if player_id == 1:
        # P0 acted before P1's first observation; reconstruct P0's dealt hand
        obs0_clues = first_obs['clues']
        obs0_board = first_obs['board']
        obs0_discard = [tuple(c) for c in first_obs['discard']]

        played_card = None
        if obs0_clues < MAX_CLUES:
            # P0 revealed → hand unchanged
            partner_init = list(partner_obs_hand)
        else:
            # P0 played (discard not legal at max clues)
            for c in COLORS:
                if obs0_board[c] > 0:
                    played_card = (c, 1)
                    break
            if played_card is None and obs0_discard:
                played_card = tuple(obs0_discard[0])

            if played_card is not None:
                partner_init = [played_card] + list(partner_obs_hand[:-1])
                partner_first_draw = partner_obs_hand[-1]
            else:
                partner_init = list(partner_obs_hand)
    else:
        partner_init = list(partner_obs_hand)

    initial_hand = [None] * HAND_SIZE
    # index_map[j] = which "slot" the current hand position j maps to
    # slots 0..4 = initial hand, slots 5+ = draws
    index_map = list(range(HAND_SIZE))
    next_draw_slot = HAND_SIZE
    draw_cards = {}  # slot_id -> inferred card (for draws)

    for i in range(n_obs):
        action = obs_action_history[i][1]
        if action is None:
            continue
        parts = action.split()
        if parts[0] in ('Play', 'Discard'):
            idx = int(parts[1])
            if idx < len(index_map):
                slot = index_map[idx]
                if i in inferred_cards:
                    if slot < HAND_SIZE:
                        initial_hand[slot] = inferred_cards[i]
                    else:
                        draw_cards[slot] = inferred_cards[i]
                index_map.pop(idx)

            # Detect draw: hand size unchanged between consecutive obs
            if i < n_obs - 1:
                hs_now = len(obs_action_history[i][0]['my_hand'])
                hs_next = len(obs_action_history[i + 1][0]['my_hand'])
                if hs_next >= hs_now:
                    index_map.append(next_draw_slot)
                    next_draw_slot += 1

    # === Phases 3-5: Fill unknowns, deal, simulate (with retry) ===
    base_pool = _full_deck()
    for card in partner_init:
        base_pool[card] -= 1
    if partner_first_draw is not None:
        if base_pool[partner_first_draw] > 0:
            base_pool[partner_first_draw] -= 1
    for p_removed, p_drawn in partner_removed_cards:
        if p_drawn and base_pool[tuple(p_drawn)] > 0:
            base_pool[tuple(p_drawn)] -= 1
    for slot in range(HAND_SIZE):
        if initial_hand[slot] is not None:
            if base_pool[initial_hand[slot]] > 0:
                base_pool[initial_hand[slot]] -= 1
    for card in draw_cards.values():
        if base_pool[card] > 0:
            base_pool[card] -= 1

    best_history: List[Action] = []
    best_obs_idx = -1

    for _attempt in range(50):
        # Phase 3: fill unknowns randomly
        pool = []
        for card, count in base_pool.items():
            pool.extend([card] * count)
        random.shuffle(pool)

        trial_hand = list(initial_hand)
        pi = 0
        for slot in range(HAND_SIZE):
            if trial_hand[slot] is None and pi < len(pool):
                trial_hand[slot] = pool[pi]
                pi += 1

        my_init = [c for c in trial_hand if c is not None]
        while len(my_init) < HAND_SIZE and pi < len(pool):
            my_init.append(pool[pi])
            pi += 1

        # Phase 4: deal
        if player_id == 0:
            p0_cards, p1_cards = my_init, partner_init
        else:
            p0_cards, p1_cards = partner_init, my_init

        history: List[Action] = []
        for card in p0_cards:
            history.append(f"deal:{card[0]},{card[1]}")
        for card in p1_cards:
            history.append(f"deal:{card[0]},{card[1]}")

        state = get_initial_state()
        for act in history:
            state = apply_action(state, act)

        # Phase 5: simulate
        obs_idx = 0
        my_draw_slot = HAND_SIZE
        dead_end = False

        while get_current_player(state) != -4:
            cp = get_current_player(state)

            if cp == -1:
                phase = state['phase']
                if not phase.startswith('draw_'):
                    break
                drawing_player = int(phase[-1])

                if drawing_player == partner_id:
                    if obs_idx < n_obs:
                        next_ph = [tuple(c) for c in obs_action_history[obs_idx][0]['partner_hand']]
                        cur_ph = [tuple(c) for c in state[f'p{partner_id}_hand']]
                        if len(next_ph) == len(cur_ph) + 1 and next_ph[:len(cur_ph)] == cur_ph:
                            drawn = next_ph[-1]
                            act = f"deal:{drawn[0]},{drawn[1]}"
                            if act in get_legal_actions(state):
                                history.append(act)
                                state = apply_action(state, act)
                                continue
                    legal = get_legal_actions(state)
                    if legal:
                        history.append(random.choice(legal))
                        state = apply_action(state, history[-1])
                    else:
                        break
                else:
                    known_card = draw_cards.get(my_draw_slot)
                    my_draw_slot += 1
                    if known_card is not None:
                        act = f"deal:{known_card[0]},{known_card[1]}"
                        if act in get_legal_actions(state):
                            history.append(act)
                            state = apply_action(state, act)
                            continue
                    legal = get_legal_actions(state)
                    if legal:
                        history.append(random.choice(legal))
                        state = apply_action(state, history[-1])
                    else:
                        break

            elif cp == player_id:
                if obs_idx >= n_obs:
                    break
                # Verify observation matches
                robs = get_observations(state)[player_id]
                exp = obs_action_history[obs_idx][0]
                mismatch = False
                for key in ['board', 'discard', 'clues', 'lives', 'partner_hand']:
                    if key in exp and key in robs and robs[key] != exp[key]:
                        mismatch = True
                        break
                if mismatch:
                    dead_end = True
                    break

                _, action = obs_action_history[obs_idx]
                if action is None:
                    break
                history.append(action)
                state = apply_action(state, action)
                obs_idx += 1

            else:
                # Partner's turn — find action matching next observation
                legal = get_legal_actions(state)
                if not legal:
                    break

                found = False
                if obs_idx < n_obs:
                    target_obs = obs_action_history[obs_idx][0]
                    target_ph = [tuple(c) for c in target_obs['partner_hand']]
                    target_clues = target_obs['clues']
                    target_lives = target_obs['lives']
                    target_board = target_obs['board']
                    target_discard = [tuple(c) for c in target_obs['discard']]

                    random.shuffle(legal)
                    for act in legal:
                        test = apply_action(state, act)
                        if test['game_over']:
                            continue
                        if (test['clues'] != target_clues
                                or test['lives'] != target_lives
                                or test['board'] != target_board
                                or [tuple(c) for c in test['discard']] != target_discard):
                            continue

                        test_ph = [tuple(c) for c in test[f'p{partner_id}_hand']]

                        if get_current_player(test) == -1 and test['phase'] == f'draw_p{partner_id}':
                            if (len(target_ph) == len(test_ph) + 1
                                    and target_ph[:len(test_ph)] == test_ph):
                                drawn = target_ph[-1]
                                draw_act = f"deal:{drawn[0]},{drawn[1]}"
                                if draw_act in get_legal_actions(test):
                                    history.append(act)
                                    state = apply_action(state, act)
                                    found = True
                                    break
                        else:
                            if test_ph == target_ph:
                                history.append(act)
                                state = apply_action(state, act)
                                found = True
                                break

                if not found:
                    dead_end = True
                    break

        if obs_idx > best_obs_idx:
            best_history = history
            best_obs_idx = obs_idx
        if not dead_end:
            return history

    return best_history
