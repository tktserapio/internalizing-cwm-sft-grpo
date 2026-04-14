import random
from typing import Any, Dict, List, Optional, Tuple

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

# Game constants
NUM_CARDS = 13
NUM_PLAYERS = 2
CHANCE_PLAYER = -1
TERMINAL_PLAYER = -4


def get_initial_state() -> State:
    """Returns the initial state (chance node to deal first prize)."""
    return {
        "prize_deck": list(range(1, NUM_CARDS + 1)),  # Cards 1-13
        "hands": [list(range(1, NUM_CARDS + 1)) for _ in range(NUM_PLAYERS)],
        "points": [0, 0],
        "current_prize": None,
        "current_bids": [None, None],  # Bids for current round
        "round": 0,
        "current_player": CHANCE_PLAYER,  # Start with chance dealing prize
        "history": [],  # Full action history
        "round_history": []  # (prize, bid0, bid1) per completed round
    }


def get_current_player(state: State) -> int:
    """Returns current player: -1 for chance, 0/1 for players, -4 for terminal."""
    if state["round"] >= NUM_CARDS:
        return TERMINAL_PLAYER
    return state["current_player"]


def get_player_name(player_id: int) -> str:
    """Returns the name of the player."""
    names = {0: "Player 1", 1: "Player 2", CHANCE_PLAYER: "Chance", TERMINAL_PLAYER: "Terminal"}
    return names.get(player_id, "Unknown")


def get_legal_actions(state: State) -> List[Action]:
    """Returns legal actions for current player."""
    cp = get_current_player(state)

    if cp == TERMINAL_PLAYER:
        return []

    if cp == CHANCE_PLAYER:
        # Deal a prize card from remaining deck
        return [f"prize:{c}" for c in state["prize_deck"]]

    # Player's turn: bid a card from hand
    return [f"bid:{c}" for c in state["hands"][cp]]


def _resolve_round(state: State) -> State:
    """Resolve the current round after both players have bid."""
    prize = state["current_prize"]
    bid0, bid1 = state["current_bids"]

    new_points = state["points"][:]
    if bid0 > bid1:
        new_points[0] += prize
    elif bid1 > bid0:
        new_points[1] += prize
    # Tie: prize is discarded (no points awarded)

    new_round_history = state["round_history"] + [(prize, bid0, bid1)]

    return {
        "prize_deck": state["prize_deck"],
        "hands": state["hands"],
        "points": new_points,
        "current_prize": None,
        "current_bids": [None, None],
        "round": state["round"] + 1,
        "current_player": CHANCE_PLAYER if state["round"] + 1 < NUM_CARDS else TERMINAL_PLAYER,
        "history": state["history"],
        "round_history": new_round_history
    }


def apply_action(state: State, action: Action) -> State:
    """Apply action and return new state."""
    cp = get_current_player(state)

    if cp == TERMINAL_PLAYER:
        return state

    new_history = state["history"] + [action]

    if cp == CHANCE_PLAYER:
        # Deal prize card
        prize = int(action.split(":")[1])
        new_deck = [c for c in state["prize_deck"] if c != prize]

        return {
            "prize_deck": new_deck,
            "hands": [h[:] for h in state["hands"]],
            "points": state["points"][:],
            "current_prize": prize,
            "current_bids": [None, None],
            "round": state["round"],
            "current_player": 0,  # Player 0 bids first
            "history": new_history,
            "round_history": state["round_history"][:]
        }

    # Player bid
    bid = int(action.split(":")[1])
    new_hands = [h[:] for h in state["hands"]]
    new_hands[cp].remove(bid)

    new_bids = state["current_bids"][:]
    new_bids[cp] = bid

    # Create intermediate state
    new_state = {
        "prize_deck": state["prize_deck"][:],
        "hands": new_hands,
        "points": state["points"][:],
        "current_prize": state["current_prize"],
        "current_bids": new_bids,
        "round": state["round"],
        "current_player": 1 - cp if cp == 0 else CHANCE_PLAYER,
        "history": new_history,
        "round_history": state["round_history"][:]
    }

    # If both players have bid, resolve the round
    if new_bids[0] is not None and new_bids[1] is not None:
        return _resolve_round(new_state)

    return new_state


