import os
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader

def generate_html_report(state: dict, weapon: dict = None, output_path: str = "security_report.html"):
    """
    Render an HTML report from the AgentGuard state using Jinja2.
    """
    # Absolute path to the templates directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    template_dir = os.path.join(project_root, "src", "templates")
    
    # Set up Jinja2 Environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html")

    # Prepare report metadata
    scan_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    weapon_info = weapon or {"id": "N/A", "name": "Unknown"}

    # Render HTML with state data + metadata
    html_content = template.render(
        attack_objective=state.get("attack_objective", ""),
        attack_prompt=state.get("attack_prompt", ""),
        target_response=state.get("target_response", ""),
        judge_report=state.get("judge_report", {}),
        weapon=weapon_info,
        scan_time=scan_time,
        model_attacker="gemini-2.5-flash-preview-05-20",
        model_judge="gemini-2.5-flash-preview-05-20",
    )
    
    # Write to file
    output_abs_path = os.path.join(project_root, output_path)
    with open(output_abs_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_abs_path
