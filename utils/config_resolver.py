# config_resolver.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(filename):
    path = PROMPTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Prompt file missing: {path}")

    content = path.read_text().strip()

    if not content:
        raise ValueError(f"Prompt file is empty: {path}")

    return content


def resolve_config(config):
    base = config.get("base_profile", {})
    ui = config.get("ui_params", {})

    resolved = {}

    # -----------------------
    # MERGE BASE + UI
    # -----------------------
    for key in set(base.keys()).union(ui.keys()):
        if ui.get(key) is not None:
            resolved[key] = ui[key]
        else:
            resolved[key] = base.get(key)

    resolved["channel_name"] = config.get("channel_name")
    resolved["limits"] = config.get("limits")

    # -----------------------
    # 🔴 NEW: USER INPUT TOPIC
    # -----------------------
    # This will come from UI later
    resolved["user_topic_input"] = ui.get("user_topic_input")

    # -----------------------
    # 🔴 NEW: LOAD PROMPTS
    # -----------------------
    resolved["prompts"] = {
        "topic_prompt": load_prompt("topic_prompt.txt"),
        "script_prompt": load_prompt("script_prompt.txt"),
        "scene_prompt": load_prompt("scene_extractor_prompt.txt"),
        "visual_prompt": load_prompt("visual_prompt.txt"),
        "voice_prompt": load_prompt("voice_prompt.txt"),
    }

    return resolved