import json
import re


def clean_json_response(text: str) -> str:
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)
    return text.strip()


def extract_json_block(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return text


def normalize_visual_output(data):
    """
    Ensures:
    - Always returns dict with string fields
    - Converts nested JSON → string
    """
    if not isinstance(data, dict):
        raise ValueError("Visual output must be an object")

    img = data.get("image_prompt")
    vid = data.get("video_prompt")

    # Convert nested objects to string
    if isinstance(img, dict):
        img = json.dumps(img)

    if isinstance(vid, dict):
        vid = json.dumps(vid)

    return {
        "image_prompt": str(img),
        "video_prompt": str(vid)
    }


def generate_single_visual(scene, character, llm, config):
    prompt_template = config.get("prompts", {}).get("visual_prompt")

    if not prompt_template:
        raise ValueError("visual_prompt missing in config")

    prompt = f"""
{prompt_template}

Scene:
{scene}

Character:
{character}

Return STRICT JSON ONLY:
{{
  "image_prompt": "string",
  "video_prompt": "string"
}}
"""

    response = llm.generate(prompt)

    cleaned = clean_json_response(response)
    extracted = extract_json_block(cleaned)

    try:
        parsed = json.loads(extracted)
        return normalize_visual_output(parsed)
    except Exception:
        raise ValueError(f"Invalid JSON for scene:\n{response}")


def run(scenes, character, llm, config):
    results = []

    from utils.retry import run_with_retry
    from utils.schema import VISUAL_SCHEMA

    for idx, scene in enumerate(scenes):
        print(f"🎨 Generating visual for scene {idx+1}/{len(scenes)}")

        try:
            visual = run_with_retry(
                generate_single_visual,
                {
                    "type": "object",  # 🔴 validate per scene
                    "properties": {
                        "image_prompt": {"type": "string"},
                        "video_prompt": {"type": "string"}
                    },
                    "required": ["image_prompt", "video_prompt"]
                },
                "visual_agent_scene",
                2,
                1,
                scene,
                character,
                llm,
                config
            )

        except Exception as e:
            print(f"⚠️ Scene {idx+1} failed, using fallback: {e}")

            visual = {
                "image_prompt": "Simple fallback scene",
                "video_prompt": "Static camera shot"
            }

        results.append(visual)

    # 🔴 FINAL SHAPE = ARRAY (schema compliant)
    return results