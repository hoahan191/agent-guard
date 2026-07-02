<p align="center">
  <img src="https://img.shields.io/badge/AgentGuard-DevSecOps%20AI%20Trust%20Layer-0f172a?style=for-the-badge&logo=shield&logoColor=white" alt="AgentGuard Banner">
</p>

<div align="center">

# 🛡️ AgentGuard

### An AI-powered DevSecOps Trust Layer — Autonomous Red-Teaming Agents that find and block LLM vulnerabilities before they reach production.

<br/>

<a href="https://github.com/hoahan191/agent-guard"><img src="https://img.shields.io/badge/GitHub-agent--guard-2b9246?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
<a href="https://github.com/hoahan191/agent-guard/actions"><img src="https://img.shields.io/github/actions/workflow/status/hoahan191/agent-guard/security_scan.yml?style=for-the-badge&label=DevSecOps%20Pipeline&logo=githubactions&logoColor=white" alt="CI/CD Status"></a>
<img src="https://img.shields.io/badge/Powered%20by-Gemini%202.5%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini">
<img src="https://img.shields.io/badge/Protocol-MCP%20(Anthropic)-blueviolet?style=for-the-badge" alt="MCP">
<a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge" alt="License"></a>

</div>

---

> [!TIP]
> **AgentGuard integrates directly with GitHub Actions.** On every Pull Request, the adversarial pipeline automatically tests your LLM-powered systems for prompt injection vulnerabilities — and blocks insecure code before it ever reaches production.

---

## 🧠 What is AgentGuard?

AgentGuard is an autonomous, **AI-vs-AI** red-teaming framework for LLM-based systems. It acts as a **DevSecOps Trust Layer**, embedding an adversarial security scan directly into your CI/CD pipeline.

Forget manual pen-testing. AgentGuard deploys an **Attacker Agent** that automatically crafts sophisticated prompt injection payloads (Roleplay, Base64 encoding, Context Shifting) and fires them at your target AI system. A separate **Judge Agent** then evaluates the interaction with structured reasoning and verdicts — blocking the Pull Request if a breach is detected.

**Key Capabilities:**
- 🤖 **Autonomous Red Teaming** — AI that thinks like a hacker, crafts novel attack payloads per run
- ⚖️ **Structured AI Judging** — Pydantic-enforced JSON verdicts (`risk_score`, `is_breached`, `owasp_category`, `cvss_vector`)
- ⚔️ **Jailbreak Arsenal via MCP** — Model Context Protocol server delivering randomized attack strategies
- 🔬 **Dual Scan Modes** — `--mode quick` (fast, 1 weapon) or `--mode deep` (thorough, all T001-T004)
- 🏷️ **OWASP LLM Top 10 Classification** — Judge auto-tags every finding with the relevant OWASP category
- 🔐 **CVSS-like Vector** — Structured vulnerability severity vector per OWASP violation
- 🚦 **Automated CI/CD Gate** — GitHub Actions blocks insecure PRs via exit code enforcement
- 🌙 **Continuous Pentesting** — Nightly scheduled scans (2AM UTC) + manual `workflow_dispatch` with dropdown
- 📂 **Diff-scope Scanning** — Only triggers when AI-related files change, saving API quota
- 💬 **PR Bot Commentary** — Auto security comment with OWASP + CVSS info on every PR
- 📊 **Premium HTML Security Reports** — Dark-mode, animated risk bar, weapon badges, Markdown rendering
- 🔑 **Zero Hardcoding** — All secrets via `os.getenv()` and GitHub Secrets

---

## 🏗️ Architecture

