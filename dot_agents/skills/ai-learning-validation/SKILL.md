---
name: ai-learning-validation
description: "Use when the user wants to validate whether they truly understand any topic well enough for real-world decisions. Triggers on learning validation, quantify learning, test my understanding, challenge me, assess my knowledge, AI examiner, learning rubric, or when the user wants a repeatable AI workflow for checking understanding beyond memorization. Produces a strict examiner + remediation coach workflow with short and deep modes."
---

# AI Learning Validation

## Purpose

Use this skill to help the user validate learning quality for any topic. The goal is not to prove that they can define terms. The goal is to test whether they can use the topic to make realistic decisions, explain trade-offs, notice risks, and improve weak reasoning with targeted drills.

## When to Use

Use when the user asks for:

- a way to quantify whether they understand a topic
- an AI prompt to challenge their learning
- a rubric for topic mastery
- a workflow to test practical understanding
- assessment beyond memorization
- real-world decision-making drills
- short or deep learning validation sessions

Do not use for:

- simple explanations of a topic
- exam-only memorization unless the user explicitly asks for interview or certification readiness
- building a note-taking system before the learning validation workflow exists

## Core Principle

The user understands a topic when they can do this:

> Given a messy situation, choose an action, explain trade-offs, identify risks, and defend why the decision fits the context.

Definitions are not enough. Familiarity is not enough. The assessment must test judgment.

## Confirm the Intent

If the user has not already clarified their goal, ask one question at a time:

```text
Q: Do you want to validate this topic for personal learning, work application, interview readiness, or teaching others?
GUESS: work application, because the strongest proof of understanding is making better decisions in real situations.
```

If they want a general reusable workflow, proceed.

## Goal Variants

Use the goal to choose the proof standard:

| Goal | Proof that learning works |
|---|---|
| Personal learning | Can explain, connect, and recognize examples |
| Work application | Can diagnose a realistic problem and choose an action |
| Interview readiness | Can answer under pressure with examples and trade-offs |
| Teaching others | Can simplify, sequence, answer objections, and design exercises |

Default to **work application** when the user wants practical value.

## Workflow Modes

### Short Mode: 15–20 minutes

Use this by default. Repeatability beats perfection.

1. **Teach-back** — user explains the topic in 3–5 sentences.
2. **Diagnosis** — AI identifies vague, wrong, or missing parts.
3. **Real-world case** — AI gives one messy scenario.
4. **Decision answer** — user chooses an action and explains why.
5. **Strict scoring** — AI scores against the rubric.
6. **Correction + drill** — AI gives one focused improvement exercise.
7. **Pass/fail** — AI decides whether the topic is usable yet.

### Deep Mode: 60–90 minutes

Use when the topic matters for work.

Add:

- 3 realistic cases
- 1 adversarial challenge
- 1 “what if constraints change?” round
- 1 teach-back rewrite
- 1 final decision memo

## Master Prompt Template

Give the user this prompt when they want to run the workflow:

```text
You are my strict learning examiner and remediation coach.

Goal:
Validate whether I understand the topic well enough to make real-world decisions, not just explain definitions.

Topic:
[INSERT TOPIC]

My current level:
[beginner / intermediate / advanced]

Expected use case:
[where I want to apply this in real life or work]

Session mode:
[short = 15–20 minutes / deep = 60–90 minutes]

Rules:
1. Do not lecture first.
2. Test my current understanding before teaching.
3. Ask one question or case at a time.
4. Focus on real-world decision-making.
5. Challenge vague, shallow, or memorized answers.
6. Score my answers strictly.
7. Correct me after each answer.
8. Give one targeted drill after finding a weakness.
9. End with a pass/fail judgment and next learning action.

Assessment dimensions:
- Concept accuracy
- Decision quality
- Trade-off awareness
- Ability to handle messy real-world context
- Ability to explain reasoning clearly
- Awareness of risks, constraints, and second-order effects

Scoring:
0 = wrong or mostly memorized
1 = partially correct but shallow
2 = correct basic understanding
3 = usable in realistic decisions
4 = strong reasoning with trade-offs
5 = expert-level judgment

Passing standard:
I pass only if I score at least 3 on decision quality and trade-off awareness.

Start by asking me to explain the topic in my own words in 3–5 sentences.
```

## Result Template

Ask the AI examiner to end with:

```text
Learning Validation Result

Topic:
Mode:
Overall result: Pass / Partial / Fail

Scores:
- Concept accuracy:
- Decision quality:
- Trade-off awareness:
- Real-world transfer:
- Explanation clarity:
- Risk awareness:

Strongest area:
Weakest area:
Main misconception:
Correction:
Next drill:
Recommended next topic:
```

## Quality Criteria

A good validation session:

- starts with the user's own explanation, not a lecture
- asks one question or case at a time
- includes at least one messy real-world scenario
- scores strictly using the 0–5 rubric
- fails weak reasoning instead of flattering it
- gives one targeted drill, not a generic study plan
- ends with pass, partial, or fail

## Branching Logic

If the user gives vague answers:

- challenge the vague claim
- ask for a concrete decision
- ask what risk or trade-off changes the answer

If the user scores below 3 on decision quality:

- mark as fail or partial
- give one correction
- run one new case focused on the weakness

If the user scores at least 3 on decision quality and trade-off awareness:

- mark pass for practical use
- recommend the next adjacent topic or harder case

If the user wants depth:

- switch to deep mode
- require multiple cases and a final decision memo

## Example Invocation

```text
Use AI learning validation for FinOps. My level is beginner. I want to apply it at work when evaluating cloud cost decisions. Short mode.
```

## Output

Produce a ready-to-run workflow or prompt. Keep it practical. Do not turn it into a note-taking system unless the user asks for that next.
