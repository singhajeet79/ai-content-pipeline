import json

def run(scenes, character_memory, llm, config):
    visuals = []

    visual_style = config.get("visual_style", "cinematic")

    for scene in scenes:
        prompt = f"""
        Generate visual prompts for this scene.

        Visual Style: {visual_style}

        Scene:
        {scene}

        Character:
        {character_memory}

        Return ONLY valid JSON:
        {{
          "image_prompt": "...",
          "video_prompt": "..."
        }}
        """

        response = llm.generate(prompt)

        try:
            parsed = json.loads(response)
        except Exception:
            raise ValueError(f"Invalid JSON from LLM:\n{response}")

        visuals.append(parsed)

    return visuals