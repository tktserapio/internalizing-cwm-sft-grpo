import argparse
import importlib.util
import os
import sys
import random
import copy
import json
import inspect
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import IMPERFECT_INFO_GAMES


def load_module(path):
    try:
        # First check syntax by compiling
        with open(path) as f:
            source = f.read()
        compile(source, path, 'exec')

        spec = importlib.util.spec_from_file_location("candidate", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, None
    except SyntaxError as e:
        return None, f"SyntaxError at line {e.lineno}: {e.msg}"
    except Exception as e:
        return None, str(e)


def safe_call(func, *args):
    try:
        return func(*args), None
    except Exception as e:
        return None, str(e)


class TierResult:
    def __init__(self, name):
        self.name = name
        self.results = []

    def add(self, name, passed, msg=""):
        self.results.append({
            "name": name,
            "passed": passed,
            "message": msg,
        })

    @property
    def passed(self):
        return sum(1 for r in self.results if r["passed"])

    @property
    def total(self):
        return len(self.results)

    @property
    def score(self):
        if not self.results:
            return 1.0
        return self.passed / self.total


class EvaluationResult:
    def __init__(self, game, path):
        self.game = game
        self.candidate_path = path
        self.tiers = {}

    @property
    def overall_score(self):
        if not self.tiers:
            return 0.0
        scores = []
        for name, t in self.tiers.items():
            if not t.results:
                continue
            # Skip information tier for perfect-info games
            if name == "information" and self.game not in IMPERFECT_INFO_GAMES:
                continue
            scores.append(t.score)
        return sum(scores) / len(scores) if scores else 0.0


# tier 1
def test_static(module, path):
    tier = TierResult("1. Static")
    tier.add("syntax", True, "compiles")

    required = ['get_initial_state', 'apply_action', 'get_current_player',
                'get_legal_actions', 'get_rewards', 'get_observations']
    missing = [f for f in required if not hasattr(module, f)]
    tier.add("api_complete", len(missing) == 0,
             f"missing: {missing}" if missing else "ok")

    if missing:
        tier.add("initial_state_type", False, "api incomplete")
        tier.add("actions_type", False, "api incomplete")
        tier.add("rewards_type", False, "api incomplete")
        tier.add("observations_type", False, "api incomplete")
        tier.add("player_type", False, "api incomplete")
        return tier

    state, err = safe_call(module.get_initial_state)
    tier.add("initial_state_type", err is None and isinstance(state, dict),
             err or ("dict" if isinstance(state, dict) else type(state).__name__))

    if state is None:
        tier.add("actions_type", False, "no state")
        tier.add("rewards_type", False, "no state")
        tier.add("observations_type", False, "no state")
        tier.add("player_type", False, "no state")
        return tier

    actions, err = safe_call(module.get_legal_actions, state)
    ok = err is None and isinstance(actions, list) and all(isinstance(a, str) for a in actions)
    tier.add("actions_type", ok, err or ("list[str]" if ok else str(type(actions))))

    rewards, err = safe_call(module.get_rewards, state)
    ok = err is None and isinstance(rewards, list) and all(isinstance(r, (int, float)) for r in rewards)
    tier.add("rewards_type", ok, err or ("list[float]" if ok else str(rewards)))

    obs, err = safe_call(module.get_observations, state)
    ok = err is None and isinstance(obs, list) and len(obs) >= 1
    tier.add("observations_type", ok, err or ("list" if ok else str(type(obs))))

    player, err = safe_call(module.get_current_player, state)
    tier.add("player_type", err is None and isinstance(player, int),
             err or ("int" if isinstance(player, int) else type(player).__name__))

    return tier


def test_dynamics(module, num_games=100):
    tier = TierResult("2. Dynamics")

    no_crash = 0
    immutable_games = 0
    determinism_games = 0
    terminal_empty = 0

    for _ in range(num_games):
        try:
            state = module.get_initial_state()
            game_immutable = True
            game_determinism = True
            game_terminal_empty = True

            for _ in range(500):
                player = module.get_current_player(state)

                if player == -4:
                    if module.get_legal_actions(state) != []:
                        game_terminal_empty = False
                    break

                actions = module.get_legal_actions(state)
                if not actions:
                    break

                # Determinism check: call twice, should be same
                actions2 = module.get_legal_actions(state)
                obs1 = module.get_observations(state)
                obs2 = module.get_observations(state)
                if actions != actions2 or obs1 != obs2:
                    game_determinism = False

                action = random.choice(actions)
                before = copy.deepcopy(state)
                next_state = module.apply_action(state, action)

                # Immutability check
                if state != before:
                    game_immutable = False

                state = next_state

            no_crash += 1
            if game_immutable:
                immutable_games += 1
            if game_determinism:
                determinism_games += 1
            if game_terminal_empty:
                terminal_empty += 1
        except:
            pass

    n = num_games
    tier.add("no_crash", no_crash == n, f"{no_crash}/{n}")
    tier.add("immutable", immutable_games == no_crash, f"{immutable_games}/{no_crash if no_crash > 0 else n}")
    tier.add("determinism", determinism_games == no_crash, f"{determinism_games}/{no_crash if no_crash > 0 else n}")
    tier.add("terminal_empty", terminal_empty == no_crash, f"{terminal_empty}/{no_crash if no_crash > 0 else n}")

    return tier


def test_information(module, num_games=100, game_name=None):
    tier = TierResult("3. Information")

    has_resample = hasattr(module, 'resample_history')
    requires_resample = game_name in IMPERFECT_INFO_GAMES if game_name else False

    if not has_resample:
        if requires_resample:
            tier.add("resample_legal", False, "resample_history not implemented")
            tier.add("obs_reconstruction", False, "resample_history not implemented")
            tier.add("action_consistency", False, "resample_history not implemented")
            tier.add("resample_complete", False, "resample_history not implemented")
            return tier
        tier.add("perfect_info", True, "N/A - no resample_history")
        return tier

    runs = 0
    legal_games = 0
    obs_match_games = 0
    action_match_games = 0
    complete_games = 0

    for _ in range(num_games):
        try:
            pid = random.choice([0, 1])
            state = module.get_initial_state()
            history = []

            for _ in range(200):
                player = module.get_current_player(state)

                if player == -4:
                    break

                actions = module.get_legal_actions(state)
                if not actions:
                    break

                action = random.choice(actions)
                if player == pid:
                    obs = module.get_observations(state)
                    if isinstance(obs, list) and len(obs) > pid:
                        history.append((copy.deepcopy(obs[pid]), action))

                state = module.apply_action(state, action)
        except Exception:
            continue

        if len(history) < 1:
            continue

        runs += 1

        try:
            resampled = module.resample_history(copy.deepcopy(history), pid)

            if not isinstance(resampled, list):
                continue

            # Replay resampled actions from initial state, checking against
            # the recorded obs/action history at each player turn.
            state = module.get_initial_state()
            obs_action_iter = iter(history)
            exp_obs, exp_action = next(obs_action_iter, (None, None))

            all_legal = True
            all_obs_match = True
            all_actions_match = True

            for action in resampled:
                if module.get_current_player(state) == -4:
                    break

                if action not in module.get_legal_actions(state):
                    all_legal = False
                    all_obs_match = False
                    all_actions_match = False
                    break

                if module.get_current_player(state) == pid:
                    if exp_obs is None:
                        all_actions_match = False
                        break

                    if module.get_observations(state)[pid] != exp_obs:
                        all_obs_match = False
                    if action != exp_action:
                        all_actions_match = False

                    exp_obs, exp_action = next(obs_action_iter, (None, None))

                state = module.apply_action(state, action)

            # All history entries must have been consumed
            game_complete = all_legal and (exp_obs is None)
            if not game_complete:
                all_obs_match = False
                all_actions_match = False

            if all_legal:
                legal_games += 1
            if all_obs_match:
                obs_match_games += 1
            if all_actions_match:
                action_match_games += 1
            if game_complete:
                complete_games += 1

        except Exception:
            pass

    if runs == 0:
        tier.add("resample_testable", False, "no tests ran")
        return tier

    tier.add("resample_legal", legal_games == runs, f"{legal_games}/{runs}")
    tier.add("obs_reconstruction", obs_match_games == runs, f"{obs_match_games}/{runs}")
    tier.add("action_consistency", action_match_games == runs, f"{action_match_games}/{runs}")
    tier.add("resample_complete", complete_games == runs, f"{complete_games}/{runs}")

    return tier


def load_scenarios(game_name):
    scenario_path = os.path.join("data/games", game_name, "scenarios.py")
    if not os.path.exists(scenario_path):
        return None, None
    try:
        spec = importlib.util.spec_from_file_location("scenarios", scenario_path)
        sm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sm)
        return sm.SCENARIOS, None
    except Exception as e:
        return None, str(e)


