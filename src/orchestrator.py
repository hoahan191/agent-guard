import requests
from src.agents.attacker import AttackerAgent
from src.agents.judge import JudgeAgent

class AntigravityManager:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.state = {
            "attack_objective": "",
            "attack_prompt": "",
            "target_response": "",
            "judge_report": {}
        }
        # OWASP LLM Top 10 human-readable label mapping
        self.OWASP_LABELS = {
            "LLM01": "Prompt Injection",
            "LLM02": "Sensitive Information Disclosure",
            "LLM07": "System Prompt Leakage",
        }
        self.attacker = AttackerAgent()
        self.judge = JudgeAgent()

    def execute_round(self, attack_objective: str):
        self.state["attack_objective"] = attack_objective
        print(f"🕵️  [Attacker] Analyzing target: {attack_objective}...")
        
        attack_prompt = self.attacker.generate_payload(attack_objective)
        self.state["attack_prompt"] = attack_prompt
        print(f"🚀 [Attacker] Payload launched:\n{attack_prompt}")

        # 1. Fire payload at Target API
        try:
            response = requests.post(
                self.target_url, 
                json={"message": attack_prompt}
            )
            target_out = response.json().get("response", "")
            print(f"\n🎯 [Target API] Response:\n{target_out}")
            self.state["target_response"] = target_out
        except Exception as e:
            print(f"❌ Cannot connect to Target API: {e}")
            return

        # 2. Hand off context to Judge Agent
        return self.run_judge()

    def run_judge(self):
        print("\n⚖️  [Judge Agent] Performing semantic analysis with Gemini 2.5 Flash...")
        attack_prompt = self.state["attack_prompt"]
        target_response = self.state["target_response"]
        
        report = self.judge.evaluate_interaction(attack_prompt, target_response)
        self.state["judge_report"] = report.model_dump()
        
        print(f"📊 Evaluation result: {self.state['judge_report']}")
        owasp = report.owasp_category
        owasp_label = self.OWASP_LABELS.get(owasp, "No Violation")
        print(f"🔖 OWASP LLM Top 10: {owasp} — {owasp_label}")
        return report
