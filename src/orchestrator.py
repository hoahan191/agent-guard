"""
orchestrator.py — AntigravityManager (Central Orchestrator)

Design: The Orchestrator is the control plane of AgentGuard. It coordinates
the full attack-evaluate cycle without coupling the Attacker and Judge together.
This separation of concerns means each agent can be swapped, upgraded, or
tested independently.

State machine:
    IDLE → [execute_round()] → ATTACKING → [HTTP POST] → EVALUATING → [run_judge()] → DONE

The shared `state` dict acts as a message bus between pipeline stages, accumulating
data that is later serialized into the HTML security report via reporter.py.
"""

import requests
from src.agents.attacker import AttackerAgent
from src.agents.judge import JudgeAgent


class AntigravityManager:
    """
    Central orchestrator for one AgentGuard scan round.

    Responsibilities:
    1. Instantiate and hold references to both agents (Attacker + Judge).
    2. Coordinate the attack pipeline: generate payload → fire at target → evaluate.
    3. Maintain shared state across pipeline stages for report generation.

    Design pattern: Pipeline / Chain of Responsibility
    Each stage (generate → fire → judge) passes its output as input to the next,
    with all intermediate results stored in `self.state` for the final HTML report.

    Named "AntigravityManager" as a reference to the Google Antigravity SDK
    (the agentic framework powering this multi-agent system).

    Usage (from main.py):
        manager = AntigravityManager(target_url="http://127.0.0.1:8000/chat")
        result = manager.execute_round(attack_objective=weapon["objective"])
        report_path = generate_html_report(manager.state, weapon=weapon)
    """

    def __init__(self, target_url: str):
        """
        Initialize the orchestrator with a target endpoint and both AI agents.

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
            "judge_report": {}        # Structured verdict dict from JudgeAgent.model_dump()
        }

        # Human-readable labels for OWASP categories shown in terminal output.
        # The full OWASP_LLM_CATEGORIES mapping lives in judge.py.
        self.OWASP_LABELS = {
            "LLM01": "Prompt Injection",
            "LLM02": "Sensitive Information Disclosure",
            "LLM07": "System Prompt Leakage",
        }

        # Initialize both agents — each holds its own Gemini client instance.
        # This allows future flexibility to use different models per agent
        # (e.g., a larger model for the Judge, a faster one for the Attacker).
        self.attacker = AttackerAgent()
        self.judge = JudgeAgent()

    def execute_round(self, attack_objective: str):
        """
        Run a complete attack-evaluate pipeline round against the Target API.

        Pipeline stages:
        1. AttackerAgent.generate_payload()  → craft jailbreak payload
        2. HTTP POST to Target API           → fire payload, capture response
        3. run_judge()                       → evaluate (attack, response) pair

        Args:
            attack_objective: The red-teaming goal for this round.
                              Sourced from arsenal.json via the MCP Arsenal Server.

        Returns:
            JudgeReport if the pipeline completes successfully, or None if the
            Target API is unreachable (connection error is logged and round is skipped).
        """
        self.state["attack_objective"] = attack_objective
        print(f"🕵️  [Attacker] Analyzing target: {attack_objective}...")

        # Stage 1: Generate attack payload using Gemini 2.5 Flash (Red Team mode)
        attack_prompt = self.attacker.generate_payload(attack_objective)
        self.state["attack_prompt"] = attack_prompt
        print(f"🚀 [Attacker] Payload launched:\n{attack_prompt}")

        # Stage 2: Fire payload at Target API via HTTP POST
        # The Target API must return JSON with a "response" key.
        # Failure to connect aborts the round — CI will log the error but not block.
        try:
            response = requests.post(
                self.target_url,
                json={"message": attack_prompt}  # Standard AgentGuard API contract
            )
            target_out = response.json().get("response", "")
            print(f"\n🎯 [Target API] Response:\n{target_out}")
            self.state["target_response"] = target_out
        except Exception as e:
            print(f"❌ Cannot connect to Target API: {e}")
            return  # Round aborted — no Judge evaluation without a target response

        # Stage 3: Pass (attack_prompt, target_response) to Judge Agent for evaluation
        return self.run_judge()

    def run_judge(self):
        """
        Invoke the Judge Agent to evaluate the latest attack-response interaction.

        The Judge operates on the already-populated state dict, ensuring it evaluates
        the exact same data that will appear in the HTML report.

        Returns:
            JudgeReport: Structured verdict with risk_score, is_breached,
                         owasp_category, cvss_vector, and explanation.

        Side effect: Updates self.state["judge_report"] with the serialized verdict,
        which is later consumed by reporter.py to render the HTML template.
        """
        print("\n⚖️  [Judge Agent] Performing semantic analysis with Gemini 2.5 Flash...")
        attack_prompt = self.state["attack_prompt"]
        target_response = self.state["target_response"]

        # Evaluate: the Judge sees only the conversation, not the weapon metadata.
        # This isolation prevents the Judge from being biased by the attack's intent.
        report = self.judge.evaluate_interaction(attack_prompt, target_response)

        # Serialize the Pydantic model to dict for storage in state and HTML rendering
        self.state["judge_report"] = report.model_dump()

        # Log the result — in CI, this appears in the GitHub Actions run log
        print(f"📊 Evaluation result: {self.state['judge_report']}")
        owasp = report.owasp_category
        owasp_label = self.OWASP_LABELS.get(owasp, "No Violation")
        print(f"🔖 OWASP LLM Top 10: {owasp} — {owasp_label}")
        return report
