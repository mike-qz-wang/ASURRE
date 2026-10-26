#!/usr/bin/env python3
"""Build the compact JSON payloads that back the ASURRE browser (docs/).

Reads the full benchmark pack under data/ and writes, per dataset, a sampled
set of paired human/AI records plus summary statistics into docs/data/.

The full pack stays in data/; this script only produces what the static page
needs to stay small enough to load in a browser.

Usage:  python scripts/build_browse_data.py [--max-per-cell N]
"""

import argparse
import json
import os
import random
import re
import statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "data")

DATASETS = ["phd2019", "springer_2017", "osmi_mh"]

# Human-readable labels, from data/docs/datasets.md
DATASET_META = {
    "phd2019": {
        "title": "Nature PhD Students Survey",
        "short": "phd2019",
        "year": "2019",
        "domain": "Doctoral education",
        "licence": "CC BY 4.0",
        "attribution": "Nature / Shift Learning",
        "doi": "10.6084/m9.figshare.10266299",
        "url": "https://doi.org/10.6084/m9.figshare.10266299",
        "sensitive": False,
    },
    "springer_2017": {
        "title": "Springer Nature Social Media Survey",
        "short": "springer_2017",
        "year": "2017",
        "domain": "Researcher social media use",
        "licence": "CC BY 4.0",
        "attribution": "Springer Nature",
        "doi": "10.6084/m9.figshare.5028212",
        "url": "https://doi.org/10.6084/m9.figshare.5028212",
        "sensitive": False,
    },
    "osmi_mh": {
        "title": "OSMI Mental Health in Tech Survey",
        "short": "osmi_mh",
        "year": "2017-2018",
        "domain": "Mental health in tech",
        "licence": "CC BY-SA 4.0",
        "attribution": "Open Sourcing Mental Illness (OSMI)",
        "doi": None,
        "url": "https://osmihelp.org",
        "sensitive": True,
    },
}

QUESTIONS = {
    "phd2019": {
        "Q26": "How would you describe the academic system based on your PhD experience?",
        "Q16": "Is there anything else that has concerned you since starting your PhD?",
        "Q55": "What one thing do you wish you'd known when you started your PhD?",
        "Q41": "What type of career are you interested in pursuing after your degree?",
        "Q60": "Any further comments?",
        "Q17": "What do you enjoy most about life as a PhD student?",
    },
    "springer_2017": {
        "Q23": "Other tasks you use social media for in relation to your work",
        "Q29": "Comments on usefulness of social media for supporting research",
        "Q37": "Comments on usefulness of social media for sharing professional content",
        "Q43": "Comments on usefulness of social media for promoting professional content",
        "Q47": "Comments on usefulness of social media for networking and collaboration",
        "Q63": "What could publishers provide or improve to help your use of social media?",
        "Q65": "Further comments on professional use of social media",
    },
    "osmi_mh": {
        "Q_EC": "Conversation with current employer about mental health",
        "Q_CC": "Conversation with current coworkers about mental health",
        "Q_CW": "Coworker's disclosure of their mental health to you",
        "Q_PE": "Conversation with previous employer about mental health",
        "Q_PC": "Conversation with previous coworkers about mental health",
        "Q_CA": "How being identified as having a mental health issue affected your career",
        "Q_BH": "Circumstances of a badly handled / unsupportive workplace response",
        "Q_SH": "Circumstances of a supportive / well-handled workplace response",
        "Q_ID": "What could the industry / employers do to improve mental health support?",
        "Q_AE": "Any additional comments",
    },
}

# Generator backbone behind each tag directory
GENERATORS = {
    "human_baseline": "—",
    "gptoss120b": "openai/gpt-oss-120b",
    "qwen35_a3b": "Qwen/Qwen3.5-35B-A3B-FP8",
    "gemini3flashpreview": "Gemini 3 Flash (preview)",
    "claude_sonnet": "Claude Sonnet",
    "persona_sonnet": "Claude Sonnet",
    "persona_sonnet_controlled": "Claude Sonnet",
    "persona_sonnet_terse": "Claude Sonnet",
    "persona_sonnet_terse_controlled": "Claude Sonnet",
    "persona_gemini_3_flash": "Gemini 3 Flash (preview)",
    "persona_gptoss120b": "openai/gpt-oss-120b",
}
for _inj in ("exact", "noisy", "stacked", "blind"):
    GENERATORS[f"inject_{_inj}_gemini"] = "Gemini 3 Flash (preview)"
    GENERATORS[f"inject_{_inj}_oss"] = "openai/gpt-oss-120b"

