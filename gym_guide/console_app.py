from gym_guide.workout import GymProfile, create_workout, parse_minutes, parse_yes


def say(text: str) -> None:
    print(f"Furhat: {text}")


def ask(text: str) -> str:
    say(text)
    return input("You: ").strip()


def main() -> None:
    say("Hi, I am your gym guide. I can suggest a simple workout and keep you motivated.")
    if not parse_yes(ask("Do you want to start?")):
        say("No problem. I will be here when you want a routine.")
        return

    profile = GymProfile(
        goal=ask("What is your main goal today? Weight loss, strength, muscle, endurance, or general fitness?") or "general fitness",
        experience=ask("How experienced are you in the gym? Beginner, intermediate, or advanced?") or "beginner",
        minutes=parse_minutes(ask("How many minutes do you have for the workout?")),
        focus=ask("Do you want full body, upper body, legs, or cardio focus?") or "full body",
        has_pain_or_injury=parse_yes(ask("Do you have any pain or injury I should consider?")),
    )

    plan = create_workout(profile)
    # say(f"Great. I suggest a {plan.title}.")
    say(plan.safety_message)
    say(plan.warmup)
    for index, exercise in enumerate(plan.exercises, start=1):
        say(f"Exercise {index}: {exercise.name}. {exercise.sets}. {exercise.instruction}")

    if not parse_yes(ask("Would you like me to guide you through the session now?")):
        say("Okay. Remember to warm up and keep the movements controlled.")
        return

    for exercise in plan.exercises:
        say(f"Now do {exercise.name}. {exercise.sets}.")
        say(exercise.encouragement)
        # response = ask("Say next when you are ready to continue, or stop if you want to end.")
        # if "stop" in response.lower():
        #     say("Session stopped. Drink some water and take care.")
        #     return

    say(plan.cooldown)
    useful = parse_yes(ask("Nice work. Did this routine feel useful?"))
    say("I am glad. You completed a structured session today." if useful else "Thanks for telling me. Next time I can adjust it.")


if __name__ == "__main__":
    main()

