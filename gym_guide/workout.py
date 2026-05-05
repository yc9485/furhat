from dataclasses import dataclass


@dataclass
class GymProfile:
    goal: str = "general fitness"
    experience: str = "beginner"
    minutes: int = 35
    focus: str = "full body"
    has_pain_or_injury: bool = False


@dataclass(frozen=True)
class Exercise:
    name: str
    sets: str
    instruction: str
    encouragement: str
    kind: str = "strength"
    set_count: int = 2
    rep_count: int = 10
    duration_minutes: int = 0
    beginner_cues: tuple[str, ...] = ()
    safety_cues: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkoutPlan:
    title: str
    warmup: str
    exercises: list[Exercise]
    cooldown: str
    safety_message: str


def _normalise_minutes(minutes: int) -> int:
    return max(15, min(minutes, 75))


def create_workout(profile: GymProfile) -> WorkoutPlan:
    goal = profile.goal.lower()
    focus = profile.focus.lower()
    experience = profile.experience.lower()
    minutes = _normalise_minutes(profile.minutes)

    exercises: list[Exercise] = [
        Exercise(
            "treadmill walk",
            "5 minutes" if minutes < 30 else "8 minutes",
            "Keep a pace where you can still speak in short sentences.",
            "Nice start. Let your breathing settle into a rhythm.",
            kind="cardio",
            set_count=1,
            rep_count=0,
            duration_minutes=5 if minutes < 30 else 8,
            beginner_cues=(
                "Stand tall, look forward, and avoid holding the rails unless you need balance.",
                "Start slow for the first minute, then increase speed only if your breathing feels controlled.",
            ),
            safety_cues=(
                "Clip the safety key if the treadmill has one.",
                "Step onto the side rails before changing settings if you feel unsteady.",
            ),
        )
    ]

    if "leg" in focus or "full" in focus or "strength" in goal or "muscle" in goal:
        exercises.append(
            Exercise(
                "leg press",
                "2 sets of 10" if experience == "beginner" else "3 sets of 10",
                "Place your feet hip-width apart and stop before your knees lock.",
                "Strong and controlled. The slow return is where the useful work happens.",
                kind="strength",
                set_count=2 if experience == "beginner" else 3,
                rep_count=10,
                beginner_cues=(
                    "Set the seat so your knees start bent but not squeezed close to your chest.",
                    "Push through the middle of your feet, not only your toes.",
                    "Keep your knees pointing in the same direction as your toes.",
                ),
                safety_cues=(
                    "Do not lock your knees at the top.",
                    "Use a light weight for the first set.",
                    "Stop if you feel sharp knee or back pain.",
                ),
            )
        )

    if "upper" in focus or "full" in focus or "muscle" in goal or "strength" in goal:
        exercises.extend(
            [
                Exercise(
                    "chest press machine",
                    "3 sets of 12" if experience == "advanced" else "2 sets of 10",
                    "Keep your shoulders down and push smoothly away from your chest.",
                    "Good power. Keep the movement clean rather than rushing the reps.",
                    kind="strength",
                    set_count=3 if experience == "advanced" else 2,
                    rep_count=12 if experience == "advanced" else 10,
                    beginner_cues=(
                        "Adjust the seat so the handles are around chest height.",
                        "Keep your back against the pad.",
                        "Push forward smoothly and return slowly.",
                    ),
                    safety_cues=(
                        "Do not shrug your shoulders up toward your ears.",
                        "Do not let the weights slam down.",
                    ),
                ),
                Exercise(
                    "seated row",
                    "3 sets of 12" if experience == "advanced" else "2 sets of 10",
                    "Pull your elbows back and squeeze your shoulder blades gently.",
                    "Great posture. Imagine pulling with your back, not just your hands.",
                    kind="strength",
                    set_count=3 if experience == "advanced" else 2,
                    rep_count=12 if experience == "advanced" else 10,
                    beginner_cues=(
                        "Sit tall with your chest lifted.",
                        "Pull your elbows back beside your body.",
                        "Pause briefly, then return with control.",
                    ),
                    safety_cues=(
                        "Avoid leaning far backward to move the weight.",
                        "Keep your wrists neutral and relaxed.",
                    ),
                ),
            ]
        )

    if "endurance" in goal or "weight" in goal or "fitness" in goal or "cardio" in focus:
        exercises.append(
            Exercise(
                "bike intervals",
                "6 minutes" if minutes < 30 else "10 minutes",
                "Alternate one minute easy and one minute slightly harder.",
                "You are building stamina now. Keep it challenging, not painful.",
                kind="cardio",
                set_count=1,
                rep_count=0,
                duration_minutes=6 if minutes < 30 else 10,
                beginner_cues=(
                    "Adjust the seat so your knee is slightly bent at the bottom of the pedal stroke.",
                    "Keep your shoulders relaxed and your hands light on the handles.",
                ),
                safety_cues=(
                    "Do not make the resistance so heavy that your hips rock side to side.",
                    "Slow down if you feel dizzy or breathless.",
                ),
            )
        )

    exercises.append(
        Exercise(
            "plank",
            "2 rounds of 20 seconds" if experience == "beginner" else "3 rounds of 30 seconds",
            "Keep your body long, breathe, and stop if your lower back hurts.",
            "Excellent finish. Small steady effort beats dramatic effort here.",
            kind="hold",
            set_count=2 if experience == "beginner" else 3,
            rep_count=0,
            duration_minutes=0,
            beginner_cues=(
                "Place elbows under shoulders.",
                "Keep ribs and hips in one long line.",
                "Breathe normally instead of holding your breath.",
            ),
            safety_cues=(
                "Stop if your lower back hurts.",
                "Drop to your knees if the full plank is too difficult.",
            ),
        )
    )

    max_exercises = 3 if minutes < 25 else 4 if minutes < 45 else 5
    safety = (
        "Because you mentioned pain or injury, use light resistance and ask gym staff before doing anything that stresses that area."
        if profile.has_pain_or_injury
        else "Use a comfortable weight, keep control, and stop if anything feels sharp or painful."
    )

    return WorkoutPlan(
        title=f"{minutes}-minute {profile.goal} routine",
        warmup="Start with light movement and one easy practice set before using resistance.",
        exercises=exercises[:max_exercises],
        cooldown="Finish with slow walking and gentle stretching for two to three minutes.",
        safety_message=safety,
    )


def parse_minutes(text: str, default: int = 35) -> int:
    digits = "".join(ch for ch in text if ch.isdigit())
    return _normalise_minutes(int(digits)) if digits else default


def parse_yes(text: str) -> bool:
    return text.strip().lower() in {"yes", "yeah", "yep", "sure", "ok", "okay", "start"}


def parse_rating(text: str, default: int = 3) -> int:
    for token in text.replace(",", " ").split():
        if token.isdigit():
            return max(1, min(int(token), 5))
    words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    lowered = text.lower()
    for word, value in words.items():
        if word in lowered:
            return value
    return default


def parse_style(text: str, default: str = "supportive") -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["energy", "energetic", "push", "intense", "hype"]):
        return "energetic"
    if any(word in lowered for word in ["calm", "support", "gentle", "quiet", "relaxed"]):
        return "supportive"
    if "neutral" in lowered:
        return "neutral"
    return default
