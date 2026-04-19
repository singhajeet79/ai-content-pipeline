# pipeline.py

from agents import topic_agent, script_agent, scene_agent, visual_agent, voice_agent
from agents.script_agent import extract_character_profile

from utils.config_loader import load_config
from utils.llm import MockLLM
from utils.output import save_outputs
from utils.config_resolver import resolve_config
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent

def load_config():
    config_path = BASE_DIR / "config" / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            f"Expected structure: /config/config.json"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("🚀 Pipeline Started")

    raw_config = load_config()
    print("✅ Config Loaded")

    config = resolve_config(raw_config)

    print("\n✅ FINAL RESOLVED CONFIG:\n")
    print(json.dumps(config, indent=2))

    run_pipeline(config)

def run_pipeline(config):
    llm = MockLLM()
    # Topic generation
    print("⚡ Generating Topics...")
    topics = topic_agent.run(config, llm)
    print("📌 Topics:\n", topics)

    selected_topic = topics[0]
    print(f"✅ Auto-selected topic: {selected_topic}")

    # Script generation
    print("🧠 Generating Script...")
    config["topic"] = selected_topic
    script = script_agent.run(config, llm)
    print("✅ Script Generated")

    print("SCRIPT PREVIEW:\n", script[:200])

    # Character extraction
    print("👤 Extracting Character...")
    character_memory = extract_character_profile(script, llm)
    print("✅ Character Extracted:", character_memory)

    # Scene extraction
    print("🎬 Extracting Scenes...")
    scenes = scene_agent.run(script, llm, config)
    print(f"✅ Scenes Generated: {len(scenes)}")

    # Visual generation
    print("🎨 Generating Visual Prompts...")
    visuals = visual_agent.run(scenes, character_memory, llm, config)
    print("✅ Visuals Generated")

    # Voice
    print("🎙️ Generating Voice Config...")
    voice = voice_agent.run(llm)
    print("✅ Voice Generated")

    print("💾 Saving Outputs...")
    save_outputs({
        "script": script,
        "scenes": scenes,
        "visuals": visuals,
        "voice": voice,
        "config": config
    })

    print("🎉 Pipeline Completed Successfully")

