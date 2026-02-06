import sys
print("Starting compare_models.py...", flush=True)

import argparse
import os
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EVAL_GAMES, TRAINING_GAMES, IMPERFECT_INFO_GAMES
from evaluation.llm_client import get_gpt4o_client

print("Imports complete.", flush=True)

STANDARD_IMPORTS = """\
import copy
import random
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
"""


def load_prompt_template(is_imperfect: bool) -> str:
    """Load the appropriate prompt template."""
    base = Path(__file__).parent.parent / "data" / "prompts"
    name = "gemini_imperfect_info.txt" if is_imperfect else "gemini_perfect_info.txt"
    with open(base / name) as f:
        return f.read()


def load_game_rules(game: str) -> str:
    """Load game rules from file."""
    rules_path = Path(__file__).parent.parent / "data" / "games" / game / "rules.txt"
    if not rules_path.exists():
        raise FileNotFoundError(f"Rules not found: {rules_path}")
    with open(rules_path) as f:
        return f.read()


def build_prompt(game: str) -> str:
    """Build the full prompt for a game."""
    is_imperfect = game in IMPERFECT_INFO_GAMES
    template = load_prompt_template(is_imperfect)
    rules = load_game_rules(game)
    return template.format(
        game_name=game.replace("_", " ").title(),
        game_desc=rules
    )


def extract_code(response: str) -> str:
    """Extract Python code from markdown response and prepend standard imports."""
    if "```python" in response:
        blocks = response.split("```python")[1:]
        code_blocks = []
        for block in blocks:
            if "```" in block:
                code_blocks.append(block.split("```")[0])
        code = max(code_blocks, key=len) if code_blocks else ""
    elif "```" in response:
        code = response.split("```")[1].split("```")[0]
    else:
        code = response

    code = code.strip()
    return STANDARD_IMPORTS + "\n" + code


def generate_with_local_model(
    model_path: str,
    prompts: list[str],
    games: list[str],
    model_name: str,
    output_dir: Path,
    max_new_tokens: int = 4096,
    num_generations: int = 1,
    base_model: str = "Qwen/Qwen2.5-3B-Instruct",
) -> None:
    """Generate code and save directly to files."""
    print(f"\n{'='*60}")
    print(f"[{model_name}] Loading model from {model_path}")
    print(f"{'='*60}")

    model_path = Path(model_path)

    # Check if LoRA adapter
    is_adapter = (model_path / "adapter_config.json").exists() and not (model_path / "model.safetensors").exists()

    if is_adapter:
        import json
        with open(model_path / "adapter_config.json") as f:
            adapter_config = json.load(f)
        adapter_base = adapter_config.get("base_model_name_or_path", base_model)
        print(f"  Loading base: {adapter_base}")

        model = AutoModelForCausalLM.from_pretrained(
            adapter_base,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device_map="cuda" if torch.cuda.is_available() else "cpu",
        )
        model = PeftModel.from_pretrained(model, str(model_path))
        print(f"  LoRA adapter applied")
        tokenizer = AutoTokenizer.from_pretrained(adapter_base, trust_remote_code=True)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device_map="cuda" if torch.cuda.is_available() else "cpu",
        )
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)

    tokenizer.pad_token = tokenizer.eos_token

    # Generate for each game
    for game, prompt in zip(games, prompts):
        print(f"\n  [{game}] Generating {num_generations} response(s)...")

        messages = [
            {"role": "user", "content": prompt}
        ]
        formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(formatted, return_tensors="pt").to(model.device)

        for gen_idx in range(1, num_generations + 1):
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=0.3,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            code = extract_code(response)

            # Save to file
            safe_model = model_name.lower().replace(" ", "_")
            file_path = output_dir / f"{game}_{safe_model}_gen{gen_idx}.py"
            file_path.write_text(code)
            print(f"    Saved: {file_path.name}")

    # Cleanup
    print(f"\n  Cleaning up {model_name}...")
    del model
    torch.cuda.empty_cache()


