#!/usr/bin/env python3
"""
GRPO reward function for game implementations.

Optimized for:
- Speed (fewer games, early termination)
- Gradient signal (partial credit, not just pass/fail)
- Gating (static checks must pass before dynamics are rewarded)
- Safety (timeouts to prevent hanging on bad code)

Usage:
    from evaluation.grpo_reward import compute_reward
    reward = compute_reward(code_string, game_name)

    # Or from file
    reward = compute_reward_from_file(path, game_name)
"""
import random
import copy
import tempfile
import os
import signal
import sys
from contextlib import contextmanager
from pathlib import Path

# Add parent dir to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import IMPERFECT_INFO_GAMES


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
    """
    Check static requirements. Returns (score, can_continue).

    Score breakdown (0-1):
    - 0.2: syntax (already passed if we got here)
    - 0.3: API complete
    - 0.5: types correct (0.1 each for 5 type checks)

    can_continue: True if we can run dynamic tests
    """
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
        if isinstance(rewards, list) and all(isinstance(r, (int, float)) for r in rewards):
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
    """
    Check runtime dynamics. Returns score 0-1.

    Weighted partial credit for each game:
    - No crash: 0.35 (most important - code must run)
    - Immutability: 0.35 (most common LLM bug - apply_action must not mutate input)
    - Idempotency: 0.15 (get_legal_actions should be consistent)
    - Terminal correctness: 0.15 (terminal states should have no legal actions)

    Removed (as in behavioral metrics):
    - Determinism: redundant, caught by other tests
    - Termination: game-dependent, penalizes complex games
    """
    total_score = 0.0

    for _ in range(num_games):
        game_score = 0.0
        try:
            state = module.get_initial_state()
            game_immutable = True
            game_idempotent = True
            terminal_correct = True

            for step in range(200):
                player = module.get_current_player(state)

                if player == -4:
                    if module.get_legal_actions(state) != []:
                        terminal_correct = False
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

            # Weighted scoring - prioritize common failure modes
            game_score += 0.35  # no crash (made it through the loop)
            if game_immutable:
                game_score += 0.35  # immutability (most common LLM bug)
            if game_idempotent:
                game_score += 0.15  # idempotency
            if terminal_correct:
                game_score += 0.15  # terminal correctness

        except:
            pass  # game_score stays 0 (crash)

        total_score += game_score

    return total_score / num_games


def check_rewards(module, num_games=20) -> float:
    """
    Check reward correctness. Returns score 0-1.

    Partial credit for:
    - Sparse rewards (0 mid-game)
    - Correct dimensions
    - Zero-sum at terminal
    """
    try:
        num_players = len(module.get_rewards(module.get_initial_state()))
    except:
        num_players = 2

    total_score = 0.0

    for _ in range(num_games):
        game_score = 0.0
        try:
            state = module.get_initial_state()
            sparse_ok = True
            dim_ok = True
            zero_sum_ok = True
            reached_terminal = False

            for _ in range(200):
                player = module.get_current_player(state)
                rewards = module.get_rewards(state)

                # Dimension check
                if not isinstance(rewards, list) or len(rewards) != num_players:
                    dim_ok = False

                if player == -4 or not module.get_legal_actions(state):
                    reached_terminal = True
                    if isinstance(rewards, list) and abs(sum(rewards)) > 1e-9:
                        zero_sum_ok = False
                    break
                else:
                    if not (isinstance(rewards, list) and all(r == 0 for r in rewards)):
                        sparse_ok = False

                actions = module.get_legal_actions(state)
                if not actions:
                    break
                state = module.apply_action(state, random.choice(actions))

            # Score (each worth 1/3)
            if sparse_ok:
                game_score += 1/3
            if dim_ok:
                game_score += 1/3
            if reached_terminal and zero_sum_ok:
                game_score += 1/3

        except:
            pass

        total_score += game_score

    return total_score / num_games


