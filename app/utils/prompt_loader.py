import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_prompt(path: str, **kwargs) -> str:
    prompt_path = BASE_DIR / "prompts" / path

    with open(prompt_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        user_content = data["user"].format(**kwargs)
        system_content = data["system"].format(**kwargs)

    return f"{system_content}\n\n{user_content}"
