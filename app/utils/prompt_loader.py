import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_prompt(path: str, **kwargs) -> str:
    prompt_path = BASE_DIR / "prompts" / path
    data = yaml.safe_load(prompt_path.read_text(encoding="utf-8"))

    system = data.get("system", "")
    user = data.get("user", "").format(**kwargs)

    return f"{system}\n\n{user}"
