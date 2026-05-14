import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import logging
from pathlib import Path
from time import sleep
from typing import Any

from furhat_realtime_api import FurhatClient

from gym_guide.coaching_styles import COACHING_STYLES
from gym_guide.workout import GymProfile, create_workout, parse_minutes, parse_rating, parse_style, parse_yes


def log_session(
    profile: GymProfile,
    style: str,
    pre_motivation: int,
    post_motivation: int,
    usefulness: int,
    comfort: int,
    trust: int,
    style_match: int,
    perceived_style: str,
    completed: bool,
    stop_point: str,
) -> None:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    path = data_dir / "sessions.csv"
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "style": style,
        "pre_motivation": pre_motivation,
        "post_motivation": post_motivation,
        "usefulness": usefulness,
        "comfort": comfort,
        "trust": trust,
        "style_match": style_match,
        "perceived_style": perceived_style,
        "completed": completed,
        "stop_point": stop_point,
        **asdict(profile),
    }
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)


class FurhatGymGuide:
    def __init__(
        self,
        host: str,
        api_key: str | None = None,
        condition: str = "ask",
        motion: bool = False,
        demo_timing: bool = True,
    ) -> None:
        self.furhat = FurhatClient(host, api_key) if api_key else FurhatClient(host)
        self.condition = condition
        self.motion = motion
        self.demo_timing = demo_timing
        self._pep_counters: dict[str, int] = {}

    def _say_rotating_pep(self, style_lines: dict[str, Any], key: str) -> None:
        raw = style_lines.get(key)
        if not isinstance(raw, list) or not raw:
            return
        i = self._pep_counters.get(key, 0) % len(raw)
        self._pep_counters[key] = self._pep_counters.get(key, 0) + 1
        self.say(str(raw[i]))

    @staticmethod
    def _rep_pep_interval(style: str) -> int:
        if style == "energetic":
            return 2
        if style == "supportive":
            return 4
        return 0

    def connect(self) -> None:
        self.furhat.set_logging_level(logging.INFO)
        self.furhat.connect()
        self.furhat.request_voice_config(language="en-US", input_language=True)
        self.furhat.request_listen_config(languages=["en-US"])
        self.calm_face()

    def calm_face(self) -> None:
        self.furhat.request_face_reset()
        self.furhat.request_face_config(face_id=None, visibility=True, microexpressions=False)
        self.furhat.request_attend_location(0.0, 0.0, 1.0)

    def disconnect(self) -> None:
        self.furhat.disconnect()

    def say(self, text: str) -> None:
        self.calm_face()
        self.furhat.request_speak_text(text, wait=True, abort=True)
        self.furhat.request_attend_location(0.0, 0.0, 1.0)

    def gesture(self, name: str, intensity: float = 0.8) -> None:
        if self.motion:
            self.furhat.request_gesture_start(name=name, intensity=intensity, duration=0.6, wait=False)

    def ask(self, text: str, default: str = "") -> str:
        self.say(text)
        self.calm_face()
        response = self.furhat.request_listen_start(
            partial=False,
            concat=True,
            stop_no_speech=True,
            stop_robot_start=True,
            stop_user_end=True,
            no_speech_timeout=8.0,
            end_speech_timeout=1.0,
        )
        self.calm_face()
        return (response or default).strip()

    def choose_style(self) -> str:
        if self.condition in COACHING_STYLES:
            return self.condition
        response = self.ask(
            "For this demo, should I coach in a calm supportive style, or a more energetic style?",
            "supportive",
        )
        return parse_style(response)

    def pause(self, seconds: float) -> None:
        sleep(seconds)

    def cue_exercise(self, exercise, profile: GymProfile) -> None:
        self.say(f"Now we will do {exercise.name}.")
        self.say(exercise.instruction)
        if profile.experience.lower() == "beginner":
            self.say("I will give you extra beginner cues before you start.")
            for cue in exercise.beginner_cues:
                self.say(cue)
        for cue in exercise.safety_cues:
            self.say(cue)

    def guide_cardio(self, exercise, style_lines: dict[str, Any]) -> bool:
        minutes = max(1, exercise.duration_minutes)
        self.say(f"This is a timed exercise. We will do {minutes} minutes.")
        checkpoints = list(range(1, minutes + 1))
        for minute in checkpoints:
            if self.demo_timing:
                self.pause(3)
            else:
                self.pause(60)
            remaining = minutes - minute
            if remaining > 0:
                left_word = "minute" if remaining == 1 else "minutes"
                self.say(
                    f"Status check. You have completed about {minute} minute. {remaining} {left_word} left."
                )
                self.say(str(style_lines["between"]))
                self._say_rotating_pep(style_lines, "cardio_pep")
                response = self.ask("Say continue to keep going, or stop to end this exercise.", "continue")
                if "stop" in response.lower():
                    return False
            else:
                self.say("Time is complete for this exercise.")
        return True

    def guide_strength(self, exercise, style_lines: dict[str, Any], style: str) -> bool:
        rep_every = self._rep_pep_interval(style)
        self.say(f"We will do {exercise.set_count} sets of {exercise.rep_count} reps.")
        for set_number in range(1, exercise.set_count + 1):
            self.say(f"Set {set_number}. Get into position.")
            response = self.ask("Say ready when you are in position, or stop to skip.", "ready")
            if "stop" in response.lower():
                return False
            for rep in range(1, exercise.rep_count + 1):
                self.say(f"{rep}")
                if rep_every and rep % rep_every == 0 and rep < exercise.rep_count:
                    self._say_rotating_pep(style_lines, "rep_pep")
                self.pause(1.2 if not self.demo_timing else 0.35)
            self.say("Set complete. Rest and breathe.")
            self._say_rotating_pep(style_lines, "after_strength_set_pep")
            self.say(str(style_lines["between"]))
            if set_number < exercise.set_count:
                response = self.ask("Say ready for the next set, or stop to end this exercise.", "ready")
                if "stop" in response.lower():
                    return False
        return True

    def guide_hold(self, exercise, style_lines: dict[str, Any], style: str) -> bool:
        seconds = 20 if "20" in exercise.sets else 30
        if self.demo_timing:
            seconds = 6
        for round_number in range(1, exercise.set_count + 1):
            response = self.ask(f"Round {round_number}. Say ready when you are in plank position, or stop to skip.", "ready")
            if "stop" in response.lower():
                return False
            mid_trigger = max(1, seconds // 2)
            mid_done = False
            for remaining in range(seconds, 0, -1):
                if remaining in {seconds, 5, 3, 1}:
                    self.say(f"{remaining}")
                if not mid_done and remaining <= mid_trigger:
                    self._say_rotating_pep(style_lines, "hold_mid_pep")
                    mid_done = True
                self.pause(1)
            self.say("Round complete. Rest.")
            self._say_rotating_pep(style_lines, "after_hold_round_pep")
            self.say(str(style_lines["between"]))
        return True

    def guide_exercise(self, exercise, profile: GymProfile, style_lines: dict[str, Any], style: str) -> bool:
        self.cue_exercise(exercise, profile)
        self._say_rotating_pep(style_lines, "exercise_opening_pep")
        if exercise.kind == "cardio":
            return self.guide_cardio(exercise, style_lines)
        if exercise.kind == "hold":
            return self.guide_hold(exercise, style_lines, style)
        return self.guide_strength(exercise, style_lines, style)

    def run(self) -> None:
        self.calm_face()
        self.gesture("Smile")
        self.say("Hi, I am your gym guide. I can suggest a simple workout and compare how different robot coaching styles feel.")
        if not parse_yes(self.ask("Do you want to start?")):
            self.say("No problem. I will be here when you want a routine.")
            return

        style = self.choose_style()
        style_lines = COACHING_STYLES[style]
        if style_lines.get("intro"):
            self.say(str(style_lines["intro"]))

        pre_motivation = parse_rating(
            self.ask("Before we start, how motivated do you feel from one to five?", "3")
        )

        profile = GymProfile(
            goal=self.ask("What is your main goal today? Weight loss, strength, muscle, endurance, or general fitness?", "general fitness"),
            experience=self.ask("How experienced are you in the gym? Beginner, intermediate, or advanced?", "beginner"),
            minutes=parse_minutes(self.ask("How many minutes do you have for the workout?", "35")),
            focus=self.ask("Do you want full body, upper body, legs, or cardio focus?", "full body"),
            has_pain_or_injury=parse_yes(self.ask("Do you have any pain or injury I should consider?", "no")),
        )

        plan = create_workout(profile)
        self.say(f"Great. I suggest a {plan.title}.")
        self.say(str(style_lines["plan"]))
        self.say(plan.safety_message)
        self.say(plan.warmup)
        for index, exercise in enumerate(plan.exercises, start=1):
            self.say(f"Exercise {index}: {exercise.name}. {exercise.sets}. {exercise.instruction}")

        if not parse_yes(self.ask("Would you like me to guide you through the session now?")):
            self.say("Okay. You now have the plan. Remember to warm up and keep the movements controlled.")
            return

        for exercise in plan.exercises:
            completed_exercise = self.guide_exercise(exercise, profile, style_lines, style)
            if not completed_exercise:
                self.say("Session stopped. Drink some water and take care.")
                post_motivation = parse_rating(
                    self.ask("Before you go, how motivated do you feel now from one to five?", str(pre_motivation))
                )
                log_session(profile, style, pre_motivation, post_motivation, 0, 0, 0, 0, "", False, exercise.name)
                return

        self.say(plan.cooldown)
        self.say(str(style_lines["finish"]))

        post_motivation = parse_rating(
            self.ask("After the session, how motivated do you feel now from one to five?", str(pre_motivation))
        )
        usefulness = parse_rating(
            self.ask("How useful was the workout plan I gave you, from one to five?", "3")
        )
        comfort = parse_rating(
            self.ask("How comfortable did my coaching style feel, from one to five?", "3")
        )
        trust = parse_rating(
            self.ask("How much did you trust my advice during the session, from one to five?", "3")
        )
        style_match = parse_rating(
            self.ask("How well did my coaching style match what you would want from a trainer, from one to five?", "3")
        )
        perceived_style = self.ask(
            "Last question. In your own words, how would you describe the style I used — calm, energetic, or neutral?",
            style,
        )

        log_session(profile, style, pre_motivation, post_motivation, usefulness, comfort, trust, style_match, perceived_style, True, "")
        self.say("Thank you for your answers. You completed a structured session today.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Furhat gym guide over the Realtime API.")
    parser.add_argument("--host", default="127.0.0.1", help="Furhat SDK or robot host")
    parser.add_argument("--api-key", default=None, help="Realtime API key if access control requires authentication")
    parser.add_argument(
        "--condition",
        default="ask",
        choices=["ask", "supportive", "energetic", "neutral"],
        help="Coaching style condition for the HRI study prototype",
    )
    parser.add_argument(
        "--motion",
        action="store_true",
        help="Enable gestures. Disabled by default to reduce virtual face shaking.",
    )
    parser.add_argument(
        "--real-timing",
        action="store_true",
        help="Use real exercise timing. By default, timers are shortened for classroom demos.",
    )
    args = parser.parse_args()

    guide = FurhatGymGuide(
        args.host,
        args.api_key,
        args.condition,
        args.motion,
        not args.real_timing,
    )
    try:
        guide.connect()
        guide.run()
    finally:
        guide.disconnect()


if __name__ == "__main__":
    main()