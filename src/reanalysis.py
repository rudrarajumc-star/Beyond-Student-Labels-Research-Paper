#!/usr/bin/env python3
"""
reanalysis.py - the corrected analysis behind the SIMBig 2026 / Springer CCIS
camera-ready version of "Beyond Student Labels".

    python3 src/reanalysis.py > results/reanalysis_output.txt

PROVENANCE, STATED PLAINLY
--------------------------
The original reanalysis.py was lost in a local disk cleanup in October 2026.
This file is a RECONSTRUCTION, rebuilt from the committed raw data against the
numbers printed in the paper. It is not the original file byte-for-byte.

It reproduces EXACTLY, from data/ alone:

  * the sample counts and the parse-failure test        (Sect. 4)
  * the entire primary model - H1, H2 and Table 1,
    every coefficient, p-value, CI, Cohen's d and
    Holm-corrected p                                     (Sect. 4.1, 4.2)
  * the output-language table, including the independent
    check that langdetect had mislabelled 152 English
    problems, 45 of them controls                        (Sect. 3.2, 4.6)
  * the clustered-standard-error robustness check        (Sect. 4.5)
  * the English-only subsample size, n = 1,271           (Sect. 4.4, 4.5)
  * the answer-key rates by model and by condition       (Sect. 4.7)
  * the correct-key subset, n = 1,220, and its
    reduced effects                                      (Sect. 5)

Four secondary quantities do NOT reproduce exactly, because the original
script's heuristics were not recorded in the paper. Each is flagged inline
below with the paper's value:

  1. Near-duplicate removal. The paper reports 106 removed; this greedy,
     order-dependent procedure removes 107. The de-duplicated p-values differ
     in the third decimal and the conclusion is unchanged.
  2. Reading grade (H3). The subsample size (n = 1,271) matches exactly but the
     coefficients differ; the original's Flesch-Kincaid implementation and its
     sentence segmentation were not fully specified in the paper.
  3. The bilingual marker count (25 here, 29 in the paper).
  4. The name-origin coding, which the original applied to judge-extracted
     names with a hand-built origin lexicon that was not recorded.

For the published numbers, src/verify_paper.py is the authority: it recomputes
69 values straight from data/ and checks each against the paper, exiting
non-zero on any mismatch. Nothing in this file contradicts it.

Specification (same as verify_paper.py):

    outcome ~ C(level, Treatment("on_grade"))
            + C(language, Treatment("control"))
            + C(model_family) + C(topic) + C(paraphrase)

with HC3 robust standard errors and Holm correction across the nine primary
tests (3 math outcomes x 3 language labels).

Requires pandas, numpy, scipy, statsmodels. Tested on Python 3.9-3.13.
"""

import difflib
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

PRIMARY = ('{y} ~ C(level, Treatment("on_grade")) + C(language, Treatment("control"))'
           ' + C(model_family) + C(topic) + C(paraphrase)')
MATH = ["n_solution_steps", "n_operations", "max_operand_magnitude"]
LABELS = ["ell_mandarin", "ell_spanish", "multilingual"]
LEVELS = ["advanced", "struggling"]
EXCLUDED = "gemini"
CELL_KEYS = ["model_family", "language", "level", "topic"]
DUP_THRESHOLD = 0.975

# Deterministic output-language rule. Replaces langdetect, which had labelled
# 152 English problems as other languages.
ES_STOP = set("el la los las un una de del y en con por para que es son se su al lo "
              "como mas si no entre".split())
EN_STOP = set("the a an of and in with by for that is are be to on at it as from how "
              "many much solve equation".split())


# --------------------------------------------------------------------------

def hr(title):
    print("\n== " + title + " ==")


def fit(df, outcome, formula=PRIMARY, cluster=None):
    sub = df.dropna(subset=[outcome])
    model = smf.ols(formula.format(y=outcome), data=sub)
    if cluster is not None:
        return model.fit(cov_type="cluster", cov_kwds={"groups": sub[cluster]})
    return model.fit(cov_type="HC3")


def grab(model, name):
    ci = model.conf_int()
    for p in model.params.index:
        if ("[T." + name + "]") in p:
            return model.params[p], model.pvalues[p], ci.loc[p, 0], ci.loc[p, 1]
    raise KeyError(name)


