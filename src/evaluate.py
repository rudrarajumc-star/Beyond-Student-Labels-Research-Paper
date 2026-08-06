"""Automated metrics over parsed generations + human-rating subset sampler.

Metrics per item (pre-registered in DESIGN.md §4.1):
  Linguistic:  fk_grade, mean_sentence_len, rare_word_ratio
  Math:        n_solution_steps, n_operations, max_operand_magnitude
  Structure:   word_count, has_context (proper noun / narrative cue), answer_numeric

Usage:
  python src/evaluate.py            # -> data/metrics.csv
  python src/evaluate.py --sample   # -> data/human_rating_sheet.csv (120 items, blinded)
"""
import argparse
import json
import random
import re

import pandas as pd
from wordfreq import zipf_frequency

GEN = "data/generations.jsonl"
RARE_ZIPF = 3.5  # words below this Zipf frequency count as "rare"


def count_syllables(word):
    """Standard vowel-group approximation (no external dictionaries needed)."""
    w = word.lower().strip("'")
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1 and not w.endswith(("le", "ee", "ye")):
        n -= 1
    return max(1, n)


def linguistic_metrics(text):
    words = re.findall(r"[A-Za-z']+", text)
    sents = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    rare = [w for w in words if zipf_frequency(w.lower(), "en") < RARE_ZIPF]
    if not words or not sents:
        return {"fk_grade": None, "mean_sentence_len": None,
                "rare_word_ratio": None, "word_count": len(words)}
    syll = sum(count_syllables(w) for w in words)
    # Flesch-Kincaid grade level formula (0.39*W/S + 11.8*Syl/W - 15.59)
    fk = 0.39 * (len(words) / len(sents)) + 11.8 * (syll / len(words)) - 15.59
    return {
        "fk_grade": round(fk, 2),
        "mean_sentence_len": len(words) / len(sents),
        "rare_word_ratio": len(rare) / len(words),
        "word_count": len(words),
    }


def math_metrics(parsed):
    steps = parsed.get("solution_steps") or []
    steps_text = " ".join(str(s) for s in steps)
    problem = str(parsed.get("problem", ""))
    ops = len(re.findall(r"[+\-*/×÷=]|plus|minus|times|divided", steps_text.lower()))
    nums = [abs(float(n)) for n in re.findall(r"-?\d+\.?\d*", problem) if n not in (".",)]
    ans = str(parsed.get("answer", ""))
    ans_nums = re.findall(r"-?\d+\.?\d*", ans)
    return {
        "n_solution_steps": len(steps),
        "n_operations": ops,
        "max_operand_magnitude": max(nums) if nums else None,
        "answer_numeric": ans_nums[0] if ans_nums else None,
    }


def structure_metrics(problem):
    # crude narrative-context cue: named person or shopping/classroom scenario words
    has_name = bool(re.search(r"\b[A-Z][a-z]+\b(?!\.)", problem[1:]))  # cap word not at sentence start
    return {"has_context": has_name}


def build_metrics():
    rows = []
    for line in open(GEN):
        g = json.loads(line)
        base = {k: g[k] for k in ("id", "level", "language", "paraphrase",
                                  "topic", "model_family", "rep", "parse_status")}
        if g.get("parsed") and g["parse_status"] == "ok":
            problem = str(g["parsed"]["problem"])
            try:
                from langdetect import detect
                base["output_language"] = detect(problem)
            except Exception:
                base["output_language"] = "unknown"
            base.update(linguistic_metrics(problem))
            base.update(math_metrics(g["parsed"]))
            base.update(structure_metrics(problem))
            # FK/rare-word formulas are only valid for English text
            if base["output_language"] != "en":
                base["fk_grade"] = None
                base["rare_word_ratio"] = None
            base["problem_text"] = problem
            base["answer_text"] = str(g["parsed"]["answer"])
        rows.append(base)
    df = pd.DataFrame(rows)
    df.to_csv("data/metrics.csv", index=False)
    ok = (df.parse_status == "ok").mean()
    print(f"Wrote data/metrics.csv — {len(df)} rows, parse-ok rate {ok:.1%}")
    print("\nParse status by condition (refusals are an outcome — check this!):")
    print(df.groupby("language").parse_status.apply(lambda s: (s != "ok").mean()).round(3))
    return df


def sample_human_sheet(n=120, seed=42, families=None, batch="1"):
    """Stratified blinded sample for human rating. Condition labels are HIDDEN;
    the key file maps sheet rows back to conditions after rating.
    families: optional list to restrict (e.g. completed families only).
    Items already in earlier batches are never re-sampled."""
    df = pd.read_csv("data/metrics.csv")
    df = df[df.parse_status == "ok"]
    if families:
        df = df[df.model_family.isin(families)]
    # exclude items sampled in previous batches
    import glob
    prev = set()
    for f in glob.glob("data/human_rating_key_batch*.csv"):
        prev |= set(pd.read_csv(f)["id"])
    df = df[~df.id.isin(prev)]
    random.seed(seed)
    per_cell = max(1, n // (df.language.nunique() * df.model_family.nunique()))
    sample = (df.groupby(["language", "model_family"], group_keys=False)
                .apply(lambda g: g.sample(min(per_cell, len(g)), random_state=seed)))
    sample = sample.sample(frac=1, random_state=seed).reset_index(drop=True)  # shuffle
    sheet = sample[["id", "topic", "problem_text", "answer_text"]].copy()
    for col in ["correctness", "difficulty_alignment", "clarity",
                "pedagogical_soundness", "cultural_neutrality"]:
        sheet[col] = ""  # rater fills 1-5
    sheet.to_csv(f"data/human_rating_sheet_batch{batch}.csv", index=False)
    sample[["id", "level", "language", "paraphrase", "model_family"]].to_csv(
        f"data/human_rating_key_batch{batch}.csv", index=False)
    print(f"Wrote blinded sheet batch {batch} ({len(sheet)} items) + key. "
          "DO NOT look at the key until rating is finished.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--families", nargs="*", default=None)
    ap.add_argument("--n", type=int, default=120)
    ap.add_argument("--batch", default="1")
    args = ap.parse_args()
    if args.sample:
        sample_human_sheet(n=args.n, families=args.families, batch=args.batch)
    else:
        build_metrics()
