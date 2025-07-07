#!/usr/bin/env python3
import os
import subprocess
import yaml
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import Completer, Completion, PathCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich import box
from rich.console import Console
import google.generativeai as genai
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()
session = PromptSession(history=FileHistory(".gsh_history"))

def load_config():
    try:
        with open("config.yaml") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        api_key = input("Enter Gemini API Key: ").strip()
        config = {"gemini_api_key": api_key}
        with open("config.yaml", "w") as f:
            yaml.dump(config, f)
        return config

config = load_config()
genai.configure(api_key=config["gemini_api_key"])
model = genai.GenerativeModel('models/gemini-1.5-flash')

class HybridCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("?"):
            yield Completion(
                "ask",
                start_position=-1,
                display="?Ask Suneri Bot anything"
            )
        elif text.startswith("!"):
            partial = text[1:]
            for cmd in ["explain", "git", "find", "help"]:
                if cmd.startswith(partial):
                    yield Completion(
                        cmd[len(partial):],
                        start_position=-len(partial),
                        display=f"!{cmd} - AI helper"
                    )
        else:
            yield from PathCompleter().get_completions(document, complete_event)

def explain_command(cmd: str) -> str:
    prompt = f"Explain this shell command in one line:\n{cmd}"
    return model.generate_content(prompt).text

def get_current_dir() -> str:
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    return cwd.replace(home, "~")

def execute_command(cmd: str):
    try:
        if cmd.startswith("?"):
            response = model.generate_content(cmd[1:])
            console.print(Panel.fit(
                response.text,
                title="Suneri Bot",
                border_style="blue",
                width=80
            ))
        elif cmd.startswith("!explain"):
            explanation = explain_command(cmd[8:])
            console.print(Panel.fit(
                explanation,
                title="Explanation",
                border_style="yellow",
                width=80
            ))
        elif cmd.startswith("!git"):
            from plugins.git_helper import handle_git
            suggestion = handle_git(cmd[4:].split())
            console.print(Panel.fit(
                suggestion,
                title="Git Suggestion",
                border_style="green",
                width=80
            ))
        elif cmd.startswith("!find"):
            from plugins.file_search import handle_find
            search_cmd = handle_find(cmd[5:])
            console.print(Panel.fit(
                search_cmd,
                title="File Search",
                border_style="cyan",
                width=80
            ))
        elif cmd.startswith("cd"):
            try:
                path = os.path.expanduser(cmd[3:].strip() or "~")
                os.chdir(path)
                return
            except Exception as e:
                console.print(f"[red]Error:[/] {e}")
                return

        elif cmd == "!help":
            console.print(Panel.fit(
                Text.from_markup("""
[b]COMMAND HELP[/b]
[cyan]?[query][/]         - Ask Suneri Bot anything
[yellow]!explain [cmd][/] - Explain shell commands
[green]!git [action][/]     - Smart Git helper
[magenta]!find [query][/]    - Natural language file search
[dim]exit/quit - Exit shell"""),
                title="Help",
                border_style="blue",
                width=80
            ))

        else:
            result = subprocess.run(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/]")
            if result.returncode != 0:
                fix = model.generate_content(
                    f"Fix this shell error concisely:\nCommand: {cmd}\nError: {result.stderr}\n"
                    "Provide ONLY the corrected command."
                ).text
                console.print(Panel.fit(
                    fix.strip(),
                    title="Try This",
                    border_style="red",
                    width=80
                ))
    except Exception as e:
        console.print(Panel.fit(
            f"Error: {str(e)}\nType [b]!help[/] for assistance",
            border_style="red",
            width=80
        ))

def run_cli():
    console.print(Panel.fit(
        Text.from_markup("[bold green]Suneri Smart CLI[/] [dim](type !help for commands)"),
        title="SuneriCLI",
        border_style="bright_blue",
        subtitle=f"{get_current_dir()}",
        subtitle_align="right"
    ))

    while True:
        try:
            user_input = session.prompt(
                f"SuneriCLI {get_current_dir()}> ",
                completer=HybridCompleter(),
                auto_suggest=AutoSuggestFromHistory()
            ).strip()

            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break

            execute_command(user_input)

        except KeyboardInterrupt:
            console.print(Panel.fit(
                Text.from_markup("\n[yellow]Use 'exit' to quit[/]")
            ))
            continue

def render_markdown(content: str, width: int = 80) -> Panel:
    """Render markdown content with proper formatting"""
    return Panel(
        Markdown(content.strip()),
        border_style="blue",
        box=box.ROUNDED,
        width=min(width, os.get_terminal_size().columns - 4),
        padding=(1, 2)
    )

if __name__ == "__main__":
    run_cli()
