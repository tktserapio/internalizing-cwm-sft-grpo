import torch
import os
import sys
import argparse
import random
import numpy as np
from pathlib import Path
from datetime import timedelta

from datasets import Dataset
from trl import GRPOConfig, GRPOTrainer
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from peft import LoraConfig, PeftModel, get_peft_model

sys.path.insert(0, str(Path(__file__).parent.parent))
from evaluation.grpo_reward import compute_reward
from config import CURRICULUM, EVAL_GAMES, IMPERFECT_INFO_GAMES, validate_curriculum

parser = argparse.ArgumentParser(description="GRPO Training Script")
parser.add_argument(
    "--resume-from-checkpoint",
    type=str,
    default=None,
    help="Path to checkpoint directory to resume from (e.g., output_dir/checkpoint-100), or 'latest' to auto-detect the latest checkpoint"
)
parser.add_argument(
    "--model-path",
    type=str,
    default=os.path.expanduser("Qwen/Qwen2.5-3B-Instruct"),
    help="Path to the base model"
)
parser.add_argument(
    "--output-dir",
    type=str,
    default=os.path.expanduser("~/scratch/experiments/cwm-sft-grpo"),
    help="Output directory for checkpoints and final model"
)
parser.add_argument(
    "--seed",
    type=int,
    default=42,
    help="Random seed for reproducibility"
)
parser.add_argument(
    "--ddp-timeout",
    type=int,
    default=7200,
    help="DDP/NCCL timeout in seconds (default: 7200 = 2 hours)"
)
parser.add_argument(
    "--reward-timeout",
    type=int,
    default=120,
    help="Per-sample reward computation timeout in seconds (default: 120)"
)
parser.add_argument(
    "--adapter-path",
    type=str,
    default=None,
    help="Path to LoRA adapter to load and merge before GRPO training (e.g., SFT adapter)"
)
parser.add_argument(
    "--no-scenarios",
    action="store_true",
    help="Disable scenario tier in reward (ablation: structural-only reward)"
)
parser.add_argument(
    "--no-curriculum",
    action="store_true",
    help="Disable curriculum (train on all games at once, original behavior)"
)
parser.add_argument(
    "--epochs-per-tier",
    type=int,
    default=2,
    help="Number of training epochs per curriculum tier (default: 2)"
)
parser.add_argument(
    "--start-tier",
    type=int,
    default=1,
    help="Curriculum tier to start from (1-indexed, default: 1). Use to resume curriculum from a specific tier."
)
args = parser.parse_args()

# Set seeds for reproducibility
set_seed(args.seed)

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = args.model_path
output_dir = args.output_dir


def load_prompt(game):
    base = Path(__file__).parent.parent / "data"
    is_imperfect = game in IMPERFECT_INFO_GAMES
    template_name = "imperfect_info.txt" if is_imperfect else "perfect_info.txt"

    with open(base / "prompts" / template_name) as f:
        template = f.read()
    with open(base / "games" / game / "rules.txt") as f:
        rules = f.read()

    return template.format(game_name=game.replace("_", " ").title(), game_desc=rules)


def build_dataset(games, tokenizer):
    """Build a GRPO dataset from a list of game names."""
    items = []
    for game in games:
        prompt = load_prompt(game)
        formatted = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True
        )
        items.append({"prompt": formatted, "game": game})
    return Dataset.from_list(items)


def make_reward_fn(timeout_seconds, use_scenarios):
    """Create reward function with configurable timeout and scenario toggle."""
    def reward_fn(completions, prompts, game, **kwargs):
        rewards = []
        for i, completion in enumerate(completions):
            code = completion
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]

            try:
                reward = compute_reward(code, game[i], num_games=10,
                                        timeout_seconds=timeout_seconds,
                                        use_scenarios=use_scenarios)
            except Exception as e:
                reward = 0.0
                debug_path = f"/tmp/failed_{game[i]}.py"
                with open(debug_path, 'w') as f:
                    f.write(code)

            rewards.append(reward)
            print(f"  {game[i]}: {reward:.3f}")

        return rewards
    return reward_fn


