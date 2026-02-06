import copy
import random
from typing import Any, List, Tuple, Dict

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Constants
COLORS = ['R', 'Y', 'G', 'B', 'W']
RANKS = [1, 2, 3, 4, 5]
DECK_COMPOSITION = {
    1: 3,
    2: 2,
    3: 2,
    4: 2,
    5: 1
}
MAX_CLUES = 8
MAX_LIVES = 3
HAND_SIZE = 5

def _create_deck() -> List[Tuple[str, int]]:
    """Create and shuffle the initial deck."""
    deck = []
    for color in COLORS:
        for rank, count in DECK_COMPOSITION.items():
            deck.extend([(color, rank)] * count)
    random.shuffle(deck)
    return deck

def _deal_cards(deck: List[Tuple[str, int]], count: int) -> Tuple[List[Tuple[str, int]], List[Tuple[str, int]]]:
    """Deal 'count' cards from the deck."""
    dealt = deck[:count]
    remaining = deck[count:]
    return dealt, remaining

def get_initial_state() -> State:
    """Returns the initial game state before any actions are taken."""
    deck = _create_deck()
    p0_hand, deck = _deal_cards(deck, HAND_SIZE)
    p1_hand, deck = _deal_cards(deck, HAND_SIZE)
    
    return {
        'deck': deck,
        'p0_hand': p0_hand,
        'p1_hand': p1_hand,
        'board': {color: 0 for color in COLORS},
        'discard': [],
        'clues': MAX_CLUES,
        'lives': MAX_LIVES,
        'current_player': -1,  # Start with chance to deal
        'turn': 0,
        'game_over': False,
        'final_round': False,
        'final_round_turns': 0
    }

def _is_game_over(state: State) -> bool:
    """Check if the game is over."""
    if state['lives'] < 0:
        return True
    if all(state['board'][c] == 5 for c in COLORS):
        return True
    if state['final_round'] and state['final_round_turns'] >= 2:
        return True
    return False

def _calculate_score(state: State) -> int:
    """Calculate the current score."""
    if state['lives'] < 0:
        return 0
    return sum(state['board'].values())

def apply_action(state: State, action: Action) -> State:
    """Returns the new state after an action has been taken."""
    new_state = copy.deepcopy(state)
    
    if new_state['game_over']:
        return new_state
    
    # Handle chance actions (initial dealing)
    if new_state['current_player'] == -1:
        if action.startswith("deal:"):
            # This is handled during initial setup, no action needed here
            new_state['current_player'] = 0
        return new_state
    
    # Handle player actions
    parts = action.split()
    
    if parts[0] == "Play":
        card_idx = int(parts[1])
        player = new_state['current_player']
        hand_key = f'p{player}_hand'
        hand = new_state[hand_key]
        
        if card_idx >= len(hand):
            return new_state
            
        card = hand[card_idx]
        color, rank = card
        
        # Check if play is valid
        if new_state['board'][color] == rank - 1:
            new_state['board'][color] = rank
            reward = 1 if rank == 5 else 0
        else:
            new_state['lives'] -= 1
            reward = -1
            new_state['discard'].append(card)
        
        # Draw new card
        if new_state['deck']:
            new_card = new_state['deck'].pop(0)
            hand.pop(card_idx)
            hand.append(new_card)
        else:
            hand.pop(card_idx)
            if not new_state['final_round']:
                new_state['final_round'] = True
                new_state['final_round_turns'] = 0
    
    elif parts[0] == "Discard":
        card_idx = int(parts[1])
        player = new_state['current_player']
        hand_key = f'p{player}_hand'
        hand = new_state[hand_key]
        
        if card_idx >= len(hand):
            return new_state
            
        card = hand[card_idx]
        new_state['discard'].append(card)
        new_state['clues'] = min(MAX_CLUES, new_state['clues'] + 1)
        
        # Draw new card
        if new_state['deck']:
            new_card = new_state['deck'].pop(0)
            hand.pop(card_idx)
            hand.append(new_card)
        else:
            hand.pop(card_idx)
            if not new_state['final_round']:
                new_state['final_round'] = True
                new_state['final_round_turns'] = 0
    
    elif parts[0] == "Reveal":
        if new_state['clues'] <= 0:
            return new_state
            
        new_state['clues'] -= 1
        # No actual state change for hints, just token consumption
    
    # Update turn
    if new_state['current_player'] == 0:
        new_state['current_player'] = 1
    else:
        new_state['current_player'] = 0
        new_state['turn'] += 1
        if new_state['final_round']:
            new_state['final_round_turns'] += 1
    
    # Check game over
    if _is_game_over(new_state):
        new_state['game_over'] = True
        new_state['current_player'] = -4
    
    return new_state

def get_current_player(state: State) -> int:
    """Returns current player, with -1 for chance and -4 for terminal."""
    if state['game_over']:
        return -4
    return state['current_player']

def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    if player_id == -1:
        return "Chance"
    elif player_id == -4:
        return "Terminal"
    return f"Player {player_id}"

def get_rewards(state: State) -> List[float]:
    """Returns the rewards per player from their last action."""
    if state['game_over']:
        score = _calculate_score(state)
        return [score, score]
    return [0.0, 0.0]

def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions that can be taken in current state."""
    if state['game_over']:
        return []
    
    if state['current_player'] == -1:
        # Chance node - no actions needed after initial deal
        return []
    
    actions = []
    player = state['current_player']
    
    # Play actions
    for i in range(len(state[f'p{player}_hand'])):
        actions.append(f"Play {i}")
    
    # Discard actions
    if state['clues'] < MAX_CLUES:
        for i in range(len(state[f'p{player}_hand'])):
            actions.append(f"Discard {i}")
    
    # Reveal actions
    if state['clues'] > 0:
        other_player = 1 - player
        other_hand = state[f'p{other_player}_hand']
        
        # Color hints
        for color in COLORS:
            if any(card[0] == color for card in other_hand):
                actions.append(f"Reveal color {other_player} {color}")
        
        # Rank hints
        for rank in RANKS:
            if any(card[1] == rank for card in other_hand):
                actions.append(f"Reveal rank {other_player} {rank}")
    
    return actions

def get_observations(state: State) -> List[PlayerObservation]:
    """Returns the observation for player."""
    obs = []
    
    for player in [0, 1]:
        other_player = 1 - player
        
        # Player sees their partner's hand but not their own
        observation = {
            'board': copy.deepcopy(state['board']),
            'discard': copy.deepcopy(state['discard']),
            'clues': state['clues'],
            'lives': state['lives'],
            'partner_hand': copy.deepcopy(state[f'p{other_player}_hand']),
            'deck_size': len(state['deck']),
            'game_over': state['game_over'],
            'current_player': state['current_player']
        }
        
        # Player doesn't see their own hand
        observation['my_hand'] = [None] * len(state[f'p{player}_hand'])
        
        obs.append(observation)
    
    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Action | None]], player_id: int) -> List[Action]:
    """
    Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    """
    # For Hanabi, this is complex due to hidden information. We'll return a simple valid sequence.
    # In practice, this would need sophisticated inference about hidden cards.
    
    # Start from initial state
    state = get_initial_state()
    actions = []
    
    # Initial dealing is handled in get_initial_state, no chance actions needed
    
    # Replay the observed actions
    for obs, action in obs_action_history:
        if action is not None:
            actions.append(action)
            state = apply_action(state, action)
    
    return actions
