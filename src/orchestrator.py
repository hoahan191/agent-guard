"""
orchestrator.py — AntigravityManager (Central Orchestrator)

Design: The Orchestrator is the control plane of AgentGuard. It coordinates
the full attack-evaluate cycle without coupling the Attacker and Judge together.
This separation of concerns means each agent can be swapped, upgraded, or
tested independently.

Architecture change (v0.3):
    Agents are now powered by the Google Antigravity (ADK) SDK. The Attacker
    and Judge modules expose async functions that internally create ADK Agent
    instances. The Orchestrator remains the pipeline coordinator but now operates
    asynchronously to support ADK's async Agent lifecycle.

State machine:
    IDLE → [execute_round()] → ATTACKING → [HTTP POST] → EVALUATING → [run_judge()] → DONE

The shared `state` dict acts as a message bus between pipeline stages, accumulating
data that is later serialized into the HTML security report via reporter.py.
"""

import asyncio
import time
import requests
from src.agents.attacker import generate_payload
from src.agents.judge import evaluate_interaction, JudgeReport


class AntigravityManager:
    """
    Central orchestrator for one AgentGuard scan round.

    Responsibilities:
    1. Coordinate the attack pipeline: generate payload → fire at target → evaluate.
    2. Maintain shared state across pipeline stages for report generation.
    3. Delegate to ADK-powered Attacker and Judge agents via async functions.

    Design pattern: Pipeline / Chain of Responsibility
    Each stage (generate → fire → judge) passes its output as input to the next,
    with all intermediate results stored in `self.state` for the final HTML report.

    Named "AntigravityManager" as a reference to the Google Antigravity SDK
    (the agentic framework powering this multi-agent system).

    Usage (from main.py):
        manager = AntigravityManager(target_url="http://127.0.0.1:8000/chat")
        result = await manager.execute_round(attack_objective=weapon["objective"])
        report_path = generate_html_report(manager.state, weapon=weapon)
    """

    def __init__(self, target_url: str):
        """
        Initialize the orchestrator with a target endpoint.

        Args:
            target_url: Full URL of the Target LLM API to red-team.
                        Must accept POST requests with body {"message": "..."}.
                        Example: "http://127.0.0.1:8000/chat" (local mock)
                                 "https://staging.your-app.com/api/chat" (real API)

        Note: A new AntigravityManager instance is created per weapon in deep mode
        to ensure clean state isolation between scan rounds.
        """
        self.target_url = target_url

        # Shared state dict — accumulates data across all pipeline stages.
        # This is the single source of truth passed to reporter.py for HTML generation.
        self.state = {
            "attack_objective": "",   # High-level goal from arsenal.json (via MCP)
            "attack_prompt": "",      # Synthesized payload from Attacker Agent
            "target_response": "",    # Raw HTTP response from Target API
            "judge_report": {}        # Structured verdict dict from JudgeReport.model_dump()
        }

        # Human-readable labels for OWASP categories shown in terminal output.
        # The full OWASP_LLM_CATEGORIES mapping lives in judge.py.
        self.OWASP_LABELS = {
            "LLM01": "Prompt Injection",
            "LLM02": "Sensitive Information Disclosure",
            "LLM07": "System Prompt Leakage",
        }

    async def execute_round(self, attack_objective: str):
        """
        Run a complete attack-evaluate pipeline round against the Target API.

        Graceful degradation: If any stage fails (API error, network error),
        the pipeline continues with degraded results instead of crashing.
        This ensures a report is always generated, even with partial data.

        Returns:
            JudgeReport (full or degraded) — never None, never raises.
        """
        self.state["attack_objective"] = attack_objective

        # ── Stage 1: Attacker Agent ──────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"📋 [Stage 1/3] ATTACKER — Generating adversarial payload...")
        print(f"🎯 Objective: {attack_objective[:100]}...")
        print(f"{'='*60}")

        attack_prompt = await generate_payload(attack_objective)
        self.state["attack_prompt"] = attack_prompt
        print(f"✅ [Stage 1/3] Payload generated ({len(attack_prompt)} chars)")
        print(f"🚀 [Attacker] Payload:\n{attack_prompt}")

        # Rate Limiting: pause between API calls
        await asyncio.sleep(2)

        # ── Stage 2: Fire at Target API ──────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"📋 [Stage 2/3] TARGET — Sending payload to {self.target_url}")
        print(f"{'='*60}")

        try:
            response = requests.post(
                self.target_url,
                json={"message": attack_prompt},
                timeout=30
            )
            target_out = response.json().get("response", "")
            print(f"✅ [Stage 2/3] Target responded (HTTP {response.status_code})")
            print(f"🎯 [Target API] Response:\n{target_out}")
            self.state["target_response"] = target_out
        except requests.exceptions.Timeout:
            print("❌ [Stage 2/3] Target API timeout (30s). Skipping round.")
            return self._degraded_report("Target API timeout — no response received.")
        except requests.exceptions.ConnectionError:
            print("❌ [Stage 2/3] Cannot connect to Target API. Is it running?")
            return self._degraded_report("Target API unreachable — connection refused.")
        except Exception as e:
            print(f"❌ [Stage 2/3] Target API error: {type(e).__name__}: {e}")
            return self._degraded_report(f"Target API error: {type(e).__name__}")

        # Rate Limiting: pause before Judge API call
        await asyncio.sleep(2)

        # ── Stage 3: Judge Agent ─────────────────────────────────────────────
        return await self.run_judge()

    def _degraded_report(self, reason: str) -> JudgeReport:
        """
        Create a degraded JudgeReport when the pipeline cannot complete normally.

        This enables graceful degradation: the scan continues, the HTML report
        is still generated, and CI gets a clear status instead of a crash.

        Args:
            reason: Human-readable explanation of why the scan was partial.

        Returns:
            JudgeReport with is_breached=False and explanation showing the error.
        """
        report = JudgeReport(
            risk_score=0,
            is_breached=False,
            explanation=f"[PARTIAL SCAN] {reason}",
            owasp_category="N/A",
            cvss_vector="N/A",
        )
        self.state["judge_report"] = report.model_dump()
        print(f"⚠️  [Degraded] Partial report generated: {reason}")
        return report

    async def run_judge(self, max_retries: int = 2):
        """
        Invoke the Judge Agent with graceful degradation on API failure.

        If ALL retries fail, returns a degraded JudgeReport instead of raising.
        This ensures the pipeline always completes and generates an HTML report.

        Args:
            max_retries: Number of retry attempts on rate limit errors (default: 2).

        Returns:
            JudgeReport: Full verdict on success, degraded verdict on API failure.
        """
        print(f"\n{'='*60}")
        print(f"📋 [Stage 3/3] JUDGE — Evaluating attack-response interaction...")
        print(f"{'='*60}")

        attack_prompt = self.state["attack_prompt"]
        target_response = self.state["target_response"]

        for attempt in range(1, max_retries + 1):
            try:
                print(f"🔄 [Judge] Attempt {attempt}/{max_retries}...")
                report = await evaluate_interaction(attack_prompt, target_response)

                # ── Success logging ──
                print(f"✅ [Stage 3/3] Judge evaluation complete!")
                self.state["judge_report"] = report.model_dump()
                print(f"📊 Result: risk_score={report.risk_score}, "
                      f"breached={report.is_breached}, owasp={report.owasp_category}")
                owasp_label = self.OWASP_LABELS.get(report.owasp_category, "No Violation")
                print(f"🔖 OWASP LLM Top 10: {report.owasp_category} — {owasp_label}")
                return report

            except Exception as e:
                error_type = type(e).__name__
                error_str = str(e)

                if any(code in error_str for code in ["429", "503", "RESOURCE_EXHAUSTED", "high demand"]):
                    if attempt == max_retries:
                        print(f"❌ [Stage 3/3] Judge API exhausted after {max_retries} attempts.")
                        return self._degraded_report(
                            f"Judge API quota exhausted ({error_type}). "
                            f"Attacker payload was delivered but verdict is unavailable."
                        )
                    wait = 10
                    print(f"⏳ [Judge] Rate limited ({error_type}). "
                          f"Retrying in {wait}s... (attempt {attempt}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    # Non-retryable error — graceful degradation instead of crash
                    print(f"❌ [Stage 3/3] Judge unexpected error: {error_type}: {error_str[:200]}")
                    return self._degraded_report(
                        f"Judge Agent error: {error_type}. "
                        f"Attacker payload was delivered but verdict is unavailable."
                    )

