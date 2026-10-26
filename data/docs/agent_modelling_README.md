# Agent Modelling

Agentic threat simulations for survey fraud detection research.

## Threat Types

### Type 1 — Malicious Scale Filler (implemented)
A user configures a Claude agent to fill surveys at scale.
Unlike `full_generate` (field-by-field, independent), this uses
**multi-turn conversation**: each question is answered in a separate
turn with full memory of all prior answers, producing internally
consistent fake respondents.

Defined in: `phd2019/`
Run with: `bash run_tasks/run_agent_phd2019.sh`

### Type 2 — Persona-based Simulation (future)
Agent is grounded in real demographic data from the survey (country,
field, year) to simulate a specific respondent type.

## Directory Layout

```
{dataset}/
├── agents/
│   └── {agent_name}.md          # System prompt + rules for the agent
├── skills/
│   └── survey_fill.md           # Multi-turn survey completion protocol
└── simulation_plans/
    └── {plan_name}.json         # List of attack profiles to simulate
```

## Output

Generated data goes to `data/augmented/{dataset}/{aug_model_tag}/agent_fill_{split}.json`
in the standard augmented format. Run `detect.py --type agent_fill` to score it.
