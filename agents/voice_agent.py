# voice_agent.py 

import json
import re


def clean_json_response(response: str) -> str:
    response = re.sub(r"```json", "", response, flags=re.IGNORECASE)
    response = re.sub(r"```", "", response)
    return response.strip()


def normalize_speed(speed: str) -> str:
    if not speed:
        return "medium"

    s = speed.strip().lower()

    mapping = {
        "slow": "slow",
        "very slow": "slow",

        "medium": "medium",
        "moderate": "medium",
        "normal": "medium",

        "fast": "fast",
        "quick": "fast",
        "rapid": "fast"
    }

    return mapping.get(s, "medium")


def run(llm, config):
    # 🔴 USE PROMPT FROM CONFIG (FIX)
    prompt = config.get("prompts", {}).get("voice_prompt")

    if not prompt:
        raise ValueError("voice_prompt missing in config")

    response = llm.generate(prompt)

    cleaned = clean_json_response(response)

    try:
        data = json.loads(cleaned)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{response}")

    # 🔴 NORMALIZATION
    if "speed" in data:
        data["speed"] = normalize_speed(data["speed"])

    return data