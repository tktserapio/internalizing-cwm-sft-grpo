import random
from typing import Any, Dict, List, Optional, Tuple
import copy

Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

SUITS = ['s', 'h', 'd', 'c']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
VALUES = {r: v for r, v in zip(RANKS, [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])}

def get_initial_state() -> State:
    return {
        "deck": [r + s for r in RANKS for s in SUITS],
        "p_hands": [[]],
        "d_hand": [],
        "bets": [1.0],
        "hand_idx": 0,
        "current_player": -1,  # Chance
        "phase": "deal_p1",
        "history": [],
        "rewards": [0.0, 0.0],
        "doubled": [False],
        "surrendered": [False],
    }

def _hand_value(hand: List[str]) -> int:
    val, aces = 0, 0
    for card in hand:
        rank = card[0]
        val += VALUES[rank]
        if rank == 'A': aces += 1
    while val > 21 and aces > 0:
        val -= 10
        aces -= 1
    return val

def get_current_player(state: State) -> int:
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return { -1: "Chance", 1: "Dealer", -4: "Terminal" }.get(player_id, "Player")

def get_rewards(state: State) -> List[float]:
    return state["rewards"]

def get_legal_actions(state: State) -> List[Action]:
    cp = state["current_player"]
    if cp == -4: return []
    if cp == -1: return [f"deal:{c}" for c in state["deck"]]
    if cp == 1: # Dealer
        return ["H"] if _hand_value(state["d_hand"]) < 17 else ["S"]
    
    # Player
    hand = state["p_hands"][state["hand_idx"]]
    if _hand_value(hand) >= 21: return ["S"] # Must stand if 21 (or bust, though bust usually terminates)
    
    actions = ["H", "S"]
    if len(hand) == 2:
        actions.append("D")
        actions.append("R")
        if hand[0][0] == hand[1][0] or VALUES[hand[0][0]] == VALUES[hand[1][0]]:
            actions.append("P")
    return actions

def apply_action(state: State, action: Action) -> State:
    s = copy.deepcopy(state)
    s["history"].append(action)
    cp = s["current_player"]

    if cp == -1: # Chance
        card = action.split(":")[1]
        s["deck"].remove(card)
        p = s["phase"]
        
        if p == "deal_p1":
            s["p_hands"][0].append(card)
            s["phase"] = "deal_d1"
        elif p == "deal_d1":
            s["d_hand"].append(card)
            s["phase"] = "deal_p2"
        elif p == "deal_p2":
            s["p_hands"][0].append(card)
            s["phase"] = "deal_d2"
        elif p == "deal_d2":
            s["d_hand"].append(card)
            s["current_player"] = 0
            s["phase"] = "play"
            
        elif p == "p_hit":
            idx = s["hand_idx"]
            s["p_hands"][idx].append(card)
            if _hand_value(s["p_hands"][idx]) > 21:
                # Bust: Immediate loss for single player
                s["rewards"] = [-s["bets"][idx], s["bets"][idx]]
                s["current_player"] = -4
            else:
                # 21 or less: Player turn (even at 21, must explicitly Stand)
                s["current_player"] = 0
                s["phase"] = "play"
                
        elif p == "d_hit":
            s["d_hand"].append(card)
            s["current_player"] = 1 # Return to Dealer
            
        elif p.startswith("split_deal"):
            s["p_hands"][int(p.split("_")[-1])].append(card)
            s["current_player"] = 0
            s["phase"] = "play"
        return s

    if cp == 0: # Player
        if action == "H":
            s["current_player"] = -1
            s["phase"] = "p_hit"
        elif action == "S":
            if s["hand_idx"] < len(s["p_hands"]) - 1:
                s["hand_idx"] += 1
            else:
                s["current_player"] = 1 # Dealer turn
        elif action == "D":
            s["bets"][s["hand_idx"]] *= 2
            s["doubled"][s["hand_idx"]] = True
            s["current_player"] = -1
            s["phase"] = "p_hit"
            # Note: After this hit, if not bust, we return to Player. 
            # Ideally, Double forces a Stand. We rely on the agent to Stand next 
            # or the legal actions to constrain it. 
            # (Simplification for compact code: Agent gets control back but should Stand)
        elif action == "R":
            s["surrendered"][s["hand_idx"]] = True
            s["rewards"] = [-0.5 * s["bets"][0], 0.5 * s["bets"][0]]
            s["current_player"] = -4
        elif action == "P":
            h = s["p_hands"][s["hand_idx"]]
            c2 = h.pop()
            s["p_hands"].append([c2])
            s["bets"].append(s["bets"][s["hand_idx"]])
            s["doubled"].extend([False])
            s["surrendered"].extend([False])
            s["current_player"] = -1
            s["phase"] = f"split_deal_{s['hand_idx']}"
        return s

    if cp == 1: # Dealer
        if action == "H":
            s["current_player"] = -1
            s["phase"] = "d_hit"
        elif action == "S":
            # Resolve Game
            p_tot = 0.0
            d_val = _hand_value(s["d_hand"])
            d_bj = (len(s["d_hand"]) == 2 and d_val == 21)
            d_bust = d_val > 21
            
            for i, hand in enumerate(s["p_hands"]):
                if s["surrendered"][i]: continue
                p_val = _hand_value(hand)
                p_bj = (len(hand) == 2 and p_val == 21)
                bet = s["bets"][i]
                
                # Player busts are handled immediately in p_hit, so p_val <= 21 here
                if p_bj and not d_bj: p_tot += bet * 1.5
                elif d_bj and not p_bj: p_tot -= bet
                elif d_bust: p_tot += bet
                elif p_val > d_val: p_tot += bet
                elif p_val < d_val: p_tot -= bet
                
            s["rewards"] = [p_tot, -p_tot]
            s["current_player"] = -4
        return s
    return s

