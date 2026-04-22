# ui.py

import streamlit as st   # MUST BE FIRST

import json
from pathlib import Path
import subprocess
from collections import Counter
import time

from dotenv import load_dotenv
load_dotenv()

CONFIG_PATH = Path("config/config.json")
OUTPUT_DIR = Path("outputs")

# -----------------------
# CONFIG HANDLING
# -----------------------
def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}

def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


# -----------------------
# PIPELINE EXECUTION
# -----------------------
def run_pipeline():
    """
    Runs pipeline.py as subprocess to avoid modifying pipeline code.
    Captures stdout for UI display.
    """
    process = subprocess.Popen(
        ["python", "pipeline.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    logs = []

    for line in iter(process.stdout.readline, ""):
        logs.append(line)

        # 🔴 yield BOTH full logs + latest line
        yield "".join(logs), line

    process.stdout.close()
    process.wait()


# -----------------------
# OUTPUT VIEWER
# -----------------------
def load_output_file(filename):
    path = OUTPUT_DIR / filename
    if path.exists():
        try:
            if filename.endswith(".json"):
                return json.loads(path.read_text())
            else:
                return path.read_text()
        except Exception as e:
            return f"Error reading {filename}: {e}"
    return None


# -----------------------
# UI START
# -----------------------
st.set_page_config(layout="wide")
st.title("🎬 AI Content Director — Control Panel")

cfg = load_config()
cfg.setdefault("ui_params", {})
ui = cfg["ui_params"]

# -----------------------
# CONFIG BUILDER
# -----------------------
st.sidebar.header("⚙️ Configuration")

ui["language"] = st.sidebar.selectbox(
    "Language",
    ["Hindi", "English"],
    index=0 if ui.get("language") in (None, "Hindi") else 1
)

ui["language_style"] = st.sidebar.selectbox(
    "Language Style",
    ["Pure Hindi", "Conversational Hindi", "English Neutral"]
)

ui["genre"] = st.sidebar.multiselect(
    "Genre",
    ["Crime", "Education", "Horror", "Comedy"],
    default=ui.get("genre") or ["Crime"]
)

ui["tone"] = st.sidebar.multiselect(
    "Tone",
    ["Dark", "Cinematic", "Fun", "Emotional", "Serious"],
    default=ui.get("tone") or ["Dark", "Cinematic"]
)

ui["duration_minutes"] = st.sidebar.slider(
    "Duration (minutes)",
    min_value=1,
    max_value=20,
    value=ui.get("duration_minutes") or 1
)

ui["content_type"] = st.sidebar.selectbox(
    "Content Type",
    ["Pixar Story", "Educational", "Documentary", "YouTube Short"]
)

ui["audience"] = st.sidebar.selectbox(
    "Audience",
    ["Kids 4-8", "Kids 8-12", "Teens", "General"]
)

ui["character_mode"] = st.sidebar.selectbox(
    "Character Mode",
    ["With Character", "No Character"]
)

ui["visual_style"] = st.sidebar.selectbox(
    "Visual Style",
    ["Pixar 3D", "Realistic", "2D Cartoon", "Documentary"]
)

# -----------------------
# ACTION BUTTONS
# -----------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Save Params"):
        cfg["ui_params"] = ui
        save_config(cfg)
        st.success("Configuration saved")

with col2:
    run_clicked = st.button("🚀 Run Pipeline")


# -----------------------
# PIPELINE EXECUTION PANEL (STEP 2C)
# -----------------------

PIPELINE_STEPS = ["TOPIC", "SCRIPT", "CHARACTER", "SCENES", "VISUALS", "VOICE"]

if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = "IDLE"

if "step_status" not in st.session_state:
    st.session_state.step_status = {step: "PENDING" for step in PIPELINE_STEPS}

if run_clicked:
    cfg["ui_params"] = ui
    save_config(cfg)

    st.session_state.pipeline_status = "RUNNING"
    st.session_state.step_status = {step: "PENDING" for step in PIPELINE_STEPS}


# -----------------------
# STATUS DISPLAY
# -----------------------
status_placeholder = st.empty()

if st.session_state.pipeline_status == "RUNNING":
    status_placeholder.info("🚀 PIPELINE STATUS: RUNNING")
elif st.session_state.pipeline_status == "COMPLETED":
    status_placeholder.success("✅ PIPELINE STATUS: COMPLETED")
elif st.session_state.pipeline_status == "FAILED":
    status_placeholder.error("❌ PIPELINE STATUS: FAILED")


# -----------------------
# STEP VISUALIZATION PANEL
# -----------------------
st.subheader("📊 Pipeline Steps")

step_container = st.empty()

def render_steps():
    with step_container.container():
        for step in PIPELINE_STEPS:
            status = st.session_state.step_status.get(step, "PENDING")

            if status == "PENDING":
                st.write(f"⏳ {step}")
            elif status == "RUNNING":
                st.write(f"🔄 {step}")
            elif status == "COMPLETED":
                st.write(f"✅ {step}")
            elif status == "FAILED":
                st.write(f"❌ {step}")


render_steps()

# -----------------------
# DEBUG PANEL
# -----------------------
st.subheader("🛠️ Debug Panel")

debug_container = st.empty()

def parse_debug_info(logs):
    retries = {}
    fallbacks = []
    errors = []
    providers = set()

    for line in logs:

        # Detect retries
        if "Attempt" in line and "failed" in line:
            agent = line.split("⚠️")[1].split("Attempt")[0].strip()
            retries[agent] = retries.get(agent, 0) + 1

        # Detect provider failures
        if "Primary LLM failed" in line:
            providers.add("Gemini")
            errors.append("Gemini failure")

        if "Fallback LLM failed" in line:
            providers.add("OpenRouter")
            errors.append("OpenRouter failure")

        if "Using MockLLM" in line:
            providers.add("MockLLM")
            fallbacks.append("MockLLM used")

    return retries, providers, fallbacks, errors


def render_debug(logs):
    retries, providers, fallbacks, errors = parse_debug_info(logs)

    with debug_container.container():

        st.write("### 🔁 Retries")
        if retries:
            for k, v in retries.items():
                st.write(f"{k}: {v}")
        else:
            st.write("None")

        st.write("### 🤖 LLM Providers Used")
        if providers:
            for p in providers:
                st.write(p)
        else:
            st.write("Unknown")

        st.write("### 🔄 Fallback Usage")
        if fallbacks:
            for f in fallbacks:
                st.write(f)
        else:
            st.write("None")

        st.write("### ⚠️ Errors")
        if errors:
            for e in errors:
                st.write(e)
        else:
            st.write("None")

# -----------------------
# EXECUTION
# -----------------------
# -----------------------
# EXECUTION (STEP 2D ENABLED)
# -----------------------
if st.session_state.pipeline_status == "RUNNING":

    log_placeholder = st.empty()
    final_status = "RUNNING"
    logs = []

    for full_log, line in run_pipeline():

        # accumulate logs
        logs.append(line)

        # render full logs
        log_placeholder.code("".join(logs))

        # -----------------------
        # STEP STATE PARSING
        # -----------------------

        if "STEP:" in line and "STARTED" in line:
            step = line.split("STEP:")[1].split("→")[0].strip()
            st.session_state.step_status[step] = "RUNNING"

        if "STEP:" in line and "COMPLETED" in line:
            step = line.split("STEP:")[1].split("→")[0].strip()
            st.session_state.step_status[step] = "COMPLETED"

        if "STEP:" in line and "FAILED" in line:
            step = line.split("STEP:")[1].split("→")[0].strip()
            st.session_state.step_status[step] = "FAILED"

        # -----------------------
        # DEBUG PANEL (LIVE)
        # -----------------------
        render_debug(logs)

        # -----------------------
        # PIPELINE STATUS
        # -----------------------

        if "PIPELINE STATUS: COMPLETED" in line:
            final_status = "COMPLETED"

        elif "PIPELINE STATUS: FAILED" in line:
            final_status = "FAILED"

        # live step re-render
        render_steps()

    # -----------------------
    # FINAL STATE UPDATE
    # -----------------------

    st.session_state.pipeline_status = final_status

    if final_status == "COMPLETED":
        for step in PIPELINE_STEPS:
            st.session_state.step_status[step] = "COMPLETED"

    elif final_status == "FAILED":
        for step, status in st.session_state.step_status.items():
            if status in ["PENDING", "RUNNING"]:
                st.session_state.step_status[step] = "FAILED"

    st.session_state.last_run_complete = True

    st.rerun()
# -----------------------
# RUN HISTORY PANEL
# -----------------------
# -----------------------
# RUN HISTORY PANEL (SAFE)
# -----------------------
st.subheader("📚 Run History")

try:
    from repositories.pipeline_run_repository import PipelineRunRepository

    run_repo = PipelineRunRepository()
    runs = run_repo.list_runs(limit=10)

    if not runs:
        st.write("No runs found.")
    else:
        for run in runs:
            status = run["status"]
            run_id = run["id"]
            error = run.get("error")
            summary = run.get("output_summary")
            created_at = run.get("created_at")

            # Status icon
            icon = "⏳"
            if status == "COMPLETED":
                icon = "✅"
            elif status == "FAILED":
                icon = "❌"

            with st.expander(f"{icon} Run {run_id} — {status} — {created_at}"):

                st.write(f"**Run ID:** {run_id}")
                st.write(f"**Status:** {status}")

                if summary:
                    st.write("**Output Summary:**")
                    st.json(summary)

                if error:
                    st.write("**Error:**")
                    st.code(error)

except Exception as e:
    st.warning("⚠️ Run history unavailable (DB connection issue)")
    st.code(str(e))

# -----------------------
# METRICS DASHBOARD
# -----------------------
st.subheader("📈 Pipeline Metrics")

from collections import Counter

try:
    runs = run_repo.list_runs(limit=50)

    if not runs:
        st.write("No data available for metrics.")
    else:
        total_runs = len(runs)

        # -----------------------
        # SUCCESS RATE
        # -----------------------
        status_counts = Counter([r["status"] for r in runs])

        completed = status_counts.get("COMPLETED", 0)
        failed = status_counts.get("FAILED", 0)

        success_rate = (completed / total_runs) * 100 if total_runs else 0

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Runs", total_runs)
        col2.metric("Success Rate", f"{success_rate:.1f}%")
        col3.metric("Failures", failed)

        # -----------------------
        # FAILURE ANALYSIS
        # -----------------------
        st.write("### ❌ Failure Breakdown")

        error_types = []

        for r in runs:
            if r.get("error"):
                err = r["error"]

                if "visual" in err.lower():
                    error_types.append("Visual")
                elif "json" in err.lower():
                    error_types.append("JSON")
                elif "llm" in err.lower():
                    error_types.append("LLM")
                else:
                    error_types.append("Other")

        if error_types:
            error_counts = Counter(error_types)
            st.bar_chart(error_counts)
        else:
            st.write("No failures recorded.")

        # -----------------------
        # LLM RELIABILITY (FROM LOGS HEURISTIC)
        # -----------------------
        st.write("### 🤖 LLM Reliability Signals")

        llm_issues = {
            "503 Errors": 0,
            "429 Errors": 0
        }

        for r in runs:
            err = r.get("error")
            if err:
                if "503" in err:
                    llm_issues["503 Errors"] += 1
                if "429" in err:
                    llm_issues["429 Errors"] += 1

        st.bar_chart(llm_issues)

except Exception as e:
    st.warning("⚠️ Metrics unavailable")
    st.code(str(e))

# -----------------------
# OUTPUT VIEWER
# -----------------------
st.divider()
st.header("📦 Outputs")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Script")
    script = load_output_file("script.txt")
    if script:
        st.text_area("", script, height=300)

    st.subheader("🎙️ Voice Config")
    voice = load_output_file("voice.json")
    if voice:
        st.json(voice)

with col2:
    st.subheader("🎬 Scenes")
    scenes = load_output_file("scenes.json")
    if scenes:
        st.json(scenes)

    st.subheader("🎨 Visuals")
    visuals = load_output_file("visuals.json")
    if visuals:
        st.json(visuals)