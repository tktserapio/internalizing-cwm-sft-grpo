# Internalizing CWM: SFT + GRPO

ArXiv: https://arxiv.org/abs/2605.24375

Training LLMs to internalize code world models for game-playing via supervised fine-tuning (SFT) and Group Relative Policy Optimization (GRPO). 

## Structure
- **`config/`** — Game curriculum and training configuration
- **`data/`** — Game definitions (rules + correct/golden implementations) and SFT dataset generation
  - `games/` — Contains `rules.txt` and `golden.py` for each game
  - `prompts/` — Prompt templates for perfect and imperfect information games
  - `generate_sft_dataset.py` — Generates SFT training data from game definitions
  - `generated_samples/` - Contains generated samples from tested LLMs
- **`training/`** — Training files
  - `train_sft_curriculum_simple.py` — Curriculum-based SFT (easy to hard games)
  - `train_grpo.py` — GRPO reinforcement learning stage
- **`evaluation/`** — Evaluation and reward computation

## Setup

```bash
pip install -r requirements.txt
```
