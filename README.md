# Beyond Student Labels

**Evaluating Prompt Sensitivity in AI-Generated Practice Problems for Multilingual Learners**

*Satyanarayana ("Rudra") Rudraraju · Whitney M. Young Magnet High School, Chicago*
Preprint v1.3 (7 August 2026) · Pre-registered · MIT (code) / CC BY 4.0 (text & figures)

**Accepted For SIMBIG 2026 oral presentation at SIMBig 2026 and will be published in the Springer CCIS Series.**

📄 **Read the paper:** [`report/REPORT.md`](report/REPORT.md)
🧾 **Pre-registration (read this first):** [`DESIGN.md`](DESIGN.md)
📊 **Data dictionary:** [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) · **Every claim traced to its evidence:** [`RESULTS_MAP.md`](RESULTS_MAP.md)

**Status:** Archived on Zenodo (6 August 2026). Not yet posted to arXiv or OSF Preprints. Short-paper version submitted to SIMBig 2026 (7 August 2026).

🔖 **Permanent archive (DOI):** [10.5281/zenodo.21824157](https://doi.org/10.5281/zenodo.21824157)

---

## The question

When you tell an AI tutor a student is an **English language learner (ELL)**, a fair model
should make the *language* of a practice problem simpler while keeping the *math* just as hard.
Making the math easier would repeat a documented harm from education research, treating a
student's English level as if it were their math ability. This project audits whether that
happens, in the free, open-weight models that low-budget edtech actually deploys.

It studies problem **writing**, not problem **solving** - the behavior where a student label
has the most room to change the content.

## Headline results

Across **1,620 generations** from three free model families (Llama 3.3 70B, GPT-OSS-120B,
Mistral Small):

- **Math difficulty: null.** After multiple-comparison correction, no language label
  significantly changed any math-difficulty measure. Pooled effects are small (Cohen's *d* ≤ 0.25),
  and the null survives a duplicate-excluded reanalysis. *In one line: the models adapted the
  language, not the math.*
- **Language: simplified.** ELL / "multilingual" labels lowered reading grade by ~0.9 grades
  (corrected *p* < .05).
- **Unprompted language switching.** 53.7% of readable ELL-Spanish problems came back in Spanish;
  19.5% of ELL-Mandarin problems in Chinese.
- **Names track the label.** χ²(9) = 365.6, *p* < 10⁻⁷²: Chinese-style names in 15.9% of
  ELL-Mandarin problems vs 0% elsewhere.
- **AI-judge cultural blind spot.** The LLM judge scored all three human-flagged,
  stereotype-adjacent problems a perfect 5/5 on cultural neutrality.
- **Reliability varies wildly by model** (unreadable-output 0.2%–8.1%; duplication 2.4%–19.3%).

The primary finding is a **null**, framed as informative. See the paper for the full,
unsoftened treatment of limitations (including a compressed "struggling" difficulty floor).

The null survives four independent robustness checks: de-duplication of near-identical
outputs, standard errors clustered on the 539 design cells, restriction to English-only
outputs, and separate estimation across all three prompt paraphrases.

## Verification status

**Second audit, 6 August 2026 (pre-preprint).** Every quantitative claim was recomputed
from raw data a second time before posting. Verified exactly: N = 1,620 (540 × 3 families);
1,567 readable (96.7%); parse failure independent of condition (χ² = 3.34, *p* = .34);
all of Table 2 (math columns), Table 3, Table 4, Table 5, Table 6, Table 7, Table 8;
H1 level effects (steps +1.84, ops +10.28, magnitude +120.8, all *p* < .001; struggling
n.s.); H3 linguistic effects (FK −0.887 / −0.918, *p*_holm = .0071 / .0120); H5 omnibus
χ²(9) = 365.6, *p* = 2.9 × 10⁻⁷³, Cramér's *V* = 0.279; judge validation ρ = 0.70, 98%
agreement, batch 1 = 28 GPT-OSS + 28 Mistral; the three human-flagged cultural items all
scored 5/5 by the judge; de-duplication (107 removed, min *p*_holm = 0.70, Llama
ELL-Spanish *d* −0.42 → −0.51); clustered-SE and English-only robustness (min *p* = .11
and .12); power (.99 / .80 pooled, .67 within-model, 80% at *d* ≈ 0.35); name counts
(Maria 80, 小明 50, María 48, Tom 27); Gemini 138 raw / 29 parsed.

This audit **corrected two errors** now fixed in the paper:

1. **Per-model duplication rates.** Previously reported as Llama 18.9% / Mistral 4.6%.
   These did not reproduce under any tested definition. The correct figures, stable across
   similarity-threshold and normalisation variants, are **Llama 19.3% / Mistral 4.2%**
   (GPT-OSS 2.4% and the 8.1% overall figure were already correct).
2. **A Discussion sentence** stated that a wrong answer ($20.93 vs. $21.00) "passed both a
   careful human rater and an AI judge." The raw data show the judge scored it 1/5, the
   human missed it and the judge caught it. Corrected to match §4.9 and Appendix C.

3. **A dropped citation.** Steele & Aronson (1995) was cut from the Introduction during a
   rewrite while remaining in the reference list. Restored; all 24 references are now cited
   and all 24 in-text citations resolve.

Two clarifications were also added: Table 2's sentence-length column is computed on all
readable items (n = 1,496), not English-only as the caption implied; and the 2×2 name
tests use Yates's continuity correction while the omnibus test does not.

The typeset PDF (`report/REPORT.pdf`, `arxiv/main.pdf`) was regenerated from the corrected
Markdown on 6 August 2026, and every number in it was re-extracted and re-checked against
the raw data files programmatically.

**Third check, 7 August 2026.** While preparing a condensed conference version, the
de-duplication sentence in §4.4 and Appendix E was found to still read "*d* = −0.42 to
−0.50", the *summary above this line has always said −0.51*, and recomputing the
de-duplicated Cohen's *d* directly from `data/metrics.csv` confirms −0.51 is correct; the
body text had not been updated to match. Fixed in both places. No conclusion changes.
The version stamp (previously stuck at "Version 1.1, 17 July 2026" from before the
6 August rewrite) is corrected to Version 1.3, 7 August 2026, matching this repository.

An earlier July 2026 audit corrected four things, each disclosed in the paper:
a mis-stated judge coefficient (−1.48 → −1.47), a word-count column corrupted by
unsegmented Chinese text, a citation with the wrong journal, and, most importantly, the
pre-registration's **overstated power claim** (`DESIGN.md` §5 says "power > .9 for d = 0.3
within model"; the true within-model figure is **0.67**, with 80% power only at d ≈ 0.35).
`DESIGN.md` was deliberately left unedited, because a pre-registration should never be
retroactively rewritten; the paper corrects it openly in §3.2 instead.

**Known reproducibility limits:** `mistral-small-latest` is a floating provider alias, so
the exact served weights cannot be reconstructed; `data/generations.jsonl` carries no
per-generation timestamps; and the registration date rests on this repository alone,
with no external timestamp.

## Pipeline

```
build_prompt_matrix.py -> generate.py -> evaluate.py -> judge.py -> analyze.py
     (1,620 prompts)       (3 APIs)       (metrics)     (cross-      (stats,
                                                          family)     figures)
```

## Repository layout

```
DESIGN.md            Pre-registration: RQs, hypotheses, metrics, analysis plan, amendments, falsification clause
config.json          Pinned model IDs, temperature, judge rotation (+ amendment notes)
requirements.txt     Python dependencies
.env.example         Template for API keys (copy to .env; never commit the real one)
src/                 Pipeline scripts (build_prompt_matrix, generate, evaluate, judge, analyze, validate_judge)
data/                Prompt matrix, raw generations, per-item metrics, judgments, human ratings
results/
  summary.txt        Full regression output
  tables/            Effect sizes, language effects, brittleness, H5 name-origin, de-dup reanalysis
  figures/           Effect-size forest, language-switch, name-origin, FK & solution-steps plots
report/
  REPORT.md          Full preprint (source)

SAMPLE_50_PROBLEMS.md   Curated example generations (incl. language-switched items)
```

## Reproduce

```bash
pip3 install -r requirements.txt
cp .env.example .env        # then paste your own free-tier keys into .env
```

Get free, no-credit-card keys from: [Groq](https://console.groq.com) (Llama 3.3 70B),
[Cerebras](https://cloud.cerebras.ai) (GPT-OSS-120B), [Mistral](https://console.mistral.ai)
(Mistral Small). Verify each model ID in its console and confirm it matches `config.json`.

```bash
python3 src/build_prompt_matrix.py     # 1. build the 1,620-task matrix
python3 src/generate.py --limit 40     # 2. SMOKE TEST first; inspect data/generations.jsonl
python3 src/generate.py                # 3. full run (resumable; free; several hours due to rate limits)
python3 src/evaluate.py                # 4. automated metrics -> data/metrics.csv
python3 src/judge.py                   # 5. cross-family LLM judging (resumable)
python3 src/analyze.py                 # 6. results/ tables + figures + summary.txt
```

To regenerate the typeset PDF from the Markdown (needs `pandoc` + `xelatex` and the DejaVu
and Noto Serif CJK fonts):

```bash
cd report
pandoc REPORT.md -o REPORT.pdf --pdf-engine=xelatex --toc --toc-depth=2 \
  -V geometry:margin=0.9in -V mainfont="DejaVu Serif"
```

## Human validation (batch 1 done; batch 2 prepared)

Judge scores are validated against blinded human ratings. Batch 1 (56 items, GPT-OSS +
Mistral) is complete: correctness Spearman ρ = 0.70 (pass mark ≥ 0.5). Batch 2 covers the
Llama family, which batch 1 did not. The blinded sheet is already generated
(`data/human_rating_sheet_batch2.csv`, 28 items, 7 per language) with its hidden key
(`data/human_rating_key_batch2.csv`). To complete it:

```bash
# 1. (already done) generate the blinded sheet + key:
python3 src/evaluate.py --sample --families llama --batch 2 --n 28

# 2. Rate data/human_rating_sheet_batch2.csv by hand - fill the five 1-5 columns,
#    WITHOUT opening the key. Save as data/human_ratings_batch2_scored.csv

# 3. Compute batch-2 and pooled judge–human validity:
python3 src/validate_judge.py --ratings data/human_ratings_batch2_scored.csv --batch 2
python3 src/validate_judge.py --pooled
```

`validate_judge.py` reproduces the committed batch-1 table exactly, so the batch-2 and
pooled numbers are directly comparable. Until batch 2 is rated, the paper reports the
Llama family as human-unvalidated, an honest limitation, not a placeholder to be faked.

## Rules of the run (integrity)

- Do **not** change prompts, conditions, or metrics once generation starts (see `DESIGN.md` §7, 
  nulls get reported too; no HARKing).
- `generate.py` and `judge.py` are **resumable** - safe to interrupt and re-run.
- Free tiers rate-limit; the scripts pace themselves and back off on HTTP 429.

## Protocol amendments (all pre-hypothesis-testing, fully disclosed)

Qwen → GPT-OSS substitution (provider retired Qwen); judge rotation reassigned for quota;
output-language detection added; Gemini dropped from confirmatory analysis (free tier returned
only 29 usable items of 540). Details in `DESIGN.md` §6b, `config.json`, and the paper's Methods.

## Ethics & data

No human-subjects data: all "students" are prompt personas; the only human ratings are the
author's own blinded scores. Committed data (`data/`, `results/`) contains model output only,
no personal information. See the paper's Ethics Statement.

## AI-assistance disclosure

The models under study generated all 1,620 practice problems and served as cross-family
judges, that is the object of the research. Separately, large language models were used to
assist in drafting the manuscript and in writing and verifying analysis code. The design,
hypotheses, data collection, human ratings, and all final claims are the author's own; every
reported number was verified against the raw data, and the author takes full responsibility
for the content. See the paper's Author Contributions section.

## Citation

See [`CITATION.cff`](CITATION.cff), or:

> Rudraraju, S. (2026). *Beyond Student Labels: Evaluating Prompt Sensitivity in AI-Generated
> Practice Problems for Multilingual Learners.* Preprint v1.3. Zenodo. https://doi.org/10.5281/zenodo.21824157

## License

Code: **MIT**. Written report, figures, and derived tables: **CC BY 4.0**. See [`LICENSE`](LICENSE).
