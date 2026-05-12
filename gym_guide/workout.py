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
            "marching in place",
            "2 minutes",
            "Lift your knees to hip height and swing your arms naturally.",
            "Nice start. Let your breathing settle into a rhythm.",
            kind="cardio",
            set_count=1,
            rep_count=0,
            duration_minutes=2,
            beginner_cues=(
                "Stand tall with feet hip-width apart and eyes forward.",
                "Start at an easy pace for the first minute, then step a little livelier if breathing allows.",
            ),
            safety_cues=(
                "Make sure you have clear space around you with no trip hazards.",
                "Slow down or stop if you feel dizzy.",
            ),
        )
    ]

    if "leg" in focus or "full" in focus or "strength" in goal or "muscle" in goal:
        exercises.append(
            Exercise(
                "bodyweight squat",
                "2 sets of 10" if experience == "beginner" else "3 sets of 12",
                "Stand feet shoulder-width apart, push hips back, and lower until thighs are parallel to the floor.",
                "Strong and controlled. The slow return is where the useful work happens.",
                kind="strength",
                set_count=2 if experience == "beginner" else 3,
                rep_count=10 if experience == "beginner" else 12,
                beginner_cues=(
                    "Keep your chest up and look slightly forward, not down at your feet.",
                    "Push through your whole foot, not just your toes.",
                    "Keep your knees tracking in the same direction as your toes.",
                ),
                safety_cues=(
                    "Hold a chair or wall lightly for balance if needed.",
                    "Only go as deep as feels comfortable for your knees.",
                    "Stop if you feel sharp knee or back pain.",
                ),
            )
        )

    if "upper" in focus or "full" in focus or "muscle" in goal or "strength" in goal:
        exercises.extend(
            [
                Exercise(
                    "push-up",
                    "3 sets of 10" if experience == "advanced" else "2 sets of 8",
                    "Place hands slightly wider than shoulder-width, lower your chest to the floor, and push back up.",
                    "Good power. Keep the movement clean rather than rushing the reps.",
                    kind="strength",
                    set_count=3 if experience == "advanced" else 2,
                    rep_count=10 if experience == "advanced" else 8,
                    beginner_cues=(
                        "Drop to your knees if the full push-up is too difficult.",
                        "Keep your body in one straight line from head to hips.",
                        "Lower slowly and push back up with control.",
                    ),
                    safety_cues=(
                        "Do not let your lower back sag toward the floor.",
                        "Keep your elbows at roughly a 45-degree angle from your body.",
                    ),
                ),
                Exercise(
                    "bent-over row",
                    "3 sets of 12" if experience == "advanced" else "2 sets of 10",
                    "Hinge forward at the hips, hold a water bottle or filled bag in each hand, and pull your elbows back.",
                    "Great posture. Imagine pulling with your back, not just your hands.",
                    kind="strength",
                    set_count=3 if experience == "advanced" else 2,
                    rep_count=12 if experience == "advanced" else 10,
                    beginner_cues=(
                        "Hinge at the hips until your torso is roughly parallel to the floor.",
                        "Let your arms hang straight down before pulling.",
                        "Pause briefly at the top, then lower with control.",
                    ),
                    safety_cues=(
                        "Keep a neutral spine throughout — do not round your lower back.",
                        "Start with a very light household item if your back feels stiff.",
                    ),
                ),
            ]
        )

    if "endurance" in goal or "weight" in goal or "fitness" in goal or "cardio" in focus:
        exercises.append(
            Exercise(
                "high knees intervals",
                "6 minutes" if minutes < 30 else "10 minutes",
                "Alternate one minute of easy marching and one minute of faster high knees.",
                "You are building stamina now. Keep it challenging, not painful.",
                kind="cardio",
                set_count=1,
                rep_count=0,
                duration_minutes=6 if minutes < 30 else 10,
                beginner_cues=(
                    "During the easy minute, march at a comfortable pace to recover.",
                    "During the harder minute, drive your knees up toward your hips and pump your arms.",
                ),
                safety_cues=(
                    "Land softly on the balls of your feet to protect your knees.",
                    "Slow down or switch to marching if you feel breathless or dizzy.",
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
        warmup="Start with two minutes of easy marching in place before the main exercises.",
        exercises=exercises[:max_exercises],
        cooldown="Finish with slow marching and gentle stretching for two to three minutes.",
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