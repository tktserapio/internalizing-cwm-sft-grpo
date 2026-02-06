# Internalizing CWM: SFT + GRPO

Training LLMs to internalize code world models for game-playing via supervised fine-tuning (SFT) and Group Relative Policy Optimization (GRPO).

## Structure

- **`data/`** — Game definitions (rules + correct/golden implementations) and SFT dataset generation
  - `games/` — Contains `rules.txt` and `golden.py` for each game
  - `prompts/` — Prompt templates for perfect and imperfect information games
  - `generate_sft_dataset.py` — Generates SFT training data from game definitions
- **`training/`** — Training files
  - `train_sft_curriculum_simple.py` — Curriculum-based SFT (easy to hard games)
  - `train_grpo.py` — GRPO reinforcement learning stage
- **`evaluation/`** — Evaluation and reward computation
- **`config/`** — Game curriculum and training configuration

## Setup

```bash
pip install -r requirements.txt
```
