import random
from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy

# Type aliases
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game Constants
RANKS = ['J', 'Q', 'K']
DECK = RANKS * 2
SMALL_BLIND = 1
BIG_BLIND = 2
BET_SIZES = {1: 2, 2: 4}
MAX_RAISES_PER_ROUND = 2

def get_initial_state() -> State:
    """Returns the initial game state."""
    return {
        'deck': DECK.copy(),
        'private_cards': [None, None],
        'public_card': None,
        'pot': SMALL_BLIND + BIG_BLIND,
        'bets': [SMALL_BLIND, BIG_BLIND],
        'stack': [SMALL_BLIND, BIG_BLIND],
        'round': 1,
        'history': [], # List of (player_id, action)
        'current_player': -1, # -1: Chance, 0: P1, 1: P2
        'raises_in_round': 0,
        'folded': None,
        'stage': 'deal_private'
    }

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = deepcopy(state)
    current_player = new_state['current_player']
    
    # Record history for all actions
    if current_player != -4:
        new_state['history'].append((current_player, action))

    # --- CHANCE ACTIONS ---
    if current_player == -1:
        _, card = action.split(':')
        new_state['deck'].remove(card)
        
        if new_state['stage'] == 'deal_private':
            if new_state['private_cards'][0] is None:
                new_state['private_cards'][0] = card
            else:
                new_state['private_cards'][1] = card
                new_state['stage'] = 'betting'
                new_state['current_player'] = 0
        elif new_state['stage'] == 'deal_public':
            new_state['public_card'] = card
            new_state['stage'] = 'betting'
            new_state['round'] = 2
            new_state['raises_in_round'] = 0
            new_state['bets'] = [0, 0]
            new_state['current_player'] = 0
            
        return new_state

    # --- PLAYER ACTIONS ---
    player_id = current_player
    opponent_id = 1 - player_id
    
    if action == "Fold":
        new_state['folded'] = player_id
        new_state['current_player'] = -4
        return new_state
        
    current_bet = new_state['bets'][player_id]
    opponent_bet = new_state['bets'][opponent_id]
    
    if action == "Call":
        amount = opponent_bet - current_bet
        new_state['bets'][player_id] += amount
        new_state['stack'][player_id] += amount
        new_state['pot'] += amount
        
        bets_equal = (new_state['bets'][0] == new_state['bets'][1])
        # P1 calling the Big Blind in Round 1 gives P2 the "option" to raise
        is_preflop_option = (new_state['round'] == 1 and bets_equal and 
                             len([h for h in new_state['history'] if h[0] != -1]) == 1)
        # P1 Checking (Calling 0) in Round 2 gives P2 the chance to act
        is_postflop_open = (new_state['round'] == 2 and bets_equal and 
                            new_state['bets'] == [0, 0] and player_id == 0)

        if is_preflop_option or is_postflop_open:
            new_state['current_player'] = opponent_id
        elif bets_equal:
            if new_state['round'] == 1:
                new_state['stage'] = 'deal_public'
                new_state['current_player'] = -1
            else:
                new_state['stage'] = 'showdown'
                new_state['current_player'] = -4
        else:
            new_state['current_player'] = opponent_id

    elif action == "Raise":
        raise_amount = BET_SIZES[new_state['round']]
        cost = (opponent_bet + raise_amount) - current_bet
        new_state['bets'][player_id] += cost
        new_state['stack'][player_id] += cost
        new_state['pot'] += cost
        new_state['raises_in_round'] += 1
        new_state['current_player'] = opponent_id

    return new_state

def get_current_player(state: State) -> int:
    return state['current_player']

def get_player_name(player_id: int) -> str:
    if player_id == -1: return "Chance"
    if player_id == -4: return "Terminal"
    return f"Player {player_id + 1}"

def get_rewards(state: State) -> List[float]:
    if state['private_cards'][0] is None:
        return [0.0, 0.0]

    p1_stack, p2_stack = state['stack']
    if state['folded'] is not None:
        return [-float(p1_stack), float(p1_stack)] if state['folded'] == 0 else [float(p2_stack), -float(p2_stack)]

    ranks = {'J': 0, 'Q': 1, 'K': 2}
    def get_rank(priv, pub):
        return (1, ranks[priv]) if priv == pub else (0, max(ranks[priv], ranks[pub]))

    r1 = get_rank(state['private_cards'][0], state['public_card'])
    r2 = get_rank(state['private_cards'][1], state['public_card'])

    if r1 > r2: return [float(p2_stack), -float(p2_stack)]
    elif r2 > r1: return [-float(p1_stack), float(p1_stack)]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    cp = state['current_player']
    if cp == -4: return []
    if cp == -1: return sorted(list(set([f"deal:{c}" for c in state['deck']])))
    
    actions = ["Fold", "Call"]
    if state['raises_in_round'] < MAX_RAISES_PER_ROUND:
        actions.append("Raise")
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observation for player."""
    def build_obs(pid):
        # Construct Public History:
        # Include all Player actions.
        # Include Chance actions (-1) ONLY if they are the Public Card (count > 2).
        public_history = []
        chance_count = 0
        for p, a in state['history']:
            if p == -1:
                chance_count += 1
                # 1 and 2 are private deals. 3 is Public (Flop).
                if chance_count > 2: 
                    public_history.append((p, a))
            else:
                public_history.append((p, a))
                
        return {
            'round': state['round'],
            'bets': state['bets'],
            'pot': state['pot'],
            'public_card': state['public_card'],
            'private_card': state['private_cards'][pid],
            'history': public_history
        }
    return [build_obs(0), build_obs(1)]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    """
    Reconstructs a full action history consistent with the player's observations.
    Samples hidden information (opponent's private card) randomly.
    """
    if not obs_action_history:
        return []

    # Get the most recent observation
    last_obs, last_action = obs_action_history[-1]

    # Extract known information
    my_card = last_obs['private_card']
    public_card = last_obs.get('public_card')
    observed_history = last_obs.get('history', [])

    # Sample opponent's card from remaining deck
    # DECK = ['J', 'Q', 'K'] * 2, so there are 2 of each rank
    remaining_deck = DECK.copy()
    remaining_deck.remove(my_card)  # Remove my card
    if public_card:
        remaining_deck.remove(public_card)  # Remove public card if dealt

    opponent_card = random.choice(remaining_deck)

    # Build full history starting with private card deals
    full_history = []

    # Deal private cards (2 chance actions)
    if player_id == 0:
        full_history.append(f"deal:{my_card}")
        full_history.append(f"deal:{opponent_card}")
    else:
        full_history.append(f"deal:{opponent_card}")
        full_history.append(f"deal:{my_card}")

    # Add all observed actions (player actions and public card deal)
    for actor, action in observed_history:
        full_history.append(action)

    # Add the final action from this observation if present
    if last_action is not None:
        full_history.append(last_action)

    return full_history