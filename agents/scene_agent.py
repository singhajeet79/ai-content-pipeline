import json

def run(script, llm, config):
    max_scenes = config.get("limits", {}).get("max_scenes", 10)
    repair_hint = config.get("repair_hint", "")

    prompt = f"""
You are a strict JSON generator.

TASK:
Break the following script into scenes.

CONSTRAINTS:
- Maximum scenes: {max_scenes}
- Return ONLY a JSON array
- NO markdown (no ``` or ```json)
- NO explanation or extra text
- Each item MUST be:
  {{
    "scene": <number>,
    "text": "<plain scene description>"
  }}

RULES:
- scene must be sequential starting from 1
- text must be clean (no **, no narrator labels, no timestamps)
- Do NOT rewrite or expand the script
- Do NOT include dialogues formatting
- Do NOT include intro/outro text

STRICT FORMAT EXAMPLE:
[
  {{"scene": 1, "text": "A toy car sits on a shelf looking outside the window."}},
  {{"scene": 2, "text": "A child plays with the toy car imagining a race."}}
]

SCRIPT:
{script}

{"IMPORTANT: Fix previous error: " + repair_hint if repair_hint else ""}
"""

    response = llm.generate(prompt)

    # ---------------------------
    # Robust JSON extraction
    # ---------------------------
    text = response.strip()

    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    text = text.strip()

    try:
        scenes = json.loads(text)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{text}")

    return scenes[:max_scenes]