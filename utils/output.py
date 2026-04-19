import os
import json

OUTPUT_DIR = "outputs"

def save_outputs(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Script
    if "script" in data:
        with open(os.path.join(OUTPUT_DIR, "script.txt"), "w", encoding="utf-8") as f:
            f.write(data["script"])

    # Scenes
    if "scenes" in data:
        with open(os.path.join(OUTPUT_DIR, "scenes.json"), "w", encoding="utf-8") as f:
            json.dump(data["scenes"], f, indent=2)

    # Visuals
    if "visuals" in data:
        with open(os.path.join(OUTPUT_DIR, "visuals.json"), "w", encoding="utf-8") as f:
            json.dump(data["visuals"], f, indent=2)

    # Voice
    if "voice" in data:
        with open(os.path.join(OUTPUT_DIR, "voice.json"), "w", encoding="utf-8") as f:
            json.dump(data["voice"], f, indent=2)

    # ✅ NEW: Config snapshot
    if "config" in data:
        with open(os.path.join(OUTPUT_DIR, "config.json"), "w", encoding="utf-8") as f:
            json.dump(data["config"], f, indent=2)