"""Pre-registered statistical analysis (DESIGN.md §5).

Inputs:  data/metrics.csv, data/judgments.jsonl, (optional) data/human_rating_sheet.csv
Outputs: results/tables/*.csv, results/figures/*.png, results/summary.txt

Usage:   python src/analyze.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

OUTCOMES_MATH = ["n_solution_steps", "n_operations", "max_operand_magnitude"]
OUTCOMES_LING = ["fk_grade", "mean_sentence_len", "rare_word_ratio"]
JUDGE_DIMS = ["correctness", "difficulty_alignment", "clarity",
              "pedagogical_soundness", "cultural_neutrality"]


def load():
    df = pd.read_csv("data/metrics.csv")
    # 2026-04-07 amendment (DESIGN.md §6b): gemini dropped from confirmatory analysis (28/540 collected)
    df = df[df.model_family != "gemini"]
    if os.path.exists("data/judgments.jsonl"):
        j = []
        for line in open("data/judgments.jsonl"):
            r = json.loads(line)
            if r.get("scores"):
                j.append({"id": r["id"], **{k: r["scores"].get(k) for k in JUDGE_DIMS}})
        if j:
            df = df.merge(pd.DataFrame(j), on="id", how="left")
    return df


def cohens_d(a, b):
    a, b = a.dropna(), b.dropna()
    if len(a) < 2 or len(b) < 2:
        return np.nan
    sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp if sp else np.nan


def regressions(df, outcomes, tag, out):
    """Primary pre-registered model with HC3 robust SEs."""
    rows = []
    for y in outcomes:
        d = df.dropna(subset=[y])
        if d[y].nunique() < 3 or len(d) < 100:
            continue
        m = smf.ols(f"{y} ~ C(level, Treatment('on_grade')) * "
                    f"C(language, Treatment('control')) + C(paraphrase) + "
                    f"C(topic) + C(model_family)", data=d).fit(cov_type="HC3")
        for name, coef, p, lo, hi in zip(m.params.index, m.params, m.pvalues,
                                         m.conf_int()[0], m.conf_int()[1]):
            if "language" in name:
                rows.append({"outcome": y, "term": name, "coef": coef,
                             "p": p, "ci_lo": lo, "ci_hi": hi, "n": len(d)})
        out.write(f"\n===== {tag}: {y} =====\n{m.summary().as_text()}\n")
    res = pd.DataFrame(rows)
    if not res.empty:
        # Holm-Bonferroni within family
        res = res.sort_values("p").reset_index(drop=True)
        m_ = len(res)
        res["p_holm"] = [min(1, p * (m_ - i)) for i, p in enumerate(res.p)]
    res.to_csv(f"results/tables/language_effects_{tag}.csv", index=False)
    return res


def effect_sizes(df):
    """H2 headline: Cohen's d of each language condition vs control, math outcomes,
    per model family and pooled."""
    rows = []
    for y in OUTCOMES_MATH + OUTCOMES_LING:
        if y not in df:
            continue
        for fam in list(df.model_family.unique()) + ["POOLED"]:
            d = df if fam == "POOLED" else df[df.model_family == fam]
            ctrl = d[d.language == "control"][y]
            for lang in ["multilingual", "ell_spanish", "ell_mandarin"]:
                rows.append({"outcome": y, "model_family": fam, "condition": lang,
                             "d_vs_control": cohens_d(d[d.language == lang][y], ctrl)})
    es = pd.DataFrame(rows)
    es.to_csv("results/tables/effect_sizes.csv", index=False)
    return es


def paraphrase_brittleness(df):
    """H4: range of the ELL-vs-control gap across paraphrases."""
    rows = []
    for y in OUTCOMES_MATH:
        if y not in df:
            continue
        for p in df.paraphrase.unique():
            d = df[df.paraphrase == p]
            gap = cohens_d(d[d.language.isin(["ell_spanish", "ell_mandarin"])][y],
                           d[d.language == "control"][y])
            rows.append({"outcome": y, "paraphrase": p, "ell_gap_d": gap})
    b = pd.DataFrame(rows)
    b.to_csv("results/tables/paraphrase_brittleness.csv", index=False)
    return b


def refusal_analysis(df, out):
    """Refusal/parse-failure rate by condition — chi-square."""
    df["failed"] = (df.parse_status != "ok").astype(int)
    tab = pd.crosstab(df.language, df.failed)
    if tab.shape[1] == 2 and tab[1].sum() > 0:
        chi2, p, _, _ = stats.chi2_contingency(tab)
        out.write(f"\nParse-failure x language: chi2={chi2:.2f}, p={p:.4f}\n{tab}\n")


def plots(df, es):
    os.makedirs("results/figures", exist_ok=True)
    # Headline figure: math difficulty by language condition, per model
    for y in ["n_solution_steps", "fk_grade"]:
        if y not in df:
            continue
        fig, ax = plt.subplots(figsize=(9, 5))
        order = ["control", "multilingual", "ell_spanish", "ell_mandarin"]
        for i, fam in enumerate(sorted(df.model_family.unique())):
            d = df[df.model_family == fam]
            means = [d[d.language == l][y].mean() for l in order]
            sems = [d[d.language == l][y].sem() for l in order]
            x = np.arange(len(order)) + i * 0.18
            ax.errorbar(x, means, yerr=sems, marker="o", capsize=3, label=fam)
        ax.set_xticks(np.arange(len(order)) + 0.27)
        ax.set_xticklabels(order)
        ax.set_ylabel(y)
        ax.set_title(f"{y} by language condition (7th grade, all levels pooled)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"results/figures/{y}_by_language.png", dpi=150)
        plt.close(fig)


def human_judge_validity(out):
    sheet = "data/human_rating_sheet.csv"
    if not os.path.exists(sheet):
        return
    h = pd.read_csv(sheet)
    if h["correctness"].isna().all() or (h["correctness"] == "").all():
        out.write("\nHuman ratings not yet completed — judge validity unverified. "
                  "Judge scores must be reported as EXPLORATORY until this is done.\n")
        return
    j = load()[["id"] + JUDGE_DIMS]
    m = h.merge(j, on="id", suffixes=("_human", "_judge"))
    out.write("\nJudge validity (Spearman rho, human vs judge):\n")
    for dim in JUDGE_DIMS:
        a = pd.to_numeric(m[f"{dim}_human"], errors="coerce")
        b = pd.to_numeric(m[f"{dim}_judge"], errors="coerce")
        ok = a.notna() & b.notna()
        if ok.sum() > 10:
            rho, p = stats.spearmanr(a[ok], b[ok])
            flag = "PASS" if rho >= 0.5 else "FAIL (report judge as exploratory)"
            out.write(f"  {dim}: rho={rho:.2f} (p={p:.3f}) {flag}\n")


if __name__ == "__main__":
    os.makedirs("results/tables", exist_ok=True)
    df = load()
    with open("results/summary.txt", "w") as out:
        out.write(f"N total: {len(df)}; parse-ok: {(df.parse_status == 'ok').mean():.1%}\n")
        refusal_analysis(df, out)
        ok = df[df.parse_status == "ok"].copy()
        regressions(ok, OUTCOMES_MATH, "math", out)
        regressions(ok, OUTCOMES_LING, "linguistic", out)
        if "correctness" in ok:
            regressions(ok, JUDGE_DIMS, "judge", out)
        es = effect_sizes(ok)
        paraphrase_brittleness(ok)
        plots(ok, es)
        human_judge_validity(out)
    print("Wrote results/summary.txt, results/tables/, results/figures/")
