import argparse
import re
import sys
import multiprocessing as mp
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent))
from evaluation.run_behavioral_metrics import (
    run_evaluation, load_module, test_static, TierResult, EvaluationResult
)
from config import IMPERFECT_INFO_GAMES


def _run_eval_worker(filepath, game, num_games, result_queue):
    """Worker function that runs in a separate process."""
    try:
        result = run_evaluation(
            candidate_path=filepath,
            game_name=game,
            num_games=num_games,
            quiet=True
        )
        # Convert to serializable dict
        result_dict = {
            "score": result.overall_score,
            "tiers": {name: tier.score for name, tier in result.tiers.items()}
        }
        result_queue.put(("ok", result_dict))
    except Exception as e:
        result_queue.put(("error", str(e)))


def run_evaluation_with_timeout(filepath, game, num_games, timeout_seconds=60):
    """
    Run evaluation with timeout using multiprocessing (actually kills the process).

    Returns (result, timed_out) where result is a simple object with overall_score and tiers.
    """
    result_queue = mp.Queue()
    proc = mp.Process(
        target=_run_eval_worker,
        args=(str(filepath), game, num_games, result_queue)
    )
    proc.start()
    proc.join(timeout=timeout_seconds)

    if proc.is_alive():
        # Timed out - kill the process
        proc.terminate()
        proc.join(timeout=1)
        if proc.is_alive():
            proc.kill()
            proc.join()

        # Give partial credit for static checks (run quickly in main process)
        module, err = load_module(str(filepath))

        # Create a simple result object
        class SimpleResult:
            def __init__(self):
                self.tiers = {}
                self.overall_score = 0.0

        result = SimpleResult()

        if err:
            static = TierResult("1. Static")
            static.add("syntax", False, err)
            result.tiers["static"] = static
            result.overall_score = 0.0
        else:
            # Run static checks only (fast)
            result.tiers["static"] = test_static(module, str(filepath))

            # Add failed tiers for timeout
            dynamics = TierResult("2. Dynamics")
            dynamics.add("timeout", False, "killed")
            result.tiers["dynamics"] = dynamics

            rewards = TierResult("3. Rewards")
            rewards.add("timeout", False, "killed")
            result.tiers["rewards"] = rewards

            information = TierResult("4. Information")
            information.add("timeout", False, "killed")
            result.tiers["information"] = information

            # Calculate score: static score / 4 tiers
            scores = [t.score for t in result.tiers.values()]
            result.overall_score = sum(scores) / len(scores)

        return result, True

    # Process finished - get result
    try:
        status, data = result_queue.get_nowait()
        if status == "ok":
            # Create simple result from dict
            class SimpleResult:
                def __init__(self, score, tiers):
                    self.overall_score = score
                    # Create fake tier objects with just .score
                    self.tiers = {}
                    for name, tier_score in tiers.items():
                        class FakeTier:
                            def __init__(self, s):
                                self.score = s
                        self.tiers[name] = FakeTier(tier_score)

            return SimpleResult(data["score"], data["tiers"]), False
        else:
            # Error in worker
            class SimpleResult:
                def __init__(self):
                    self.overall_score = 0.0
                    self.tiers = {}
            return SimpleResult(), False
    except Exception:
        class SimpleResult:
            def __init__(self):
                self.overall_score = 0.0
                self.tiers = {}
        return SimpleResult(), False


def parse_filename(filename: str) -> tuple[str, str, int] | None:
    """Parse filename like 'tic_tac_toe_base_qwen_gen1.py' -> (game, model, gen_num)."""
    # Pattern: {game}_{model}_gen{n}.py
    # --- FIX: Add gpt4o to the pattern ---
    match = re.match(r'^(.+?)_(base_qwen|sft_qwen|grpo_qwen|sft_grpo_qwen|gpt4o)_gen(\d+)\.py$', filename)
    # ----------------------------------------
    if match:
        game, model, gen = match.groups()
        return game, model, int(gen)
    return None


