# Data Dictionary

Every column in the committed data files, with meaning, type, range, and missing-value handling. All values below were computed directly from the files, not copied from documentation.

## `data/metrics.csv` — one row per generation (N = 1,758: 1,620 main + 138 Gemini)

| Variable | Meaning | Type | Range / allowed values | Missing | Notes |
|---|---|---|---|---|---|
| `id` | Unique 12-hex generation ID | string | 1,758 unique | 0 | Primary key; joins to `generations.jsonl` and `judgments.jsonl` |
| `level` | Stated ability level (factor) | categorical | `struggling`, `on_grade`, `advanced` | 0 | Reference level in models: `on_grade` |
| `language` | Language-background label (factor) | categorical | `control`, `multilingual`, `ell_spanish`, `ell_mandarin` | 0 | Reference level: `control` (empty clause) |
| `paraphrase` | Prompt wording (factor) | categorical | `A`, `B`, `C` | 0 | Semantically equivalent templates |
| `topic` | Math topic (factor) | categorical | `proportions`, `percents`, `two_step_eq`, `rationals`, `circles` | 0 | |
| `model_family` | Generating model | categorical | `llama`, `gptoss`, `mistral`, `gemini` | 0 | `gemini` excluded from all confirmatory analysis (n=138 collected, 29 parsed) |
| `rep` | Repetition index within cell | integer | 1–3 | 0 | Temperature 0.7 samples; **not fully independent** (see duplication, §4.8) |
| `parse_status` | JSON parse outcome | categorical | `ok` (1,596), `no_json` (145), `bad_json` (17) | 0 | Pre-registered exclusion; analyses use `ok` only |
| `output_language` | Detected output language | categorical | 13 values incl. `en`, `es`, `zh-cn`, `zh-tw`, `ko`, `da`, … | 162 | `langdetect`; **noisy on short text** — bucket to en/es/zh/other. Missing where parse failed |
| `fk_grade` | Flesch–Kincaid grade level | float | −3.01 to 16.53 | 611 | **English outputs only** (invalid otherwise). 68 items < 0 = formula floor on very short text |
| `mean_sentence_len` | Mean words per sentence | float | 0.33 to 40.0 | 233 | |
| `rare_word_ratio` | Share of words with Zipf freq < 3.5 | float | 0.0 to 0.45 | 611 | English only; `wordfreq` lists. Romanized names inflate this |
| `word_count` | Words in problem text | float | 0 to 120 | 162 | **Zero for unsegmented Chinese** (no spaces) — use English-only subset for cross-condition comparison |
| `n_solution_steps` | Steps in model's own solution | float | 2 to 35 | 162 | **Math difficulty outcome.** Measures the model's *narration* of difficulty, not intrinsic difficulty |
| `n_operations` | Arithmetic operations parsed from solution | float | 0 to 216 | 162 | **Math difficulty outcome.** Same narration caveat |
| `max_operand_magnitude` | Largest number appearing in solution | float | 1.5 to 5,280 | 165 | **Math difficulty outcome.** Property of the problem, but heavy-tailed/noisiest |
| `answer_numeric` | First number parsed from answer text | float | −653 to 123,200 | 163 | **Descriptive only — used in NO analysis.** Heuristic ("first number"); known artifacts (may capture a list marker or a restated radius). Do not treat as a correctness measure |
| `has_context` | Problem has a real-world setting | boolean | True / False | 162 | Proper-noun / narrative cue heuristic |
| `problem_text` | Generated problem statement | string | 1,427 unique of 1,596 | 162 | Duplication is itself a reported outcome (§4.8) |
| `answer_text` | Generated answer, verbatim | string | 919 unique | 162 | |

**Missing-value convention:** blank = not applicable or upstream parse failure. The 162 blanks across content columns are exactly the 162 unparseable generations (145 `no_json` + 17 `bad_json`). `fk_grade` / `rare_word_ratio` carry 611 blanks because they are additionally restricted to English outputs.

## `data/generations.jsonl` — raw record, one JSON object per line (1,758)
`id`, `level`, `language`, `paraphrase`, `topic`, `model_family`, `rep`, `prompt` (full text sent), `model_id` (exact pinned API ID), `raw_output` (verbatim API response), `parsed` (JSON object or null), `parse_status`. **This is the raw file — never edit it.** No timestamps were recorded per generation (a provenance gap; add them in future runs).

## `data/judgments.jsonl` — LLM judge scores (1,596 judged items)
`id`, `judge_family` (cross-family: llama→gptoss, gptoss→mistral, mistral→gptoss), and `scores`: `correctness`, `difficulty_alignment`, `clarity`, `pedagogical_soundness`, `cultural_neutrality` (each integer 1–5; verified 0 out-of-range across 7,979 scores), plus extracted `person_names` and `context_setting` feeding the H5 analysis.

## `data/human_ratings_batch1_scored.csv` / `judge_validation_batch1.csv`
Author's blinded ratings of 56 items (GPT-OSS + Mistral, 28 each) on the same five 1–5 dimensions, and the agreement table (`dimension`, `human_mean`, `judge_mean`, `exact_agree`, `within_1`, `spearman`, `n`). Correctness ρ = 0.70; the other four dimensions hit a ceiling, leaving ρ undefined. Batch 2 (Llama) sheet and key exist but are **unrated** — disclosed as a limitation.

## Derived files
`results/summary.txt` (full regression output), `results/tables/*.csv` (language effects, effect sizes, brittleness, H5 name origin, de-duplicated reanalysis, descriptives, judge means), `results/figures/*.png`. All regenerable via `python3 src/analyze.py`; verified byte-identical on re-run.

## Known data-quality issues (all disclosed in the paper)
1. `word_count` = 0 for Chinese outputs — corrected in Table 2 by restricting to English.
2. `langdetect` mislabels 18 ELL-Mandarin items as Korean and some short English as Danish/Romanian — hence bucketing.
3. `fk_grade` floors below zero on very short text; contrast-based analyses are unaffected.
4. `answer_numeric` is a crude first-number heuristic; not used in any result.
5. Within-cell repetitions are not independent (duplication 2.4–19.3% by model); addressed by de-duplication and cell-clustered standard errors, neither of which changes any conclusion.
6. `mistral-small-latest` is a floating provider alias, not a pinned version — the exact served weights cannot be reconstructed.
