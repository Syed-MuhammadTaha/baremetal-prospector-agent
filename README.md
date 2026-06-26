# 🤖 Sable Prospector: Baremetal Autonomous SDR

**Sable Prospector** is a production-grade, framework-free Autonomous Sales Development Representative (SDR). Built without heavy abstractions like LangChain or LlamaIndex, this project demonstrates raw agentic loops, strict syntax parsing, tiered corporate memory, and heuristic-driven evaluations.

The agent autonomously researches target companies via the web, scrapes their websites, applies corporate context and stylistic heuristics, and drafts highly personalized cold emails.

## 🏗️ The Intense Prospector Architecture (The 6 Modules)

### 1. Context Engineering & Filter Harness

Protects weak models from "Lost in the Middle" syndrome and context overflow. Features a custom truncation pipe that slices bloated HTML scrapes and dynamically assembles the "Prompt Sandwich" before every loop.

### 2. The Core Agent Harness & State Parser

A raw Python `while` loop implementation of the ReAct (Reasoning and Acting) framework. Features a highly robust Syntax-Directed Parser (`parser.py`) that isolates JSON Action blocks and an Auto-Healing mechanism that catches hallucinated formats and forces the LLM to self-correct.

### 3. The Critic Node (Evaluation Pipeline)

An LLM-as-a-Judge pipeline (`llm_as_judge.py`) that operates as a ruthless VP of Sales. It evaluates the generated cold emails heuristically (checking for brevity, personalization, and lack of buzzwords like "synergy") and outputs strict JSON scorecards to prevent model drift.

### 4. Dual-Tier Memory System

* **Tier 3 (Static Corporate Memory):** A Git-Diff style JSON store (`sable_knowledge.json`) representing the core startup pitch and hard facts (pricing, tech stack). Managed via `long_term_facts.py`.

* **Tier 2 (Semantic Vector DB):** A baremetal vector database powered by Jina Embeddings (`semantic_memory.json` & `vectorstore.py`). Stores and retrieves industry playbooks, case studies, and stylistic heuristics using Cosine Similarity via `semantic_read_write.py`.

### 5. The Action Layer & Tool Registry

A custom `@tool` decorator (`registry.py`) that automatically extracts function docstrings and type hints into JSON schemas. Core tools include:

* `search.py`: Tavily API integration with smart snippet compression.

* `scrape.py`: BeautifulSoup-based web scraper.

* `dossier.py`: Markdown file generation for final emails.

* `hitl.py`: Interactive Human-in-the-Loop escalation.

### 6. Evals & Deployment

A concurrent execution harness (`eval.py`) using `ThreadPoolExecutor` to run the agent against multiple targets simultaneously. Tracks exact inference latency, queue times, and token usage to measure true operational cost.

## 📁 Project Structure

```
baremetal-prospector-agent/
├── .env                        # API keys (OPENAI, TAVILY, JINA, GROQ)
├── pyproject.toml & uv.lock    # Fast dependency management via uv
├── config.py                   # Global configuration loading
├── main.py                     # Streamlit UI entry point for the agent
├── eval.py                     # Concurrent evaluation harness
├── sable_knowledge.json        # Tier 3 Memory (Corporate Identity)
├── semantic_memory.json        # Tier 2 Memory (Vector DB heuristics)
│
├── tools/                      # The Action Layer
│   ├── registry.py             # @tool decorator & schema generation
│   ├── hitl.py                 # ask_human() escalation
│   ├── search.py               # live_web_search()
│   ├── scrape.py               # scrape_website()
│   ├── dossier.py              # save_dossier() 
│   ├── long_term_facts.py      # update_company_knowledge()
│   └── semantic_read_write.py  # save_lesson() & recall_knowledge()
│
└── agent/                      # Core Intelligence & Memory
    ├── engine.py               # Main ReAct loop
    ├── parser.py               # Syntax parsing & error handling
    ├── prompt.py               # System directives & ReAct schema
    ├── context.py              # Dynamic prompt assembly
    ├── memory.py               # Short-term token rolling & summarization
    ├── llm.py                  # API Wrappers (Groq/OpenAI)
    ├── llm_as_judge.py         # Quality evaluation node
    └── vectorstore.py          # Baremetal Jina embedding logic


```

## 🚀 Getting Started

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv), an extremely fast Python package and project manager written in Rust.

```
# 1. Clone the repository
git clone [https://github.com/Syed-MuhammadTaha/baremetal-prospector-agent.git](https://github.com/Syed-MuhammadTaha/baremetal-prospector-agent.git)
cd baremetal-prospector-agent

# 2. Install uv (if you haven't already)
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# 3. Sync dependencies (Automatically creates a .venv and installs requirements)
uv sync


```

### Environment Variables

Create a `.env` file in the root directory and add your API keys:

```
OPENAI_API_KEY=your_openai_or_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
JINA_API_KEY=your_jina_key_here


```

## 💻 Usage

### 1. Streamlit Dashboard (Interactive Agent)

Launch the clean, professional web dashboard to interact with the prospector agent. This UI replaces the raw terminal loop for a better presentation and testing experience.

```
uv run streamlit run main.py


```

### 2. Evaluation Harness

Run the threaded evaluation script to test the agent against a golden dataset of targets. Measures exact API latency and grades the final output using the Critic Node.

```
uv run eval.py


```

## 🧠 Memory Management Guide

**Sable Prospector** uses strict boundaries to prevent "Persona Bleed":

1. **`sable_knowledge.json`:** Edit this file directly to set the initial identity of the agent. The agent will dynamically append "patches" to this file via `long_term_facts.py`.

2. **`semantic_memory.json`:** This file populates automatically when the agent learns new heuristics via `semantic_read_write.py`. If the agent saves a bad habit, simply delete the entry from this JSON file.

## 🛡️ License

Distributed under the MIT License.