#!/usr/bin/env python3
"""
verify_paper.py - recompute every headline number in the SIMBig 2026 /
Springer CCIS camera-ready version of "Beyond Student Labels" from the raw
data in data/, and check each one against the value printed in the paper.

    pip3 install -r requirements.txt
    python3 src/verify_paper.py

Every claim prints PASS or FAIL with the paper's value next to the recomputed
one. The script exits 1 if anything fails. No API keys needed; it reads the
committed data only.

Why this file exists
--------------------
src/analyze.py estimated the language effect from an ability x language
interaction with on-grade as the reference category, which identifies the
effect for on-grade students only - and on-grade is the single ability level
where no effect appears. The reviewed version of the paper reported that null
as the result. The camera-ready reports the effect averaged over ability
levels, which is what hypothesis H2 was about. See CORRECTIONS.md.

Primary specification:

    outcome ~ C(level, Treatment("on_grade"))
            + C(language, Treatment("control"))
            + C(model_family) + C(topic) + C(paraphrase)

with HC3 robust standard errors and Holm correction across the nine primary
tests (3 math outcomes x 3 language labels).

Tested on Python 3.9-3.13.
"""

import json
import os
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
EXCLUDED = "gemini"

FAILURES = []


def check(section, claim, paper, got, tol):
    ok = abs(got - paper) <= tol
    if not ok:
        FAILURES.append((section, claim, paper, got))
    print("  [{0}] {1:<44} paper {2:>10}   recomputed {3:>10}".format(
        "PASS" if ok else "FAIL", claim, "{0:g}".format(paper),
        "{0:.4f}".format(got).rstrip("0").rstrip(".")))


def check_lt(section, claim, bound, got):
    ok = got < bound
    if not ok:
        FAILURES.append((section, claim, bound, got))
    print("  [{0}] {1:<44} paper {2:>10}   recomputed {3:>10}".format(
        "PASS" if ok else "FAIL", claim, "< {0:g}".format(bound), "{0:.5f}".format(got)))


def hr(title):
    print("\n" + title)
    print("-" * len(title))


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


def holm_nine(d):
    ps, keys = [], []
    for y in MATH:
        m = fit(d, y)
        for lab in LABELS:
            ps.append(grab(m, lab)[1])
            keys.append((y, lab))
    _, adj, _, _ = multipletests(ps, method="holm")
    return dict(zip(keys, adj))


def load():
    m = pd.read_csv(os.path.join(DATA, "metrics.csv"))
    d = m[(m.model_family != EXCLUDED) & (m.parse_status == "ok")].copy()
    scores = {}
    with open(os.path.join(DATA, "judgments.jsonl")) as fh:
        for line in fh:
            r = json.loads(line)
            scores[r["id"]] = (r.get("scores") or {}).get("correctness")
    d["correctness"] = d["id"].map(scores)
    return m, d