def make_grpo_config(tier_output_dir, run_name, epochs, seed):
    """Create GRPOConfig for a curriculum tier."""
    return GRPOConfig(
        output_dir=tier_output_dir,
        seed=seed,

        learning_rate=2e-5,

        num_train_epochs=epochs,

        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        generation_batch_size=8,
        num_generations=8,

        beta=0.1,
        max_grad_norm=0.1,

        report_to="wandb",
        run_name=run_name,

        save_strategy="steps",
        save_steps=50,
        save_total_limit=5,
        bf16=True,

        optim="adamw_8bit",

        max_prompt_length=4096,
        max_completion_length=4096,

        gradient_checkpointing=True,

        temperature=0.6,

        shuffle_dataset=False,
    )


lora_config = LoraConfig(
    r=16,
    lora_alpha=64,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)


def load_base_model(model_path, adapter_path=None):
    """Load base model, optionally merging an adapter."""
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2"
    )

    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)
        model = model.merge_and_unload()

    return model.to(device)


# ── Main ─────────────────────────────────────────────────────────────────

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

reward_fn = make_reward_fn(args.reward_timeout, use_scenarios=not args.no_scenarios)

if args.no_curriculum:
    all_games = [g for tier in CURRICULUM for g in tier]
    dataset = build_dataset(all_games, tokenizer)

    model = load_base_model(model_path, args.adapter_path)
    config = make_grpo_config(output_dir, "cwm-grpo", epochs=3, seed=args.seed)

    resume_from_checkpoint = args.resume_from_checkpoint
    if resume_from_checkpoint == "latest":
        checkpoint_dirs = [d for d in Path(output_dir).glob("checkpoint-*") if d.is_dir()]
        if checkpoint_dirs:
            resume_from_checkpoint = str(max(checkpoint_dirs, key=lambda x: int(x.name.split("-")[1])))
            print(f"Resuming from latest checkpoint: {resume_from_checkpoint}")
        else:
            resume_from_checkpoint = None

    trainer = GRPOTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
        processing_class=tokenizer,
        reward_funcs=reward_fn,
        peft_config=lora_config,
    )

    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    trainer.model.save_pretrained(f"{output_dir}/final_adapter")
    merged_model = trainer.model.merge_and_unload()
    merged_model.save_pretrained(f"{output_dir}/final_merged")
    tokenizer.save_pretrained(f"{output_dir}/final_merged")

else:
    carry_adapter = args.adapter_path

    for tier_idx in range(len(CURRICULUM)):
        tier_num = tier_idx + 1
        if tier_num < args.start_tier:
            tier_adapter = os.path.join(output_dir, f"tier{tier_num}_adapter")
            if os.path.exists(tier_adapter):
                carry_adapter = tier_adapter
            else:
                print(f"\n--- Skipping Tier {tier_num} but adapter not found")
            continue

        cumulative_games = [g for t in CURRICULUM[:tier_num] for g in t]
        tier_games = CURRICULUM[tier_idx]

        dataset = build_dataset(cumulative_games, tokenizer)
        model = load_base_model(model_path, carry_adapter)

        tier_output = os.path.join(output_dir, f"tier{tier_num}")
        config = make_grpo_config(
            tier_output,
            run_name=f"cwm-grpo-tier{tier_num}",
            epochs=args.epochs_per_tier,
            seed=args.seed,
        )

        tier_checkpoint = None
        if args.resume_from_checkpoint == "latest" and tier_num == args.start_tier:
            checkpoint_dirs = [d for d in Path(tier_output).glob("checkpoint-*") if d.is_dir()]
            if checkpoint_dirs:
                tier_checkpoint = str(max(checkpoint_dirs, key=lambda x: int(x.name.split("-")[1])))
                print(f"Resuming tier {tier_num} from checkpoint: {tier_checkpoint}")

        trainer = GRPOTrainer(
            model=model,
            args=config,
            train_dataset=dataset,
            processing_class=tokenizer,
            reward_funcs=reward_fn,
            peft_config=lora_config if tier_checkpoint is None else None,
        )

        trainer.train(resume_from_checkpoint=tier_checkpoint)

        tier_adapter_path = os.path.join(output_dir, f"tier{tier_num}_adapter")
        trainer.model.save_pretrained(tier_adapter_path)
        tokenizer.save_pretrained(tier_adapter_path)
        print(f"Saved tier {tier_num} adapter to {tier_adapter_path}")

        carry_adapter = tier_adapter_path

        del trainer, model
        torch.cuda.empty_cache()

    final_model = load_base_model(model_path, carry_adapter)
    final_model.save_pretrained(f"{output_dir}/final_merged")
    tokenizer.save_pretrained(f"{output_dir}/final_merged")
    print(f"Saved to {output_dir}/final_merged")