def holm_nine(frame):
    rows, ps, keys = [], [], []
    for y in MATH:
        res = fit(frame, y)
        for lab in LABELS:
            c, p, _, _ = grab(res, lab)
            rows.append({"outcome": y, "term": lab, "coef": c})
            ps.append(p)
            keys.append((y, lab))
    _, adj, _, _ = multipletests(ps, method="holm")
    out = pd.DataFrame(rows)
    out["p_holm9"] = adj
    return out


def output_language(text):
    """Chinese if more than 20% of characters are Han; otherwise Spanish if
    Spanish stopwords outnumber English ones; otherwise English."""
    t = str(text)
    if len(re.findall(r"[一-鿿]", t)) / max(1, len(t)) > 0.20:
        return "zh"
    words = re.findall(r"[a-záéíóúñü]+", t.lower())
    es = sum(1 for w in words if w in ES_STOP)
    en = sum(1 for w in words if w in EN_STOP)
    return "es" if es > en else "en"


def normalise(text):
    return " ".join(str(text).lower().split())


def drop_near_duplicates(frame, threshold=DUP_THRESHOLD, keys=CELL_KEYS):
    """Greedy pairwise removal of near-identical problem statements, within
    each model x label x level x topic cell. Order-dependent by construction:
    each item is compared against those already kept. The length band and
    difflib's cheap ratio bounds are speed-ups only and cannot change which
    pairs clear the threshold."""
    keep = []
    for _, group in frame.groupby(keys, sort=False):
        kept = []
        for idx, raw in zip(group.index, group.problem_text.fillna("").astype(str)):
            t = normalise(raw)
            n = len(t)
            duplicate = False
            matcher = difflib.SequenceMatcher(None, "", t, autojunk=False)
            for prev, prev_n in kept:
                if 2.0 * min(n, prev_n) / max(1, n + prev_n) <= threshold:
                    continue
                matcher.set_seq1(prev)
                if matcher.real_quick_ratio() <= threshold:
                    continue
                if matcher.quick_ratio() <= threshold:
                    continue
                if matcher.ratio() > threshold:
                    duplicate = True
                    break
            if not duplicate:
                keep.append(idx)
                kept.append((t, n))
    return frame.loc[keep]


def load():
    metrics = pd.read_csv(os.path.join(DATA, "metrics.csv"))
    d = metrics[(metrics.model_family != EXCLUDED)
                & (metrics.parse_status == "ok")].copy()
    scores = {}
    with open(os.path.join(DATA, "judgments.jsonl")) as fh:
        for line in fh:
            rec = json.loads(line)
            scores[rec["id"]] = (rec.get("scores") or {}).get("correctness")
    d["correctness"] = d["id"].map(scores)
    d["lang_rule"] = [output_language(t) for t in d.problem_text.fillna("")]
    d["cell"] = d[CELL_KEYS + ["paraphrase"]].astype(str).agg("|".join, axis=1)
    return metrics, d


# --------------------------------------------------------------------------

def section_sample(metrics, d):
    hr("1. Sample")
    full = metrics[metrics.model_family != EXCLUDED]
    print("generations={0} readable={1} ({2:.1f}%)".format(
        len(full), len(d), 100.0 * len(d) / len(full)))
    tab = pd.crosstab(full.language, full.parse_status == "ok")
    chi2, p, _, _ = stats.chi2_contingency(tab)
    print("parse failure by language: chi2({0})={1:.2f}, p={2:.2f}".format(
        tab.shape[0] - 1, chi2, p))
    for fam in sorted(full.model_family.unique()):
        f = full[full.model_family == fam]
        bad = f[f.parse_status != "ok"]
        print("  {0}: unreadable {1} ({2:.1f}%); at advanced level {3}".format(
            fam, len(bad), 100.0 * len(bad) / len(f), (bad.level == "advanced").sum()))
    gem = metrics[metrics.model_family == EXCLUDED]
    print("Gemini (dropped): requests answered {0} of 540; parsed {1}".format(
        len(gem), (gem.parse_status == "ok").sum()))