def main():
    print("Beyond Student Labels - verification of the camera-ready paper")
    print("pandas {0} | numpy {1} | python {2}".format(
        pd.__version__, np.__version__, sys.version.split()[0]))

    m, d = load()
    full = m[m.model_family != EXCLUDED]

    hr("Sections 3.1 and 4 - sample")
    check("4", "generations", 1620, float(len(full)), 0)
    check("4", "readable JSON", 1567, float(len(d)), 0)
    check("4", "readable %", 96.7, 100.0 * len(d) / len(full), 0.05)
    tab = pd.crosstab(full.language, full.parse_status == "ok")
    chi2, p, _, _ = stats.chi2_contingency(tab)
    check("4", "parse failure x language, chi2", 3.34, chi2, 0.01)
    check("4", "parse failure x language, p", 0.34, p, 0.005)
    gem = m[m.model_family == EXCLUDED]
    check("3.1", "Gemini requests answered", 138, float(len(gem)), 0)
    check("3.1", "Gemini parsed", 29, float((gem.parse_status == "ok").sum()), 0)

    models = {y: fit(d, y) for y in MATH}
    holm = holm_nine(d)

    hr("Section 4.1 - H1 manipulation check (advanced vs on-level)")
    for y, claim, paper, tol in [
            ("n_solution_steps", "advanced -> solution steps", 1.19, 0.01),
            ("n_operations", "advanced -> operations", 7.04, 0.01),
            ("max_operand_magnitude", "advanced -> largest number", 115.0, 0.5)]:
        c, p, _, _ = grab(models[y], "advanced")
        check("4.1", claim, paper, c, tol)
        check_lt("4.1", claim + ", p", 0.001, p)
    for y, claim, paper in [
            ("n_solution_steps", "struggling -> steps, p", 0.91),
            ("n_operations", "struggling -> operations, p", 0.61),
            ("max_operand_magnitude", "struggling -> largest number, p", 0.63)]:
        check("4.1", claim, paper, grab(models[y], "struggling")[1], 0.006)

    hr("Table 1 - ability label vs language labels, uncorrected")
    dd = d.copy()
    dd["log10_largest"] = np.log10(dd.max_operand_magnitude.clip(lower=1))
    log_model = fit(dd, "log10_largest")
    check("T1", "struggling -> steps", -0.01, grab(models["n_solution_steps"], "struggling")[0], 0.006)
    check("T1", "struggling -> operations", 0.34, grab(models["n_operations"], "struggling")[0], 0.006)
    check("T1", "struggling -> log10(largest)", 0.01, grab(log_model, "struggling")[0], 0.006)
    for lab, s_c, s_p, o_c, o_p, l_c, l_p in [
            ("ell_spanish", -0.52, 0.0010, -2.61, 0.0099, -0.10, 0.0011),
            ("ell_mandarin", -0.65, 0.0001, -4.24, 0.0001, -0.08, 0.0075)]:
        c, p, _, _ = grab(models["n_solution_steps"], lab)
        check("T1", lab + " -> steps", s_c, c, 0.006)
        if lab == "ell_spanish":
            check("T1", lab + " -> steps, p", s_p, p, 0.0002)
        else:
            check_lt("T1", lab + " -> steps, p", 0.0001, p)
        c, p, _, _ = grab(models["n_operations"], lab)
        check("T1", lab + " -> operations", o_c, c, 0.006)
        if lab == "ell_spanish":
            check("T1", lab + " -> operations, p", o_p, p, 0.0002)
        else:
            check_lt("T1", lab + " -> operations, p", 0.0001, p)
        c, p, _, _ = grab(log_model, lab)
        check("T1", lab + " -> log10(largest)", l_c, c, 0.006)
        check("T1", lab + " -> log10(largest), p", l_p, p, 0.0002)

    hr("Section 4.2 - H2, Holm-corrected over the nine primary tests")
    for y, lab, coef, lo, hi, dv, ph in [
            ("n_solution_steps", "ell_mandarin", -0.65, -0.96, -0.35, -0.26, 0.0002),
            ("n_operations", "ell_mandarin", -4.24, -6.15, -2.33, -0.26, 0.0001),
            ("n_solution_steps", "ell_spanish", -0.52, -0.84, -0.21, -0.21, 0.0067)]:
        c, _, clo, chi = grab(models[y], lab)
        sd = d[y].dropna().std(ddof=1)
        pretty = {"ell_mandarin": "ELL-Mandarin", "ell_spanish": "ELL-Spanish"}[lab]
        tag = pretty + " -> " + {"n_solution_steps": "steps", "n_operations": "operations"}[y]
        check("4.2", tag, coef, c, 0.006)
        check("4.2", tag + ", CI low", lo, clo, 0.006)
        check("4.2", tag + ", CI high", hi, chi, 0.006)
        check("4.2", tag + ", Cohen's d", dv, c / sd, 0.006)
        check("4.2", tag + ", Holm p", ph, holm[(y, lab)], 0.0002)
    check("4.2", "ELL-Spanish -> operations, Holm p", 0.059, holm[("n_operations", "ell_spanish")], 0.0006)
    check("4.2", "multilingual -> steps", -0.08, grab(models["n_solution_steps"], "multilingual")[0], 0.006)
    check("4.2", "multilingual -> steps, p", 0.68, grab(models["n_solution_steps"], "multilingual")[1], 0.006)
    worst = min(grab(models["max_operand_magnitude"], l)[1] for l in LABELS)
    ok = worst > 0.16
    if not ok:
        FAILURES.append(("4.2", "largest number raw, all p > .16", 0.16, worst))
    print("  [{0}] {1:<44} paper {2:>10}   recomputed {3:>10}".format(
        "PASS" if ok else "FAIL", "largest number (raw), smallest p", "> .16", "{0:.4f}".format(worst)))
    check("4.2", "multilingual -> log10(largest), p", 0.018, grab(log_model, "multilingual")[1], 0.0006)

    hr("Section 4.5 - robustness: standard errors clustered on design cells")
    dc = d.copy()
    dc["cell"] = (dc.model_family + "|" + dc.level + "|" + dc.language + "|"
                  + dc.topic + "|" + dc.paraphrase.astype(str))
    check("4.5", "number of design cells", 539, float(dc.cell.nunique()), 0)
    ps, keys = [], []
    for y in MATH:
        mdl = fit(dc, y, cluster="cell")
        for lab in LABELS:
            ps.append(grab(mdl, lab)[1])
            keys.append((y, lab))
    _, adj, _, _ = multipletests(ps, method="holm")
    cl = dict(zip(keys, adj))
    check("4.5", "clustered, Mandarin -> steps", 0.0011, cl[("n_solution_steps", "ell_mandarin")], 0.0002)
    check("4.5", "clustered, Mandarin -> operations", 0.0003, cl[("n_operations", "ell_mandarin")], 0.0002)
    check("4.5", "clustered, Spanish -> steps", 0.028, cl[("n_solution_steps", "ell_spanish")], 0.0006)
    check("4.5", "clustered, Spanish -> operations", 0.075, cl[("n_operations", "ell_spanish")], 0.0006)

    hr("Section 4.7 - answer keys flagged by the cross-family judge")
    check("4.7", "wrong key, overall %", 22.1, 100.0 * (d.correctness < 5).mean(), 0.05)
    for fam, paper in [("llama", 38.5), ("mistral", 28.9), ("gptoss", 0.4)]:
        g = d[d.model_family == fam]
        check("4.7", "wrong key, " + fam + " %", paper, 100.0 * (g.correctness < 5).mean(), 0.05)
    for lab, paper in [("control", 25.8), ("ell_mandarin", 18.8), ("ell_spanish", 18.5)]:
        g = d[d.language == lab]
        check("4.7", "wrong key, " + lab + " %", paper, 100.0 * (g.correctness < 5).mean(), 0.05)

    hr("Section 5 - the correct-key subset (the paper's largest caveat)")
    okd = d[d.correctness >= 5]
    check("5", "problems whose key the judge accepted", 1220, float(len(okd)), 0)
    mk = fit(okd, "n_solution_steps")
    c, p, _, _ = grab(mk, "ell_mandarin")
    check("5", "correct keys only, Mandarin -> steps", -0.33, c, 0.006)
    check("5", "correct keys only, Mandarin -> steps, p", 0.008, p, 0.0006)
    c, p, _, _ = grab(mk, "ell_spanish")
    check("5", "correct keys only, Spanish -> steps", -0.19, c, 0.006)
    check("5", "correct keys only, Spanish -> steps, p", 0.16, p, 0.006)

    print("\n" + "=" * 78)
    if FAILURES:
        print("{0} CHECK(S) FAILED".format(len(FAILURES)))
        for sec, claim, paper, got in FAILURES:
            print("  Sect. {0}: {1} - paper {2}, recomputed {3}".format(sec, claim, paper, got))
        return 1
    print("ALL CHECKS PASSED - every headline number in the camera-ready paper")
    print("reproduces from the raw data in data/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
