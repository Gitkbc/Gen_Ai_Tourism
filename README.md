# Travel AI — Multi-Agent Itinerary Orchestration & Multilingual Intelligence System

Travel AI is a structured, multi-agent travel planning backend built using FastAPI and LLM orchestration.

Instead of relying on a single prompt-based workflow, the system decomposes itinerary generation into modular agents responsible for discovery, ranking, clustering, prioritization, culinary intelligence, and final route construction.

In addition, it includes a multilingual place-detail pipeline capable of generating structured narration and synthesized audio artifacts.

The focus of the system is:

- Deterministic structure
- Modular orchestration
- Latency visibility
- Strict JSON enforcement
- Language-aware content generation

---

# 🎥 Demo

👉 **2-Minute System Walkthrough:**
[![Watch the Demo](https://img.youtube.com/vi/TjnphdCaJds/0.jpg)](https://youtu.be/TjnphdCaJds)
---

# 🧠 System Overview

The backend accepts structured travel constraints and produces a fully organized itinerary through coordinated agent execution.

It emphasizes:

- Multi-stage planning instead of single-shot generation
- Deterministic scoring outside the LLM
- Parallel async execution for latency optimization
- Intelligent caching for repeated requests
- Structured schema validation
- Multilingual structured narration

This project explores how LLMs can be embedded inside controlled planning pipelines rather than used as free-form text generators.

---

# 🏗 High-Level Architecture Flow

```
Request
   │
   ├─▶ Parallel Generation Phase
   │   ├─ 1️⃣ Discovery Agent
   │   └─ 2️⃣ Culinary Intelligence Agent
   │
   └─▶ Sequential Planning Phase
       ├─ 3️⃣ Ranking Engine (uses Discovery output)
       ├─ 4️⃣ Clustering Layer
       ├─ 5️⃣ Priority Assignment Agent
       ├─ Transport Estimation
       │
       └─▶ 6️⃣ Final Route Architect (Merges all outputs)
             │
             └─▶ Structured JSON Response
```

---

# 🔎 Core Planning Pipeline

## Parallel Generation Phase

### 1️⃣ Discovery Agent

- Loads verified city dataset
- Augments culturally meaningful places using LLM
- Enforces strict JSON structure
- Normalizes coordinates, ratings, and metadata
- Merges deterministic dataset logic with model augmentation

### 2️⃣ Culinary Intelligence Agent

- Generates culturally contextual food insights
- Executes in parallel with discovery using `asyncio.gather`
- Contributes to final itinerary construction

## Sequential Planning Phase

### 3️⃣ Ranking Engine

- Scores places based on:
  - User interests
  - Ratings
  - Category relevance
- Extracts mandatory must-cover locations
- Keeps scoring logic deterministic and outside the LLM

### 4️⃣ Clustering Layer

- Groups places by geographic proximity
- Minimizes intra-day travel friction
- Produces structured cluster objects for planning

### 5️⃣ Priority Assignment Agent

- Organizes clusters into day-wise themes
- Assigns morning / afternoon / evening flows
- Avoids mixing high-effort outskirts with dense walking zones
- Respects requested number of days

### 6️⃣ Final Route Architect

- Merges:
  - Ranked places
  - Cluster priorities
  - Culinary intelligence
  - Transport estimation
- Produces structured itinerary JSON
- Returns latency and observability metadata

---

# 🌍 Multilingual Place Intelligence & Audio Layer

Beyond itinerary orchestration, the system includes a dedicated multilingual place-detail pipeline.

For each place request, the backend generates:

- English narration (structured and contextual)
- Hindi narration
- Local language narration (region-aware, native script enforced)
- Structured constraints (timings, dress codes, entry rules)
- Cultural cautions and contextual advisories

---

## 📝 Native Script Enforcement

The system verifies that the local-language narration contains valid native script characters (e.g., Devanagari, Tamil, Telugu, Bengali, Kannada, Malayalam, etc.).

If transliteration or incorrect script is detected:

- The narration is automatically regenerated
- Strict prompt conditioning enforces native script output
- JSON schema is preserved

This ensures linguistic integrity rather than superficial translation.

---

## 🔊 Text-to-Speech (TTS) Generation

For English and Hindi narrations:

- Audio files are generated using `gTTS`
- Audio artifacts are stored locally
- File paths and URLs are returned in structured JSON
- Audio generation runs concurrently to reduce latency

This enables both textual and spoken delivery of place-level intelligence.

---

## 🛕 Cultural Context Handling

The pipeline includes deterministic rule-based enhancements such as:

- Religious site constraints (dress codes, silence rules)
- Fort and heritage-specific advisories
- Honorific corrections for historical figures
- Structured caution lists

This ensures culturally grounded output rather than generic descriptions.

---

## 💾 Caching & Validation

Generated place-detail responses are cached, including:

- Multilingual text
- Audio artifacts
- Metadata
- Constraints

Before serving cached responses, the system verifies:

- Audio file existence
- Native script integrity
- Structural completeness

Only validated artifacts are reused.

Full itinerary responses are also cached to reduce repeated LLM calls and improve latency.

---

# ⚙ Performance & Engineering Design

## Async Execution

Discovery and culinary agents execute concurrently using `asyncio.gather` to reduce total response latency.

## Deterministic JSON Enforcement

All LLM responses:

- Are parsed using strict JSON extraction
- Are validated before merging
- Are normalized for frontend stability

This prevents schema drift and unpredictable UI behavior.

## Observability Metadata

Each itinerary response includes:

- Total latency
- Cache hit status
- Cluster count
- Number of discovered places
- SLA-style threshold tracking

This makes the system measurable and debuggable.

---

# 🧩 Architectural Principles

- Separation of reasoning stages
- Deterministic scoring outside LLM
- Controlled schema enforcement
- Modular agent orchestration
- Language-layer abstraction
- Maintainable FastAPI routing structure

---

# 📁 Repository Structure

```
travel_ai/
   ├── services/
   ├── models/
   ├── utils/
   ├── cache/

travel-ai-frontend/
```

Each major folder contains its own README with detailed installation steps.

---

# 🚀 Setup Summary

Detailed setup instructions are available inside respective folders.

---

# 🔮 Future Improvements

- Structured evaluation framework
- Agent extensibility layer
- Streaming itinerary generation
- Enhanced cost-aware optimization
- Expanded multilingual abstraction
- Monitoring dashboard for pipeline observability

---

This project demonstrates a multi-agent LLM workflow combining structured orchestration, deterministic validation, multilingual generation, audio synthesis, and measurable backend architecture.