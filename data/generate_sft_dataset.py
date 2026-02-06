"""Generate SFT dataset from games."""
import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import TRAINING_GAMES, EVAL_GAMES, IMPERFECT_INFO_GAMES, validate_curriculum

# Validate config on import
validate_curriculum()

def load_prompt_template(is_imperfect: bool) -> str:
    """Load the appropriate prompt template."""
    base_path = Path(__file__).parent / "prompts"
    if is_imperfect:
        template_path = base_path / "gemini_imperfect_info.txt"
    else:
        template_path = base_path / "gemini_perfect_info.txt"

    with open(template_path, 'r') as f:
        return f.read()

def load_game_data(game_name: str) -> tuple[str, str]:
    """Load rules.txt and golden.py for a game."""
    game_path = Path(__file__).parent / "games" / game_name

    rules_path = game_path / "rules.txt"
    golden_path = game_path / "golden.py"

    with open(rules_path, 'r') as f:
        rules = f.read()

    with open(golden_path, 'r') as f:
        golden = f.read()

    return rules, golden

def format_game_name(game_name: str) -> str:
    """Convert game_name to display name."""
    return game_name.replace("_", " ").title()

def create_example(game_name: str) -> dict:
    """Create a single training example."""
    is_imperfect = game_name in IMPERFECT_INFO_GAMES

    template = load_prompt_template(is_imperfect)
    rules, golden = load_game_data(game_name)

    # Format the prompt
    prompt = template.format(
        game_name=format_game_name(game_name),
        game_desc=rules
    )

    # Create chat format
    return {
        "messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": golden}
        ],
        "game": game_name,
        "info_type": "imperfect" if is_imperfect else "perfect"
    }

def main():
    dataset = []

    for game_name in TRAINING_GAMES:
        try:
            example = create_example(game_name)
            dataset.append(example)
            print(f"✓ Added {game_name} ({example['info_type']} info)")
        except FileNotFoundError as e:
            print(f"✗ Skipping {game_name}: {e}")

    # Save dataset
    output_path = Path(__file__).parent / "sft_train.json"
    with open(output_path, 'w') as f:
        json.dump(dataset, f, indent=2)

    print(f"\nCreated {len(dataset)} training examples")
    print(f"Saved to: {output_path}")

    # Also create eval dataset
    eval_dataset = []

    for game_name in EVAL_GAMES:
        try:
            example = create_example(game_name)
            eval_dataset.append(example)
            print(f"✓ Added {game_name} to eval ({example['info_type']} info)")
        except FileNotFoundError as e:
            print(f"✗ Skipping {game_name}: {e}")

    eval_output_path = Path(__file__).parent / "sft_eval.json"
    with open(eval_output_path, 'w') as f:
        json.dump(eval_dataset, f, indent=2)

    print(f"\nCreated {len(eval_dataset)} eval examples")
    print(f"Saved to: {eval_output_path}")

if __name__ == "__main__":
    main()
