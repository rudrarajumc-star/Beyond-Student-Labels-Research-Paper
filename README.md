# Beyond Student Labels

**Evaluating Prompt Sensitivity in AI-Generated Practice Problems for Multilingual Learners**

*Satyanarayana ("Rudra") Rudraraju · Whitney M. Young Magnet High School, Chicago*

**Accepted for oral presentation at SIMBig 2026; to appear in Springer CCIS.**
Camera-ready submitted 5 October 2026 · MIT (code) / CC BY 4.0 (text & figures)

📄 **The paper:** [`simbig2026/104.pdf`](simbig2026/104.pdf)
⚠️ **Read first if you saw an earlier version:** [`CORRECTIONS.md`](CORRECTIONS.md)
✅ **Verify every number yourself:** `python3 src/verify_paper.py`
🧾 **Analysis plan:** [`DESIGN.md`](DESIGN.md) · 📊 **Columns:** [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md)
🔖 **Archive of the earlier preprint:** [10.5281/zenodo.21824157](https://doi.org/10.5281/zenodo.21824157)

> A re-analysis after acceptance found an error in the statistical specification. The headline
> result changed from a null to a significant effect, and one secondary claim was withdrawn
> entirely. Both are documented in [`CORRECTIONS.md`](CORRECTIONS.md), and the correction was
> disclosed to the SIMBig programme chairs before the camera-ready was submitted.

---

## The question

When you tell an AI tutor a student is an **English language learner (ELL)**, a fair model
should make the *language* of a practice problem simpler while keeping the *mathematics* just
as hard. Making the mathematics easier would repeat a documented harm from education research
— treating a student's English proficiency as if it were their mathematical ability. This
project audits whether that happens, in the free, open-weight models that low-budget edtech
actually deploys.

It studies problem **writing**, not problem **solving** — the behaviour where a student label
has the most room to change the content.

## Headline results

Across **1,620 generations** (1,567 readable, 96.7%) from three free model families
(Llama 3.3 70B, GPT-OSS-120B, Mistral Small), averaged over ability levels and Holm-corrected
across the nine primary tests:

| Label | Solution steps | Operations |
|---|---|---|
| **ELL-Mandarin** | **−0.65** (corrected *p* = .0002) | **−4.24** (corrected *p* = .0001) |
| **ELL-Spanish** | **−0.52** (corrected *p* = .0067) | −2.61 (corrected *p* = .059, n.s.) |
| "multilingual" | −0.08 (*p* = .68) | −1.54 (*p* = .17) |
| **"struggling with this topic"** | **−0.01 (*p* = .91)** | +0.34 (*p* = .61) |

**The last row is the finding.** In the same regression, on the same problems, an explicit
statement that the student is *behind in mathematics* moved nothing, while naming the
student's first language shortened the written solution by about half a step. Pooled effects
are small: Cohen's *d* = −0.21 to −0.26.

Also:

- **The manipulation check works.** An "advanced" label raised solution steps by 1.19,
  operations by 7.04 and the largest number by 115.0 (all *p* < .001), so the measures do track
  difficulty.
- **Unprompted language switching.** 50.4% of ELL-Spanish problems came back in Spanish and
  24.4% of ELL-Mandarin in Chinese, against 0% for control and 0.5% for "multilingual" — from
  English prompts that never asked for a translation. By model, ELL-Spanish: Mistral 93%,
  Llama 57%, GPT-OSS 1.5%.
- **Wrong answer keys are common.** The cross-family judge flags a wrong key in 22.1% of
  problems (Llama 38.5%, Mistral 28.9%, GPT-OSS 0.4%). An independent exact-arithmetic audit of
  every problem reducible to a pure rational-number expression found Llama wrong on 13 of 14,
  Mistral on 14 of 27, GPT-OSS on 0 of 28, with the judge agreeing on all 69.
- **Names track the label.** χ²(9) = 365.6, Cramér's *V* = 0.28. Chinese-style names appear in
  15.9% of ELL-Mandarin problems and nowhere else.
- **Language simplification is uneven.** On English output (*n* = 1,271), ELL-Mandarin lowered
  Flesch-Kincaid grade by 0.77 (*p* = .0003) and "multilingual" by 0.42 (*p* = .046);
  ELL-Spanish did not (+0.03, *p* = .94).

## What this does *not* show

These belong next to the result, not in a footnote.

1. **Narration, not necessarily difficulty.** Solution steps and operations are read from the
   model's *own solution*. A model that simply writes more tersely for an English learner scores
   identically to one writing easier mathematics. Settling that needs a fixed solver or blind
   teacher ratings.
2. **The effect shrinks on correct keys.** Among the **1,220** problems whose answer key the
   judge accepted, the ELL-Mandarin effect on steps halves to **−0.33** (*p* = .008) and the
   ELL-Spanish effect is **no longer significant** (−0.19, *p* = .16). Part of the headline may
   run through fewer wrong keys — and fewer in-line corrections — under the ELL labels.
3. **ELL-Spanish is confounded with language switching.** Only 49.6% of ELL-Spanish output
   stayed in English, and output language is itself an effect of the label.
4. **Significant in two model families, not detected in the third.** GPT-OSS shows nothing
   significant, but its estimates point the same way and it fails the equivalence test, so this
   is not evidence of absence.
5. **Two languages, three models, no students.** Telugu — the language the author's own students
   speak — was not tested. Personas are not students, and nothing here extends to learning
   outcomes or to frontier models.

## Verify it yourself

```bash
pip3 install -r requirements.txt
python3 src/verify_paper.py
```

`verify_paper.py` recomputes **69 published values** from the raw data in `data/` — the sample
counts, every coefficient and *p*-value in Table 1, the Holm-corrected H2 results with their
confidence intervals and effect sizes, the clustered-SE robustness check, the answer-key rates,
and the correct-key caveat in §5 — and prints PASS or FAIL against the number printed in the
paper. It exits non-zero if anything disagrees. No API keys needed; it reads committed data
only. The committed run is in [`results/verify_paper_output.txt`](results/verify_paper_output.txt).

The primary specification is:

```
outcome ~ C(level, Treatment("on_grade")) + C(language, Treatment("control"))
        + C(model_family) + C(topic) + C(paraphrase)
```

with HC3 robust standard errors and Holm correction across the nine primary tests
(3 math outcomes × 3 language labels).

## Pipeline

```
build_prompt_matrix.py -> generate.py -> evaluate.py -> judge.py -> analyze.py
     (1,620 prompts)       (3 APIs)       (metrics)     (cross-      (original
                                                          family)     analysis)

                                                      verify_paper.py
                                                   (camera-ready numbers)
```

`analyze.py` is kept unchanged as the record of the original, superseded analysis. The
camera-ready numbers come from the specification in `verify_paper.py`. See `CORRECTIONS.md`.

## Repository layout

```
CORRECTIONS.md       What changed after acceptance, and why
DESIGN.md            Analysis plan: RQs, hypotheses, metrics, amendments, falsification clause
DATA_DICTIONARY.md   Every column in every data file
config.json          Pinned model IDs, temperature, judge rotation (+ amendment notes)
requirements.txt     Python dependencies
.env.example         Template for API keys (copy to .env; never commit the real one)
src/
  build_prompt_matrix.py, generate.py, evaluate.py, judge.py, run_study.py   pipeline
  analyze.py           original analysis (superseded; kept for the record)
  verify_paper.py      recomputes and checks every number in the camera-ready
  validate_judge.py    judge-vs-human validity
data/                Prompt matrix, raw generations, per-item metrics, judgments, human ratings
results/
  verify_paper_output.txt   the 69 verification checks, as run
  summary.txt               original regression output (superseded)
  tables/                   effect sizes, language effects, brittleness, name origin
  figures/                  104-fig1/2 (as published) plus the original exploratory plots
simbig2026/          Camera-ready: 104.pdf, LaTeX source, figure alt text
SAMPLE_50_PROBLEMS.md   Curated example generations, including language-switched items
```

The earlier long-form preprint (`report/`, `arxiv/`) and its claim map (`RESULTS_MAP.md`) have
been removed: they reported the superseded null and the withdrawn judge claim, and leaving them
alongside the camera-ready would have left contradictory documents in one repository. They
remain in this repository's git history and in the Zenodo archive.

## Reproduce from scratch

```bash
pip3 install -r requirements.txt
cp .env.example .env        # then paste your own free-tier keys into .env
```

Free, no-credit-card keys: [Groq](https://console.groq.com) (Llama 3.3 70B),
[Cerebras](https://cloud.cerebras.ai) (GPT-OSS-120B), [Mistral](https://console.mistral.ai)
(Mistral Small). Verify each model ID in its console against `config.json`.

```bash
python3 src/build_prompt_matrix.py     # 1. build the 1,620-task matrix
python3 src/generate.py --limit 40     # 2. SMOKE TEST first; inspect data/generations.jsonl
python3 src/generate.py                # 3. full run (resumable; free; several hours, rate limits)
python3 src/evaluate.py                # 4. automated metrics -> data/metrics.csv
python3 src/judge.py                   # 5. cross-family LLM judging (resumable)
python3 src/verify_paper.py            # 6. check the paper's numbers against your run
```

**Known reproducibility limits.** `mistral-small-latest` is a floating provider alias, so the
exact served weights cannot be reconstructed. `data/generations.jsonl` carries no
per-generation timestamps. Regenerating will not reproduce these exact outputs; the committed
data will.

## Analysis plan, honestly described

`DESIGN.md` was written before data collection and records five hypotheses, the metrics, the
analysis plan and three dated amendments. It is **not** an independently registered protocol:
it is dated 2026-07-03 but was first committed publicly on 2026-08-06, after data collection,
and there is no external timestamp. The paper therefore calls it *pre-specified*, not
*pre-registered*, and §3.1 says so in those words. Earlier versions of this README called the
study pre-registered; that was overclaiming, and it has been corrected.

`DESIGN.md` is deliberately left unedited — an analysis plan should never be retroactively
rewritten. Where it is wrong, the paper corrects it openly:

- Its power claim (">.9 for *d* = 0.3 within model") is overstated; the true within-model
  figure is **0.67**, with 80% power only at *d* ≈ 0.35.
- Its specification asks for the language coefficients from an interacted model, which estimate
  the on-level effect. See `CORRECTIONS.md`.

Amendments recorded there: judge rotation reassigned for quota; output-language detection
added; Gemini dropped from confirmatory analysis (free tier returned 138 of 540 requests, 29
usable). Not recorded there, and disclosed in the paper instead: GPT-OSS-120B replaced a
retired Qwen model on 2026-07-04 before any usable data existed in that slot; two planned parse
retries were never implemented; `langdetect` was replaced by a deterministic rule after it
mislabelled 152 English problems; and human validation covers 56 items from two families, not
the planned 120.

## Human validation (batch 1 done; batch 2 prepared)

Batch 1 (56 items, GPT-OSS + Mistral) is complete: correctness agreement 98.2%, κ = 0.66,
Spearman ρ = 0.70. The pre-specified two-part bar also required a difficulty correlation; the
author rated every item 5 on difficulty, leaving that correlation undefined, so **the bar was
not fully met and all judge-derived quantities are reported as descriptive.** Batch 2 would
cover the Llama family, which batch 1 did not; the blinded sheet and hidden key are generated
but the ratings are not done, so the paper reports Llama as human-unvalidated.

```bash
# rate data/human_rating_sheet_batch2.csv by hand, WITHOUT opening the key,
# save as data/human_ratings_batch2_scored.csv, then:
python3 src/validate_judge.py --ratings data/human_ratings_batch2_scored.csv --batch 2
python3 src/validate_judge.py --pooled
```

## Ethics & data

No human-subjects data: all "students" are prompt personas, and the only human ratings are the
author's own blinded scores. Committed data contains model output only, no personal
information.

## AI-assistance disclosure

The models under study generated all 1,620 practice problems and served as cross-family judges
— that is the object of the research. Separately, Claude (Anthropic) was used for drafting and
revision, code review, and an audit of the statistical analysis; that audit is what caught the
specification error in `CORRECTIONS.md`. The design, data collection, human ratings, and all
final claims are the author's own, and the author is responsible for the analysis and its
interpretation.

## Citation

See [`CITATION.cff`](CITATION.cff), or:

> Rudraraju, S. (2026). *Beyond Student Labels: Evaluating Prompt Sensitivity in AI-Generated
> Practice Problems for Multilingual Learners.* In: Proceedings of SIMBig 2026, Communications
> in Computer and Information Science, Springer. (To appear.)

## License

Code: **MIT**. Written report, figures, and derived tables: **CC BY 4.0**. See [`LICENSE`](LICENSE).
