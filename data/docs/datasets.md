# Source Datasets

Three publicly available, pre-LLM survey datasets are used in this study. All were collected before large language models were in widespread use (pre-2020), guaranteeing that every response in the original data is human-written with no AI contamination risk.

---

## 1. Nature PhD Students Survey (phd2019)

| Field | Detail |
|---|---|
| **Full name** | 2019 Nature PhD Students Survey |
| **Conducted by** | *Nature* / Shift Learning |
| **Year** | 2019 |
| **Access** | Figshare — DOI [10.6084/m9.figshare.10266299](https://doi.org/10.6084/m9.figshare.10266299) |
| **Licence** | CC BY 4.0 |
| **Format** | xlsx |
| **Total respondents** | 6,813 |
| **Columns** | 274 |

### About
A global survey of PhD students covering experiences, satisfaction, supervisor relationships, mental health, and career intentions. Published by *Nature* alongside a research article in 2019 and widely cited in the doctoral education literature. Respondents span all disciplines and countries. The survey includes both quantitative (Likert, multiple choice) and qualitative (open-text) items — this study uses the six open-text fields only.

### Response length statistics (human entries, n = 3,407)

| Measure | Value |
|---|---|
| Words per respondent — mean | 49 |
| Words per respondent — median | 26 |
| Words per respondent — IQR | 10 – 61 |
| Words per respondent — max | 848 |
| Fields answered per respondent — mean | 4.0 |
| Eligible respondents (≥ 80 chars total) | 2,497 / 3,407 (73%) |

### Open-text fields

| ID | Question | Responses | Words: mean | median | max |
|---|---|---:|---:|---:|---:|
| Q26 | How would you describe the academic system based on your PhD experience? | 2,685 | 24 | 11 | 489 |
| Q16 | Is there anything else that has concerned you since starting your PhD? | 1,805 | 13 | 7 | 384 |
| Q55 | What one thing do you wish you'd known when you started your PhD? | 2,175 | 14 | 10 | 234 |
| Q41 | What type of career are you interested in pursuing after your degree? | 2,899 | 7 | 3 | 117 |
| Q60 | Any further comments? | 771 | 18 | 5 | 454 |
| Q17 | What do you enjoy most about life as a PhD student? | 3,407 | 4 | 2 | 15 |

> Q17 is answered by all respondents but responses are uniformly very short (≤ 15 words). Q26 is the richest field, with many substantive multi-sentence answers.

### Train / test split

| Split | n |
|---|---:|
| Train | 5,450 |
| Test | 1,363 |
| **Total** | **6,813** |

---

## 2. Springer Nature Social Media Survey (springer_2017)

| Field | Detail |
|---|---|
| **Full name** | Springer Nature Social Media Survey 2017 |
| **Conducted by** | Springer Nature |
| **Year** | 2017 |
| **Access** | Figshare — DOI [10.6084/m9.figshare.5028212](https://doi.org/10.6084/m9.figshare.5028212) |
| **Licence** | CC BY 4.0 |
| **Format** | xlsx |
| **Total respondents** | 5,292 raw (1,596 retained with sufficient open-text content) |
| **Columns** | 507 |

### About
A global survey of academic researchers on their professional use of social media and scholarly collaboration networks (SCNs). Topics include research discovery, content sharing and promotion, networking, and publisher services. Part of a longitudinal series — a comparable 2024 edition also exists, enabling cross-period comparisons. The survey was distributed via institutional channels and researcher mailing lists. Although 5,292 responses were collected, only 1,596 respondents contributed sufficient open-text content to be usable in this study.

### Response length statistics (human entries, n = 798)

| Measure | Value |
|---|---|
| Words per respondent — mean | 24 |
| Words per respondent — median | 9 |
| Words per respondent — IQR | 4 – 27 |
| Words per respondent — max | 442 |
| Fields answered per respondent — mean | 3.3 |
| Eligible respondents (≥ 80 chars total) | 325 / 798 (41%) |

> Responses in this dataset are generally shorter and more telegraphic than the other two surveys. Many respondents answered only one or two open-text fields.

### Open-text fields

| ID | Question | Responses | Words: mean | median | max |
|---|---|---:|---:|---:|---:|
| Q23 | Other tasks you use social media for in relation to your work | 650 | 6 | 1 | 370 |
| Q29 | Comments on usefulness of social media for supporting research | 358 | 9 | 3 | 77 |
| Q37 | Comments on usefulness of social media for sharing professional content | 275 | 9 | 2 | 115 |
| Q43 | Comments on usefulness of social media for promoting professional content | 236 | 6 | 1 | 113 |
| Q47 | Comments on usefulness of social media for networking and collaboration | 234 | 6 | 1 | 74 |
| Q63 | What could publishers provide or improve to help your use of social media? | 471 | 9 | 3 | 83 |
| Q65 | Further comments on professional use of social media | 427 | 6 | 1 | 217 |

> Median word counts of 1–3 across most fields reflect a large proportion of very short answers (single phrases or sentence fragments). The distribution is highly right-skewed in all fields.

### Train / test split

| Split | n |
|---|---:|
| Train | 1,276 |
| Test | 320 |
| **Total** | **1,596** |

---

## 3. OSMI Mental Health in Tech Survey (osmi_mh)

| Field | Detail |
|---|---|
| **Full name** | Mental Health in Tech Survey 2017–2018 (combined) |
| **Conducted by** | Open Sourcing Mental Illness (OSMI) |
| **Year** | 2017 and 2018 |
| **Access** | [osmihelp.org](https://osmihelp.org) |
| **Licence** | CC BY-SA 4.0 |
| **Format** | csv (survey_2017.csv + survey_2018.csv) |
| **Total respondents** | 1,173 raw (534 retained with ≥ 80 chars across text fields) |
| **Columns** | 95 |

### About
An annual survey by the non-profit Open Sourcing Mental Illness, targeting workers in the technology industry. Questions cover personal mental health history, disclosure experiences, and workplace attitudes. The open-text fields ask respondents to describe specific conversations with employers and colleagues about mental health — making responses notably personal, narrative-rich, and emotionally sensitive. This is the smallest but most qualitatively dense dataset in the study, and the only one centred on a sensitive personal topic rather than professional practices.

### Response length statistics (all respondents, n = 534)

| Measure | Value |
|---|---|
| Words per respondent — mean | 62 |
| Words per respondent — median | 45 |
| Words per respondent — IQR | 26 – 79 |
| Words per respondent — max | 385 |
| Fields answered per respondent — mean | 2.6 |
| Eligible respondents (≥ 80 chars total) | 534 / 534 (100%) |

> All 534 retained respondents meet the eligibility threshold by construction. The narrative fields (Q_EC, Q_CC, Q_CW etc.) tend to be substantially longer than in the other two surveys.

### Open-text fields

| ID | Question | Responses | Words: mean | median | max |
|---|---|---:|---:|---:|---:|
| Q_EC | Conversation with current employer about mental health | 251 | 37 | 29 | 284 |
| Q_CC | Conversation with current coworkers about mental health | 301 | 26 | 21 | 141 |
| Q_CW | Coworker's disclosure of their mental health to you | 290 | 22 | 18 | 129 |
| Q_PE | Conversation with previous employer about mental health | 155 | 32 | 26 | 220 |
| Q_PC | Conversation with previous coworkers about mental health | 197 | 22 | 18 | 79 |
| Q_CA | How being identified as having a mental health issue affected your career | 2 | — | — | — |
| Q_BH | Circumstances of a badly handled / unsupportive workplace response | 12 | — | — | — |
| Q_SH | Circumstances of a supportive / well-handled workplace response | 90 | — | — | — |
| Q_ID | What could the industry / employers do to improve mental health support? | 24 | — | — | — |
| Q_AE | Any additional comments | 58 | — | — | — |

> The five narrative fields (Q_EC, Q_CC, Q_CW, Q_PE, Q_PC) carry the bulk of the textual content. The remaining fields are answered by a small minority of respondents and tend to be brief.

### Train / test split

| Split | n |
|---|---:|
| Train | 427 |
| Test | 107 |
| **Total** | **534** |

---

## Summary

| Dataset | Domain | Year | Total | Train | Test | Median words/resp | Eligible (%) |
|---|---|---|---:|---:|---:|---:|---:|
| phd2019 | Doctoral education | 2019 | 6,813 | 5,450 | 1,363 | 26 | 73% |
| springer_2017 | Researcher social media use | 2017 | 1,596 | 1,276 | 320 | 9 | 41% |
| osmi_mh | Mental health in tech | 2017–2018 | 534 | 427 | 107 | 45 | 100% |
| **Total** | | | **8,943** | **7,153** | **1,790** | | |

All three datasets predate the widespread availability of LLMs (GPT-3: June 2020; ChatGPT: November 2022), providing a clean human-only baseline with no AI contamination risk. The datasets vary substantially in domain sensitivity, response verbosity, and text density, enabling evaluation of AI detection methods across diverse survey contexts.
