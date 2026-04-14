import random
import copy
import tempfile
import os
import signal
import sys
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import IMPERFECT_INFO_GAMES, TIER_WEIGHTS
from evaluation.scenario_runner import run_scenarios


class CodeTimeoutError(Exception):
    """Raised when code execution times out."""
    pass


@contextmanager
def timeout(seconds: int, error_message: str = "Code execution timed out"):
    """Context manager that raises CodeTimeoutError after specified seconds.

    Only works on Unix systems and in the main thread.
    Falls back to no timeout if signal is not available.
    """
    def timeout_handler(signum, frame):
        raise CodeTimeoutError(error_message)

    # Check if we can use signals (Unix + main thread)
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        can_timeout = True
    except (ValueError, AttributeError):
        # Not on main thread or signal not available
        can_timeout = False

    try:
        yield
    finally:
        if can_timeout:
            signal.alarm(0)  # Cancel the alarm
            signal.signal(signal.SIGALRM, old_handler)


def load_module_from_string(code: str):
    """Load module from code string. Returns (module, error)."""
    try:
        compiled = compile(code, '<generated>', 'exec')
    except SyntaxError as e:
        return None, f"SyntaxError line {e.lineno}: {e.msg}"

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        import importlib.util
        spec = importlib.util.spec_from_file_location("candidate", temp_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        os.unlink(temp_path)
        return module, None
    except Exception as e:
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        return None, str(e)


def load_module_from_file(path: str):
    """Load module from file path. Returns (module, error)."""
    try:
        with open(path) as f:
            code = f.read()
        compile(code, path, 'exec')

        import importlib.util
        spec = importlib.util.spec_from_file_location("candidate", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module, None
    except SyntaxError as e:
        return None, f"SyntaxError line {e.lineno}: {e.msg}"
    except Exception as e:
        return None, str(e)


def check_static(module) -> tuple[float, bool]:
    score = 0.2  # syntax passed

    required = ['get_initial_state', 'apply_action', 'get_current_player',
                'get_legal_actions', 'get_rewards', 'get_observations']
    missing = [f for f in required if not hasattr(module, f)]

    if missing:
        return score, False

    score += 0.3  # API complete

    # Type checks
    try:
        state = module.get_initial_state()
        if isinstance(state, dict):
            score += 0.1
        else:
            return score, False
    except:
        return score, False

    try:
        actions = module.get_legal_actions(state)
        if isinstance(actions, list) and all(isinstance(a, str) for a in actions):
            score += 0.1
    except:
        pass

    try:
        rewards = module.get_rewards(state)
        if (isinstance(rewards, list)
            and len(rewards) >= 2
            and all(isinstance(r, (int, float)) for r in rewards)):
            score += 0.1
    except:
        pass

    try:
        obs = module.get_observations(state)
        if isinstance(obs, list) and len(obs) >= 1:
            score += 0.1
    except:
        pass

    try:
        player = module.get_current_player(state)
        if isinstance(player, int):
            score += 0.1
    except:
        pass

    return score, True


def check_dynamics(module, num_games=20) -> float:
    total_score = 0.0

    for _ in range(num_games):
        game_score = 0.0
        try:
            state = module.get_initial_state()
            game_immutable = True
            game_idempotent = True
            terminal_correct = True
            reward_correct = True

            for step in range(200):
                player = module.get_current_player(state)

                if player == -4:
                    if module.get_legal_actions(state) != []:
                        terminal_correct = False
                    # Validate terminal rewards
                    rewards = module.get_rewards(state)
                    if (not isinstance(rewards, list)
                        or len(rewards) < 2
                        or not all(isinstance(r, (int, float)) for r in rewards)):
                        reward_correct = False
                    break

                actions = module.get_legal_actions(state)
                if not actions:
                    break

                # Idempotency (sample check - not every step for speed)
                if step % 5 == 0:
                    actions2 = module.get_legal_actions(state)
                    if actions != actions2:
                        game_idempotent = False

                action = random.choice(actions)
                before = copy.deepcopy(state)
                next_state = module.apply_action(state, action)

                # Immutability - check EVERY step since this is the most common bug
                if state != before:
                    game_immutable = False

                state = next_state

            game_score += 0.25  
            if game_immutable:
                game_score += 0.30  # immutability 
            if game_idempotent:
                game_score += 0.15  # idempotency
            if terminal_correct:
                game_score += 0.15  # terminal correctness
            if reward_correct:
                game_score += 0.15  # reward well-formedness

        except:
            pass  # game_score stays 0 (crash)

        total_score += game_score

    return total_score / num_games


def _validate_resample(module, resampled, history, pid) -> float:
    state = module.get_initial_state()
    obs_action_iter = iter(history)
    exp_obs, exp_action = next(obs_action_iter, (None, None))

    obs_ok = True
    action_ok = True

    for action in resampled:
        if module.get_current_player(state) == -4:
            break

        # Legality — hard fail, all checks 0
        if action not in module.get_legal_actions(state):
            return 0.0

        if module.get_current_player(state) == pid:
            if exp_obs is None:
                # Resampler produced more player turns than history has
                action_ok = False
                break

            if module.get_observations(state)[pid] != exp_obs:
                obs_ok = False
            if action != exp_action:
                action_ok = False

            exp_obs, exp_action = next(obs_action_iter, (None, None))

        state = module.apply_action(state, action)

    # All history entries must have been consumed
    complete_ok = (exp_obs is None)
    if not complete_ok:
        obs_ok = False
        action_ok = False

    score = 0.25  # legality passed (didn't early-return)
    if obs_ok:
        score += 0.25
    if action_ok:
        score += 0.25
    if complete_ok:
        score += 0.25
    return score


def check_information(module, num_games=20, requires_resample=False) -> float:
    if not hasattr(module, 'resample_history'):
        if requires_resample:
            return 0.0
        return 1.0

    # Detect stub implementations by checking source code
    import inspect
    import re
    try:
        source = inspect.getsource(module.resample_history)

        stub_phrases = [
            '# TODO',
            '# This function would need',
            'NotImplementedError',
            'for simplicity',
            'not implemented',
            'placeholder',
            'needs to be implemented',
        ]
        has_stub_phrase = any(phrase.lower() in source.lower() for phrase in stub_phrases)

        hardcoded_return = re.search(r"return\s*\[\s*['\"][^]]+['\"]", source)

        lines = source.split('\n')
        body_lines = [l for l in lines[1:] if l.strip() and not l.strip().startswith('#')]
        uses_input = any('obs_action_history' in l and 'for' in l or 'obs_action_history[' in l
                        for l in body_lines)

        is_stub = has_stub_phrase or (hardcoded_return and not uses_input)
        if is_stub:
            return 0.0
    except:
        pass

    sig = inspect.signature(module.resample_history)
    has_terminal_arg = 'last_is_terminal' in sig.parameters

    total_score = 0.0
    runs = 0

    for _ in range(num_games):
        try:
            pid = random.choice([0, 1])
            state = module.get_initial_state()
            history = []
            is_terminal = False

            for _ in range(100):
                player = module.get_current_player(state)
                if player == -4:
                    is_terminal = True
                    break
                actions = module.get_legal_actions(state)
                if not actions:
                    is_terminal = True
                    break
                action = random.choice(actions)
                if player == pid:
                    obs = module.get_observations(state)
                    if isinstance(obs, list) and len(obs) > pid:
                        history.append((copy.deepcopy(obs[pid]), action))
                state = module.apply_action(state, action)

            if len(history) < 1:
                continue

            runs += 1

            # Call resample twice; average scores for robustness
            resample_scores = []
            for _ in range(2):
                if has_terminal_arg:
                    resampled = module.resample_history(copy.deepcopy(history), pid, is_terminal)
                else:
                    resampled = module.resample_history(copy.deepcopy(history), pid)

                if not isinstance(resampled, list):
                    resample_scores.append(0.0)
                    continue

                resample_scores.append(_validate_resample(module, resampled, history, pid))

            total_score += sum(resample_scores) / len(resample_scores)

        except Exception:
            runs += 1

    if runs == 0:
        return 0.0

    return total_score / runs


def check_scenarios(module, game_name: str) -> float:
    scenarios_path = Path(__file__).parent.parent / "data" / "games" / game_name / "scenarios.py"
    if not scenarios_path.exists():
        return 1.0

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("scenarios", str(scenarios_path))
        sm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sm)
        scenarios = sm.SCENARIOS
    except Exception:
        return 0.0

    try:
        result = run_scenarios(module, scenarios)
        return result["score"]
    except Exception:
        return 0.0


def compute_reward(
    code: str,
    game_name: str,
    num_games: int,
    seed: int = None,
    gated: bool = True,
    weights: dict = None,
    timeout_seconds: int = 60,
    use_scenarios: bool = True,
) -> float:
    try:
        with timeout(timeout_seconds, f"Reward computation for {game_name} timed out after {timeout_seconds}s"):
            return _compute_reward_inner(code, game_name, num_games, seed, gated, weights, use_scenarios)
    except CodeTimeoutError:
        # Timed out - return 0 reward
        return 0.0


def _compute_reward_inner(
    code: str,
    game_name: str,
    num_games: int,
    seed: int,
    gated: bool,
    weights: dict,
    use_scenarios: bool = True,
) -> float:
    """Inner reward computation (without timeout wrapper)."""
    if seed is not None:
        random.seed(seed)

    if weights is None:
        # Build weights from applicable tiers, then renormalize to sum to 1.
        requires_info = game_name in IMPERFECT_INFO_GAMES
        applicable = {k: v for k, v in TIER_WEIGHTS.items()
                      if not (k == "information" and not requires_info)
                      and not (k == "scenarios" and not use_scenarios)}
        total_w = sum(applicable.values())
        weights = {k: v / total_w for k, v in applicable.items()}

    module, err = load_module_from_string(code)

    if err:
        return 0.0

    # static and gating check (if you don't have the basic structure, you shouldn't get rewarded for CWM)
    static_score, can_continue = check_static(module)

    if gated and not can_continue:
        return static_score * weights["static"]

    # fuzz / dynamics
    dynamics_score = check_dynamics(module, num_games)

    if gated and dynamics_score < 0.5:
        return (static_score * weights["static"] +
                dynamics_score * weights["dynamics"])

    total = (static_score * weights["static"] +
             dynamics_score * weights["dynamics"])

    if "information" in weights:
        info_score = check_information(module, num_games, requires_resample=True)
        total += info_score * weights["information"]

    if "scenarios" in weights:
        scenario_score = check_scenarios(module, game_name)
        total += scenario_score * weights["scenarios"]

    return total


def compute_reward_from_file(
    path: str,
    game_name: str,
    num_games: int = 20,
    seed: int = None,
    gated: bool = True,
    weights: dict = None,
    timeout_seconds: int = 60,
    use_scenarios: bool = True,
) -> float:
    """Compute reward from file path instead of code string."""
    with open(path) as f:
        code = f.read()
    return compute_reward(code, game_name, num_games, seed, gated, weights, timeout_seconds, use_scenarios)


def compute_reward_batch(
    codes: list[str],
    game_name: str,
    num_games: int = 20,
    seed: int = None,
    gated: bool = True,
    timeout_seconds: int = 60,
    use_scenarios: bool = True,
) -> list[float]:
    """Compute rewards for a batch of code samples."""
    rewards = []
    for i, code in enumerate(codes):
        # Use different seed for each sample for diversity
        sample_seed = seed + i if seed is not None else None
        r = compute_reward(code, game_name, num_games, sample_seed, gated,
                          timeout_seconds=timeout_seconds, use_scenarios=use_scenarios)
        rewards.append(r)
    return rewards


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GRPO reward computation")
    parser.add_argument('--candidate', required=True, help="Path to candidate code")
    parser.add_argument('--game', required=True, help="Game name")
    parser.add_argument('--num-games', type=int, default=20)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--no-gate', action='store_true', help="Disable gating")
    parser.add_argument('--timeout', type=int, default=60, help="Timeout in seconds (default: 60)")
    parser.add_argument('--no-scenarios', action='store_true', help="Disable scenario tier (ablation)")

    args = parser.parse_args()

    reward = compute_reward_from_file(
        args.candidate,
        args.game,
        args.num_games,
        args.seed,
        gated=not args.no_gate,
        timeout_seconds=args.timeout,
        use_scenarios=not args.no_scenarios,
    )

    print(f"Game: {args.game}")
    print(f"Reward: {reward:.4f}")