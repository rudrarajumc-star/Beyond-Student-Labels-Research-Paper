#!/usr/bin/env python3
"""
Regenerate every figure that appears in report/REPORT.md, at publication DPI.

All five figures are produced here directly from the raw data files
(data/metrics.csv, data/judgments.jsonl) and the derived tables in
results/tables/. No figure in the paper is drawn by hand or by any
generative tool; each one is the deterministic output of this script.

Usage:
    python3 src/make_report_figures.py [--dpi 300] [--outdir results/figures]

Outputs (also copied to arxiv/figures/ for the LaTeX build):
    effect_sizes_forest.png
    n_solution_steps_by_language.png
    fk_grade_by_language.png
    name_origin.png
    language_switch.png
"""
import argparse
import json
import os
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MAIN_FAMILIES = ["llama", "gptoss", "mistral"]
CONDITIONS = ["control", "multilingual", "ell_spanish", "ell_mandarin"]
COND_LABELS = ["control", "multilingual", "ELL-Spanish", "ELL-Mandarin"]
FAMILY_LABELS = {
    "llama": "Llama 3.3 70B",
    "gptoss": "GPT-OSS-120B",
    "mistral": "Mistral Small",
}
# Colour-blind-safe qualitative palette (Okabe-Ito subset)
FAMILY_COLORS = {"llama": "#0072B2", "gptoss": "#D55E00", "mistral": "#009E73"}

plt.rcParams.update({
    "font.family": "DejaVu Sans",   # sans-serif, journal-standard
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.autolayout": True,
})


def load_metrics(path="data/metrics.csv"):
    df = pd.read_csv(path)
    return df[df.model_family.isin(MAIN_FAMILIES) & (df.parse_status == "ok")].copy()


def _save(fig, name, outdir, dpi):
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, name)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    # keep the LaTeX build directory in sync
    arxiv_dir = os.path.join("arxiv", "figures")
    if os.path.isdir(arxiv_dir):
        shutil.copy2(out, os.path.join(arxiv_dir, name))
    print(f"  wrote {out} ({dpi} dpi)")


def fig_effect_sizes_forest(outdir, dpi):
    """Figure 1: forest plot of language effects on solution steps."""
    es = pd.read_csv("results/tables/effect_sizes.csv")
    es = es[es.outcome == "n_solution_steps"]
    order = MAIN_FAMILIES + ["POOLED"]
    rows = []
    for fam in order:
        for cond in ["multilingual", "ell_spanish", "ell_mandarin"]:
            r = es[(es.model_family == fam) & (es.condition == cond)]
            if len(r):
                rows.append((fam, cond, float(r.d_vs_control.iloc[0])))

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.axvspan(-0.2, 0.2, color="0.90", zorder=0,
               label="small effect (|d| < 0.2)")
    ax.axvline(0, color="0.35", lw=1, zorder=1)

    ypos, ylabels = [], []
    y = 0
    cond_marker = {"multilingual": "o", "ell_spanish": "s", "ell_mandarin": "^"}
    for fam in order:
        for cond in ["multilingual", "ell_spanish", "ell_mandarin"]:
            m = [r for r in rows if r[0] == fam and r[1] == cond]
            if not m:
                continue
            d = m[0][2]
            pooled = fam == "POOLED"
            ax.scatter(d, y,
                       marker="D" if pooled else cond_marker[cond],
                       s=85 if pooled else 55,
                       color="black" if pooled else FAMILY_COLORS[fam],
                       zorder=3)
            ylabels.append(("Pooled" if pooled else FAMILY_LABELS[fam]) + " — " +
                           dict(zip(["multilingual", "ell_spanish", "ell_mandarin"],
                                    ["multilingual", "ELL-Spanish", "ELL-Mandarin"]))[cond])
            ypos.append(y)
            y += 1
        y += 0.6

    ax.set_yticks(ypos)
    ax.set_yticklabels(ylabels)
    ax.invert_yaxis()
    ax.set_xlabel("Cohen's $d$ vs. control (solution steps)")
    ax.set_title("Effect of language label on math difficulty")
    ax.legend(loc="lower right", frameon=False)
    _save(fig, "effect_sizes_forest.png", outdir, dpi)


