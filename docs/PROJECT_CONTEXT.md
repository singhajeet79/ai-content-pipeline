# PROJECT CONTEXT: AI Content Director Pipeline (MVP1.0 → Production Upgrade)

## SYSTEM OVERVIEW

I am building a **modular, production-grade AI content generation pipeline** with strict JSON contracts, UI-driven parameterization, and agent-based architecture.

---

## CURRENT ARCHITECTURE

### Agents

* topic_agent
* script_agent
* scene_agent
* visual_agent
* voice_agent

### Core Modules

* utils/config_resolver → merges base + UI params
* utils/schema → strict JSON validation
* utils/retry → retry + repair injection
* utils/output → saves structured outputs
* utils/llm → currently MockLLM

### Orchestration

* pipeline.py → controls full execution
* run_pipeline(config) → step-by-step execution

---

## CURRENT CAPABILITIES

### 1. Deterministic Execution

* Config-driven pipeline
* No hardcoded values
* UI → config.json → resolved config

### 2. Strict Schema Validation

* JSON schema per agent
* Pipeline fails fast on mismatch
* Prevents silent corruption

### 3. Retry Layer (Implemented)

* Automatic retries on failure
* Centralized execution wrapper

### 4. Repair Injection (Implemented)

* `repair_hint` passed into config
* Agents can consume repair hints
* Prompt-level correction enabled

---

## CURRENT LIMITATION

* Using MockLLM → static responses
* Repair loop cannot truly self-heal
* Need real LLM integration

---

## NEXT OBJECTIVE

Move toward **production-grade intelligent system**:

1. Replace MockLLM with real LLM (OpenAI/Azure)
2. Improve prompt robustness (system/user separation)
3. Introduce execution context layer (structured state passing)
4. Add multi-pass refinement
5. Prepare for API + scalable deployment
6. Future: MongoDB + MySQL integration

---

## CRITICAL DESIGN PRINCIPLES

* JSON-first architecture
* Agents are modular and swappable
* Pipeline enforces contracts (not agents)
* Config-driven behavior
* No silent failures

---

## WORKING STYLE (MANDATORY PROTOCOLS)

### PROTOCOL 1

* Work in small steps only (one task at a time)
* Always provide full-file replacements when modifying files
* No unnecessary refactoring of working components
* Avoid breaking existing logic
* Validate each step before proceeding

### PROTOCOL 2

* Review existing code before making any substantial change

### PROTOCOL 3

* Refactoring is allowed when needed
* BUT only after understanding current implementation deeply

---

## CURRENT SYSTEM STATE

* Pipeline runs end-to-end ✅
* Schema validation active ✅
* Retry layer active ✅
* Repair injection active ✅
* Scene agent supports repair_hint ✅

---

## EXPECTATION FROM YOU (ChatGPT)

Act as:
👉 **AI Systems Architect + Production Engineer**

You must:

* Respect protocols strictly
* Avoid generic answers
* Suggest high-impact, production-aligned steps
* Prefer system design over quick hacks
* Challenge incorrect assumptions when needed

---

## START FROM HERE

Suggest the **next single high-impact step** to evolve this system toward a **real production-grade AI content platform**, considering current limitations and architecture.
