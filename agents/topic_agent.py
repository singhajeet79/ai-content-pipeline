import json
import re


def clean_json_response(response: str) -> str:
    response = re.sub(r"```json", "", response, flags=re.IGNORECASE)
    response = re.sub(r"```", "", response)
    return response.strip()


def run(config, llm):
    prompt = config.get("prompts", {}).get("topic_prompt")

    # 🔴 HARD VALIDATION (NEW)
    if not prompt or not prompt.strip():
        raise ValueError("topic_prompt is missing or empty in config")

    response = llm.generate(prompt)

    cleaned = clean_json_response(response)

    try:
        return json.loads(cleaned)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{response}")