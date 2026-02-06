import random
import itertools
from typing import Any, Dict, List, Optional, Tuple

# --- Type Definitions & Constants ---
Action = str
State = Dict[str, Any]
PlayerObservation = Dict[str, Any]

SUITS = ['s', 'c', 'd', 'h']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
RANK_VALUES = {r: min(i + 1, 10) for i, r in enumerate(RANKS)}
RANK_INDICES = {r: i for i, r in enumerate(RANKS)}

# --- Helper Functions ---
def get_deck() -> List[str]:
    return [r + s for s in SUITS for r in RANKS]

def get_card_value(card: str) -> int:
    return RANK_VALUES[card[:-1]]

def get_deadwood_value(hand: List[str]) -> int:
    if not hand: return 0
    hand_tuple = tuple(sorted(hand, key=lambda c: (SUITS.index(c[-1]), RANK_INDICES[c[:-1]])))
    
    memo = {}
    def solve(curr_hand):
        if curr_hand in memo: return memo[curr_hand]
        res = sum(get_card_value(c) for c in curr_hand)
        
        ranks = {}
        for c in curr_hand: ranks.setdefault(c[:-1], []).append(c)
        for r, cards in ranks.items():
            if len(cards) >= 3:
                for k in range(3, len(cards) + 1):
                    for combo in itertools.combinations(cards, k):
                        rem = list(curr_hand)
                        for x in combo: rem.remove(x)
                        res = min(res, solve(tuple(rem)))
                        
        suits = {}
        for c in curr_hand: suits.setdefault(c[-1], []).append(c)
        for s, cards in suits.items():
            cards.sort(key=lambda x: RANK_INDICES[x[:-1]])
            if len(cards) >= 3:
                for i in range(len(cards)):
                    for j in range(i + 3, len(cards) + 1):
                        sub = cards[i:j]
                        idxs = [RANK_INDICES[x[:-1]] for x in sub]
                        if all(idxs[z] + 1 == idxs[z+1] for z in range(len(idxs)-1)):
                            rem = list(curr_hand)
                            for x in sub: rem.remove(x)
                            res = min(res, solve(tuple(rem)))
        
        memo[curr_hand] = res
        return res
    return solve(hand_tuple)

def get_valid_melds(hand: List[str]) -> List[List[str]]:
    melds = []
    ranks = {}
    for c in hand: ranks.setdefault(c[:-1], []).append(c)
    for r in ranks:
        if len(ranks[r]) >= 3:
            for n in range(3, len(ranks[r]) + 1):
                for combo in itertools.combinations(ranks[r], n):
                    melds.append(list(combo))
    suits = {}
    for c in hand: suits.setdefault(c[-1], []).append(c)
    for s in suits:
        cards = sorted(suits[s], key=lambda c: RANK_INDICES[c[:-1]])
        if len(cards) >= 3:
            for i in range(len(cards)):
                for j in range(i + 3, len(cards) + 1):
                    sub = cards[i:j]
                    idxs = [RANK_INDICES[x[:-1]] for x in sub]
                    if all(idxs[k] + 1 == idxs[k+1] for k in range(len(idxs)-1)):
                        melds.append(sub)
    return melds

# --- Main API Functions ---

def get_initial_state() -> State:
    return {
        "deck": [],
        "hands": [[], []],
        "discard_pile": [],
        "current_player": -1, # Chance
        "phase": "init", 
        "turn_history": [],
        "scores": [0.0, 0.0],
        "dealer": 0,
        "knocker": None,
        "knock_melds": [],
        "gin": False,
        "game_over": False
    }

def get_current_player(state: State) -> int:
    if state["game_over"]: return -4
    return state["current_player"]

def get_player_name(player_id: int) -> str:
    return "Chance" if player_id == -1 else f"Player {player_id}"

def get_legal_actions(state: State) -> List[Action]:
    if state["game_over"]: return []
    cp = state["current_player"]
    phase = state["phase"]
    
    if cp == -1: return ["deal_random"]

    hand = state["hands"][cp]

    if phase == "first_turn":
        if len(state["turn_history"]) <= 1: 
            return ["Draw upcard", "Pass"]
        return []

    if phase == "draw":
        return ["Draw upcard", "Draw stock"]

    if phase == "discard":
        actions = [f"Action: {c}" for c in hand]
        if get_deadwood_value(hand) <= 10:
            actions.append("Action: Knock")
        return actions

    if phase == "knock":
        poss = get_valid_melds(hand)
        actions = ["Action: Done"]
        for m in poss:
            m_str = "".join(sorted(m, key=lambda c: (SUITS.index(c[-1]), RANK_INDICES[c[:-1]])))
            actions.append(f"Action: {m_str}")
        return list(set(actions))

    if phase == "layoff":
        actions = ["Action: Done"]
        for card in hand:
            actions.append(f"Action: {card}") 
        return actions

    if phase == "wall":
        return ["Action: Pass"]

    return []