def check_information(module, num_games=20, requires_resample=False) -> float:
    """
    Check information handling (imperfect info games only).
    Returns score 0-1, or 1.0 for perfect info games (N/A).

    Checks:
    - resample_legal: resampled actions are legal
    - obs_reconstruction: observations match original
    - action_consistency: resampled actions match original player actions
    - resample_complete: resampler covers all observations
    - privacy: observations differ between players

    Args:
        requires_resample: If True, penalize missing resample_history (for imperfect info games)
    """
    if not hasattr(module, 'resample_history'):
        if requires_resample:
            return 0.0  # Imperfect info game missing required function
        return 1.0  # Perfect info game, skip

    # Detect stub implementations by checking source code
    import inspect
    import re
    try:
        source = inspect.getsource(module.resample_history)

        # Check for obvious stub comments/patterns
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

        # Check for hardcoded return like: return ['Right', 'Up'] (string literals in list)
        # But NOT: return [] (empty list guard) or return [action for ...]
        hardcoded_return = re.search(r"return\s*\[\s*['\"][^]]+['\"]", source)

        # Check if function body actually uses obs_action_history meaningfully
        # (not just in signature or a trivial check)
        lines = source.split('\n')
        body_lines = [l for l in lines[1:] if l.strip() and not l.strip().startswith('#')]
        uses_input = any('obs_action_history' in l and 'for' in l or 'obs_action_history[' in l
                        for l in body_lines)

        # Flag as stub if: has stub phrase, or hardcoded return without using input
        is_stub = has_stub_phrase or (hardcoded_return and not uses_input)

        if is_stub:
            return 0.0  # Stub/hardcoded implementation
    except:
        pass  # Can't get source, continue with normal checks

    import inspect
    sig = inspect.signature(module.resample_history)
    has_terminal_arg = 'last_is_terminal' in sig.parameters

    total_score = 0.0
    runs = 0
    privacy_found = False

    for _ in range(num_games):
        try:
            pid = random.choice([0, 1])
            state = module.get_initial_state()
            history = []
            is_terminal = False

            for _ in range(100):  # Shorter trajectories for speed
                player = module.get_current_player(state)

                # Privacy check
                if not privacy_found and player >= 0:
                    obs = module.get_observations(state)
                    if isinstance(obs, list) and len(obs) >= 2 and obs[0] != obs[1]:
                        privacy_found = True

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

            if has_terminal_arg:
                resampled = module.resample_history(copy.deepcopy(history), pid, is_terminal)
            else:
                resampled = module.resample_history(copy.deepcopy(history), pid)

            if not isinstance(resampled, list):
                continue

            # Replay check
            replay = module.get_initial_state()
            hist_iter = iter(history)
            exp_obs, exp_action = next(hist_iter, (None, None))
            has_expectations = exp_obs is not None

            legal_ok = True
            obs_ok = True
            action_ok = True

            for action in resampled:
                cp = module.get_current_player(replay)
                if cp == -4:
                    break

                legal_actions = module.get_legal_actions(replay)
                if not legal_actions or action not in legal_actions:
                    legal_ok = False
                    break

                if cp == pid:
                    if not has_expectations:
                        # Resampler generated extra moves not in original history
                        action_ok = False
                    else:
                        # Check observation matches
                        actual = module.get_observations(replay)
                        if isinstance(actual, list) and len(actual) > pid:
                            if actual[pid] != exp_obs:
                                obs_ok = False

                        # Check action matches
                        if action != exp_action:
                            action_ok = False

                        # Advance to next expected obs/action
                        exp_obs, exp_action = next(hist_iter, (None, None))
                        has_expectations = exp_obs is not None

                replay = module.apply_action(replay, action)

            # Check resampler covered all observations (didn't stop early)
            complete_ok = not has_expectations

            # Score this run (each check worth 0.2, privacy handled separately)
            game_score = 0.0
            if legal_ok:
                game_score += 0.2
            if obs_ok:
                game_score += 0.2
            if action_ok:
                game_score += 0.2
            if complete_ok:
                game_score += 0.2

            total_score += game_score

        except:
            runs += 1  # Count failed runs

    if runs == 0:
        return 0.0

    base_score = total_score / runs
    privacy_bonus = 0.2 if privacy_found else 0.0

    return min(1.0, base_score + privacy_bonus)