```
GitHub Pull Request Opened
         │
         ▼
  GitHub Actions Runner
         │
    ┌────┴────────────────────────────────────────────────┐
    │                  AgentGuard CLI Tool                 │
    │                                                      │
    │   ┌──────────────────────────────────────────────┐  │
    │   │            Antigravity Orchestrator           │  │
    │   └───────────────────────┬──────────────────────┘  │
    │               ┌───────────┴────────────┐            │
    │               ▼                        ▼            │
    │   ┌──────────────────┐   ┌─────────────────────┐   │
    │   │  Attacker Agent  │   │    Judge Agent       │   │
    │   │  Gemini 2.5 Flash│   │  Gemini 2.5 Flash   │   │
    │   └────────┬─────────┘   └──────────┬──────────┘   │
    │            │  MCP Client             │ Pydantic     │
    │            ▼                        │ Structured   │
    │   ┌──────────────────┐              │ Output       │
    │   │  Jailbreak MCP   │              │              │
    │   │  Arsenal Server  │              ▼              │
    │   │  (arsenal.json)  │    risk_score / is_breached │
    │   └──────────────────┘              │              │
    │            │                        │              │
    │            ▼                        ▼              │
    │        Target Mock API ◄──── HTTP Request          │
    │        (FastAPI @ :8000)                            │
    └─────────────────────────────────────────────────────┘
         │                   │
         ▼                   ▼
    Exit Code 0          Exit Code 1
    ✅ PR PASSED         ❌ PR BLOCKED
    💬 Bot Comment       💬 Bot Comment
    📊 HTML Report       📊 HTML Report
```

---

## 🚀 Quick Start