MODE_LABELS = {
    "human": "Human only",
    "llm_revision": "LLM revision",
    "full_generate": "Full generation",
    "agent_fill": "Persona-grounded agent",
}

# Short description of what each tag varies, shown in the UI
TAG_NOTES = {
    "human_baseline": "Unmodified human responses — the shared reference.",
    "persona_sonnet_controlled": "Length-controlled: agent output matched to human length distribution.",
    "persona_sonnet_terse": "Length ablation.",
    "persona_sonnet_terse_controlled": "Combined ablation.",
}

# What a run is called on screen, where the directory name is not the name the
# paper uses for that ablation. The tag itself stays in the option's tooltip,
# since it is what the files are named after.
DISPLAY_NAMES = {
    "persona_sonnet_terse": "length",
    "persona_sonnet_terse_controlled": "combined",
}
for _inj, _desc in (
    ("exact", "Distribution injection, exact target statistics."),
    ("noisy", "Distribution injection, noisy target statistics."),
    ("stacked", "Distribution injection, stacked cue targeting."),
    ("blind", "Distribution injection without target statistics."),
):
    TAG_NOTES[f"inject_{_inj}_gemini"] = _desc
    TAG_NOTES[f"inject_{_inj}_oss"] = _desc


def words(text):
    if not text:
        return 0
    return len(re.findall(r"\S+", text))


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def take(bucket, n, rng):
    """Up to n items from bucket, sampled without replacement."""
    if n <= 0 or not bucket:
        return []
    if len(bucket) <= n:
        return list(bucket)
    return rng.sample(bucket, n)


def discover(dataset):
    """Return {tag: {mode: {split: path}}} for one dataset."""
    base = os.path.join(DATA, "augmented", dataset)
    out = defaultdict(lambda: defaultdict(dict))
    if not os.path.isdir(base):
        return out
    for tag in sorted(os.listdir(base)):
        tdir = os.path.join(base, tag)
        if not os.path.isdir(tdir):
            continue
        for fn in sorted(os.listdir(tdir)):
            if not fn.endswith(".json") or "split_info" in fn or ".unpaired." in fn:
                continue
            stem = fn[:-5]
            if stem.endswith("_train"):
                mode, split = stem[:-6], "train"
            elif stem.endswith("_test"):
                mode, split = stem[:-5], "test"
            else:
                continue
            out[tag][mode][split] = os.path.join(tdir, fn)
    return out


def record_rows(rec, dataset):
    """Flatten one record into per-field rows."""
    rows = []
    for fid, f in (rec.get("fields") or {}).items():
        text = f.get("text")
        if not text or not str(text).strip():
            continue
        rows.append(
            {
                "f": fid,
                "t": str(text).strip(),
                "o": (str(f.get("original_text")).strip() if f.get("original_text") else None),
                "l": int(f.get("label") or 0),
            }
        )
    return rows


def summarise(paths, dataset):
    """Length / coverage statistics over the FULL split (not the sample)."""
    per_field = defaultdict(lambda: {"human": [], "ai": []})
    n_records = 0
    n_ai_records = 0
    for path in paths:
        for rec in load(path):
            n_records += 1
            has_ai = False
            for row in record_rows(rec, dataset):
                side = "ai" if row["l"] == 1 else "human"
                per_field[row["f"]][side].append(words(row["t"]))
                if row["l"] == 1:
                    has_ai = True
            if has_ai:
                n_ai_records += 1
    stats = {}
    for fid, sides in per_field.items():
        entry = {}
        for side, lens in sides.items():
            if not lens:
                continue
            entry[side] = {
                "n": len(lens),
                "mean": round(statistics.mean(lens), 1),
                "median": int(statistics.median(lens)),
                "p90": int(sorted(lens)[int(0.9 * (len(lens) - 1))]),
                "max": max(lens),
            }
        if entry:
            stats[fid] = entry
    return {"records": n_records, "ai_records": n_ai_records, "fields": stats}


