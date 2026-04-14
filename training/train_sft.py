import sys
import torch
import os
import json
from pathlib import Path
from datasets import Dataset
from trl import SFTTrainer, SFTConfig
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CURRICULUM, TRAINING_GAMES, validate_curriculum

validate_curriculum()

def load_curriculum_data_ordered(data_path: str) -> list:
    """Load SFT data ordered by curriculum tier (Easy -> Hard)."""
    with open(data_path, 'r') as f:
        all_data = json.load(f)

    by_game = {}
    for entry in all_data:
        game = entry.get('game')
        if game not in by_game:
            by_game[game] = []
        by_game[game].append(entry)

    # Build ordered dataset
    ordered_data = []
    print("\n--- Curriculum Order ---")
    for tier_idx, tier_games in enumerate(CURRICULUM):
        tier_data = []
        for game in tier_games:
            if game in by_game:
                tier_data.extend(by_game[game])
            else:
                print(f"  Warning: {game} not found in dataset")
        ordered_data.extend(tier_data)
        print(f"  Tier {tier_idx + 1}: {len(tier_data)} examples")
    
    print(f"Total ordered examples: {len(ordered_data)}\n")
    return ordered_data

def train_curriculum_simple(
    model_name: str = "Qwen/Qwen2.5-3B-Instruct",
    output_dir: str = "~/scratch/experiments/cwm-sft",
    data_path: str = "~/cwm-sft-grpo/data/sft_train.json",
    num_epochs: int = 3,
    learning_rate: float = 1e-5,
    lora_r: int = 16,
    lora_alpha: int = 32,
    batch_size: int = 1,
    grad_accum: int = 4,
    max_seq_length: int = 6000,
    seed: int = 42,
    resume_from_checkpoint: str = None,
):
    set_seed(seed)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    output_dir = os.path.expanduser(output_dir)
    data_path = os.path.expanduser(data_path)

    print(f"Loading tokenizer from {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    def format_chat(example):
        msgs = example["messages"]
        return {
            "text": tokenizer.apply_chat_template(
                msgs,
                tokenize=False
            )
        }

    ordered_data = load_curriculum_data_ordered(data_path)

    processed_data = [format_chat(ex) for ex in ordered_data]

    dataset = Dataset.from_list(processed_data)

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="auto" 
    )

    lora_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules = [
            "q_proj", "k_proj", "v_proj", "o_proj",
            # "gate_proj", "up_proj", "down_proj", # commented out
        ], 
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    training_args = SFTConfig(
        output_dir=output_dir,
        dataset_text_field="text",
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=learning_rate,
        lr_scheduler_type="cosine",
        num_train_epochs=num_epochs, 
        bf16=True,
        warmup_ratio=0.03,
        logging_steps=10,
        max_length=max_seq_length,
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        report_to="none",
        packing=False, 
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset, 
        args=training_args,
        peft_config=lora_config,
    )
    
    total_examples = len(ordered_data)
    print(f"\nStarting 'Gentle SFT' for {num_epochs} epochs ({total_examples} examples, Curriculum Order: Easy->Hard)...")
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)

    adapter_path = os.path.join(output_dir, "adapter")
    trainer.model.save_pretrained(adapter_path)
    tokenizer.save_pretrained(adapter_path)
    print(f"\nSaved adapter to {adapter_path}")

    return adapter_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen2.5-3B-Instruct")

    parser.add_argument("--output-dir", default="~/scratch/experiments/cwm-sft") 
    parser.add_argument("--data-path", default="~/cwm-sft-grpo/data/sft_train.json")

    parser.add_argument("--epochs", type=int, default=2) 

    parser.add_argument("--lr", type=float, default=1e-5) 
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--max-seq-length", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume-from-checkpoint", type=str, default=None)

    args = parser.parse_args()

    train_curriculum_simple(
        model_name=args.model,
        output_dir=args.output_dir,
        data_path=args.data_path,
        num_epochs=args.epochs,
        learning_rate=args.lr,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        batch_size=args.batch_size,
        grad_accum=args.grad_accum,
        max_seq_length=args.max_seq_length,
        seed=args.seed,
        resume_from_checkpoint=args.resume_from_checkpoint,
    )