def test_scenarios(module, game_name):
    scenarios, err = load_scenarios(game_name)

    if scenarios is None and err is None:
        return None  # no scenarios file — skip this tier

    tier = TierResult("4. Scenarios")

    if err:
        tier.add("load_scenarios", False, err)
        return tier

    runner_path = os.path.join(os.path.dirname(__file__), "scenario_runner.py")
    spec = importlib.util.spec_from_file_location("scenario_runner", runner_path)
    sr_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr_mod)
    sr = sr_mod.run_scenarios(module, scenarios)
    for d in sr["details"]:
        tier.add(d["name"], d["passed"], d["failure"] or "ok")

    return tier


def make_failed_tiers(error_msg):
    static = TierResult("1. Static")
    static.add("syntax", False, error_msg)
    static.add("api_complete", False, "load failed")
    static.add("initial_state_type", False, "load failed")
    static.add("actions_type", False, "load failed")
    static.add("rewards_type", False, "load failed")
    static.add("observations_type", False, "load failed")
    static.add("player_type", False, "load failed")

    dynamics = TierResult("2. Dynamics")
    dynamics.add("no_crash", False, "load failed")
    dynamics.add("immutable", False, "load failed")
    dynamics.add("determinism", False, "load failed")
    dynamics.add("terminal_empty", False, "load failed")

    information = TierResult("3. Information")
    information.add("resample_legal", False, "load failed")
    information.add("obs_reconstruction", False, "load failed")
    information.add("action_consistency", False, "load failed")
    information.add("resample_complete", False, "load failed")

    return static, dynamics, information