def field_catalogue(config, dataset):
    """Field order and question text.

    `attributes` in the configs is an object keyed by field id, whose `label`
    holds the verbatim survey question. Prefer that over the shorter paraphrases
    in QUESTIONS, which are only a fallback.
    """
    attrs = config.get("attributes")
    fallback = QUESTIONS.get(dataset, {})
    if isinstance(attrs, dict):
        order = list(attrs.keys())
        questions = {}
        details = {}
        for fid, meta in attrs.items():
            meta = meta if isinstance(meta, dict) else {}
            questions[fid] = meta.get("label") or fallback.get(fid) or fid
            detail = {}
            for key in ("responses", "response_rate", "tier"):
                if meta.get(key) is not None:
                    detail[key] = meta[key]
            if detail:
                details[fid] = detail
        return order, questions, details
    if isinstance(attrs, list):
        return list(attrs), {f: fallback.get(f, f) for f in attrs}, {}
    return list(fallback), dict(fallback), {}


PAIRED_MODES = ("llm_revision", "full_generate")

MODE_VERB = {
    "llm_revision": "rewrote it",
    "full_generate": "answered instead",
    "agent_fill": "answered as them",
}


def norm(text):
    return " ".join((text or "").split())[:300]


# The agent runs are not one set. Four of them vary the prompt and length
# control on a single Claude Sonnet backbone — the ablation the paper reports —
# while others swap the backbone entirely, and the inject_* runs are a separate
# attack study. Grouping them together in one list hides which is which.
FAMILY_LABELS = {
    "llm_revision": "Rewrote their answer",
    "full_generate": "Answered the question instead",
    "agent_claude": "Answered as them — Claude Sonnet ablation",
    "agent_backbone": "Answered as them — other backbones",
    "agent_inject": "Answered as them — distribution-injection attacks",
}

FAMILY_ORDER = [
    "llm_revision",
    "full_generate",
    "agent_claude",
    "agent_backbone",
    "agent_inject",
]


def family_of(tag, mode):
    if mode != "agent_fill":
        return mode, FAMILY_LABELS.get(mode, mode)
    if tag.startswith("inject_"):
        key = "agent_inject"
    elif tag.startswith("persona_sonnet"):
        key = "agent_claude"
    else:
        key = "agent_backbone"
    return key, FAMILY_LABELS[key]


def link_agents(tree, respondents):
    """Attach persona-agent answers to the respondent each persona was built from.

    An agent invents a whole respondent, so its answers carry no original_text.
    But `persona_portrait.source_text_fields` quotes the human answers the
    persona was grounded in, which identifies that respondent exactly. Index
    pairing also works wherever the agent and human counts match, and breaks
    where agents dropped out, so the portrait is the reliable key.
    """
    # (field, text) -> respondent positions
    lookup = defaultdict(set)
    for pos, r in enumerate(respondents):
        for fid, a in r["answers"].items():
            if a["human"]:
                lookup[(fid, norm(a["human"]))].add(pos)

    linked = Counter()
    for tag in sorted(tree):
        path = (tree[tag].get("agent_fill") or {}).get("test")
        if not path:
            continue
        for rec in load(path):
            fields = rec.get("fields") or {}
            if not any(f.get("label") == 1 for f in fields.values()):
                continue
            portrait = (rec.get("persona_portrait") or {}).get("source_text_fields") or {}
            candidates = None
            for fid, meta in portrait.items():
                hit = lookup.get((fid, norm((meta or {}).get("text"))))
                if not hit:
                    continue
                candidates = set(hit) if candidates is None else (candidates & hit)
            if not candidates or len(candidates) != 1:
                continue
            pos = next(iter(candidates))
            target = respondents[pos]["answers"]
            for fid, f in fields.items():
                text = (f.get("text") or "").strip()
                if f.get("label") != 1 or not text:
                    continue
                slot = target.setdefault(fid, {"human": "", "variants": []})
                slot["variants"].append({"tag": tag, "mode": "agent_fill", "t": text})
            linked[tag] += 1
    return linked


