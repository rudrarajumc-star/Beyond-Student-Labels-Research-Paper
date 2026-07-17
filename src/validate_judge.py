"""Judge–human validity from a completed human rating sheet.

Computes, per rubric dimension: human mean, judge mean, exact agreement,
within-1 agreement, and Spearman rho (only where both raters have variance;
otherwise 'n/a*' for a ceiling effect). Mirrors data/judge_validation_batch1.csv.

WORKFLOW
  1. Generate a blinded sheet:
         python src/evaluate.py --sample --families llama --batch 2 --n 28
  2. Rate data/human_rating_sheet_batch2.csv by hand (fill the five 1-5 columns),
     WITHOUT looking at data/human_rating_key_batch2.csv. Save the filled file as
     data/human_ratings_batch2_scored.csv (or just fill the sheet in place).
  3. Run one of:
         python src/validate_judge.py --ratings data/human_ratings_batch2_scored.csv --batch 2
         python src/validate_judge.py --pooled            # combines every batch it finds

OUTPUT
  data/judge_validation_batch{B}.csv   (or data/judge_validation_pooled.csv)

The pre-registered pass mark is Spearman rho >= 0.5 on correctness (DESIGN.md 4.3).
Nothing here fills in ratings for you — that is the human's job, and doing it by
hand is what makes the validation meaningful.
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

DIMS = ["correctness", "difficulty_alignment", "clarity",
        "pedagogical_soundness", "cultural_neutrality"]


def load_judge_scores(path="data/judgments.jsonl"):
    """id -> {dimension: score} from the cross-family judge."""
    rows = {}
    with open(path) as fh:
        for line in fh:
            rec = json.loads(line)
            scores = rec.get("scores") or rec
            vals = {d: scores.get(d) for d in DIMS if scores.get(d) is not None}
            if vals:
                rows[rec["id"]] = vals
    return rows


def load_human_ratings(path):
    """Read a filled sheet or a scored file; return id -> {dimension: numeric}."""
    df = pd.read_csv(path)
    if "id" not in df.columns:
        raise SystemExit(f"{path}: no 'id' column found.")
    keep = ["id"] + [d for d in DIMS if d in df.columns]
    df = df[keep].copy()
    for d in DIMS:
        if d in df.columns:
            df[d] = pd.to_numeric(df[d], errors="coerce")
    # drop rows where every rating is blank (not yet rated)
    rated = df.dropna(subset=[d for d in DIMS if d in df.columns], how="all")
    return {r["id"]: {d: r[d] for d in DIMS if d in df.columns and pd.notna(r[d])}
            for _, r in rated.iterrows()}


def agreement_table(human, judge):
    """human, judge: id -> {dim: score}. Returns a DataFrame like judge_validation_batch1.csv."""
    out = []
    for dim in DIMS:
        h, j = [], []
        for _id, hv in human.items():
            if dim in hv and _id in judge and dim in judge[_id]:
                h.append(float(hv[dim]))
                j.append(float(judge[_id][dim]))
        n = len(h)
        if n == 0:
            out.append({"dimension": dim, "human_mean": None, "judge_mean": None,
                        "exact_agree": None, "within_1": None, "spearman": "n/a", "n": 0})
            continue
        h, j = np.array(h), np.array(j)
        exact = float(np.mean(np.round(h) == np.round(j)))
        within1 = float(np.mean(np.abs(h - j) <= 1))
        # Spearman only meaningful if BOTH sides vary (ceiling -> undefined)
        if h.std() > 0 and j.std() > 0:
            rho = round(float(stats.spearmanr(h, j).correlation), 2)
        else:
            rho = "n/a*"  # ceiling effect: one or both raters constant
        out.append({"dimension": dim,
                    "human_mean": round(float(h.mean()), 4),
                    "judge_mean": round(float(j.mean()), 4),
                    "exact_agree": round(exact, 4),
                    "within_1": round(within1, 4),
                    "spearman": rho, "n": n})
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ratings", help="a completed rating sheet / scored CSV")
    ap.add_argument("--batch", default=None, help="batch label for the output filename")
    ap.add_argument("--pooled", action="store_true",
                    help="combine every human_ratings_batch*_scored.csv found")
    args = ap.parse_args()

    judge = load_judge_scores()

    if args.pooled:
        human = {}
        paths = sorted(glob.glob("data/human_ratings_batch*_scored.csv"))
        if not paths:
            raise SystemExit("No data/human_ratings_batch*_scored.csv files found.")
        for p in paths:
            human.update(load_human_ratings(p))
        tag, sources = "pooled", ", ".join(os.path.basename(p) for p in paths)
    else:
        if not args.ratings:
            raise SystemExit("Provide --ratings <file> or --pooled.")
        human = load_human_ratings(args.ratings)
        tag = args.batch or "x"
        sources = os.path.basename(args.ratings)

    if not human:
        raise SystemExit("No completed ratings found (all five columns blank?).")

    table = agreement_table(human, judge)
    out_path = f"data/judge_validation_{'pooled' if args.pooled else 'batch' + str(tag)}.csv"
    table.to_csv(out_path, index=False)

    corr = table.loc[table.dimension == "correctness"].iloc[0]
    print(f"Source: {sources}  (n items with ratings: {len(human)})")
    print(table.to_string(index=False))
    print(f"\nWrote {out_path}")
    verdict = ("PASS" if isinstance(corr["spearman"], (int, float)) and corr["spearman"] >= 0.5
               else "below 0.5 or undefined — treat judge as exploratory")
    print(f"Pre-registered check (correctness Spearman >= 0.5): {corr['spearman']}  -> {verdict}")


if __name__ == "__main__":
    main()
