import streamlit as st
import json
from pathlib import Path

CONFIG_PATH = Path("config.json")

def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}

def save_config(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))

st.title("AI Content Director")

cfg = load_config()
cfg.setdefault("ui_params", {})

ui = cfg["ui_params"]

# ---- UI Fields (only ui_params) ----
ui["language"] = st.selectbox(
    "Language",
    ["Hindi", "English"],
    index=0 if ui.get("language") in (None, "Hindi") else 1
)

ui["language_style"] = st.selectbox(
    "Language Style",
    ["Pure Hindi", "Conversational Hindi", "English Neutral"],
    index=0
)

ui["genre"] = st.multiselect(
    "Genre",
    ["Crime", "Education", "Horror", "Comedy"],
    default=ui.get("genre") or ["Crime"]
)

ui["tone"] = st.multiselect(
    "Tone",
    ["Dark", "Cinematic", "Fun", "Emotional", "Serious"],
    default=ui.get("tone") or ["Dark", "Cinematic"]
)

ui["duration_minutes"] = st.slider(
    "Duration (minutes)",
    min_value=1,
    max_value=20,
    value=ui.get("duration_minutes") or 1
)

ui["content_type"] = st.selectbox(
    "Content Type",
    ["Pixar Story", "Educational", "Documentary", "YouTube Short"]
)

ui["audience"] = st.selectbox(
    "Audience",
    ["Kids 4-8", "Kids 8-12", "Teens", "General"]
)

ui["character_mode"] = st.selectbox(
    "Character Mode",
    ["With Character", "No Character"]
)

ui["visual_style"] = st.selectbox(
    "Visual Style",
    ["Pixar 3D", "Realistic", "2D Cartoon", "Documentary"]
)

# ---- Actions ----
col1, col2 = st.columns(2)

with col1:
    if st.button("Save Params"):
        cfg["ui_params"] = ui
        save_config(cfg)
        st.success("ui_params saved to config.json")

with col2:
    if st.button("Run Pipeline"):
        cfg["ui_params"] = ui
        save_config(cfg)
        st.success("Saved. Now run: python pipeline.py")