def apply_action(state: State, action: Action) -> State:
    ns = {k: (v[:] if isinstance(v, list) else v) for k, v in state.items()}
    ns["hands"] = [h[:] for h in state["hands"]]
    
    cp = state["current_player"]
    phase = state["phase"]

    if cp == -1:
        deck = []
        if action.startswith("deal:"):
            deck = action.split(":")[1].split(",")
        else:
            deck = get_deck()
            random.shuffle(deck)
        
        ns["hands"][0] = deck[0:10]
        ns["hands"][1] = deck[10:20]
        ns["discard_pile"] = [deck[20]]
        ns["deck"] = deck[21:]
        ns["dealer"] = 0
        ns["current_player"] = 1 
        ns["phase"] = "first_turn"
        ns["turn_history"] = []
        return ns

    if phase == "wall":
        if action == "Action: Pass":
            ns["game_over"] = True
        return ns

    def check_wall(s):
        if len(s["deck"]) < 2:
            s["phase"] = "wall"
            s["current_player"] = 0 
            return True
        return False

    if phase == "first_turn":
        if action == "Draw upcard":
            card = ns["discard_pile"].pop()
            ns["hands"][cp].append(card)
            ns["phase"] = "discard"
        elif action == "Pass":
            ns["turn_history"].append("Pass")
            if len(ns["turn_history"]) == 1:
                ns["current_player"] = 1 - cp 
            else:
                ns["current_player"] = 1 
                card = ns["deck"].pop(0)
                ns["hands"][ns["current_player"]].append(card)
                ns["phase"] = "discard"
        return ns

    if phase == "draw":
        if action == "Draw upcard":
            ns["hands"][cp].append(ns["discard_pile"].pop())
        elif action == "Draw stock":
            if ns["deck"]:
                ns["hands"][cp].append(ns["deck"].pop(0))
        ns["phase"] = "discard"
        check_wall(ns)
        return ns

    if phase == "discard":
        if action == "Action: Knock":
            ns["phase"] = "knock"
            ns["knocker"] = cp
            if get_deadwood_value(ns["hands"][cp]) == 0: ns["gin"] = True
            return ns
        
        card = action.replace("Action: ", "")
        if card in ns["hands"][cp]:
            ns["hands"][cp].remove(card)
            ns["discard_pile"].append(card)
            if check_wall(ns): return ns
            ns["current_player"] = 1 - cp
            ns["phase"] = "draw"
        return ns

    if phase == "knock":
        if action == "Action: Done":
            ns["current_player"] = 1 - state["knocker"]
            if ns["gin"]: calculate_score(ns)
            else: ns["phase"] = "layoff"
        else:
            meld_str = action.replace("Action: ", "")
            cards = [meld_str[i:i+2] for i in range(0, len(meld_str), 2)]
            ns["knock_melds"].append(cards)
            for c in cards:
                if c in ns["hands"][cp]: ns["hands"][cp].remove(c)
        return ns

    if phase == "layoff":
        if action == "Action: Done":
            calculate_score(ns)
        else:
            card = action.replace("Action: ", "")
            if card in ns["hands"][cp]: ns["hands"][cp].remove(card)
        return ns

    return ns

def calculate_score(state: State):
    k, o = state["knocker"], 1 - state["knocker"]
    dw_k = sum(get_card_value(c) for c in state["hands"][k])
    dw_o = get_deadwood_value(state["hands"][o])
    
    if state["gin"]:
        state["scores"][k] = 25.0 + dw_o
    elif dw_k < dw_o:
        state["scores"][k] = float(dw_o - dw_k)
    else:
        state["scores"][o] = 25.0 + (dw_k - dw_o)
    state["game_over"] = True

def get_rewards(state: State) -> List[float]:
    return state["scores"] if state["game_over"] else [0.0, 0.0]

def get_observations(state: State) -> List[PlayerObservation]:
    if state["current_player"] == -1: return [{}, {}]
    obs = []
    for pid in range(2):
        obs.append({
            "hand": sorted(state["hands"][pid]),
            "discard_top": state["discard_pile"][-1] if state["discard_pile"] else None,
            "knock_melds": state["knock_melds"],
            "phase": state["phase"],
            "legal_actions": get_legal_actions(state) if state["current_player"] == pid else []
        })
    return obs