def section_primary(d):
    hr("2. Primary model: additive, HC3, Holm over nine tests (H1, H2, Table 1)")
    rows, ps, keys = [], [], []
    for y in MATH:
        res = fit(d, y)
        sd = d[y].dropna().std(ddof=1)
        for term in LEVELS + LABELS:
            c, p, lo, hi = grab(res, term)
            rows.append({"outcome": y, "term": term, "coef": c, "p": p,
                         "lo": lo, "hi": hi, "d": c / sd})
            if term in LABELS:
                ps.append(p)
                keys.append((y, term))
    _, adj, _, _ = multipletests(ps, method="holm")
    hmap = dict(zip(keys, adj))
    tab = pd.DataFrame(rows)
    tab["p_holm9"] = [hmap.get((r.outcome, r.term), np.nan) for r in tab.itertuples()]
    with pd.option_context("display.width", 200, "display.max_columns", 20):
        print(tab.to_string(index=False, float_format=lambda x: "{0:.4f}".format(x)))

    dd = d.copy()
    dd["log10_largest"] = np.log10(dd.max_operand_magnitude.clip(lower=1))
    res = fit(dd, "log10_largest")
    print("\nlog10(largest number), post hoc:")
    for term in LEVELS + LABELS:
        c, p, _, _ = grab(res, term)
        print("  {0:<14}{1:+.4f}  p={2:.4f}".format(term, c, p))


def section_interaction(d):
    hr("3. Ability x language (the interacted model written in DESIGN.md)")
    formula = ('{y} ~ C(level, Treatment("on_grade")) * C(language, Treatment("control"))'
               ' + C(model_family) + C(topic) + C(paraphrase)')
    for y in ["n_solution_steps", "n_operations"]:
        res = fit(d, y, formula)
        inter = [p for p in res.params.index if ":" in p]
        idx = [list(res.params.index).index(i) for i in inter]
        test = res.f_test(np.eye(len(res.params))[idx])
        print("{0}: joint interaction chi2({1})={2:.2f}, p={3:.3f}".format(
            y, len(inter), float(test.fvalue) * len(inter), float(test.pvalue)))
        for lab in LABELS:
            parts = []
            for lev in ["on_grade", "struggling", "advanced"]:
                sub = d[(d.level == lev) & (d.language.isin(["control", lab]))]
                mm = smf.ols('{0} ~ C(language, Treatment("control")) + C(model_family)'
                             ' + C(topic) + C(paraphrase)'.format(y),
                             data=sub.dropna(subset=[y])).fit(cov_type="HC3")
                c, p, _, _ = grab(mm, lab)
                parts.append("{0} {1:.2f} (p={2:.3f})".format(lev, c, p))
            print("  {0}: {1}".format(lab, "; ".join(parts)))


def section_language(d):
    hr("4. Output language (deterministic rule)")
    print(pd.crosstab(d.language, d.lang_rule).to_string())
    print()
    print((pd.crosstab(d.language, d.lang_rule, normalize="index") * 100).round(1).to_string())

    switched = d[d.language.isin(["ell_spanish", "ell_mandarin"])].copy()
    switched["switched"] = [
        (rule == "es" if lang == "ell_spanish" else rule == "zh")
        for lang, rule in zip(switched.language, switched.lang_rule)]
    print("\nswitch rate by label and model:")
    print(switched.groupby(["language", "model_family"])
          .switched.agg(["mean", "sum", "count"]).round(3).to_string())

    english = d[d.lang_rule == "en"]
    mismatch = english[english.output_language != "en"]
    print("\nEnglish by rule: {0}; of these langdetect had labelled {1} as another"
          " language ({2} were controls)".format(
              len(english), len(mismatch), (mismatch.language == "control").sum()))

    g = d[(d.model_family == "gptoss") & (d.language == "ell_spanish")]
    bilingual = sum(1 for t in g.problem_text.fillna("").astype(str)
                    if any(w in ES_STOP for w in re.findall(r"[a-záéí"
                                                            r"óúñü]+",
                                                            t.lower())))
    print("GPT-OSS ELL-Spanish problems containing Spanish markers: {0} of {1}"
          "   [paper: 29 of 135 - see the provenance note]".format(bilingual, len(g)))


