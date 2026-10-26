# ASURRE

**A**I-assisted **SUR**vey **RE**sponses — a benchmark for detecting language-model
assistance in open-text survey answers.

Companion data and browser for *Towards Detecting AI-Assisted Responses in Online
Surveys* (EMNLP 2026, Computational Social Science and Cultural Analytics).

**[Browse the dataset →](https://mike-qz-wang.github.io/ASURRE/)**

---

## What this is

Three pre-LLM surveys supply human answers that are guaranteed free of AI
contamination. Language models then re-answer the same questions under four
strategies of increasing sophistication, from a visible rewrite to a
persona-grounded agent that completes an entire questionnaire in character.

| Strategy | What the respondent did | Paired with the human answer? |
|---|---|---|
| `human` | Answered the survey themselves | — |
| `llm_revision` | Wrote an answer, then had a model rewrite it | Yes, via `original_text` |
| `full_generate` | Handed the question to a model and submitted the output | Yes, by respondent |
| `agent_fill` | A persona-grounded agent completed the questionnaire in character | Yes, via `persona_portrait.source_text_fields` |

The last row is the hard case. The agent writes a whole respondent rather than
editing an answer, so no agent sentence derives from a human one, and detectors
that work on the first three strategies lose most of their signal. The persona
is still grounded in a real respondent, and the portrait records which — so the
two questionnaires can be read against each other even though no individual
answer is a rewrite of another.

## Source surveys

| Dataset | Survey | Year | Respondents | Licence |
|---|---|---|---:|---|
| `phd2019` | Nature PhD Students Survey | 2019 | 3,407 | CC BY 4.0 |
| `springer_2017` | Springer Nature Social Media Survey | 2017 | 798 | CC BY 4.0 |
| `osmi_mh` | OSMI Mental Health in Tech Survey | 2017–18 | 534 | CC BY-SA 4.0 |

All three predate general LLM availability, so every answer in `data/raw/` was
written by a person.

`osmi_mh` contains first-hand accounts of mental health at work. It is published
by OSMI under CC BY-SA 4.0 and is reproduced here under that licence; treat it
as you would any interview material.

## Generators

| Tag | Backbone | Strategies |
|---|---|---|
| `gptoss120b` | `openai/gpt-oss-120b` | revision, generation |
| `qwen35_a3b` | `Qwen/Qwen3.5-35B-A3B-FP8` | revision, generation |
| `gemini3flashpreview` | Gemini 3 Flash (preview) | revision, generation |
| `claude_sonnet` | Claude Sonnet | revision (`phd2019` only) |
| `persona_sonnet*` | Claude Sonnet | agent fill; `_controlled` matches human length, `_terse` applies a terse style |
| `persona_gemini_3_flash`, `persona_gptoss120b` | as named | agent fill (`osmi_mh` only) |
| `inject_{exact,noisy,stacked,blind}_{gemini,oss}` | as named | agent fill with distribution-injection attacks (`osmi_mh` only) |

## Layout

```
data/
  configs/<dataset>.json       field metadata; open-text fields under "attributes"
  raw/                         original survey exports, human-only
  augmented/<dataset>/<tag>/   benchmark splits
  docs/datasets.md             per-dataset and per-field statistics
docs/                          the browser published at GitHub Pages
scripts/build_browse_data.py   regenerates docs/data/ from data/
```

## Record format

Each split file is a list of respondents:

```json
{
  "response_id": "osmi_2017_0460",
  "fields": {
    "Q_EC": {
      "text": "the answer as submitted",
      "label": 1,
      "original_text": "what the person originally wrote"
    }
  },
  "num_perturbed": 1,
  "num_total_fields": 3,
  "perturbed_fields": ["Q_EC"]
}
```

`label` is 1 when the text came from a model and 0 when it came from a person.
`original_text` is present only where a human answer was the model's input, so
it appears under `llm_revision` and `full_generate` but not under `agent_fill`.

Two conventions differ between datasets and will bite anyone who concatenates
splits naively:

- In `phd2019` and `springer_2017`, each respondent appears **twice** in an
  augmented split — once with clean human fields and once with perturbed
  fields. `human_baseline` holds only the clean half, so it is half the length
  of the file beside it.
- In `osmi_mh`, respondents are **partitioned** instead: each appears once, and
  `human_baseline` covers the whole split.

## Browsing

The site under `docs/` puts one person's completed questionnaire beside one
model's version of it. Pick a respondent and a comparison, and every question
appears as a row: their answer on the left, that model's version on the right,
blank where either left it unanswered. Because `llm_revision` perturbs only
some fields per respondent, a blank on the right is common and means the model
did not touch that answer.

All three strategies appear in that one form, persona agents included. An agent
carries no `original_text`, but its `persona_portrait.source_text_fields`
quotes the human answers the persona was grounded in, which identifies that
respondent exactly — so an agent's whole questionnaire can be shown against the
person it was built from. This is often where the contrast is sharpest: agents
answer questions the person left blank, and at a different length.

Respondents join across generator files by position. The human originals agree
at every index in all three datasets, which is what makes the join sound —
and necessary, since `response_id` is unusable in `phd2019` (see Known issues).

The page loads a sample; the full data is in `data/`.

To run it locally:

```bash
python -m http.server --directory docs 8000
```

To regenerate the sample after changing `data/`:

```bash
python scripts/build_browse_data.py --max-respondents 60
```

## Known issues

- `gemini3flashpreview` outputs do not align with the respondent they are
  attached to. In both `llm_revision` and `full_generate`, every Gemini text
  found in `springer_2017` and `osmi_mh` also appears in `phd2019`, and the
  revisions share almost no vocabulary with the `original_text` they claim to
  revise (median Jaccard ≈ 0.00, against ≈ 0.45 for the other generators).
  The outputs appear to have been pooled across datasets before being written
  back. `gptoss120b` and `qwen35_a3b` are unaffected. Treat Gemini cells as
  unreliable pending regeneration.
- `response_id` is not an identifier in `phd2019`. The config points at the
  `ID.format` column, which records the survey platform rather than the
  respondent, so the field takes only three distinct values. `springer_2017`
  and `osmi_mh` carry proper identifiers.

## Licence

The source surveys keep their own licences, listed above; respect them when
redistributing, in particular the ShareAlike term on `osmi_mh`.

<!-- TODO: choose a licence for the generated responses, code and browser, and
     add a LICENSE file. CC BY-SA 4.0 for the data keeps it compatible with the
     OSMI-derived portion; MIT or Apache-2.0 is conventional for the scripts. -->

## Citation

```bibtex
@inproceedings{wang2026asurre,
  title     = {Towards Detecting AI-Assisted Responses in Online Surveys},
  author    = {Wang, Qizhou and Mamaev, Bogdan and Leckie, Christopher},
  booktitle = {Proceedings of the 2026 Conference on Empirical Methods in
               Natural Language Processing},
  year      = {2026}
}
```