def build_respondents(dataset, tree, max_respondents, rng):
    """One entry per respondent: their own answer, plus every model's version.

    Respondents line up by position across every generator file — verified by
    comparing original_text at each index — so position is the join key. That
    matters for phd2019, whose response_id column is not an identifier.
    """
    columns = []  # (tag, mode, records)
    for tag in sorted(tree):
        for mode in PAIRED_MODES:
            path = (tree[tag].get(mode) or {}).get("test")
            if path:
                columns.append((tag, mode, load(path)))
    if not columns:
        return [], [], [], False

    # Some generators cover only a prefix of the split (claude_sonnet's phd2019
    # test file is 38 records against 1363). Those are index-aligned prefixes,
    # verified against the longer files, so the spine is the longest column and
    # short ones simply contribute nothing past their end.
    length = max(len(recs) for _, _, recs in columns)
    respondents = []

    for i in range(length):
        answers = {}
        rid = ""
        for tag, mode, recs in columns:
            if i >= len(recs):
                continue
            rec = recs[i]
            rid = rid or str(rec.get("response_id") or "")
            for fid, f in (rec.get("fields") or {}).items():
                text = (f.get("text") or "").strip()
                original = (f.get("original_text") or "").strip()
                human = original or (text if f.get("label") != 1 else "")
                if not human and not text:
                    continue
                slot = answers.setdefault(fid, {"human": "", "variants": []})
                if human and not slot["human"]:
                    slot["human"] = human
                if f.get("label") == 1 and text:
                    slot["variants"].append({"tag": tag, "mode": mode, "t": text})

        answers = {k: v for k, v in answers.items() if v["human"] or v["variants"]}
        respondents.append({"i": i, "rid": rid, "answers": answers})

    # Persona agents attach here too, by the respondent their persona was built
    # from, so every strategy is shown in the same per-respondent form.
    linked = link_agents(tree, respondents)

    # Respondents no model touched at all are the clean half of a paired split;
    # they carry no comparison.
    for r in respondents:
        r["n_variants"] = sum(len(a["variants"]) for a in r["answers"].values())
        r["human_words"] = sum(words(a["human"]) for a in r["answers"].values())
    respondents = [r for r in respondents if r["n_variants"]]

    # Rank by how much there is to compare: several model versions AND a
    # substantive human answer to compare them against. Ranking on variant
    # count alone surfaces respondents who wrote two words, which shows
    # nothing.
    pool = [r for r in respondents if r["n_variants"] >= 2 and r["human_words"] >= 25]
    if len(pool) < max_respondents:
        pool = respondents
    pool.sort(key=lambda r: (-min(r["n_variants"], 8), -r["human_words"], r["i"]))
    chosen = pool[: max_respondents * 3]
    if len(chosen) > max_respondents:
        chosen = rng.sample(chosen, max_respondents)
    chosen.sort(key=lambda r: (-min(r["n_variants"], 8), -r["human_words"]))
    for r in chosen:
        r.pop("human_words", None)

    # phd2019's response_id column holds the survey platform, not an
    # identifier, so it is worth nothing on screen. Detect that rather than
    # hard-coding it.
    rids = [r["rid"] for r in respondents if r["rid"]]
    rid_usable = bool(rids) and len(set(rids)) > 0.9 * len(rids)

    # Order the comparison choices by how many of the shown respondents they
    # actually cover, so the default selection is not a generator that only ran
    # on a fraction of the split (claude_sonnet covers 38 of 1363 on phd2019).
    coverage = Counter()
    for r in chosen:
        for a in r["answers"].values():
            for v in a["variants"]:
                coverage[f"{v['tag']}|{v['mode']}"] += 1

    legend = [
        {
            "key": f"{t}|{m}",
            "tag": t,
            "mode": m,
            "generator": GENERATORS.get(t, t),
            "verb": MODE_VERB.get(m, m),
            "coverage": coverage.get(f"{t}|{m}", 0),
        }
        for t, m in sorted(
            {(t, m) for t, m, _ in columns}
            | {(t, "agent_fill") for t in linked}
        )
    ]
    for g in legend:
        g["note"] = TAG_NOTES.get(g["tag"])
        g["label"] = DISPLAY_NAMES.get(g["tag"], g["tag"])
        g["family"], g["family_label"] = family_of(g["tag"], g["mode"])
    # Revision first on a tie: it is the comparison where the model demonstrably
    # saw the human answer, so it reads most clearly as a first example.
    legend.sort(key=lambda g: (-g["coverage"], g["mode"] != "llm_revision", g["tag"]))
    families = [
        {"key": k, "label": FAMILY_LABELS[k]}
        for k in FAMILY_ORDER
        if any(g["family"] == k for g in legend)
    ]
    for g in legend:
        g.pop("family_label", None)
    return chosen, legend, families, rid_usable


