import json

def run(script, llm, config):
    max_scenes = config.get("limits", {}).get("max_scenes", 10)

    prompt = f"""
    Break the following script into scenes.

    Maximum scenes: {max_scenes}

    Script:
    {script}

    Return ONLY valid JSON in this format:
    [
      {{"scene": 1, "text": "..." }},
      {{"scene": 2, "text": "..." }}
    ]
    """

    response = llm.generate(prompt)

    try:
        scenes = json.loads(response)
    except Exception:
        raise ValueError(f"Invalid JSON from LLM:\n{response}")

    # Enforce hard limit as safety
    return scenes[:max_scenes]