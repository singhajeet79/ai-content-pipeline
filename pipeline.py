import json
from pathlib import Path
from agents import topic_agent, script_agent, scene_agent, visual_agent, voice_agent
from agents.script_agent import extract_character_profile
from utils.llm import get_llm
from utils.output import save_outputs
from utils.config_resolver import resolve_config
from utils.retry import run_with_retry
from repositories.pipeline_run_repository import PipelineRunRepository
from utils.schema import (
    TOPIC_SCHEMA, SCRIPT_SCHEMA, CHARACTER_SCHEMA,
    SCENE_SCHEMA, VISUAL_SCHEMA, VOICE_SCHEMA
)

BASE_DIR = Path(__file__).resolve().parent


# -----------------------
# CONFIG
# -----------------------
def load_config():
    path = BASE_DIR / "config" / "config.json"
    if not path.exists():
        raise FileNotFoundError(f"Config missing at {path}")
    with open(path, "r") as f:
        return json.load(f)


# -----------------------
# EXECUTION CONTRACT
# -----------------------
def validate_required_output(step_name, output):
    """
    Enforces that required steps must return valid, non-empty output.
    """
    if output is None:
        raise Exception(f"{step_name} returned None")

    if isinstance(output, list) and len(output) == 0:
        raise Exception(f"{step_name} returned empty list")

    if isinstance(output, dict) and len(output) == 0:
        raise Exception(f"{step_name} returned empty dict")

    return output


def execute_step(step_name, fn, schema, agent_name, retries, delay, *args):
    """
    Wrapper for step execution with:
    - retry
    - validation
    - clean logging
    """
    print(f"\n🔹 STEP: {step_name} → STARTED")

    result = run_with_retry(fn, schema, agent_name, retries, delay, *args)

    # enforce required output
    result = validate_required_output(step_name, result)

    print(f"✅ STEP: {step_name} → COMPLETED")

    return result


# -----------------------
# PIPELINE
# -----------------------
def run_pipeline(config):
    llm = get_llm(config)
    run_repo = PipelineRunRepository()

    run_id = run_repo.create_run(config)
    print(f"🆔 Pipeline Run ID: {run_id}")

    try:
        # -----------------------
        # TOPIC (REQUIRED)
        # -----------------------
        user_input = config.get("user_topic_input")

        if user_input and user_input.strip():
            print("\n🔹 STEP: TOPIC → SKIPPED (Using User Input)")
            config["topic"] = user_input.strip()
            run_repo.update_status(run_id, "TOPIC_SKIPPED_USER_INPUT")
        else:
            topics = execute_step(
                "TOPIC",
                topic_agent.run,
                TOPIC_SCHEMA,
                "topic_agent",
                2,
                1,
                config,
                llm
            )
            config["topic"] = topics[0]
            run_repo.update_status(run_id, "TOPIC_DONE")

            import time
            time.sleep(1.5)

        # -----------------------
        # SCRIPT (REQUIRED)
        # -----------------------
        script = execute_step(
            "SCRIPT",
            script_agent.run,
            SCRIPT_SCHEMA,
            "script_agent",
            2,
            1,
            config,
            llm
        )

        run_repo.update_status(run_id, "SCRIPT_DONE")

        time.sleep(1.5)

        # -----------------------
        # CHARACTER (REQUIRED)
        # -----------------------
        character = execute_step(
            "CHARACTER",
            extract_character_profile,
            CHARACTER_SCHEMA,
            "character_agent",
            2,
            1,
            script,
            llm
        )

        run_repo.update_status(run_id, "CHARACTER_DONE")

        time.sleep(1.5) 
        
        # -----------------------
        # SCENES (REQUIRED)
        # -----------------------
        scenes = execute_step(
            "SCENES",
            scene_agent.run,
            SCENE_SCHEMA,
            "scene_agent",
            2,
            1,
            script,
            llm,
            config
        )

        run_repo.update_status(run_id, "SCENES_DONE")

        time.sleep(1.5)

        # -----------------------
        # VISUALS (REQUIRED)
        # -----------------------
        visuals = execute_step(
            "VISUALS",
            visual_agent.run,
            VISUAL_SCHEMA,
            "visual_agent",
            2,
            1,
            scenes,
            character,
            llm,
            config
        )

        time.sleep(1.5)

        # -----------------------
        # VOICE (REQUIRED)
        # -----------------------
        voice = execute_step(
            "VOICE",
            voice_agent.run,
            VOICE_SCHEMA,
            "voice_agent",
            2,
            1,
            llm,
            config
        )

        time.sleep(1.5)
        
        # -----------------------
        # SAVE OUTPUTS
        # -----------------------
        save_outputs({
            "script": script,
            "scenes": scenes,
            "visuals": visuals,
            "voice": voice,
            "config": config
        })

        run_repo.update_status(
            run_id,
            "COMPLETED",
            output_summary={"scenes": len(scenes)}
        )

        print("\n🎉 PIPELINE STATUS: COMPLETED")

    except Exception as e:
        run_repo.update_status(run_id, "FAILED", error=str(e))
        print(f"\n❌ PIPELINE STATUS: FAILED → {e}")
        raise


# -----------------------
# ENTRYPOINT
# -----------------------
def main():
    print("🚀 PIPELINE STATUS: RUNNING")
    config = resolve_config(load_config())
    print("\n🔍 DEBUG: CONFIG KEYS →", list(config.keys()))

    if "prompts" not in config:
        print("❌ DEBUG: prompts NOT FOUND in config")
    else:
        print("✅ DEBUG: prompts FOUND")
        print("🔍 DEBUG: topic_prompt length →", len(config["prompts"].get("topic_prompt", "")))
    run_pipeline(config)


if __name__ == "__main__":
    main()