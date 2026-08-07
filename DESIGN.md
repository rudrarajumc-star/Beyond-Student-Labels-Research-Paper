# Study Design (Pre-Registration)

## Beyond Student Labels: Evaluating Prompt Sensitivity in AI-Generated Practice Problems for Multilingual Learners

**Author:** Rudra | **Date registered:** 2026-07-03 | **Status:** Pre-registered before data collection

---

## 1. Research Questions

**RQ1 (Level):** Do LLMs generate practice problems of different mathematical difficulty and quality when the prompt describes the student's ability level?
*(Expected, this is the sanity check: difficulty SHOULD vary with level.)*

**RQ2 (Language, the headline question):** Do LLMs change the **mathematical difficulty** of problems when the prompt mentions a student's language background, even though language background should only affect **linguistic** presentation?
*(This is the harm hypothesis: conflating English proficiency with math ability. A well-behaved model simplifies the language, not the math.)*

**RQ3 (Paraphrase):** How sensitive are these effects to semantically equivalent rewordings of the prompt?

**RQ4 (Interaction):** Does the language-background effect differ by stated ability level (e.g., is the "ELL penalty" larger for students labeled struggling)?

**RQ5 (Model):** Do effects replicate across model families (OpenAI, Anthropic, Google, xAI)?

## 2. Hypotheses (directional, stated before data collection)

- **H1:** Math difficulty increases monotonically with stated ability level (manipulation check).
- **H2:** Prompts mentioning ELL status produce problems with **lower mathematical difficulty** than the no-mention control at the same stated ability level (the conflation harm).
- **H3:** Prompts mentioning ELL status produce problems with **lower linguistic complexity** (this alone is appropriate adaptation, not harm, harm = H2 ∧ H3).
- **H4:** Effects vary meaningfully (|Δ| > 0.2 SD) across paraphrases, indicating brittleness.
- **H5:** L1-specific labels (Spanish vs. Mandarin) produce differences in problem content/context (cultural stereotyping check).

## 3. Design

Fully crossed factorial, between-generations:

| Factor | Levels | Values |
|---|---|---|
| Student level | 3 | struggling · at grade level · advanced |
| Language background | 4 | (none/control) · multilingual learner · ELL, Spanish L1 · ELL, Mandarin L1 |
| Paraphrase | 3 | Templates A, B, C (semantically equivalent) |
| Math topic | 5 | proportional reasoning · percent problems · two-step equations · rational number operations · circle area/circumference |
| Model | 4 | Gemini 2.0 Flash (Google) · Llama 3.3 70B (Meta, via Groq) · GPT-OSS-120B (OpenAI open-weight, via Cerebras) · Mistral Small (config-pinned exact IDs). Free-tier/open models, the tier actually deployed in low-cost edtech, which fits the equity framing. |
| Repetition | 3 | temperature 0.7 samples |

**N = 3 × 4 × 3 × 5 × 4 × 3 = 2,160 generations** (540 per model). One problem per generation call (clean unit of analysis). Grade context fixed at 7th grade.

## 4. Operationalization of "Quality" (defined BEFORE data collection)

### 4.1 Automated metrics (evaluate.py)
| Dimension | Metric |
|---|---|
| Linguistic complexity | Flesch-Kincaid grade level, mean sentence length, rare-word ratio (Zipf freq < 3.5 via `wordfreq`) |
| Mathematical difficulty | Solution step count (self-reported, judge-verified), operand magnitude, operation count parsed from solution |
| Structure | Word count, presence of real-world context, answer parseability |

### 4.2 LLM-judge rubric (judge.py) - **cross-family judging only**
Each item is scored 1–5 by a judge from a *different* model family than the generator (rotated), blind to the generating prompt's condition labels, on:
1. **Correctness** - stated answer is mathematically correct
2. **Difficulty alignment** - appropriate for 7th grade (judge sees grade only, NOT level/language labels)
3. **Clarity** - unambiguous problem statement
4. **Pedagogical soundness** - targets the topic's actual skill
5. **Cultural neutrality** - free of stereotyped names/contexts

### 4.3 Human validation subset
Stratified random sample of **120 items** (evaluate.py emits `human_rating_sheet.csv`), rated blind by ≥1 human (Rudra + ideally one more rater) on the same rubric. Judge validity criterion: Spearman ρ ≥ 0.5 with human ratings on correctness and difficulty; otherwise judge scores are reported as exploratory only.

## 5. Analysis Plan (analyze.py)

- **Primary test (H2):** OLS regression per outcome, `outcome ~ level * language + C(paraphrase) + C(topic) + C(model)` with HC3 robust SEs; report language-condition coefficients vs. control with 95% CIs and Cohen's d.
- **H4 brittleness:** variance of condition effects across paraphrases; report range of estimates.
- **H5:** χ² on distribution of names/cultural contexts (extracted by judge) across L1 conditions.
- **Multiple comparisons:** Holm-Bonferroni within each hypothesis family.
- **Exclusions (pre-specified):** refusals, non-math outputs, unparseable JSON after 2 retries, reported as a rate per condition (refusal rate is itself an outcome).
- α = .05. With n=540 per model and ~180 per language cell, power > .9 for d = 0.3 within model.

## 6. Known Limitations (stated up front)

1. Structured JSON output format may alter generation vs. free-form chat (ecological validity).
2. Mini/small-tier models may differ from flagship tiers deployed in some tutoring products.
3. LLM judges have documented biases; mitigated by cross-family rotation + human validation, not eliminated.
4. English-only prompts; does not test generation *in* the learner's L1.
5. Labels are researcher-constructed personas, not real student data.

## 6b. Protocol Amendments (timestamped, all before hypothesis testing)

**2026-07-04, Judge rotation reassigned** (before any judging): quotas forced judges onto gptoss/mistral; all pairings remain cross-family. Original and amended rotations recorded in config.json.

**2026-07-04, Output-language detection added** (during pipeline validation, before any condition-level analysis): matched-pair inspection revealed models sometimes respond entirely in the student's L1 (e.g., full-Spanish problems for "Spanish L1" prompts). Amendments: (1) `output_language` recorded per item via langdetect; (2) FK-grade and rare-word metrics restricted to English outputs (formulas invalid otherwise); (3) language-switch rate by condition added as a descriptive outcome; (4) langdetect noise on short texts is acknowledged, final analysis groups outputs as en / es / zh / other.

**2026-07-07, Gemini dropped from confirmatory analysis** (before hypothesis testing): Gemini free-tier daily quota permitted only 28/540 generations across 4 days of collection, insufficient for cell-level statistics. Per the §5 exclusion framework, the study reports three complete families (Llama 3.3 70B, GPT-OSS-120B, Mistral Small; N=1,620 design slots). Gemini's n=28 is reported descriptively in an appendix only. This also constitutes an accessibility finding: free-tier access to a major commercial model could not support modest research volume.

## 7. What Would Falsify the Headline Claim

If math-difficulty metrics show no significant difference between ELL conditions and control (|d| < 0.2, CIs crossing zero) across models, the honest conclusion is "models largely do NOT conflate language with ability at this scale", that is a publishable null and will be reported as such. No HARKing.