def generate_with_gpt4o(
    prompts: list[str],
    games: list[str],
    output_dir: Path,
    num_generations: int = 1,
    temperature: float = 0.3,
) -> None:
    """Generate code using GPT-4o API and save to files."""
    print(f"\n{'='*60}")
    print(f"[gpt4o] Using OpenAI GPT-4o API")
    print(f"{'='*60}")

    client = get_gpt4o_client(temperature=temperature)

    for game, prompt in zip(games, prompts):
        print(f"\n  [{game}] Generating {num_generations} response(s)...")

        for gen_idx in range(1, num_generations + 1):
            response = client.generate(prompt, temperature=temperature)
            code = extract_code(response.content)

            # Save to file
            file_path = output_dir / f"{game}_gpt4o_gen{gen_idx}.py"
            file_path.write_text(code)
            print(f"    Saved: {file_path.name} ({response.usage['total_tokens']} tokens)")


def get_games_list(game_arg: str) -> list[str]:
    """Parse game argument into list of games."""
    game_arg = game_arg.lower().strip()

    if game_arg in ('eval', 'all-eval'):
        return list(EVAL_GAMES)
    elif game_arg in ('train', 'all-train'):
        return list(TRAINING_GAMES)
    elif game_arg == 'all':
        return list(TRAINING_GAMES) + list(EVAL_GAMES)
    elif ',' in game_arg:
        return [g.strip() for g in game_arg.split(',')]
    else:
        return [game_arg]


def main():
    parser = argparse.ArgumentParser(description="Generate code from models")
    parser.add_argument("--game", type=str, required=True,
                        help="Game(s): name, comma-list, 'eval', 'train', or 'all'")
    parser.add_argument("--grpo-path", type=str,
                        default=os.path.expanduser("~/scratch/experiments/cwm-grpo-v2/final_adapter"))
    parser.add_argument("--sft-path", type=str,
                        default=os.path.expanduser("~/scratch/experiments/cwm-sft/adapter"))
    parser.add_argument("--sft-grpo-path", type=str,
                        default=os.path.expanduser("~/scratch/experiments/cwm-sft-grpo-v2/final_adapter"))
    parser.add_argument("--base-model", type=str, default="Qwen/Qwen2.5-3B-Instruct")
    parser.add_argument("--output-dir", type=str, default="evaluation/generated/comparison")
    parser.add_argument("--num-generations", type=int, default=3)
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--skip-base", action="store_true")
    parser.add_argument("--skip-sft", action="store_true")
    parser.add_argument("--skip-grpo", action="store_true")
    parser.add_argument("--skip-sft-grpo", action="store_true")
    parser.add_argument("--skip-gpt4o", action="store_true")

    args = parser.parse_args()

    games = get_games_list(args.game)
    print(f"Games: {games}")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build prompts
    print("\nBuilding prompts...")
    prompts = [build_prompt(game) for game in games]

    # Generate from each model
    if not args.skip_base:
        generate_with_local_model(
            model_path=args.base_model,
            prompts=prompts,
            games=games,
            model_name="base_qwen",
            output_dir=output_dir,
            num_generations=args.num_generations,
            max_new_tokens=args.max_new_tokens,
        )

    if not args.skip_sft and Path(args.sft_path).exists():
        generate_with_local_model(
            model_path=args.sft_path,
            prompts=prompts,
            games=games,
            model_name="sft_qwen",
            output_dir=output_dir,
            num_generations=args.num_generations,
            max_new_tokens=args.max_new_tokens,
            base_model=args.base_model,
        )

    if not args.skip_grpo and Path(args.grpo_path).exists():
        generate_with_local_model(
            model_path=args.grpo_path,
            prompts=prompts,
            games=games,
            model_name="grpo_qwen",
            output_dir=output_dir,
            num_generations=args.num_generations,
            max_new_tokens=args.max_new_tokens,
            base_model=args.base_model,
        )

    if not args.skip_sft_grpo and Path(args.sft_grpo_path).exists():
        generate_with_local_model(
            model_path=args.sft_grpo_path,
            prompts=prompts,
            games=games,
            model_name="sft_grpo_qwen",
            output_dir=output_dir,
            num_generations=args.num_generations,
            max_new_tokens=args.max_new_tokens,
            base_model=args.base_model,
        )

    if not args.skip_gpt4o:
        generate_with_gpt4o(
            prompts=prompts,
            games=games,
            output_dir=output_dir,
            num_generations=args.num_generations,
        )

    print(f"\n{'='*60}")
    print(f"Done! Files saved to: {output_dir}")
    print(f"Run evaluation with: python scripts/eval_comparison.py --dir {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
