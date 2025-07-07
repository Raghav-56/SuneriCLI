import google.generativeai as genai
from typing import List
import yaml
import os

def load_gemini_config():
    config_path = os.path.expanduser("config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    genai.configure(api_key=config["gemini_api_key"])
    return genai.GenerativeModel('models/gemini-1.5-flash')

model = load_gemini_config()

def handle_git(args: List[str]) -> str:
    """
    Generate precise Git commands using Gemini AI.
    Returns ONLY the executable Git command without explanations.
    """
    if not args:
        return "git status"

    simple_commands = {
        "status": "git status",
        "log": "git log --oneline -n 10",
        "branch": "git branch -vv",
        "stash": "git stash list",
        "diff": "git diff --cached"
    }

    if args[0] in simple_commands:
        return simple_commands[args[0]]

    prompt = f"""
    Convert this natural language Git request to a SINGLE executable Git command.
    Return ONLY the command without any explanations or formatting.

    Request: git {' '.join(args)}

    Command: git """

    try:
        response = model.generate_content(prompt)
        full_command = response.text.strip()
        if full_command.startswith("git "):
            return full_command
        return f"git {full_command}"
    except Exception:
        return f"git {' '.join(args)}"
