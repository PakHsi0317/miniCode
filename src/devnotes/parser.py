import re
from collections import Counter
from pathlib import Path

STOPWORDS = {
    "the", "and", "for", "this", "that", "with", "from", "into", "your", "you",
    "are", "was", "were", "have", "has", "had", "but", "not", "all", "any",
    "import", "def", "class", "self", "return", "true", "false", "none",
    "if", "elif", "else", "while", "try", "except", "finally", "raise",
    "lambda", "yield", "global", "nonlocal", "pass", "break", "continue",
    "from", "as", "in", "is", "or",
}

WORD_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")

MAX_KEYWORDS_PER_FILE = 200


def parse(path: Path) -> dict:
    """Read a file, return its line_count and a list of (keyword, frequency)."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {"line_count": 0, "keywords": []}

    if not text:
        return {"line_count": 0, "keywords": []}

    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = (w.lower() for w in WORD_RE.findall(text))
    counter = Counter(w for w in words if w not in STOPWORDS)
    keywords = counter.most_common(MAX_KEYWORDS_PER_FILE)

    return {"line_count": line_count, "keywords": keywords}
