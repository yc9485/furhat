"""Gemini-backed copy for the gym guide (optional; used once at guided-session start)."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv

from gym_guide.workout import GymProfile

load_dotenv()

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "gemini-2.0-flash"


def _style_system_instruction(style: str) -> str:
    base = (
        "You are Furhat, a gym guide robot speaking aloud to one user. "
        "Output exactly one or two short sentences, under forty words total. "
        "No lists, no bullet points, no medical diagnosis, no promises of results. "
        "Do not ask questions. Use only plain spoken English."
    )
    if style == "energetic":
        return (
            base
            + " Coaching style: energetic. Be upbeat and push them to give strong effort, "
            "but stay safe and respectful."
        )
    if style == "neutral":
        return base + " Coaching style: neutral. Be concise and instructional, minimal emotional language."
    return (
        base
        + " Coaching style: supportive. Be warm, calm, and encouraging; focus on confidence and showing up."
    )


def session_start_guided_line(
    style: str,
    profile: GymProfile,
    plan_title: str,
    exercise_names: list[str],
) -> str | None:
    """
    One tailored spoken line when the guided session begins (after the user says yes to coaching).

    Returns None if ``GEMINI_API_KEY`` is unset or the model call fails.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.info("session_start_guided_line skipped: GEMINI_API_KEY not set.")
        return None

    model = os.getenv("GEMINI_MODEL", _DEFAULT_MODEL)
    names = ", ".join(exercise_names[:5])
    if len(exercise_names) > 5:
        names += ", and more"

    user_prompt = (
        f"The user said their main goal is: {profile.goal}. "
        f"Experience level: {profile.experience}. "
        f"Session focus: {profile.focus}. "
        f"They have about {profile.minutes} minutes. "
        f"Injury or pain to respect: {'yes' if profile.has_pain_or_injury else 'no'}. "
        f"The workout title is: {plan_title}. "
        f"Exercises they will be guided through include: {names}. "
        "Acknowledge them and this plan in your voice, and set a positive tone for starting the first exercise now."
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=_style_system_instruction(style),
                max_output_tokens=120,
                temperature=0.7,
            ),
        )
    except Exception:
        logger.exception("Gemini session_start_guided_line failed.")
        return None

    text = (response.text or "").strip()
    if not text:
        return None
    # One paragraph for TTS; trim very long outputs
    text = text.split("\n")[0].strip()
    if len(text) > 400:
        text = text[:397] + "..."
    return text