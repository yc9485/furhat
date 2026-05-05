import argparse
import csv
from dataclasses import asdict
from datetime import datetime
import logging
from pathlib import Path
from time import sleep

from furhat_realtime_api import FurhatClient

from gym_guide.workout import GymProfile, create_workout, parse_minutes, parse_rating, parse_style, parse_yes


COACHING_STYLES = {
    "supportive": {
        "intro": "I will use a calm and supportive coaching style.",
        "plan": "I will keep the routine manageable and focus on confidence.",
        "between": "Take your time. Controlled effort is enough.",
        "finish": "You showed up and completed the structure. That matters.",
    },
    "energetic": {
        "intro": "I will use a more energetic coaching style.",
        "plan": "I will keep the routine clear and add a little push.",
        "between": "Good pace. Keep the energy up for this next step.",
        "finish": "Strong finish. You kept moving through the session.",
    },
    "neutral": {
        "intro": "I will use a neutral instruction style.",
        "plan": "I will give concise instructions for each exercise.",
        "between": "Continue when ready.",
        "finish": "The session is complete.",
    },
}


def log_session(
    profile: GymProfile,
    style: str,
    pre_motivation: int,
    post_motivation: int,
    usefulness: bool,
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

    def guide_cardio(self, exercise, style_lines: dict[str, str]) -> bool:
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
                self.say(f"Status check. You have completed about {minute} minute. {remaining} minutes left.")
                if "treadmill" in exercise.name.lower():
                    distance = minute * 0.08
                    self.say(f"At an easy walking pace, that is roughly {distance:.2f} kilometers walked.")
                self.say(style_lines["between"])
                response = self.ask("Say continue to keep going, or stop to end this exercise.", "continue")
                if "stop" in response.lower():
                    return False
            else:
                self.say("Time is complete for this exercise.")
        return True

    def guide_strength(self, exercise, style_lines: dict[str, str]) -> bool:
        self.say(f"We will do {exercise.set_count} sets of {exercise.rep_count} reps.")
        for set_number in range(1, exercise.set_count + 1):
            self.say(f"Set {set_number}. Get into position.")
            response = self.ask("Say ready when you are in position, or stop to skip.", "ready")
            if "stop" in response.lower():
                return False
            for rep in range(1, exercise.rep_count + 1):
                self.say(f"{rep}")
                self.pause(1.2 if not self.demo_timing else 0.35)
            self.say("Set complete. Rest and breathe.")
            self.say(style_lines["between"])
            if set_number < exercise.set_count:
                response = self.ask("Say ready for the next set, or stop to end this exercise.", "ready")
                if "stop" in response.lower():
                    return False
        return True

    def guide_hold(self, exercise, style_lines: dict[str, str]) -> bool:
        seconds = 20 if "20" in exercise.sets else 30
        if self.demo_timing:
            seconds = 6
        for round_number in range(1, exercise.set_count + 1):
            response = self.ask(f"Round {round_number}. Say ready when you are in plank position, or stop to skip.", "ready")
            if "stop" in response.lower():
                return False
            for remaining in range(seconds, 0, -1):
                if remaining in {seconds, 5, 3, 1}:
                    self.say(f"{remaining}")
                self.pause(1)
            self.say("Round complete. Rest.")
            self.say(style_lines["between"])
        return True

    def guide_exercise(self, exercise, profile: GymProfile, style_lines: dict[str, str]) -> bool:
        self.cue_exercise(exercise, profile)
        if exercise.kind == "cardio":
            return self.guide_cardio(exercise, style_lines)
        if exercise.kind == "hold":
            return self.guide_hold(exercise, style_lines)
        return self.guide_strength(exercise, style_lines)

    def run(self) -> None:
        self.calm_face()
        self.gesture("Smile")
        self.say("Hi, I am your gym guide. I can suggest a simple workout and compare how different robot coaching styles feel.")
        if not parse_yes(self.ask("Do you want to start?")):
            self.say("No problem. I will be here when you want a routine.")
            return

        style = self.choose_style()
        style_lines = COACHING_STYLES[style]
        self.say(style_lines["intro"])
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
        self.say(style_lines["plan"])
        self.say(plan.safety_message)
        self.say(plan.warmup)
        for index, exercise in enumerate(plan.exercises, start=1):
            self.say(f"Exercise {index}: {exercise.name}. {exercise.sets}. {exercise.instruction}")

        if not parse_yes(self.ask("Would you like me to guide you through the session now?")):
            self.say("Okay. You now have the plan. Remember to warm up and keep the movements controlled.")
            return

        for exercise in plan.exercises:
            completed_exercise = self.guide_exercise(exercise, profile, style_lines)
            if not completed_exercise:
                self.say("Session stopped. Drink some water and take care.")
                post_motivation = parse_rating(
                    self.ask("Before you go, how motivated do you feel now from one to five?", str(pre_motivation))
                )
                log_session(profile, style, pre_motivation, post_motivation, False, False, exercise.name)
                return

        self.say(plan.cooldown)
        self.say(style_lines["finish"])
        post_motivation = parse_rating(
            self.ask("After the session, how motivated do you feel from one to five?", str(pre_motivation))
        )
        useful = parse_yes(self.ask("Did this robot coaching style feel useful?"))
        log_session(profile, style, pre_motivation, post_motivation, useful, True, "")
        if useful:
            self.say("I am glad. You completed a structured session today.")
        else:
            self.say("Thanks for telling me. Next time I can adjust the routine to be easier, shorter, or more focused.")


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

    guide = FurhatGymGuide(args.host, args.api_key, args.condition, args.motion, not args.real_timing)
    try:
        guide.connect()
        guide.run()
    finally:
        guide.disconnect()


if __name__ == "__main__":
    main()
