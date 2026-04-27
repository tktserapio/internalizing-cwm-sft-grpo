import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter

def resample_history(obs_action_history: list[tuple[PlayerObservation, Action | None]], player_id: int) -> list[Action]:
    """Stochastically sample a valid sequence of actions (including 'chance' outcomes) that explains the current observations.
    CRITICAL: The returned list must be a complete trajectory that can be replayed starting EXACTLY from get_initial_state().
    """
    def sample_action(observation: PlayerObservation) -> Action:
        if observation['phase'] == 'Wall':
            return 'Deal:' + ''.join(str(card) for card in observation['deck'])
        if observation['phase'] == 'Knock':
            return 'Action:' + str(random.choice(observation['hand']))
        if observation['phase'] == 'Draw':
            return 'Draw stock' if random.random() < 0.5 else 'Draw upcard'
        if observation['phase'] == 'Layoff':
            return 'Knock' if random.random() < 0.5 else 'Pass'
        return 'Action:' + str(random.choice(observation['hand']))

    history = obs_action_history[::-1]
    actions = [sample_action(history.pop())]
    while history:
        observation, _ = history.pop()
        if observation['phase'] == 'Wall':
            actions.append('Deal:' + ''.join(str(card) for card in observation['deck']))
        else:
            actions.append(sample_action(observation))
    return actions