def fig_outcome_by_language(df, outcome, ylabel, title, fname, outdir, dpi,
                            english_only=False):
    """Figures 2 and 3: condition means per model, with standard-error bars."""
    d = df[df.output_language == "en"] if english_only else df
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    x = np.arange(len(CONDITIONS))
    for fam in MAIN_FAMILIES:
        sub = d[d.model_family == fam]
        means, ses = [], []
        for c in CONDITIONS:
            v = sub[sub.language == c][outcome].dropna()
            means.append(v.mean())
            ses.append(v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else 0.0)
        ax.errorbar(x, means, yerr=ses, marker="o", capsize=3, lw=1.6,
                    color=FAMILY_COLORS[fam], label=FAMILY_LABELS[fam])
    ax.set_xticks(x)
    ax.set_xticklabels(COND_LABELS)
    ax.set_xlabel("Language condition")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)
    _save(fig, fname, outdir, dpi)


def fig_name_origin(outdir, dpi):
    """Figure 4: name-origin distribution by condition."""
    ct = pd.read_csv("results/tables/h5_name_origin_crosstab.csv", index_col=0)
    ct = ct.reindex(CONDITIONS)
    cols = ["none", "anglo_other", "hispanic", "chinese"]
    labels = ["no name", "Anglo/other", "Hispanic-style", "Chinese-style"]
    colors = ["0.80", "#56B4E9", "#E69F00", "#CC79A7"]
    pct = ct[cols].div(ct[cols].sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    bottom = np.zeros(len(ct))
    for col, lab, col_c in zip(cols, labels, colors):
        ax.bar(COND_LABELS, pct[col], bottom=bottom, label=lab,
               color=col_c, edgecolor="white", linewidth=0.6)
        bottom += pct[col].values
    ax.set_ylabel("Percent of problems")
    ax.set_ylim(0, 100)
    ax.set_title("Person-name origin by language condition")
    ax.legend(frameon=False, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, -0.12))
    _save(fig, "name_origin.png", outdir, dpi)


def fig_language_switch(df, outdir, dpi):
    """Figure 5: unprompted output language by condition."""
    def bucket(v):
        if v == "en":
            return "English"
        if v == "es":
            return "Spanish"
        if v in ("zh-cn", "zh-tw"):
            return "Chinese"
        return "other / undetected"

    b = df.copy()
    b["bucket"] = b.output_language.map(bucket)
    order = ["English", "Spanish", "Chinese", "other / undetected"]
    colors = ["#0072B2", "#E69F00", "#CC79A7", "0.80"]
    pct = (pd.crosstab(b.language, b.bucket, normalize="index") * 100)
    pct = pct.reindex(index=CONDITIONS, columns=order).fillna(0.0)

    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    x = np.arange(len(CONDITIONS))
    w = 0.2
    for i, (col, c) in enumerate(zip(order, colors)):
        ax.bar(x + (i - 1.5) * w, pct[col], w, label=col, color=c)
    ax.set_xticks(x)
    ax.set_xticklabels(COND_LABELS)
    ax.set_ylabel("Percent of readable problems")
    ax.set_xlabel("Language condition")
    ax.set_title("Unprompted output language by condition")
    ax.legend(frameon=False, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, -0.15))
    _save(fig, "language_switch.png", outdir, dpi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dpi", type=int, default=300,
                    help="output resolution (journals require >= 300)")
    ap.add_argument("--outdir", default="results/figures")
    a = ap.parse_args()

    df = load_metrics()
    print(f"Regenerating report figures at {a.dpi} dpi from {len(df)} readable items")
    fig_effect_sizes_forest(a.outdir, a.dpi)
    fig_outcome_by_language(
        df, "n_solution_steps", "Solution steps (mean ± SE)",
        "Math difficulty by language condition",
        "n_solution_steps_by_language.png", a.outdir, a.dpi)
    fig_outcome_by_language(
        df, "fk_grade", "Flesch–Kincaid grade (mean ± SE)",
        "Reading grade by language condition (English outputs)",
        "fk_grade_by_language.png", a.outdir, a.dpi, english_only=True)
    fig_name_origin(a.outdir, a.dpi)
    fig_language_switch(df, a.outdir, a.dpi)
    print("done")


if __name__ == "__main__":
    main()