def run_evaluation(candidate_path, game_name, num_games=100, seed=None, quiet=False):
    if seed is not None:
        random.seed(seed)

    if not quiet:
        print(f"Loading: {candidate_path}")

    module, err = load_module(candidate_path)

    result = EvaluationResult(game_name, candidate_path)

    if err:
        # Failed to load - all tiers fail with consistent test counts
        static, dynamics, information = make_failed_tiers(err)
        result.tiers["static"] = static
        result.tiers["dynamics"] = dynamics
        result.tiers["information"] = information
        # Scenarios tier: mark each scenario as failed (module wouldn't load)
        scenarios, _ = load_scenarios(game_name)
        if scenarios is not None:
            scenarios_tier = TierResult("4. Scenarios")
            for s in scenarios:
                scenarios_tier.add(s["name"], False, "load failed")
            result.tiers["scenarios"] = scenarios_tier
        return result

    if not quiet:
        print(f"Evaluating '{game_name}' with {num_games} games\n")

    result.tiers["static"] = test_static(module, candidate_path)
    result.tiers["dynamics"] = test_dynamics(module, num_games)
    result.tiers["information"] = test_information(module, num_games, game_name=game_name)
    scenarios_tier = test_scenarios(module, game_name)
    if scenarios_tier is not None:
        result.tiers["scenarios"] = scenarios_tier

    return result


def print_results(result):
    print("\n" + "=" * 60)
    print(f"EVALUATION: {result.game}")
    print("=" * 60 + "\n")

    for name, tier in result.tiers.items():
        if not tier.results:
            continue

        print(f"  {tier.name}: {tier.passed}/{tier.total}")

        for t in tier.results:
            sym = "+" if t["passed"] else "-"
            msg = f" ({t['message']})" if t["message"] else ""
            print(f"    {sym} {t['name']}{msg}")
        print()

    total_passed = sum(t.passed for t in result.tiers.values())
    total_tests = sum(t.total for t in result.tiers.values())

    print("=" * 60)
    print(f"TOTAL: {total_passed}/{total_tests} | Score: {result.overall_score:.2%}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', required=True)
    parser.add_argument('--candidate')
    parser.add_argument('--num-games', type=int, default=100)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.candidate is None:
        args.candidate = f"evaluation/generated/{args.game}_gpt_4o.py"

    result = run_evaluation(args.candidate, args.game, args.num_games, args.seed, quiet=args.json)

    if args.json:
        out = {
            "game": result.game,
            "score": result.overall_score,
            "tiers": {
                name: {"score": t.score, "passed": t.passed, "total": t.total, "tests": t.results}
                for name, t in result.tiers.items()
            }
        }
        print(json.dumps(out, indent=2))
    else:
        print_results(result)