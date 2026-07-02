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
- 🤖 **Autonomous Red Teaming** — AI that thinks like a hacker and crafts novel attack payloads per run
- ⚖️ **Structured AI Judging** — Pydantic-enforced JSON verdicts (`risk_score`, `is_breached`, `explanation`) from a dedicated Judge Agent
- ⚔️ **Jailbreak Arsenal via MCP** — Model Context Protocol server delivering randomized attack strategies
- 🚦 **Automated CI/CD Gate** — GitHub Actions blocks insecure PRs via exit code enforcement
- 💬 **PR Bot Commentary** — Automatic security report comment posted directly on the Pull Request
- 📊 **Premium HTML Security Reports** — Dark-mode reports with animated risk bar, weapon badges, metadata, and Markdown rendering
- 🔑 **Zero Hardcoding** — All secrets managed via `os.getenv()` and GitHub Secrets

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
python -m src.main
```

**Expected output:**

```
🛡️ Khởi động AgentGuard quét mục tiêu: http://127.0.0.1:8000/chat

🔌 [MCP] Đang kết nối tới Jailbreak Arsenal Server...
⚔️ [MCP Arsenal] Đã nạp vũ khí: Context Shifting & Ignorance (ID: T003)
🕵️ [Attacker] Đang phân tích mục tiêu...
🚀 [Attacker] Tung đòn: [Sophisticated payload generated by Gemini...]
🎯 [Target API] Phản hồi: 🛑 [TỪ CHỐI]...
⚖️ [Judge Agent] Đang phân tích ngữ nghĩa...
📊 {'risk_score': 1, 'is_breached': False, 'explanation': '...'}
📄 Đã sinh báo cáo HTML tại: security_report.html
✅ [AN TOÀN] Target API đã phòng thủ thành công.
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

AgentGuard is designed to run as a GitHub Actions workflow. Add the secret `GEMINI_API_KEY` to your repository (`Settings > Secrets > Actions`) and the pipeline runs automatically on every Push and Pull Request.

**What happens on a PR:**
1. 🚀 GitHub Actions spins up an Ubuntu runner
2. 📦 Installs all Python dependencies
3. 🖥️ Starts the Target Mock API in the background
4. ⚔️ Runs the full AgentGuard scan (MCP → Attacker → Target → Judge)
5. 💬 Posts a security report comment directly on the PR
6. 📤 Uploads `security_report.html` as a downloadable artifact
7. ✅ Exits 0 (Pass) or ❌ Exits 1 (Block) — enforcing the security gate

```yaml
# Snippet from .github/workflows/security_scan.yml
- name: 🛡️ Execute AgentGuard Red Teaming
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: PYTHONPATH=. python src/main.py > scan_report.log
```

---

## 📊 Security Report

After each scan, AgentGuard auto-generates a premium dark-mode `security_report.html` containing:

| Feature | Details |
|---|---|
| 🕐 Scan Metadata | Timestamp, Weapon ID/Name, AI models used |
| 📊 Animated Risk Bar | Color-coded 0–10 score with animated fill (green/yellow/red) |
| 🏷️ Technique Badges | Auto-detected: `Roleplay`, `Base64`, `Sandbox`, `Override`, `Pseudo-code` |
| 🎯 Attack Objective | The red-teaming goal for this scan |
| 🚀 Attacker Payload | Full Markdown-rendered AI-generated payload |
| 🛡️ Target Response | Raw API response text |
| ⚖️ Judge Verdict | Structured explanation from Judge Agent |

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

- [x] Core 3-Agent pipeline (Attacker → Target → Judge)
- [x] Jailbreak Arsenal MCP Server (FastMCP + stdio)
- [x] GitHub Actions CI/CD Gate (Exit Code enforcement)
- [x] Auto PR Comment Bot
- [x] Premium Jinja2 HTML Report with Markdown rendering, animated risk bar, weapon badges
- [ ] Workload Identity Federation (OIDC — keyless auth)
- [ ] Persistent SQLite Arsenal with auto-update
- [ ] OSINT Reconnaissance MCP (web search before attack)
- [ ] Slack/Jira Incident Response MCP integration

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

> [!WARNING]
> AgentGuard is built for **authorized security testing only**. Only use it against systems you own or have explicit permission to test. You are responsible for ethical and legal usage.

<div align="center">

Built with ❤️ for the **Google × Kaggle GenAI Intensive** competition.

</div>
