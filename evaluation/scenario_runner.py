import math


def run_scenarios(module, scenarios: list) -> dict:
    """
    Replay each scenario against the given game module.

    Returns:
        {
            "passed": int,
            "total": int,
            "score": float,   # 0.0–1.0
            "details": [{"name": str, "passed": bool, "failure": str | None}]
        }
    """
    results = []
    for s in scenarios:
        passed = True
        failure = None
        try:
            state = module.get_initial_state()
            for action in s["actions"]:
                state = module.apply_action(state, action)

            checks = s.get("checks", {})

            if "terminal" in checks:
                is_term = module.get_current_player(state) == -4
                if is_term != checks["terminal"]:
                    passed = False
                    failure = f"terminal={is_term}, want {checks['terminal']}"

            if passed and "current_player" in checks:
                cp = module.get_current_player(state)
                if cp != checks["current_player"]:
                    passed = False
                    failure = f"current_player={cp}, want {checks['current_player']}"

            if passed and "rewards_sign" in checks:
                rewards = module.get_rewards(state)
                signs = [int(math.copysign(1, r)) if r != 0.0 else 0 for r in rewards]
                if signs != checks["rewards_sign"]:
                    passed = False
                    failure = f"rewards_sign={signs}, want {checks['rewards_sign']} (rewards={rewards})"

            if passed and "winner" in checks:
                rewards = module.get_rewards(state)
                winner = rewards.index(max(rewards))
                if winner != checks["winner"]:
                    passed = False
                    failure = f"winner={winner}, want {checks['winner']} (rewards={rewards})"

        except Exception as e:
            passed = False
            failure = f"{type(e).__name__}: {e}"

        results.append({"name": s["name"], "passed": passed, "failure": failure})

    total = len(results)
    passed_count = sum(r["passed"] for r in results)
    return {
        "passed": passed_count,
        "total": total,
        "score": passed_count / total if total > 0 else 0.0,
        "details": results,
    }