def build_agent_pool(dataset, tree, per_tag, rng):
    """Persona-agent responses have no respondent counterpart, so they are
    pooled per question against the human answers instead."""
    pool = []
    for tag in sorted(tree):
        path = (tree[tag].get("agent_fill") or {}).get("test")
        if not path:
            continue
        humans, agents = defaultdict(list), defaultdict(list)
        for rec in load(path):
            for fid, f in (rec.get("fields") or {}).items():
                text = (f.get("text") or "").strip()
                if not text:
                    continue
                who = agents if f.get("label") == 1 else humans
                who[fid].append({"t": text, "id": rec.get("persona_id") or rec.get("response_id") or ""})
        fields = {}
        for fid in set(humans) | set(agents):
            fields[fid] = {
                "human": take(humans.get(fid, []), per_tag, rng),
                "agent": take(agents.get(fid, []), per_tag, rng),
            }
        if fields:
            pool.append(
                {
                    "tag": tag,
                    "generator": GENERATORS.get(tag, tag),
                    "note": TAG_NOTES.get(tag),
                    "fields": fields,
                }
            )
    return pool


def build_dataset(dataset, max_respondents, rng):
    config_path = os.path.join(DATA, "configs", f"{dataset}.json")
    config = load(config_path) if os.path.exists(config_path) else {}
    field_order, questions, field_details = field_catalogue(config, dataset)
    tree = discover(dataset)

    respondents, legend, families, rid_usable = build_respondents(dataset, tree, max_respondents, rng)

    # Word-count statistics over the whole test split, per question.
    stats = {}
    for tag in tree:
        for mode in tree[tag]:
            path = tree[tag][mode].get("test")
            if path:
                stats[f"{tag}|{mode}"] = summarise([path], dataset)

    payload = {
        "dataset": dataset,
        "meta": DATASET_META.get(dataset, {}),
        "config": {
            k: config.get(k)
            for k in ("description", "attribution", "licence", "year", "url")
            if config.get(k) is not None
        },
        "questions": questions,
        "field_order": field_order,
        "field_details": field_details,
        "generators": legend,
        "families": families,
        "respondents": respondents,
        "rid_usable": rid_usable,
        "stats": stats,
    }
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-respondents", type=int, default=60,
                    help="respondents included per dataset in the browser")
    ap.add_argument("--seed", type=int, default=20261026)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(args.seed)

    index = {"datasets": [], "built_with": "scripts/build_browse_data.py",
             "max_respondents": args.max_respondents, "seed": args.seed}

    for ds in DATASETS:
        payload = build_dataset(ds, args.max_respondents, rng)
        path = os.path.join(OUT, f"{ds}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
        size = os.path.getsize(path)
        index["datasets"].append(
            {
                "id": ds,
                "meta": payload["meta"],
                "respondents": len(payload["respondents"]),
                "generators": payload["generators"],
                "questions": payload["questions"],
                "field_order": payload["field_order"],
                "bytes": size,
            }
        )
        print(f"{ds:15s} respondents={len(payload['respondents']):4d} "
              f"generators={len(payload['generators']):2d} "
              f"{size/1024:8.0f} KiB")

    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)
    print("index.json written")


if __name__ == "__main__":
    main()
