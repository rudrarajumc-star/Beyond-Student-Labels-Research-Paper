# Results Map — every claim in the paper traced to its evidence

Each row: what the paper says → the data it comes from → the code that produced it → the output file. Every number below was **independently recomputed** during the July 2026 audit and matched unless noted.

| Paper item | Claim / number | Source data | Analysis | Output file | Audit status |
|---|---|---|---|---|---|
| §4 opening | 1,567 of 1,620 readable (96.7%) | `metrics.csv` | `analyze.py` load + parse filter | `summary.txt` line 1 | ✔ reproduced |
| §4 opening | Parse failure × language χ²=3.34, p=.34 | `metrics.csv` | `analyze.py: refusal_analysis()` | `summary.txt` | ✔ reproduced |
| **Table 2** | Descriptives by condition | `metrics.csv` (readable; FK/rare/word-count English-only) | groupby means | `tables/descriptives_by_condition.csv` | ✔ reproduced; **word-count column corrected** (Chinese = 0 words artifact) |
| **§4.1 (H1)** | advanced +1.84 steps, +10.28 ops, +120.8 max operand, all p<.001 | `metrics.csv` | `analyze.py: regressions()` HC3 | `summary.txt` | ✔ reproduced exactly |
| §4.1 (H1) | struggling n.s. (p=.09/.60/.41) | same | same | `summary.txt` | ✔ reproduced |
| §4.1 | judge difficulty −0.32, correctness −1.47 (advanced) | `judgments.jsonl` + `metrics.csv` | judge-family regressions | `summary.txt` | ✔ reproduced; **paper's −1.48 corrected to −1.47** |
| **Table 3 (H2)** | 9 language effects on math, all n.s. | `metrics.csv` | `analyze.py: regressions()` | `tables/language_effects_math.csv` | ✔ reproduced exactly |
| §4.2 | All 9 language main effects Holm p=1.0; smallest math Holm p=0.24 | same | Holm within family | same | ✔ reproduced |
| **Table 4** | Cohen's d by model (llama −0.42, mistral −0.38, gptoss −0.13; pooled −0.02/−0.19/−0.25) | `metrics.csv` | `analyze.py: effect_sizes()` | `tables/effect_sizes.csv` | ✔ reproduced |
| §3.2 | Power: pooled .99 (d=0.3), .80 (d=0.2); within-model .67 (d=0.3), 80% at d≈0.35 | design n's | `statsmodels TTestIndPower` (audit) | stated in text | ✔ computed in audit; **corrects the pre-registration's false ">.9" claim** |
| **§4.3 (H3)** | FK −0.887 multilingual (Holm .0071), −0.918 ell_mandarin (.0120); ell_spanish −0.55 n.s. | `metrics.csv` English-only (n=1,121) | `analyze.py: regressions()` | `tables/language_effects_linguistic.csv` | ✔ reproduced exactly |
| §4.3 | rare-word ell_mandarin +0.0197 (Holm .0415) | same | same | same | ✔ reproduced |
| §4.3 | struggling×ell_spanish FK +1.39 (Holm .0418) | same | same | same | ✔ reproduced |
| **§4.4** | De-dup: 107 removed → 1,460; null holds (smallest Holm p=0.70); llama d −0.42→−0.50 | `metrics.csv` | audit de-dup script | `tables/language_effects_math_dedup.csv` | ✔ reproduced (106 vs 107 — off-by-one from ≥90% vs >90% threshold; immaterial) |
| **§4.4** | Cell-clustered SEs (539 cells): smallest p .07→.11 | `metrics.csv` | audit reanalysis | in text | ✔ new robustness check added by audit |
| **§4.4** | English-only H2 (n=1,121): null holds, smallest p=.12 | `metrics.csv` | audit reanalysis | in text | ✔ new robustness check added by audit |
| **Table 5 (H4)** | ELL-vs-control gap by paraphrase | `metrics.csv` | `analyze.py: paraphrase_brittleness()` | `tables/paraphrase_brittleness.csv` | ✔ reproduced |
| **Table 6 (H5)** | χ²(9)=365.6, p<10⁻⁷², Cramér's V=0.28 | `judgments.jsonl` names | audit χ² (post-hoc coding, disclosed) | `tables/h5_name_origin*.csv` | ✔ reproduced (V=0.279; **min expected count 13.1**, so χ² valid) |
| §4.6 | Chinese names 15.9% ELL-Mandarin vs 0% elsewhere; Hispanic 21.8% vs 6.3% | same | same | same | ✔ reproduced |
| §4.6 | Top names: Maria 80, 小明 50, María 48, Tom 27 | `judgments.jsonl` | audit count | in text | ✔ reproduced exactly |
| **Table 7** | Switch rates: ELL-Spanish 53.7% es; ELL-Mandarin 19.5% zh; 18 Korean-tagged | `metrics.csv` `output_language` | audit recount | in text | ✔ reproduced (zh = zh-cn + zh-tw) |
| **§4.8** | Parse failure llama 8.1% / mistral 1.5% / gptoss 0.2% | `metrics.csv` | audit recount | in text | ✔ reproduced exactly |
| §4.8 | Duplication 8.1% overall; llama 19.3%, mistral 4.2%, gptoss 2.4% | `metrics.csv` | audit recount | in text | ✔ reproduced exactly (124/1,523 within-cell pairs of readable items, `problem_text` similarity ≥ 0.90; stable across ≥/> and whitespace-normalisation variants). Corrected 2026-08-06 from earlier 18.9%/4.6%, which did not reproduce under any tested definition. |
| §5 | $20.93 item: human scored 5/5, judge scored 1/5 | `human_ratings_batch1_scored.csv`, `judgments.jsonl` | direct lookup (`f7e6a584031c`) | in text | ✔ Discussion previously said it "passed both"; corrected 2026-08-06 to match §4.9 and Appendix C |
| §1 | Steele & Aronson (1995) stereotype-threat citation | — | citation balance check | in text | ✔ dropped during an Introduction rewrite, restored 2026-08-06; all 24 references now cited |
| **Table 8** | Judge means by condition | `judgments.jsonl` | groupby | `tables/judge_means_by_condition.csv` | ✔ reproduced from raw JSONL |
| **§4.9** | Judge validity ρ=0.70, 98% exact/within-1, n=56 | `judge_validation_batch1.csv` | `validate_judge.py` | same | ✔ reproduced |
| Appendix C | 4 worked examples (IDs, answers, judge scores) | `metrics.csv`, `judgments.jsonl` | audit lookup | in text | ✔ all 4 IDs verified; arithmetic re-derived ($21.00, −2.1, 50.24/25.12, 64元) |
| Appendix D | Gemini 138 raw / 29 parsed | `metrics.csv` | audit count | in text | ✔ reproduced (DESIGN.md's "28" corrected) |

## Independent answer verification (audit-only; not a paper claim)
Symbolic solving of simple linear equations in English outputs: **2 of 57 stated answers wrong (3.5%)** — items `5a6e9b814d05` / `8bcac78c5934` (Llama), "2x+5=11−3x" answered 2 where the true root is 1.2. A strict no-tax percent-discount subset found **0 of 64** genuine model errors. Broader automated checks on percents and circles produced high apparent error rates that were traced to **the auditor's own parser**, not the models (missed "tax of X%" phrasing; radius/diameter confusion), and are therefore **not reported as findings**. Reliable evidence on answer correctness remains the judge's correctness scores and the 56-item human validation.

## Not reproducible from the repo
- **Registration date.** `DESIGN.md` asserts 2026-07-03 but no external timestamp, OSF record, or intact git history corroborates it, and `generations.jsonl` carries no per-row timestamps. Audit item **A002 — open**.
- **Exact Mistral weights.** `mistral-small-latest` is a floating alias.
