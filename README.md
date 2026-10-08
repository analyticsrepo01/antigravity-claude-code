# 🚀 Antigravity for Claude Code (Gemini BYOK)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-green.svg)](https://claude.com)
[![Gemini BYOK](https://img.shields.io/badge/Gemini-3.8_Flash_%2F_Pro-orange.svg)](https://deepmind.google/technologies/gemini/)

A native **Claude Code Plugin** and **Model Context Protocol (MCP)** server bringing the autonomous software engineering capabilities of **Google Antigravity (`agy`)** into **Claude Code** using your personal **Google Gemini API Key (Bring Your Own Key - BYOK)**.

---

## 💡 Why This Plugin?

Claude Code is exceptional at conversational codebase interaction and targeted modifications. Pairing Claude Code with **Antigravity + Gemini** enables a **dual-model peer collaboration system**:

| Capability | Claude Code Default | With Antigravity Plugin |
| :--- | :--- | :--- |
| **Model Collaboration** | Single Anthropic model | **Dual-model consensus** (Claude Opus 5.5 + Gemini 3.8 Flash/Pro) |
| **Autonomous Turn Execution** | Turn-by-turn interactive prompts | **Deep autonomous software engineering runs** (`agy --effort high`) |
| **Architectural Second Opinions** | Single perspective | Independent review & architectural critiques via `/antigravity-consult` |
| **Automated Diff Audits** | Manual review | Multi-agent security & OWASP audit on active diffs via `/antigravity-review` |
| **Execution Architecture** | Local agent | **Native FastMCP (stdio)** — zero external cloud tunnels or open ports |
| **API Cost** | Anthropic API / Subscription | **BYOK** (Free / low-cost Google AI Studio API for delegated tasks) |

---

## 🏛️ Architecture

For an interactive, explorable SVG diagram with route tracing and theme toggles, see [`docs/claude_antigravity_diagram.html`](docs/claude_antigravity_diagram.html).

```
 ┌─────────────────────────────────────────────────────────────┐
 │                         Claude Code                         │
 │                                                             │
 │  Developer Prompt ──► Claude Opus 5.5 ──► Slash Commands    │
 │                              │              (/antigravity)  │
 └──────────────────────────────┼──────────────────────────────┘
                                │ Local Stdio (JSON-RPC)
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │             Antigravity FastMCP Server (Local)              │
 │                                                             │
 │   • antigravity_task      • antigravity_consult             │
 │   • antigravity_review    • antigravity_status              │
 └──────────────────────────────┬──────────────────────────────┘
                                │ Subprocess Exec
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                Google Antigravity CLI (agy)                 │
 │                                                             │
 │   Local Workspace (Edits/Tests) ◄──► Gemini 3.8 BYOK API    │
 └─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation & Marketplace

### Option 1: Direct Marketplace Install (Instant)

Register this repository directly inside Claude Code:

```bash
# Add marketplace catalog
claude plugin marketplace add analyticsrepo01/antigravity-claude-code

# Install plugin
claude plugin install antigravity@antigravity-marketplace
```

*(Or within an active Claude Code interactive session, run: `/plugin marketplace add analyticsrepo01/antigravity-claude-code` followed by `/plugin install antigravity@antigravity-marketplace`)*.

---

### Option 2: Local Developer Mode

Clone and register the plugin locally:

```bash
git clone https://github.com/analyticsrepo01/antigravity-claude-code.git
cd antigravity-claude-code

# Install dependencies
pip install -e .

# Register with Claude Code
claude mcp add antigravity -- python3 $(pwd)/servers/antigravity_mcp.py
```

---

## 🔑 Configuration (Gemini BYOK)

Set your Google AI Studio API Key in your environment:

```bash
export GEMINI_API_KEY="AIzaSy..."
```

Or create a `.env` file in your workspace:
```bash
GEMINI_API_KEY=AIzaSy...
ANTIGRAVITY_MODEL=gemini-3.8-flash-high
ANTIGRAVITY_EFFORT=high
```

Get a key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## ⚡ Slash Commands & Usage

This plugin registers three dedicated slash commands in Claude Code:

### 1. `/antigravity <task>`
Delegates an autonomous engineering task to Antigravity. It performs code edits, executes bash tests, and returns a structured summary with modified files and git diffs.
```text
/antigravity "Refactor the payment retry logic with exponential backoff and add pytest coverage"
```

### 2. `/antigravity-review [focus]`
Performs a multi-perspective code and security review on your active git diff (`git diff HEAD`).
```text
/antigravity-review security
```

### 3. `/antigravity-consult <question>`
Gets an architectural second opinion from Gemini 3.8 Pro/Flash without modifying any files.
```text
/antigravity-consult "Should we use Redis or SQLite for the task queue in this service?"
```

---

## 🎯 Example Use Cases

### 1. Autonomous Coding Sprints with Dual-Model Synergy
A developer working in Claude Code delegates heavy, multi-file refactoring and automated test execution to Google Antigravity powered by Gemini 3.8 Flash (BYOK).
```text
/antigravity "Refactor our authentication middleware to support asynchronous JWT rotation with Redis caching, and run the test suite to verify zero regressions."
```

### 2. Independent Cross-Model Code & Security Review
Before opening a Pull Request, the developer uses Antigravity to conduct a second-opinion audit on pending git diffs, checking for OWASP vulnerabilities, logic edge cases, and performance regressions.
```text
/antigravity-review "Perform a strict security and concurrency audit on the active git changes."
```

### 3. High-Reasoning Architectural Consultation
The developer queries Gemini 3.8 Pro/Flash for design tradeoffs, algorithmic complexity analysis, and database schema recommendations without touching any local files.
```text
/antigravity-consult "What are the latency, memory, and scalability tradeoffs between using RocksDB vs SQLite for our local caching layer?"
```

### 4. Cost-Effective Test & Fixture Generation
Developers utilize their personal Google AI Studio API key (BYOK) to generate extensive unit test suites and mock fixtures at near-zero cost, offloading repetitive token-heavy tasks while Claude manages high-level architecture.
```text
/antigravity "Generate complete pytest coverage for src/models.py including edge cases for null inputs and serialization failures."
```

---

## 🛠️ MCP Tools Reference

Claude Code can also invoke the underlying MCP tools directly during conversation:

* **`antigravity_task(task, working_dir, model, effort)`**: Runs full autonomous agent turns.
* **`antigravity_consult(question, context_files, model)`**: Pure architectural and algorithmic reasoning.
* **`antigravity_review(diff, focus, model)`**: In-depth logic, OWASP security, and performance analysis.
* **`antigravity_status()`**: Verifies local environment, `agy` binary path, and Gemini key availability.

---

## 🔒 Security & Privacy

* **Local-Only Communication**: Unlike webhook-based integrations that require exposing public HTTPS tunnels, this plugin operates purely through local stdio IPC.
* **Ephemeral Memory Key Injection**: Your `GEMINI_API_KEY` is injected only into the memory of the spawned child process. It is never logged or cached.
* **Automatic Key Redaction**: All outputs, logs, and stderr streams pass through regex filters that automatically mask secret key patterns (`AIza...`, `sk-...`, `Bearer...`).
* **Path Traversal Guards**: Tool executions are strictly sandboxed within the active project directory.

---

## 🧪 Testing

Run the test suite:

```bash
pytest -v
```

---

## 🌐 Submitting to Anthropic Official Community Marketplace

To have this plugin appear by default in Claude Code's global `/plugin discover` tab:

1. Fork [`anthropics/claude-community`](https://github.com/anthropics/claude-community).
2. Add the entry to `marketplace.json`:
   ```json
   {
     "name": "antigravity",
     "description": "Google Antigravity autonomous software engineering and Gemini BYOK integration.",
     "version": "0.1.0",
     "repository": "https://github.com/analyticsrepo01/antigravity-claude-code",
     "author": "analyticsrepo01"
   }
   ```
3. Submit a Pull Request. Once approved, the plugin is universally available across all Claude Code clients.

---

## 📄 License

Licensed under the [Apache 2.0 License](LICENSE).