def compute_reward(
    code: str,
    game_name: str,
    num_games: int,
    seed: int = None,
    gated: bool = True,
    weights: dict = None,
    timeout_seconds: int = 60
) -> float:
    """
    Compute GRPO reward for generated code.

    Args:
        code: Python code string
        game_name: Name of the game (for logging)
        num_games: Number of random games per tier (default 20)
        seed: Random seed for reproducibility
        gated: If True, must pass static to get dynamics reward, etc.
        weights: Custom weights for tiers (default: equal)
        timeout_seconds: Maximum time allowed for reward computation (default 60s)

    Returns:
        Reward score 0-1
    """
    try:
        with timeout(timeout_seconds, f"Reward computation for {game_name} timed out after {timeout_seconds}s"):
            return _compute_reward_inner(code, game_name, num_games, seed, gated, weights)
    except CodeTimeoutError:
        # Timed out - return 0 reward
        return 0.0


def _compute_reward_inner(
    code: str,
    game_name: str,
    num_games: int,
    seed: int,
    gated: bool,
    weights: dict
) -> float:
    """Inner reward computation (without timeout wrapper)."""
    if seed is not None:
        random.seed(seed)

    if weights is None:
        # Dynamics weighted higher - this is where most LLM bugs occur (immutability, crashes)
        # Information kept high - important for imperfect info games
        weights = {"static": 0.15, "dynamics": 0.35, "rewards": 0.20, "information": 0.30}

    # Load module
    module, err = load_module_from_string(code)

    if err:
        # Syntax error - partial credit for getting close
        # Could analyze error to give more nuanced feedback
        return 0.0

    # Static checks
    static_score, can_continue = check_static(module)

    if gated and not can_continue:
        # Failed static - only get static score
        return static_score * weights["static"]

    # Dynamics
    dynamics_score = check_dynamics(module, num_games)

    if gated and dynamics_score < 0.5:
        # Failed dynamics - don't reward further
        return (static_score * weights["static"] +
                dynamics_score * weights["dynamics"])

    # Rewards
    rewards_score = check_rewards(module, num_games)

    # Information - penalize missing resample_history for imperfect info games
    requires_resample = game_name in IMPERFECT_INFO_GAMES
    info_score = check_information(module, num_games, requires_resample=requires_resample)

    total = (static_score * weights["static"] +
             dynamics_score * weights["dynamics"] +
             rewards_score * weights["rewards"] +
             info_score * weights["information"])

    return total


def compute_reward_from_file(
    path: str,
    game_name: str,
    num_games: int = 20,
    seed: int = None,
    gated: bool = True,
    weights: dict = None,
    timeout_seconds: int = 60
) -> float:
    """Compute reward from file path instead of code string."""
    with open(path) as f:
        code = f.read()
    return compute_reward(code, game_name, num_games, seed, gated, weights, timeout_seconds)


def compute_reward_batch(
    codes: list[str],
    game_name: str,
    num_games: int = 20,
    seed: int = None,
    gated: bool = True,
    timeout_seconds: int = 60
) -> list[float]:
    """Compute rewards for a batch of code samples."""
    rewards = []
    for i, code in enumerate(codes):
        # Use different seed for each sample for diversity
        sample_seed = seed + i if seed is not None else None
        r = compute_reward(code, game_name, num_games, sample_seed, gated,
                          timeout_seconds=timeout_seconds)
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

    args = parser.parse_args()

    reward = compute_reward_from_file(
        args.candidate,
        args.game,
        args.num_games,
        args.seed,
        gated=not args.no_gate,
        timeout_seconds=args.timeout
    )

    print(f"Game: {args.game}")
    print(f"Reward: {reward:.4f}")
