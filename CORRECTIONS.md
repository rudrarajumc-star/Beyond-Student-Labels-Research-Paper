# Corrections

Every correction made to *Beyond Student Labels* after the version reviewed for SIMBig 2026,
with what changed and how to check it. Nothing here was found by a reviewer; all of it came
from re-analysis by the author, and all of it was disclosed to the programme chairs in writing
before the camera-ready was submitted.

The chairs' meta-reviewer responded on 1 October 2026: *"I think the changes are totally
acceptable and make the paper stronger if anything."*

Run `python3 src/verify_paper.py` to check every number below against the raw data.

---

## 1. The statistical specification (changes the main result)

**What was wrong.** `DESIGN.md` specified a model in which ability level is *interacted* with
language label, with on-grade as the reference category, and asked for the language
coefficients. In that specification a language coefficient does not estimate the overall effect
of the label. It estimates the effect **for on-grade students only.**

On-grade turns out to be the one ability level at which no ELL effect appears (ELL-Mandarin
−0.10 steps, *p* = .59). The reviewed version of the paper reported that coefficient as the
result, and therefore reported a null — while printing effect sizes computed across all three
ability levels. A *p*-value describing one third of the data sat next to an effect size
describing all of it.

**What changed.** The effect is now estimated as the average over ability levels, which is what
hypothesis H2 was about and what the figure had always shown:

```
outcome ~ C(level, Treatment("on_grade")) + C(language, Treatment("control"))
        + C(model_family) + C(topic) + C(paraphrase)          # HC3 robust SEs
```

Nothing else changed. Same 1,620 generations, same 1,567 readable items, same design, same
models, same hypotheses. No data was added, removed, or re-collected.

**What it changes.**

| Claim | Reviewed version | Camera-ready |
|---|---|---|
| ELL-Mandarin → solution steps | −0.10 (*p* = .59), null | **−0.65** (Holm-corrected *p* = .0002) |
| ELL-Mandarin → operations | null | **−4.24** (Holm-corrected *p* = .0001) |
| ELL-Spanish → solution steps | null | **−0.52** (Holm-corrected *p* = .0067) |
| ELL-Spanish → operations | null | −2.61 (Holm-corrected *p* = .059, still n.s.) |
| "multilingual" label | null | null, unchanged; passes the equivalence test |
| H1, advanced → steps / ops / largest | +1.84 / +10.28 / +120.8 | **+1.19 / +7.04 / +115.0** (still *p* < .001) |

H1 moved because the manipulation check was re-estimated under the same corrected model, for
consistency. It still holds comfortably.

**How the paper handles it.** §3.3 states the departure explicitly and tells a reader who holds
to the plan as written to read the pre-specified test as null and the averaged estimates as a
departure, noting both are reproducible from the study data. §4.3 reports the
ability-by-language breakdown so the on-level null is visible rather than buried.

---

## 2. A withdrawn claim: the "AI-judge cultural blind spot"

**What was claimed.** That the LLM judge scored all three human-flagged, stereotype-adjacent
problems a perfect 5/5 on cultural neutrality, revealing a blind spot in the judge.

**Why it was withdrawn.** On re-examination the judge was right and the author's own ratings
were not. The three items were flagged for being written in Spanish or Chinese — the author had
penalised the *output language*, not any stereotype in the content. That is a defect in the
human rating, not in the judge.

§4.7 of the paper now says: *"I also flagged three items as culturally stereotyped that the
judge passed; on review the judge was right and I had penalised the output language."*

Any earlier README, abstract, or summary listing an "AI-judge cultural blind spot" among the
findings is superseded.

---

## 3. Language detection replaced

`langdetect` had labelled **152 English problems** as other languages (129 as
Danish/Romanian/Catalan; 45 of them controls). It was replaced with a deterministic rule:
Chinese if more than 20% of characters are Han, otherwise Spanish if Spanish stopwords
outnumber English ones, otherwise English.

| Quantity | Old (`langdetect`) | Corrected |
|---|---|---|
| ELL-Spanish problems returned in Spanish | 53.7% | **50.4%** |
| ELL-Mandarin problems returned in Chinese | 19.5% | **24.4%** |
| English-output subsample for reading grade | — | ***n* = 1,271** |

The rule is binary, so it cannot represent bilingual output; 29 of GPT-OSS's 135 ELL-Spanish
problems contain some Spanish while classifying as English. The paper says so.

---

## 4. Smaller corrections

- **Near-duplicate count.** 107 → **106**. The removal is greedy and pairwise, so the result
  depends on row order; 106 is the figure under the committed order.
- **"Pre-registered" → "pre-specified".** `DESIGN.md` is dated 2026-07-03 but was first
  committed publicly on 2026-08-06, after data collection, with no external timestamp. It is an
  analysis plan, not an independently registered protocol, and §3.1 now says exactly that.
  Earlier versions of this README described the study as pre-registered. That was overclaiming.
- **Holm correction family.** Two robustness checks had been corrected over six tests while the
  primary analysis used nine. Brought onto the nine-test family, the ELL-Spanish effect on
  **operations** does *not* survive: *p* = .038/.047 becomes **.075/.095**. The earlier figures
  made a result look rescued that was not.
- **Measure descriptions.** The paper had implied all three math measures were read from the
  model's solution. In fact `max_operand_magnitude` is taken from the **problem statement**, and
  `n_operations` counts equals signs among its arithmetic symbols. §3.2 now says both.
- **Reference count.** 24 → **27** references, all cited and all resolving.
- **Author list.** An earlier draft listed a second author. The published paper is
  single-author: the design, data collection, ratings, analysis and writing are the author's
  own.
- **Typesetting.** The earlier conference PDF embedded 11 Type 3 bitmap fonts and had a broken
  text layer (copying "difficulty" produced mojibake). Fixed with `lmodern`; the camera-ready
  has zero Type 3 fonts and a clean, searchable text layer.

---

## 5. What did *not* change

- The data. All 1,620 generations and 1,567 readable items are the originals, collected
  2026-07-03 to 2026-07-07 and committed unchanged.
- The design, the five hypotheses, the prompts, or the conditions.
- The manipulation check's direction or significance.
- The unprompted-language-switching finding, the name-origin finding (χ²(9) = 365.6,
  Cramér's *V* = 0.28), or the answer-key audit (Llama wrong on 13 of 14 audited
  rational-number items, Mistral 14 of 27, GPT-OSS 0 of 28, judge agreeing on all 69).
- The conclusion that a language label should change language and not mathematics.

---

## 6. Where to check

| To check | Run or read |
|---|---|
| Every headline number in the camera-ready | `python3 src/verify_paper.py` (69 checks) |
| That script's output, as committed | `results/verify_paper_output.txt` |
| The original, superseded analysis | `src/analyze.py`, `results/summary.txt` |
| The analysis plan as written, unedited | `DESIGN.md` |
| The published paper | `simbig2026/104.pdf` |

Last updated 7 October 2026.