def resample_history(obs_action_history: List[Tuple[PlayerObservation, Optional[Action]]], player_id: int, last_is_terminal: bool = False) -> List[Action]:
    if not obs_action_history: return ["deal_random"]

    first_obs = obs_action_history[0][0]
    initial_hand = set(first_obs.get("hand", []))
    initial_discard = first_obs.get("discard_top")
    
    known_player_stock_draws = [] 
    opponent_discards = [] 
    
    for i in range(len(obs_action_history) - 1):
        curr_obs, action = obs_action_history[i]
        next_obs, _ = obs_action_history[i+1]
        
        if action == "Draw stock":
            new_cards = set(next_obs.get("hand", [])) - set(curr_obs.get("hand", []))
            if new_cards:
                card = list(new_cards)[0]
                known_player_stock_draws.append(card)
                if card in initial_hand: initial_hand.remove(card) 

        my_discard = None
        if action and action.startswith("Action: ") and action not in ["Action: Knock", "Action: Done"]:
             my_discard = action.replace("Action: ", "")
             
        pile_after_me = curr_obs.get("discard_top")
        if my_discard: pile_after_me = my_discard
        
        next_disc_top = next_obs.get("discard_top")
        if next_disc_top and next_disc_top != pile_after_me:
             opponent_discards.append(next_disc_top)

    full_deck = set(get_deck())
    used_cards = set(initial_hand)
    if initial_discard: used_cards.add(initial_discard)
    for c in known_player_stock_draws: used_cards.add(c)
    for c in opponent_discards: used_cards.add(c)
    
    unknowns = list(full_deck - used_cards)
    random.shuffle(unknowns)
    
    p_cards = list(initial_hand)
    while len(p_cards) < 10: p_cards.append(unknowns.pop())
    
    o_cards = list(opponent_discards) 
    while len(o_cards) < 10: o_cards.append(unknowns.pop())
    
    temp_stock = ["?"] * 31 
    stock_cursor = 0
    sim_p = 1 
    phase_sim = "first_turn"
    
    sim_p_draws = list(known_player_stock_draws)
    obs_idx = 0
    
    # Simulation to assign stock slots
    for _ in range(100): 
        if obs_idx >= len(obs_action_history): break
        is_me = (sim_p == player_id)
        
        if is_me:
            _, act = obs_action_history[obs_idx]
            obs_idx += 1
            
            if act == "Draw stock":
                if stock_cursor < 31:
                    if sim_p_draws:
                        temp_stock[stock_cursor] = sim_p_draws.pop(0)
                    stock_cursor += 1
                phase_sim = "discard"
            elif act == "Draw upcard":
                phase_sim = "discard"
            elif act == "Pass":
                # If first pass, stay in first_turn. If second, force draw happens logic implies valid draw.
                # Keep simplified phase tracking
                pass 
            elif act.startswith("Action: ") and act != "Action: Knock":
                 phase_sim = "draw" # After discard, back to draw
            
            sim_p = 1 - sim_p
        else:
            # Opponent Logic
            if phase_sim == "first_turn":
                # Opp cannot draw stock in first turn
                pass # Assume pass or upcard draw
            else:
                # Assume stock draw for standard play
                if stock_cursor < 31:
                    stock_cursor += 1
                phase_sim = "discard"
            sim_p = 1 - sim_p

    final_stock = []
    for x in temp_stock:
        if x == "?":
            final_stock.append(unknowns.pop() if unknowns else "Ah")
        elif x is not None:
             final_stock.append(x)
    final_stock = [x for x in final_stock if isinstance(x, str)]

    deck_ordered = []
    if player_id == 0:
        deck_ordered.extend(p_cards)
        deck_ordered.extend(o_cards)
    else:
        deck_ordered.extend(o_cards)
        deck_ordered.extend(p_cards)
        
    if initial_discard: deck_ordered.append(initial_discard)
    else: deck_ordered.append(unknowns.pop() if unknowns else "Ah")
    
    deck_ordered.extend(final_stock)
    
    actions = [f"deal:{','.join(deck_ordered)}"]
    sim_state = apply_action(get_initial_state(), actions[0])
    my_hist_iter = iter(obs_action_history)
    
    while not sim_state["game_over"]:
        cp = sim_state["current_player"]
        
        if cp == player_id:
            try:
                obs, act = next(my_hist_iter)
                actions.append(act)
                sim_state = apply_action(sim_state, act)
            except StopIteration:
                break
        else:
            if sim_state["phase"] == "first_turn":
                op_act = "Pass"
                actions.append(op_act)
                sim_state = apply_action(sim_state, op_act)
            elif sim_state["phase"] == "wall":
                op_act = "Action: Pass"
                actions.append(op_act)
                sim_state = apply_action(sim_state, op_act)
            else:
                if not sim_state["deck"]:
                    actions.append("Action: Pass") 
                    sim_state = apply_action(sim_state, "Action: Pass")
                    continue

                op_act_1 = "Draw stock"
                actions.append(op_act_1)
                sim_state = apply_action(sim_state, op_act_1)
                
                if opponent_discards:
                    disc = opponent_discards.pop(0)
                    if disc not in sim_state["hands"][cp]:
                        sim_state["hands"][cp].append(disc) 
                    op_act_2 = f"Action: {disc}"
                else:
                    c = sim_state["hands"][cp][0]
                    op_act_2 = f"Action: {c}"
                
                actions.append(op_act_2)
                sim_state = apply_action(sim_state, op_act_2)
            
    return actions