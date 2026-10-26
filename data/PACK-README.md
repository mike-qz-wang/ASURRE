# Survey AI-assistance benchmark — data pack

Companion data for "Towards Detecting AI-Assisted Responses in Online Surveys"
(ACL ARR May 2026, submission 6213). Packed 2026-10-26.

## Layout

    configs/<dataset>.json          column metadata: open-text fields under "attributes"
    raw/                            original survey exports (all pre-LLM, human-only)
      phd2019.xlsx                  Nature PhD Students Survey 2019 (CC BY 4.0)
      springer_2017.xlsx            Springer Nature Social Media Survey 2017 (CC BY 4.0)
      osmi_mh/survey_2017.csv       OSMI Mental Health in Tech 2017 (CC BY-SA 4.0)
      osmi_mh/survey_2018.csv       OSMI Mental Health in Tech 2018 (CC BY-SA 4.0)
    augmented/<dataset>/<tag>/      benchmark splits (see below)
    docs/datasets.md                per-dataset and per-field statistics

## Augmented splits

Each `<tag>` directory is one generator / threat configuration:

| tag                        | threat mode(s)              | generator                     |
|----------------------------|-----------------------------|-------------------------------|
| human_baseline             | none (all human)            | –                             |
| gptoss120b                 | llm_revision, full_generate | openai/gpt-oss-120b           |
| qwen35_a3b                 | llm_revision, full_generate | Qwen/Qwen3.5-35B-A3B-FP8      |
| gemini3flashpreview        | llm_revision, full_generate | Gemini 3 Flash (preview)      |
| claude_sonnet              | llm_revision                | Claude Sonnet (phd2019 only)  |
| persona_sonnet*            | agent_fill (persona-grounded agentic completion); `_controlled` = length-controlled, `_terse` = terse-style skill |
| persona_gemini_3_flash, persona_gptoss120b | agent_fill, other backbones (osmi_mh only) |
| inject_{exact,noisy,stacked,blind}_{gemini,oss} | agent_fill distribution-injection attacks, rebuttal E1 (osmi_mh only) |

Files: `<mode>_{train,test}.json`, plus `<mode>_split_info.json` where present.
`*.unpaired.json` is the pre-pairing agentic output; use the paired `agent_fill_test.json`.

## Record format

Each JSON file is a list of respondents:

    {
      "response_id": "...",
      "fields": {
        "Q16": {"text": "...", "label": 0|1, "original_text": "..."},   # label 1 = AI
        ...
      },
      "num_perturbed": int, "num_total_fields": int, "perturbed_fields": [...]
    }

Splits are identical across tags for a given dataset (same respondents in train/test),
so human_baseline/human_*.json is the shared human reference.

Respondent counts (train / test): phd2019 5,450 / 1,363; springer_2017 1,276 / 320;
osmi_mh 427 / 107.

Please respect the source licences (CC BY 4.0 for Nature/Springer, CC BY-SA 4.0 for OSMI)
when redistributing.
