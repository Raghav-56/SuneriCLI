import google.generativeai as genai
import yaml
import os
import re

def get_gemini_model():
    config_path = os.path.expanduser("config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    genai.configure(api_key=config["gemini_api_key"])
    return genai.GenerativeModel('models/gemini-1.5-flash')

model = get_gemini_model()

def handle_find(query: str) -> str:
    """
    Generate precise, executable find commands matching the exact request
    Returns sanitized, shell-ready commands
    """
    clean_query = ' '.join(query.strip().split()).lower()

    simple_cases = {
        'count all .txt files': 'find . -type f -name "*.txt" | wc -l',
        'sh files': 'find . -type f -name "*.sh"',
        'python or javascript files': r'find . -type f \( -name "*.py" -o -name "*.js" \)',
    }

    if clean_query in simple_cases:
        return simple_cases[clean_query]

    prompt = f"""
    Generate a SINGLE LINE, executable UNIX find command for:
    "{query}"

    REQUIREMENTS:
    1. Must begin with "find ."
    2. Can include: -name, -type, -size, -o, -a, parentheses
    3. Must work in bash/zsh
    4. Quote filenames/patterns
    5. If counting files, append "| wc -l"
    6. Only add counting (| wc -l) if the user asks for "count"

    ONLY OUTPUT THE COMMAND ITSELF, no explanations.
    Command: find ."""

    try:
        response = model.generate_content(prompt)
        command = response.text.strip()

        command = re.sub(r'^\s*find\s*\.', 'find .', command)
        command = re.sub(r'\s+', ' ', command).split('\n')[0].split('#')[0].strip()

        if not command.startswith('find .'):
            command = f"find . {command}"

        if any(char in command for char in [';', '&&', '||', '`', '$(']):
            raise ValueError("Potential command injection")

        if not command.startswith('find . '):
            raise ValueError("Command must start with 'find .'")

        return command
    except Exception as e:
        print(f"Gemini error: {str(e)}")
        return _basic_find_handler(query)

def _basic_find_handler(query: str) -> str:
    """Fallback handler with basic patterns"""
    patterns = {
        "sh": "-type f -name '*.sh'",
        "shell": "-type f -name '*.sh'",
        "py": "-type f -name '*.py'",
        "python": "-type f -name '*.py'",
        "js": "-type f -name '*.js'",
        "large": "-size +10M",
        "empty": "-empty",
        "dir": "-type d",
        "file": "-type f"
    }

    terms = []
    for word in re.findall(r'[\w\.]+', query.lower()):
        if word in patterns:
            terms.append(patterns[word])
        elif re.match(r'^\..+$', word):  # Handle extensions like .sh
            terms.append(f"-type f -name '*{word}'")
        elif word.isnumeric():
            terms.append(f"-size +{word}M")

    return f"find . {' '.join(terms)}" if terms else "find . -type f"

if __name__ == "__main__":
    test_queries = [
        "!find .sh files",
        "find python files",
        "locate large javascript files",
        "find empty directories"
    ]

    for query in test_queries:
        print(f"Query: {query}")
        cmd = handle_find(query)
        print(f"Command: {cmd}\n")
