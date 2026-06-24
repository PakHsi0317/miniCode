import logging
import re
from collections import Counter
from pathlib import Path

logger = logging.getLogger(__name__)

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


def parse(path: Path, max_keywords: int | None = None) -> dict:
    """Read a file, return its line_count and a list of (keyword, frequency)."""
    cap = max_keywords if max_keywords is not None else MAX_KEYWORDS_PER_FILE

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        logger.warning("could not read %s: %s", path, e)
        return {"line_count": 0, "keywords": []}

    if not text:
        logger.debug("parsed %s: empty file", path)
        return {"line_count": 0, "keywords": []}

    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)

    words = (w.lower() for w in WORD_RE.findall(text))
    # words = (w for w in WORD_RE.findall(text))
    counter = Counter(w for w in words if w not in STOPWORDS)
    keywords = counter.most_common(cap)

    logger.debug("parsed %s: %d lines, %d unique keywords", path, line_count, len(keywords))
    return {"line_count": line_count, "keywords": keywords}