def get_rewards(state: State) -> List[float]:
    """Returns rewards based on point totals."""
    p0, p1 = state["points"]
    if p0 > p1:
        return [1.0, -1.0]
    elif p1 > p0:
        return [-1.0, 1.0]
    else:
        return [0.0, 0.0]


def get_observations(state: State) -> List[PlayerObservation]:
    """Returns observations for each player.

    Players see:
    - Their own hand
    - Their own bids
    - Current prize card
    - Completed round history (prize, winner, but not opponent's exact bid)
    - Their own points
    """
    observations = []

    for pid in range(NUM_PLAYERS):
        # What rounds have completed and what was revealed
        public_history = []
        for prize, bid0, bid1 in state["round_history"]:
            # After round ends, players see who won but maybe not exact bids
            # In standard Goofspiel, bids are revealed after each round
            public_history.append({
                "prize": prize,
                "my_bid": bid0 if pid == 0 else bid1,
                "opp_bid": bid1 if pid == 0 else bid0
            })

        obs = {
            "hand": state["hands"][pid][:],
            "my_points": state["points"][pid],
            "opp_points": state["points"][1 - pid],
            "current_prize": state["current_prize"],
            "my_current_bid": state["current_bids"][pid],
            "round_history": public_history,
            "round": state["round"]
        }
        observations.append(obs)

    return observations


def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]],
                     player_id: int,
                     last_is_terminal: bool = False) -> List[Action]:
    """Reconstruct a plausible action history consistent with player's observations.

    For Goofspiel, the hidden information is:
    - Which prize cards were dealt (before being revealed)
    - Opponent's bids (until round ends)
    """
    if not obs_action_history:
        return []

    # Get the most recent observation
    last_obs, last_action = obs_action_history[-1]

    # Reconstruct history from observation
    history = []

    # Prize cards that have been seen (from round history)
    round_history = last_obs.get("round_history", [])
    current_prize = last_obs.get("current_prize")

    # Figure out what prizes were dealt
    prizes_seen = [r["prize"] for r in round_history]
    if current_prize is not None:
        prizes_seen.append(current_prize)

    # For completed rounds, we know both bids (revealed after round)
    for r in round_history:
        prize = r["prize"]
        my_bid = r["my_bid"]
        opp_bid = r["opp_bid"]

        history.append(f"prize:{prize}")
        if player_id == 0:
            history.append(f"bid:{my_bid}")
            history.append(f"bid:{opp_bid}")
        else:
            history.append(f"bid:{opp_bid}")
            history.append(f"bid:{my_bid}")

    # Current round (if in progress)
    if current_prize is not None:
        history.append(f"prize:{current_prize}")

        my_bid = last_obs.get("my_current_bid")

        # Reconstruct based on who has bid
        if player_id == 0:
            # P0 bids first - add our bid if we've already bid
            if my_bid is not None:
                history.append(f"bid:{my_bid}")
        else:
            # Player 1: player 0 must have bid first
            # We need to sample player 0's bid (hidden from us)
            opp_hand_start = list(range(1, NUM_CARDS + 1))
            for r in round_history:
                opp_hand_start.remove(r["opp_bid"])
            if opp_hand_start:
                sampled_opp_bid = random.choice(opp_hand_start)
                history.append(f"bid:{sampled_opp_bid}")

            if my_bid is not None:
                history.append(f"bid:{my_bid}")

    # Add final action if provided and not already added
    # We track whether we've added the player's action for the current round
    # to avoid the bug where sampled opponent bid == player's bid
    if last_action is not None:
        # Count how many of the player's bids are in the history
        player_bids_in_history = len(round_history)  # completed rounds
        if current_prize is not None:
            my_bid = last_obs.get("my_current_bid")
            if my_bid is not None:
                player_bids_in_history += 1

        # obs_action_history has one entry per player turn, so we know how many bids we need
        expected_player_bids = len(obs_action_history)

        # If we're missing the player's final bid, add it
        if player_bids_in_history < expected_player_bids:
            history.append(last_action)

    return history
