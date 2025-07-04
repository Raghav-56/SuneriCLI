def handle_find(query: str) -> str:
    """Convert natural language to find command"""
    patterns = {
        "python": "-name '*.py'",
        "recent": "-mtime -7",
        "large": "-size +10M",
    }
    terms = []
    for word in query.split():
        if word in patterns:
            terms.append(patterns[word])
        elif word.isnumeric():
            terms.append(f"-size +{word}M")

    return f"find . {' '.join(terms)}" if terms else "find . -name '*.*'"