def section_reading(d):
    hr("5. Reading grade, English output only (H3)")
    en = d[(d.lang_rule == "en")].dropna(subset=["fk_grade"])
    sd = en.fk_grade.std(ddof=1)
    print("n={0}".format(len(en)))
    res = fit(en, "fk_grade")
    for lab in LABELS:
        c, p, _, _ = grab(res, lab)
        print("  {0:<14}{1:+.4f}  p={2:.4f}  d={3:+.3f}".format(lab, c, p, c / sd))
    print("  [paper: ELL-Mandarin -0.77 p=.0003; ELL-Spanish +0.03 p=.94;"
          " multilingual -0.42 p=.046 - see the provenance note]")


def section_robustness(d):
    hr("6. Robustness (nine-test Holm throughout)")
    print("clustered on {0} design cells".format(d.cell.nunique()))
    rows, ps, keys = [], [], []
    for y in MATH:
        res = fit(d, y, cluster="cell")
        for lab in LABELS:
            c, p, _, _ = grab(res, lab)
            rows.append({"outcome": y, "term": lab, "coef": c})
            ps.append(p)
            keys.append((y, lab))
    _, adj, _, _ = multipletests(ps, method="holm")
    tab = pd.DataFrame(rows)
    tab["p_holm9"] = adj
    print(tab.to_string(index=False, float_format=lambda x: "{0:.4f}".format(x)))

    dedup = drop_near_duplicates(d)
    print("\nnear-duplicates removed: {0}; n={1}   [paper: 106 removed, n=1461]".format(
        len(d) - len(dedup), len(dedup)))
    print(holm_nine(dedup).to_string(index=False, float_format=lambda x: "{0:.4f}".format(x)))

    english = d[d.lang_rule == "en"]
    print("\nEnglish-only output: n={0}".format(len(english)))
    print(holm_nine(english).to_string(index=False, float_format=lambda x: "{0:.4f}".format(x)))

    print("\nH4: Cohen's d of the pooled ELL contrast, by prompt wording")
    for y in MATH:
        ds = []
        for wording in sorted(d.paraphrase.unique()):
            sub = d[(d.paraphrase == wording)
                    & (d.language.isin(["control", "ell_spanish", "ell_mandarin"]))]
            mm = smf.ols('{0} ~ C(language, Treatment("control")) + C(level)'
                         ' + C(model_family) + C(topic)'.format(y),
                         data=sub.dropna(subset=[y])).fit(cov_type="HC3")
            ds.append(np.mean([grab(mm, l)[0] for l in ["ell_mandarin", "ell_spanish"]])
                      / sub[y].std(ddof=1))
        print("  {0}: {1}  range {2:.3f}".format(y, np.round(ds, 3).tolist(),
                                                 max(ds) - min(ds)))


def section_keys(d):
    hr("7. Answer keys and judge validity")
    flagged = d.correctness < 5
    print("judge flags a wrong key in {0:.1f}% of problems".format(100.0 * flagged.mean()))
    by_model = {f: round(100.0 * (g.correctness < 5).mean(), 1)
                for f, g in d.groupby("model_family")}
    by_label = {f: round(100.0 * (g.correctness < 5).mean(), 1)
                for f, g in d.groupby("language")}
    print("  by model: {0}".format(by_model))
    print("  by label: {0}".format(by_label))

    hr("8. The correct-key subset (the paper's largest caveat, Sect. 5)")
    ok = d[d.correctness >= 5]
    print("problems whose key the judge accepted: n={0}".format(len(ok)))
    res = fit(ok, "n_solution_steps")
    for lab in LABELS:
        c, p, _, _ = grab(res, lab)
        print("  solution steps  {0:<14}{1:+.3f}  p={2:.4f}".format(lab, c, p))


def main():
    metrics, d = load()
    print("Beyond Student Labels - corrected analysis (reconstruction)")
    print("see the module docstring for what does and does not reproduce exactly")
    print("pandas {0}, numpy {1}, python {2}".format(
        pd.__version__, np.__version__, sys.version.split()[0]))
    section_sample(metrics, d)
    section_primary(d)
    section_interaction(d)
    section_language(d)
    section_reading(d)
    section_robustness(d)
    section_keys(d)
    print("\ndone.")


if __name__ == "__main__":
    main()
