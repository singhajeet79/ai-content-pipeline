# 📄 PRD 1.0 — AI Content Pipeline System (UI + Observability Phase)

---

## 1. 📌 Overview

The **AI Content Pipeline System** is a modular, production-oriented platform designed to generate structured multimedia content (scripts, scenes, visuals, voice) using LLMs, with **strict validation, fault tolerance, and full observability via UI**.

This PRD (v1.0) documents the system after completion of:

- Pipeline stabilization
- UI control layer
- Observability (debug + step tracking)
- Run history (DB-backed)
- Metrics dashboard

---

## 2. 🎯 Objectives

### Primary Goals

- Enable **deterministic AI content generation**
- Ensure **zero pipeline crashes**
- Provide **real-time visibility into execution**
- Track system performance over time

### Non-Goals (for this phase)

- API-based architecture (planned in v2)
- Multi-user access control
- Advanced analytics (latency, per-agent metrics)

---

## 3. 🏗️ System Architecture

### 3.1 Core Pipeline
Topic → Script → Character → Scenes → Visuals → Voice

Each stage:
- Uses LLM
- Validates output via schema
- Retries on failure
- Falls back if needed

---

### 3.2 Modules

#### Agents
- `topic_agent`
- `script_agent`
- `scene_agent`
- `visual_agent`
- `voice_agent`

#### Utilities
- `config_resolver` → merges base + UI config
- `schema` → strict JSON validation
- `retry` → exponential retry + backoff
- `llm` → multi-provider abstraction
- `output` → structured persistence

#### Data Layer
- MySQL → pipeline run tracking
- MongoDB → content storage (if used)

---

### 3.3 LLM System

| Layer | Provider |
|------|--------|
| Primary | Gemini |
| Fallback | OpenRouter |
| Final | MockLLM |

**Behavior:**
- Automatic fallback on failure
- Graceful degradation
- No pipeline crash

---

## 4. ⚙️ Execution Model

### 4.1 Pipeline Behavior

- Sequential execution
- Each step:
  - validated
  - retried
  - logged
- Failures:
  - isolated (per scene in visuals)
  - recorded in DB

---

### 4.2 Retry System

- Exponential backoff
- Error-aware delay scaling
- Max retry limit enforced

---

### 4.3 Schema Enforcement

Strict validation per agent:

| Agent | Schema Type |
|------|------------|
| Topic | Array |
| Script | String |
| Character | Object |
| Scenes | Array |
| Visuals | Array |
| Voice | Object |

Invalid outputs → retry → fail if unresolved

---

## 5. 🖥️ UI SYSTEM (STREAMLIT)

### 5.1 Config Builder

User-controlled parameters:

- Language
- Genre
- Tone
- Duration
- Audience
- Visual Style
- Character Mode

Saved to `config.json`

---

### 5.2 Pipeline Control

- Run pipeline from UI
- Status tracking:
  - IDLE
  - RUNNING
  - COMPLETED
  - FAILED

---

### 5.3 Step Visualization

Real-time step tracking:


Each step shows:
- ⏳ Pending
- 🔄 Running
- ✅ Completed
- ❌ Failed

---

### 5.4 Live Log Streaming

- Subprocess-based execution
- Real-time log streaming
- Full log accumulation

---

### 5.5 Debug Panel (Observability Layer)

Displays:

- Retry counts per agent
- LLM providers used
- Fallback usage
- Error signals (503, 429, etc.)

---

### 5.6 Run History (MySQL-backed)

Tracks:

- Run ID
- Status
- Timestamp
- Output summary
- Errors

UI Features:
- Expandable run details
- Error inspection

---

### 5.7 Metrics Dashboard (System Intelligence)

#### KPIs
- Total runs
- Success rate
- Failure count
- System health

#### Analytics
- Failure breakdown:
  - Visual
  - JSON
  - LLM
  - Other
- LLM reliability:
  - 503 (overload)
  - 429 (rate limit)
- Trend graph:
  - Success vs failure over time

---

### 5.8 Output Viewer

Displays generated outputs:

- Script (text)
- Scenes (JSON)
- Visual prompts (JSON)
- Voice config (JSON)

---

## 6. 🧠 System Capabilities

### 6.1 Resilience

- Multi-LLM fallback
- Retry with backoff
- Scene-level isolation (visual agent)

---

### 6.2 Determinism

- Strict schema validation
- Config-driven execution
- Controlled output format

---

### 6.3 Observability

- Step-level visibility
- Debug signals
- Historical tracking
- Metrics dashboard

---

### 6.4 Fault Tolerance

- No pipeline crash on LLM failure
- Controlled degradation via MockLLM

---

## 7. 🔐 Configuration Management

- `.env` based DB configuration
- No hardcoded secrets
- Config merged via resolver

---

## 8. 📊 Current Limitations

### 8.1 Architecture

- UI tightly coupled with pipeline
- No API abstraction layer

---

### 8.2 Metrics

- Based on error string heuristics
- No structured logging

---

### 8.3 UI

- Streamlit-based (not production frontend)
- Limited interactivity (no async updates)

---

### 8.4 Data

- No per-agent performance tracking
- No latency metrics

---

## 9. 🚀 Next Phase (v2 Roadmap)

### Step 3 — API Layer
- FastAPI backend
- UI decoupling
- Async execution

### Step 4 — Advanced Observability
- Structured logs
- Per-agent metrics
- Latency tracking

### Step 5 — UI Upgrade
- React frontend
- Real-time streaming
- Advanced charts (Plotly)

---

## 10. 📦 Version Summary

### PRD Version: 1.0

| Feature | Status |
|--------|-------|
| Pipeline Execution | ✅ |
| Retry System | ✅ |
| LLM Fallback | ✅ |
| Schema Validation | ✅ |
| UI Control Panel | ✅ |
| Step Visualization | ✅ |
| Debug Panel | ✅ |
| Run History | ✅ |
| Metrics Dashboard | ✅ |

---

## 11. 🧭 System Positioning

This system is no longer an AI Script Generator, It is now AI Content Production Engine with Observability + Control + Metrics

---

## 12. 🏁 Conclusion

PRD 1.0 represents a **stable, observable, and controllable AI pipeline system** capable of:

- Generating structured content reliably
- Handling LLM instability gracefully
- Providing full execution transparency
- Tracking system performance over time

This forms the foundation for scaling into a **production-grade AI platform**.