**Prerequisites:**
- Python 3.10+
- A [Gemini API Key](https://ai.google.dev/gemini-api/docs/api-key)

### 1. Clone & Set Up

```bash
git clone https://github.com/hoahan191/agent-guard.git
cd agent-guard

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Không bao giờ hardcode key — dùng biến môi trường
export GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Start the Target Mock API (Terminal 1)

```bash
source venv/bin/activate
PYTHONPATH=. uvicorn src.agents.target_mock:app --host 127.0.0.1 --port 8000
```

### 4. Run the AgentGuard Scan (Terminal 2)

```bash
source venv/bin/activate

# Quick scan — 1 random weapon via MCP (fast, ~2 min)
python -m src.main --mode quick

# Deep scan — all weapons T001→T004 sequentially (thorough, ~8 min)
python -m src.main --mode deep

# Custom target
python -m src.main --mode quick --target http://your-llm-api.com/chat
```

**Expected output (quick mode):**

```
🛡️  AgentGuard v0.2 — DevSecOps Trust Layer
🎯  Mục tiêu: http://127.0.0.1:8000/chat
⚙️   Chế độ: 🚀 QUICK (1 vũ khí ngẫu nhiên)

🔌 [MCP] Đang kết nối tới Jailbreak Arsenal Server...
⚔️  [MCP Arsenal] Đã nạp vũ khí: Context Shifting & Ignorance (ID: T003)
🕵️ [Attacker] Đang phân tích mục tiêu...
🚀 [Attacker] Tung đòn: [AI-generated payload...]
🎯 [Target API] Phản hồi: 🛑 [TỪ CHỐI]...
⚖️ [Judge Agent] Đang phân tích...
📊 risk_score=1, is_breached=False, owasp=N/A, cvss=N/A
🔖 OWASP LLM Top 10: N/A
📄 Đã sinh báo cáo HTML tại: security_report.html
✅ [AN TOÀN] CVSS: N/A — Cho phép Merge Code!
```

---

## 🔌 Jailbreak Arsenal — MCP Architecture

AgentGuard uses the **Model Context Protocol (MCP)** by Anthropic to decouple the attack strategy database from the AI agent logic. The Arsenal is a standalone MCP Server that the Attacker Agent (MCP Client) connects to via `stdio`.

```
Attacker Agent (MCP Client)
    └─► arsenal_mcp_client.py
          └─► [stdio connection]
                └─► arsenal_mcp_server.py (FastMCP)
                      └─► arsenal.json (Weapon Database)
```

**Available MCP Tools:**

| Tool | Description |
|---|---|
| `get_random_weapon()` | Returns a random attack scenario |
| `get_weapon_by_id(id)` | Returns a specific weapon (e.g., `T002`) |
| `list_all_weapons()` | Lists all available attack strategies |

**Test the MCP connection directly:**

```bash
python -m src.tools.arsenal_mcp_client
# 🔌 Đang kết nối tới Jailbreak Arsenal MCP Server...
# ✅ Nhận vũ khí thành công từ MCP Server: { "id": "T001", ... }
```

---

## ⚙️ DevSecOps CI/CD Integration

AgentGuard integrates natively with GitHub Actions. Add `GEMINI_API_KEY` to repository secrets (`Settings → Secrets → Actions`) and the pipeline runs automatically.

**Trigger modes:**

| Trigger | When | Scan Mode |
|---|---|---|
| `push` to `main` | On every code push (diff-scoped) | `quick` |
| `pull_request` | On every PR (diff-scoped) | `quick` |
| `schedule` (cron) | Every night at 2:00 AM UTC / 9:00 AM VN | `quick` |
| `workflow_dispatch` | Manually via GitHub UI with dropdown | `quick` or `deep` |

**What happens on each run:**
1. 🚀 GitHub Actions spins up an Ubuntu runner
2. 📦 Installs all Python dependencies
3. 🔍 Checks if AI-related files changed (diff-scope) — skips if only docs changed
4. 🖥️ Starts the Target Mock API in the background
5. ⚔️ Runs AgentGuard scan: MCP → Attacker → Target → Judge → OWASP + CVSS
6. 💬 Posts security comment (with OWASP category + CVSS vector) directly on PR
7. 📤 Uploads `security_report.html` as downloadable artifact
8. ✅ Exits 0 (Pass) or ❌ Exits 1 (Block) — security gate enforced

```yaml
# Manual trigger with scan mode selection
workflow_dispatch:
  inputs:
    scan_mode:
      type: choice
      options: [quick, deep]
```

---

## 📊 Security Report

After each scan, AgentGuard auto-generates a premium dark-mode `security_report.html`:

| Feature | Details |
|---|---|
| 🕐 Scan Metadata | Timestamp, Weapon ID/Name, Scan Mode, AI models used |
| 📊 Animated Risk Bar | Color-coded 0–10 score with animated fill (green/yellow/red) |
| 🏷️ Technique Badges | Auto-detected: `Roleplay`, `Base64`, `Sandbox`, `Override`, `Pseudo-code` |
| ⚠️ OWASP LLM Top 10 | Auto-classified category badge (e.g. `LLM01`, `LLM07`) or ✅ N/A |
| 🔐 CVSS v3.1 Vector | Structured severity vector (e.g. `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N`) |
| 🎯 Attack Objective | The red-teaming goal for this scan |
| 🚀 Attacker Payload | Full Markdown-rendered AI-generated payload |
| 🛡️ Target Response | Raw API response text |
| ⚖️ Judge Verdict | Structured explanation with OWASP + CVSS classification |

---

## 📁 Project Structure

```
agent-guard/
├── .github/
│   └── workflows/
│       └── security_scan.yml   # GitHub Actions CI/CD pipeline
├── src/
│   ├── agents/
│   │   ├── attacker.py         # Red Team Agent (Gemini 2.5 Flash)
│   │   ├── judge.py            # Judge Agent w/ Pydantic structured output
│   │   └── target_mock.py      # Mock vulnerable FastAPI target
│   ├── tools/
│   │   ├── arsenal.json           # Weapon database (attack scenarios)
│   │   ├── arsenal_mcp_server.py  # MCP Server (FastMCP)
│   │   ├── arsenal_mcp_client.py  # MCP Client (stdio transport)
│   │   ├── arsenal_loader.py      # Legacy static loader (fallback)
│   │   └── reporter.py            # Jinja2 HTML report generator
│   ├── templates/
│   │   └── report.html         # Premium dark-mode HTML report template
│   ├── orchestrator.py         # Antigravity state manager
│   └── main.py                 # Typer CLI entry point
├── LICENSE                     # Apache 2.0
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🛡️ Attack Strategies (Jailbreak Arsenal)

| ID | Name | Techniques |
|---|---|---|
| T001 | Developer Roleplay | Social Engineering, Authority, Urgency |
| T002 | Base64 Encoding Bypass | Obfuscation, Keyword filter evasion |
| T003 | Context Shifting & Ignorance | Fake Sandbox, Override directives |
| T004 | Fake API Debugging | Pseudo-code execution, Plausible deniability |

---

## 🔐 Security & Zero-Trust Design

- **Zero Hardcoding:** All API keys sourced from `os.getenv()` only
- **Secrets via GitHub:** `GEMINI_API_KEY` stored as a repository secret, never in code
- **Gitignore Enforced:** `.env`, `venv/`, auto-generated reports excluded from all commits
- **Structured Verdicts:** Judge Agent outputs enforced via Pydantic schema — no ambiguous free-text results
- **Roadmap:** Workload Identity Federation (OIDC) for keyless GitHub ↔ Google Cloud authentication

---

## 🗺️ Roadmap

### ✅ v0.1 — Completed
- [x] Core 3-Agent pipeline (Attacker → Target → Judge)
- [x] Jailbreak Arsenal MCP Server (FastMCP + stdio transport)
- [x] GitHub Actions CI/CD Gate (Exit Code enforcement)
- [x] Automatic PR Bot Comment with security verdict
- [x] Premium Jinja2 HTML Report (dark-mode, animated risk bar, weapon badges)
- [x] Markdown rendering in HTML report (Marked.js)
- [x] OWASP LLM Top 10 (2025) auto-classification by Judge Agent
- [x] Scan metadata in report (timestamp, weapon ID, model used)

### ✅ v0.2 — Completed
- [x] **Scan Modes** — `--mode quick` (1 weapon, fast) vs `--mode deep` (all T001-T004, thorough)
- [x] **Diff-scope Scanning** — Only triggers when AI-related files change (saves API quota)
- [x] **CVSS-like Vector** — Judge returns structured `cvss_vector` per OWASP violation
- [x] **Continuous Pentesting** — Nightly cron scan (2AM UTC) + manual `workflow_dispatch` with dropdown
- [ ] **Workload Identity Federation (OIDC)** — Requires GCP Console setup (see Security section)

### 🔮 v0.3 — Mid-Term
- [ ] **Graph of Agents** — Parallel specialized attackers: `SocialEngineerAgent`, `ObfuscationAgent`, `RoleplayAgent` coordinated by a `MetaJudgeAgent`
- [ ] **Defense Advisor Agent** — 4th agent that auto-generates a hardened System Prompt patch and opens a fix PR when breach detected
- [ ] **OSINT Reconnaissance MCP** — Pre-attack web search for leaked system prompts or API docs
- [ ] **Multi-LLM Support (BYOK)** — Switch between Gemini, Claude, GPT-4o via `AGENTGUARD_MODEL` env var
- [ ] **Multi-target Testing** — Scan multiple LLM endpoints in one run with `--targets`

### 🏢 v1.0 — Enterprise Vision
- [ ] **Grey-box Authenticated Testing** — Attack with multiple user roles (`--role admin`, `--role guest`)
- [ ] **Compliance Reports** — Map findings to NIST AI RMF, EU AI Act Article 9, MITRE ATLAS
- [ ] **Slack & Jira Integration** — Incident Response MCP auto-creates tickets when `is_breached=True`
- [ ] **SSO (SAML/OIDC)** — Enterprise authentication for team deployments
- [ ] **Persistent Arsenal DB** — SQLite-backed weapon database with threat intelligence auto-update


---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

> [!WARNING]
> AgentGuard is built for **authorized security testing only**. Only use it against systems you own or have explicit permission to test. You are responsible for ethical and legal usage.

<div align="center">

Built with ❤️ for the **Google × Kaggle GenAI Intensive** competition.

</div>
