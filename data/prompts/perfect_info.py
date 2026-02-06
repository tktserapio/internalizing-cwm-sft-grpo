from pathlib import Path

_PROMPT_FILE = Path(__file__).parent / "gemini_perfect_info.txt"
USER_PROMPT = _PROMPT_FILE.read_text()
