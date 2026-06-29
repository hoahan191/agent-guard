import os
from jinja2 import Environment, FileSystemLoader

def generate_html_report(state: dict, output_path: str = "security_report.html"):
    """
    Render báo cáo HTML từ state của AgentGuard sử dụng Jinja2.
    """
    # Lấy đường dẫn tuyệt đối đến thư mục templates
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    template_dir = os.path.join(project_root, "src", "templates")
    
    # Thiết lập Jinja2 Environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html")
    
    # Render HTML với dữ liệu từ state
    html_content = template.render(
        attack_objective=state.get("attack_objective", ""),
        attack_prompt=state.get("attack_prompt", ""),
        target_response=state.get("target_response", ""),
        judge_report=state.get("judge_report", {})
    )
    
    # Ghi ra file
    output_abs_path = os.path.join(project_root, output_path)
    with open(output_abs_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_abs_path
