"""Coaching style copy used by the Furhat gym guide."""

from __future__ import annotations

from . import energetic, neutral, supportive

COACHING_STYLES: dict[str, dict[str, str | list[str]]] = {
    "supportive": supportive.LINES,
    "energetic": energetic.LINES,
    "neutral": neutral.LINES,
}

__all__ = ["COACHING_STYLES"]
