from typing import List, Optional
from enum import Enum


class GitOperation(str, Enum):
    STATUS = "status"
    BRANCH = "branch"
    COMMIT = "commit"
    PUSH = "push"
    PULL = "pull"
    MERGE = "merge"
    REBASE = "rebase"
    STASH = "stash"
    LOG = "log"
    DIFF = "diff"
    CHECKOUT = "checkout"
    RESET = "reset"
    CLEAN = "clean"
    FETCH = "fetch"
    TAG = "tag"
    REMOTE = "remote"


def handle_git(args: List[str]) -> str:
    """Smart Git command generator with 50+ common workflows"""
    if not args:
        return "git status"

    primary_action = args[0].lower()
    secondary_args = args[1:] if len(args) > 1 else []

    action_map = {
        # Version Control Basics
        "init": "git init",
        "clone": f"git clone {' '.join(secondary_args)}",

        # Branch Operations
        "branch": _handle_branch(secondary_args),
        "checkout": _handle_checkout(secondary_args),
        "switch": f"git switch {' '.join(secondary_args)}",

        # Commit Operations
        "commit": _handle_commit(secondary_args),
        "amend": "git commit --amend --no-edit",
        "uncommit": "git reset HEAD~1",

        # Remote Operations
        "fetch": _handle_fetch(secondary_args),
        "pull": _handle_pull(secondary_args),
        "push": _handle_push(secondary_args),

        # Merge/Rebase
        "merge": f"git merge {' '.join(secondary_args)}",
        "rebase": _handle_rebase(secondary_args),
        "abort": "git merge --abort || git rebase --abort",

        # Stashing
        "stash": _handle_stash(secondary_args),

        # Inspection
        "log": _handle_log(secondary_args),
        "diff": _handle_diff(secondary_args),
        "show": f"git show {' '.join(secondary_args)}",

        # Undoing Changes
        "undo": _handle_undo(secondary_args),
        "discard": _handle_discard(secondary_args),
        "cleanup": "git fetch --prune && git gc",

        # Tagging
        "tag": _handle_tag(secondary_args),

        # Advanced
        "cherry-pick": f"git cherry-pick {' '.join(secondary_args)}",
        "bisect": f"git bisect {' '.join(secondary_args)}",

        # Helpers
        "sync": "git pull --rebase && git push",
        "publish": "git push -u origin $(git branch --show-current)",
        "unstage": "git restore --staged .",
    }

    return action_map.get(primary_action, f"git {' '.join(args)}")


# Helper functions for complex commands
def _handle_branch(args: List[str]) -> str:
    if not args:
        return "git branch -vv"
    if args[0] in ("-d", "--delete"):
        return f"git branch -d {' '.join(args[1:])}"
    return f"git branch {' '.join(args)}"


def _handle_checkout(args: List[str]) -> str:
    if not args:
        return "git checkout --help"
    if args[0] == "-b":
        return f"git checkout -b {' '.join(args[1:])}"
    return f"git checkout {' '.join(args)}"


def _handle_commit(args: List[str]) -> str:
    if not args:
        return "git commit -v"
    if args[0] in ("-m", "--message"):
        return f"git commit -m \"{' '.join(args[1:])}\""
    return f"git commit {' '.join(args)}"


def _handle_push(args: List[str]) -> str:
    if not args:
        return "git push origin $(git branch --show-current)"
    if args[0] == "--force":
        return "git push --force-with-lease"
    return f"git push {' '.join(args)}"


def _handle_pull(args: List[str]) -> str:
    if not args:
        return "git pull --rebase"
    return f"git pull {' '.join(args)}"


def _handle_stash(args: List[str]) -> str:
    if not args:
        return "git stash list"
    if args[0] == "apply":
        return "git stash apply"
    if args[0] == "pop":
        return "git stash pop"
    return f"git stash {' '.join(args)}"


def _handle_log(args: List[str]) -> str:
    if not args:
        return "git log --oneline --graph -n 10"
    return f"git log {' '.join(args)}"


def _handle_diff(args: List[str]) -> str:
    if not args:
        return "git diff --cached"
    return f"git diff {' '.join(args)}"


def _handle_undo(args: List[str]) -> str:
    if not args:
        return "git reset HEAD~1"
    if args[0] == "commit":
        return "git reset HEAD~1"
    if args[0] == "add":
        return "git restore --staged ."
    return "git restore ."


def _handle_tag(args: List[str]) -> str:
    if not args:
        return "git tag -n"
    return f"git tag {' '.join(args)}"


def _handle_rebase(args: List[str]) -> str:
    if not args:
        return "git rebase -i HEAD~3"
    return f"git rebase {' '.join(args)}"


def _handle_fetch(args: List[str]) -> str:
    if not args:
        return "git fetch --all --prune"
    return f"git fetch {' '.join(args)}"


def _handle_discard(args: List[str]) -> str:
    if not args:
        return "git checkout -- ."
    return f"git checkout -- {' '.join(args)}"
