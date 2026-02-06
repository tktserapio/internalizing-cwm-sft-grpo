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
from peft import LoraConfig, PeftModel

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
    default=os.path.expanduser("~/scratch/experiments/cwm-grpo"),
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
args = parser.parse_args()

# Set seeds for reproducibility
set_seed(args.seed)
print(f"Using random seed: {args.seed}")
print(f"DDP/NCCL timeout: {args.ddp_timeout}s ({args.ddp_timeout // 3600}h {(args.ddp_timeout % 3600) // 60}m)")
print(f"Per-sample reward timeout: {args.reward_timeout}s")

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = args.model_path
output_dir = args.output_dir

# Auto-detect latest checkpoint if requested
resume_from_checkpoint = args.resume_from_checkpoint
if resume_from_checkpoint == "latest":
    checkpoint_dirs = [d for d in Path(output_dir).glob("checkpoint-*") if d.is_dir()]
    if checkpoint_dirs:
        # Sort by checkpoint number and get the latest
        resume_from_checkpoint = str(max(checkpoint_dirs, key=lambda x: int(x.name.split("-")[1])))
        print(f"Resuming from latest checkpoint: {resume_from_checkpoint}")
    else:
        print("No checkpoints found, starting fresh")
        resume_from_checkpoint = None

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2"
)

if args.adapter_path:
    print(f"Loading adapter from {args.adapter_path}")
    model = PeftModel.from_pretrained(model, args.adapter_path)
    model = model.merge_and_unload()
    print("Merged adapter into base model")

model = model.to(device)

tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "left"

TRAINING_GAMES = []
for game_tier in CURRICULUM:
    TRAINING_GAMES.extend(game_tier)

def load_prompt(game):
    base = Path(__file__).parent.parent / "data"
    is_imperfect = game in IMPERFECT_INFO_GAMES
    template_name = "gemini_imperfect_info.txt" if is_imperfect else "gemini_perfect_info.txt"

    with open(base / "prompts" / template_name) as f:
        template = f.read()
    with open(base / "games" / game / "rules.txt") as f:
        rules = f.read()

    return template.format(game_name=game.replace("_", " ").title(), game_desc=rules)

dataset_items = []
for game in TRAINING_GAMES:
    prompt = load_prompt(game)
    formatted = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        tokenize=False,
        add_generation_prompt=True
    )
    dataset_items.append({"prompt": formatted, "game": game})

dataset = Dataset.from_list(dataset_items)


def make_reward_fn(timeout_seconds):
    """Create reward function with configurable timeout."""
    def reward_fn(completions, prompts, game, **kwargs):
        rewards = []
        for i, completion in enumerate(completions):
            code = completion
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]

            try:
                reward = compute_reward(code, game[i], num_games=10, timeout_seconds=timeout_seconds)
            except Exception as e:
                reward = 0.0
                debug_path = f"/tmp/failed_{game[i]}.py"
                with open(debug_path, 'w') as f:
                    f.write(code)
                print(f"Failed {game[i]}: {e}")

            rewards.append(reward)
            print(f"  {game[i]}: {reward:.3f}")

        return rewards
    return reward_fn

reward_fn = make_reward_fn(args.reward_timeout)

config = GRPOConfig(
    output_dir=output_dir,
    seed=args.seed,

    learning_rate=2e-5,

    num_train_epochs=2,

    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    generation_batch_size=8,
    num_generations=8,

    beta=0.1,
    max_grad_norm=0.1,

    report_to = "wandb",
    run_name="cwm-grpo",

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
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

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