def main():
    parser = argparse.ArgumentParser(description="Evaluate comparison files")
    parser.add_argument("--dir", default="evaluation/generated/comparison",
                        help="Directory with generated files")
    parser.add_argument("--num-games", type=int, default=100,
                        help="Number of games for evaluation")
    parser.add_argument("--timeout", type=int, default=60,
                        help="Timeout per file in seconds (default: 60)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    comparison_dir = Path(args.dir)
    if not comparison_dir.exists():
        print(f"Directory not found: {comparison_dir}")
        sys.exit(1)

    # Find all .py files and group by game and model
    files = list(comparison_dir.glob("*.py"))
    print(f"Found {len(files)} files in {comparison_dir}\n")

    # Structure: {game: {model: [(gen_num, path, result)]}}
    results = defaultdict(lambda: defaultdict(list))

    for filepath in sorted(files):
        parsed = parse_filename(filepath.name)
        if not parsed:
            print(f"  Skipping (unrecognized format): {filepath.name}")
            continue

        game, model, gen_num = parsed
        print(f"Evaluating: {filepath.name}...", end=" ", flush=True)

        try:
            result, timed_out = run_evaluation_with_timeout(
                filepath=filepath,
                game=game,
                num_games=args.num_games,
                timeout_seconds=args.timeout
            )
            score = result.overall_score
            tier_scores = {name: tier.score for name, tier in result.tiers.items()}
            suffix = " (timeout)" if timed_out else ""
            print(f"{score:.1%}{suffix}")
            results[game][model].append({
                "gen": gen_num,
                "score": score,
                "tiers": tier_scores,
                "timed_out": timed_out
            })
        except KeyboardInterrupt:
            print("Interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            results[game][model].append({
                "gen": gen_num,
                "score": 0.0,
                "error": str(e)
            })

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY BY GAME")
    print("=" * 80)

    all_models = set()
    for game_results in results.values():
        all_models.update(game_results.keys())
    all_models = sorted(all_models)

    # Header
    print(f"\n{'Game':<20}", end="")
    for model in all_models:
        print(f"{model:>15}", end="")
    print()
    print("-" * (20 + 15 * len(all_models)))

    # Collect all tier names first
    all_tiers = set()
    for game_results in results.values():
        for model_results in game_results.values():
            for r in model_results:
                if "tiers" in r:
                    all_tiers.update(r["tiers"].keys())
    tier_names = sorted(all_tiers)

    # Per-game scores
    model_all_scores = defaultdict(list)

    for game in sorted(results.keys()):
        print(f"{game:<20}", end="")
        for model in all_models:
            scores = [r["score"] for r in results[game][model]]
            if scores:
                mean = np.mean(scores)
                model_all_scores[model].extend(scores)
                print(f"{mean:>14.1%}", end=" ")
            else:
                print(f"{'N/A':>14}", end=" ")
        print()

    # Per-tier per-game breakdown
    if tier_names:
        print("\n" + "=" * 80)
        print("PER-TIER BY GAME")
        print("=" * 80)

        for game in sorted(results.keys()):
            print(f"\n{game}:")
            print(f"  {'Model':<15}", end="")
            for tier in tier_names:
                print(f"{tier[:10]:>12}", end="")
            print()
            print("  " + "-" * (15 + 12 * len(tier_names)))

            for model in all_models:
                print(f"  {model:<15}", end="")
                for tier in tier_names:
                    tier_scores = []
                    for r in results[game][model]:
                        if "tiers" in r and tier in r["tiers"]:
                            tier_scores.append(r["tiers"][tier])
                    if tier_scores:
                        print(f"{np.mean(tier_scores):>11.1%}", end=" ")
                    else:
                        print(f"{'N/A':>11}", end=" ")
                print()

    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n{'Model':<20} {'N':>6} {'Mean':>10} {'95% CI':>20} {'Std':>10}")
    print("-" * 70)

    for model in all_models:
        scores = model_all_scores[model]
        if scores:
            n = len(scores)
            mean = np.mean(scores)
            std = np.std(scores, ddof=1) if n > 1 else 0

            if n > 1:
                sem = stats.sem(scores)
                ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)
                ci_str = f"[{ci[0]:.1%}, {ci[1]:.1%}]"
            else:
                ci_str = "[n=1]"

            print(f"{model:<20} {n:>6} {mean:>10.1%} {ci_str:>20} {std:>10.1%}")
        else:
            print(f"{model:<20} {'N/A':>6}")

    # Per-tier breakdown (aggregate)
    print("\n" + "-" * 80)
    print("PER-TIER AGGREGATE (information tier: imperfect info games only)")
    print("-" * 80)

    if tier_names:
        print(f"\n{'Model':<20}", end="")
        for tier in tier_names:
            print(f"{tier[:12]:>14}", end="")
        print()
        print("-" * (20 + 14 * len(tier_names)))

        for model in all_models:
            print(f"{model:<20}", end="")
            for tier in tier_names:
                tier_scores = []
                for game, game_results in results.items():
                    # For information tier, only include imperfect info games
                    if tier == "information" and game not in IMPERFECT_INFO_GAMES:
                        continue
                    for r in game_results[model]:
                        if "tiers" in r and tier in r["tiers"]:
                            tier_scores.append(r["tiers"][tier])
                if tier_scores:
                    print(f"{np.mean(tier_scores):>13.1%}", end=" ")
                else:
                    print(f"{'N/A':>13}", end=" ")
            print()


if __name__ == "__main__":
    # Required for multiprocessing on some platforms
    mp.set_start_method('fork', force=True)
    main()
