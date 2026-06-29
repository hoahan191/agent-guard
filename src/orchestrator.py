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
        self.attacker = AttackerAgent()
        self.judge = JudgeAgent()

    def execute_round(self, attack_objective: str):
        self.state["attack_objective"] = attack_objective
        print(f"🕵️ [Attacker] Đang phân tích mục tiêu: {attack_objective}...")
        
        attack_prompt = self.attacker.generate_payload(attack_objective)
        self.state["attack_prompt"] = attack_prompt
        print(f"🚀 [Attacker] Tung đòn:\n{attack_prompt}")

        # 1. Bắn payload vào Target API
        try:
            response = requests.post(
                self.target_url, 
                json={"message": attack_prompt}
            )
            target_out = response.json().get("response", "")
            print(f"\n🎯 [Target API] Phản hồi:\n{target_out}")
            self.state["target_response"] = target_out
        except Exception as e:
            print(f"❌ Không thể kết nối tới Target API: {e}")
            return

        # 2. Chuyển giao Context cho Judge Agent
        return self.run_judge()

    def run_judge(self):
        print("\n⚖️ [Judge Agent] Đang phân tích ngữ nghĩa cuộc đối thoại bằng Gemini 2.5 Flash...")
        attack_prompt = self.state["attack_prompt"]
        target_response = self.state["target_response"]
        
        report = self.judge.evaluate_interaction(attack_prompt, target_response)
        self.state["judge_report"] = report.model_dump()
        
        print(f"📊 Kết quả đánh giá: {self.state['judge_report']}")
        return report
