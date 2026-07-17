# Beyond Student Labels: Evaluating Prompt Sensitivity in AI-Generated Practice Problems for Multilingual Learners

**Author:** Rudra · **Date:** _____ · **Models audited:** _____ (exact IDs from config.json)

## Abstract
_150 words. Lead with the RQ2 finding (did models change math difficulty for ELL-labeled students?), the effect size, and the paraphrase-brittleness result. If null: say so plainly — "across 2,160 generations and 4 model families, we find no/limited evidence that..."_

## 1. Introduction
- AI tutoring adoption context; problem generation is a core feature
- The specific harm hypothesis: conflating English proficiency with math ability lowers expectations — connect to expectancy-effect literature in education (Rosenthal & Jacobson; tracking research)
- Contributions: (1) pre-registered factorial audit, (2) multilingual × paraphrase interaction, (3) cross-family replication

## 2. Related Work
_Fill after a literature pass. Anchor areas: LLM bias audits with persona labels; LLM-generated educational content quality; prompt sensitivity/brittleness; LLM-as-judge validity. Position novelty honestly: the multilingual-learner × prompt-paraphrase interaction in problem GENERATION is the gap._

## 3. Method
Summarize DESIGN.md §3–5 (design table, metrics, judge rotation, human validation). State pre-registration explicitly.

## 4. Results
- **Manipulation check (H1):** difficulty by stated level — must pass or nothing else is interpretable
- **Headline (H2):** math-difficulty gap ELL vs control — coefficients table + effect-size figure; per model + pooled
- **H3:** linguistic adaptation (appropriate behavior) — contrast with H2 explicitly
- **H4:** paraphrase brittleness — range of the gap across templates
- **H5:** names/contexts by L1 condition (χ²) — stereotyping check
- **Refusal/parse-failure rates by condition**
- **Judge validity:** human–judge ρ; state whether judge results are confirmatory or exploratory

## 5. Discussion
- Interpret: is the language→math effect adaptation or harm? (Simplified language = good; simplified math = lowered expectations)
- Practical guidance for teachers/edtech: which prompt wordings avoid the effect
- Limitations (DESIGN.md §6) — all of them, unsoftened

## 6. Conclusion
_Three sentences. Finding, scope, one concrete recommendation._

## Appendix
- Full prompt templates; exact model IDs and dates; all regression tables; human rating protocol