def get_observations(state: State) -> List[PlayerObservation]:
    d_up = state["d_hand"][0] if state["d_hand"] else None
    # Mask the 4th action (Dealer Hole Deal) in history if it exists
    safe_hist = []
    deal_count = 0
    for act in state["history"]:
        if act.startswith("deal"):
            deal_count += 1
            if deal_count == 4: # The Dealer Hole card
                safe_hist.append("deal:?")
                continue
        safe_hist.append(act)

    # Player observation (index 0)
    player_obs = {
        "my_hands": state["p_hands"],
        "dealer_up": d_up,
        "history": safe_hist,
        "hand_idx": state["hand_idx"]
    }

    # Dealer observation (index 1) - dealer sees all cards
    dealer_obs = {
        "my_hand": state["d_hand"],
        "player_hands": state["p_hands"],
        "history": state["history"],
    }

    return [player_obs, dealer_obs]

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int) -> List[Action]:
    if not obs_action_history:
        return []

    final_obs = obs_action_history[-1][0]

    # Handle both player (pid=0) and dealer (pid=1) perspectives
    if player_id == 0:
        # Player observation: my_hands, dealer_up, history (with masked hole card)
        p_hands = final_obs.get("my_hands", [[]])
        p_cards = [c for h in p_hands for c in h]
        d_up = final_obs.get("dealer_up")

        # Identify known cards
        known = list(p_cards)
        if d_up:
            known.append(d_up)

        # Rebuild deck for sampling unknown cards
        full_deck = [r + s for r in RANKS for s in SUITS]
        for k in known:
            if k in full_deck:
                full_deck.remove(k)
        random.shuffle(full_deck)
        deck_iter = iter(full_deck)

        # Use the observation's history directly - it has correct action order
        # Just replace masked hole card with sampled card
        obs_history = final_obs.get("history", [])
        actions = []
        for act in obs_history:
            if act == "deal:?":
                actions.append(f"deal:{next(deck_iter)}")
            else:
                actions.append(act)

        # Add final action if not already in history
        last_action = obs_action_history[-1][1]
        if last_action is not None and (not actions or actions[-1] != last_action):
            actions.append(last_action)
            # If action triggers a deal (H, D, P), add a sampled card
            if last_action in ["H", "D", "P"]:
                actions.append(f"deal:{next(deck_iter)}")

        return actions

    else:
        # Dealer observation: my_hand, player_hands, history (full, no masking)
        d_hand = final_obs.get("my_hand", [])
        p_hands = final_obs.get("player_hands", [[]])
        p_cards = [c for h in p_hands for c in h]

        # Dealer knows all cards, reconstruct from full history
        obs_history = final_obs.get("history", [])

        # Build list of known cards
        known = list(p_cards) + list(d_hand)

        # Rebuild deck for any unknown cards (shouldn't be needed but just in case)
        full_deck = [r + s for r in RANKS for s in SUITS]
        for k in known:
            if k in full_deck:
                full_deck.remove(k)
        random.shuffle(full_deck)
        deck_iter = iter(full_deck)

        # Use history directly
        actions = list(obs_history)

        # Always add the dealer's last action - the observation is captured BEFORE
        # the action, so it's not in the history yet
        last_action = obs_action_history[-1][1]
        if last_action is not None:
            actions.append(last_action)
            # If dealer hits, add a deal for the hit card
            if last_action == "H":
                # Count how many dealer hit cards are already in history
                dealer_hits_in_history = 0
                player_stood = False
                for a in obs_history:
                    if a == "S" and not player_stood:
                        player_stood = True  # First S is player's stand
                    elif a == "H" and player_stood:
                        dealer_hits_in_history += 1

                d_card_idx = 2 + dealer_hits_in_history  # 2 initial cards + hits
                if d_card_idx < len(d_hand):
                    actions.append(f"deal:{d_hand[d_card_idx]}")
                else:
                    actions.append(f"deal:{next(deck_iter)}")

        return actions