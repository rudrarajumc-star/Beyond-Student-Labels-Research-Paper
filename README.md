# Beyond Student Labels

**Evaluating Prompt Sensitivity in AI-Generated Practice Problems for Multilingual Learners**

*Satyanarayana ("Rudra") Rudraraju · Whitney M. Young Magnet High School, Chicago*
Preprint v1.1 (17 July 2026) · Pre-registered · MIT (code) / CC BY 4.0 (text & figures)

📄 **Read the paper:** [`report/REPORT.md`](report/REPORT.md)
🧾 **Pre-registration (read this first):** [`DESIGN.md`](DESIGN.md)

---

## The question

When you tell an AI tutor a student is an **English language learner (ELL)**, a fair model
should make the *language* of a practice problem simpler while keeping the *math* just as hard.
Making the math easier would repeat a documented harm from education research — treating a
student's English level as if it were their math ability. This project audits whether that
happens, in the free, open-weight models that low-budget edtech actually deploys.

It studies problem **writing**, not problem **solving** — the behavior where a student label
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
- **Reliability varies wildly by model** (unreadable-output 0.2%–8.1%; duplication 2.4%–18.9%).

The primary finding is a **null**, framed as informative. See the paper for the full,
unsoftened treatment of limitations (including a compressed "struggling" difficulty floor).

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

# 2. Rate data/human_rating_sheet_batch2.csv by hand — fill the five 1-5 columns,
#    WITHOUT opening the key. Save as data/human_ratings_batch2_scored.csv

# 3. Compute batch-2 and pooled judge–human validity:
python3 src/validate_judge.py --ratings data/human_ratings_batch2_scored.csv --batch 2
python3 src/validate_judge.py --pooled
```

`validate_judge.py` reproduces the committed batch-1 table exactly, so the batch-2 and
pooled numbers are directly comparable. Until batch 2 is rated, the paper reports the
Llama family as human-unvalidated — an honest limitation, not a placeholder to be faked.

## Rules of the run (integrity)

- Do **not** change prompts, conditions, or metrics once generation starts (see `DESIGN.md` §7 —
  nulls get reported too; no HARKing).
- `generate.py` and `judge.py` are **resumable** — safe to interrupt and re-run.
- Free tiers rate-limit; the scripts pace themselves and back off on HTTP 429.

## Protocol amendments (all pre-hypothesis-testing, fully disclosed)

Qwen → GPT-OSS substitution (provider retired Qwen); judge rotation reassigned for quota;
output-language detection added; Gemini dropped from confirmatory analysis (free tier returned
only 29 usable items of 540). Details in `DESIGN.md` §6b, `config.json`, and the paper's Methods.

## Ethics & data

No human-subjects data: all "students" are prompt personas; the only human ratings are the
author's own blinded scores. Committed data (`data/`, `results/`) contains model output only,
no personal information. See the paper's Ethics Statement.

## Citation

See [`CITATION.cff`](CITATION.cff), or:

> Rudraraju, S. (2026). *Beyond Student Labels: Evaluating Prompt Sensitivity in AI-Generated
> Practice Problems for Multilingual Learners.* Preprint v1.1.

## License

Code: **MIT**. Written report, figures, and derived tables: **CC BY 4.0**. See [`LICENSE`](LICENSE).
