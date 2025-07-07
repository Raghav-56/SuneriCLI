from typing import List
from .gemini_utils import gemini_generate_content


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
        "diff": "git diff --cached",
    }

    if args[0] in simple_commands:
        return simple_commands[args[0]]

    prompt = f"""
    Convert this natural language Git request to a SINGLE executable Git command.
    Return ONLY the command without any explanations or formatting.

    Request: git {' '.join(args)}

    Command: git """

    try:
        full_command = gemini_generate_content(prompt)
        if full_command.startswith("git "):
            return full_command
        return f"git {full_command}"
    except Exception:
        return f"git {' '.join(args)}"
