"""
AI Response Parser for CloudSentinel AI.

Converts free-form LLM output into structured, storable data. Phase 1
stub: bullet/numbered-list extraction with sanity limits. Phase 3 adds
JSON-mode validation against the provider schemas
(roadmap_part3_risk_ai_dashboard.md).
"""

from typing import Any

from app.core.logging import logger

# Sanity limits so a runaway response can't flood the UI.
MAX_ITEMS = 10
MAX_ITEM_LENGTH = 300

_BULLET_PREFIXES = ("-", "*", "•", "–")
_NUMBERED = ("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.")


def parse_recommendations(text: str) -> list[str]:
    """Extract recommendation lines from LLM text.

    Recognizes markdown bullets, dashes, and numbered items; drops empty,
    duplicate, and prose (non-bulleted) lines; enforces the sanity limits.
    Returns at least the trimmed original text as one item when nothing
    structured is found, so callers never get an empty list on non-empty
    input.
    """
    if not text or not text.strip():
        return []

    items: list[str] = []
    seen: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        matched = False
        for prefix in (*_BULLET_PREFIXES, *_NUMBERED):
            if line.startswith(prefix):
                line = line[len(prefix) :].strip()
                matched = True
                break
        if not matched:
            continue  # prose line (summary text, headers): not a recommendation
        if not line or line.casefold() in seen:
            continue
        seen.add(line.casefold())
        items.append(line[:MAX_ITEM_LENGTH])
        if len(items) >= MAX_ITEMS:
            break

    if not items:
        trimmed = text.strip()[:MAX_ITEM_LENGTH]
        items = [trimmed]
        logger.debug("Parser found no structured items; returning raw text")
    return items


def parse_explanation(text: str) -> dict[str, Any]:
    """Split an explanation into summary and recommendation sections.

    Looks for a 'Recommendations:' marker; everything before it is
    summary text. Without a marker, the whole text is the summary.
    """
    text = text or ""
    marker = "recommendations:"
    lowered = text.lower()
    idx = lowered.find(marker)
    if idx == -1:
        return {"summary": text.strip(), "recommendations": parse_recommendations(text)}
    summary = text[:idx].strip()
    rec_text = text[idx + len(marker) :]
    return {"summary": summary, "recommendations": parse_recommendations(rec_text)}


__all__ = ["parse_recommendations", "parse_explanation"]
