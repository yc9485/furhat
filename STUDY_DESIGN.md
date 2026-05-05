# HRI Study Design Notes

## Research Focus

The instructor feedback suggests that higher grades depend on a clear HRI contribution, not on perfect workout advice. This project should therefore be framed as a study of robot coaching style and user motivation.

## Possible Research Questions

RQ1: How does a social robot's coaching style affect users' motivation during a short gym-planning interaction?

RQ2: Do users perceive a supportive robot coach as more appropriate, trustworthy, or comfortable than an energetic robot coach?

RQ3: Does a user's self-reported motivation change after receiving a personalized workout plan from a social robot?

## Suggested Hypotheses

H1: A supportive robot coaching style will be rated as more comfortable than an energetic style for beginner gym-goers.

H2: An energetic robot coaching style will increase short-term motivation more than a neutral instruction style.

H3: Users will report higher usefulness when the robot's style matches their preferred coaching style.

## Literature Grounding

The project fits socially assistive HRI because it studies how a robot can motivate and support users during a health-related activity.

Relevant starting points:

- Andrist, Mutlu, and Tapus, "Look Like Me: Matching Robot Personality via Gaze to Increase Motivation", CHI 2015. This work shows that robot personality cues can affect motivation.
- Esterwood and Robert, "A Systematic Review of Human and Robot Personality in Health Care Human-Robot Interaction", Frontiers in Robotics and AI, 2021. This is useful for justifying personality/coaching style as an HRI variable.
- Sussenbach et al., "A robot as fitness companion: Towards an interactive action-based motivation model", 2014. This directly relates motivation and robot behavior in a fitness context.

## Study Conditions

The current app supports three conditions:

- `supportive`: calm, confidence-focused coaching.
- `energetic`: higher-energy, push-oriented coaching.
- `neutral`: concise instruction with minimal motivational framing.

Run a fixed condition:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition supportive
```

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition energetic
```

```powershell
powershell -ExecutionPolicy Bypass -File .\run_furhat.ps1 -Condition neutral
```

Default mode is `ask`, where the participant chooses a style.

## Measures

The app logs:

- selected/assigned coaching style
- pre-session motivation, 1 to 5
- post-session motivation, 1 to 5
- perceived usefulness
- whether the session was completed
- goal, experience, time, focus, and injury flag

Logs are saved to:

```text
data/sessions.csv
```

## Recommended Participant Procedure

1. Give the participant a short consent-style explanation.
2. Tell them the robot is a prototype and not a real trainer.
3. Start one condition.
4. Ask the participant to answer naturally.
5. After the interaction, ask 2-4 short follow-up questions:
   - How comfortable was the robot's coaching style?
   - Did the robot feel motivating?
   - Did anything feel awkward or unnatural?
   - Would you prefer a different coaching style in a real gym?
6. Save notes immediately after each participant.

## Report Angle

Do not spend too much space explaining the workout algorithm. In the final report, emphasize:

- why robot coaching style matters in HRI
- how the interaction was designed
- what data was collected
- what participants said or rated
- limitations, especially small sample size and simulator realism

