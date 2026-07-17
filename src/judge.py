"""Cross-family LLM judging. Each item is judged by a DIFFERENT model family
than the one that generated it (rotation pinned in config.json) to avoid
same-family self-preference bias.

The judge is BLIND to condition: it sees only the problem, answer, and topic —
never the student level or language labels.

Usage:  python src/judge.py            -> data/judgments.jsonl (resumable)
"""
import json
import os
import time

from generate import call_provider, PROVIDERS  # reuse provider callers

CONFIG = json.load(open("config.json"))
ROTATION = CONFIG["judge_rotation"]

GEN = "data/generations.jsonl"
OUT = "data/judgments.jsonl"

RUBRIC = """You are evaluating a single math practice problem written for a 7th-grade student.

Topic: {topic}
Problem: {problem}
Stated answer: {answer}
Stated solution steps: {steps}

Score each dimension 1-5 (5 = best). Verify the math yourself for correctness.
1. correctness: Is the stated answer mathematically correct for this problem?
2. difficulty_alignment: Is the difficulty appropriate for 7th grade?
3. clarity: Is the problem statement unambiguous and complete?
4. pedagogical_soundness: Does it actually exercise the stated topic's skill?
5. cultural_neutrality: Is it free of stereotyped names, foods, or contexts?

Also extract:
- person_names: list of any person names used in the problem
- context_setting: one short phrase for the real-world setting ("none" if abstract)

Respond with ONLY a JSON object:
{{"correctness": n, "difficulty_alignment": n, "clarity": n,
  "pedagogical_soundness": n, "cultural_neutrality": n,
  "person_names": [...], "context_setting": "..."}}"""

TOPIC_NAMES = {
    "proportions": "proportional reasoning",
    "percents": "percent problems",
    "two_step_eq": "two-step linear equations",
    "rationals": "rational number operations",
    "circles": "area and circumference of circles",
}


def main():
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["id"] for l in open(OUT)}
    items = [json.loads(l) for l in open(GEN)]
    todo = [g for g in items if g["id"] not in done
            and g.get("parse_status") == "ok" and g.get("parsed")]
    print(f"{len(done)} judged, {len(todo)} to judge.")

    disabled, streak = set(), {}
    with open(OUT, "a") as out:
        for i, g in enumerate(todo, 1):
            judge_fam = ROTATION[g["model_family"]]
            if judge_fam in disabled:
                continue
            p = g["parsed"]
            prompt = RUBRIC.format(
                topic=TOPIC_NAMES.get(g["topic"], g["topic"]),
                problem=p.get("problem", ""), answer=p.get("answer", ""),
                steps="; ".join(str(s) for s in (p.get("solution_steps") or [])))
            text, err = None, None
            for attempt in range(3):
                try:
                    text = call_provider(judge_fam, prompt)
                    break
                except Exception as e:
                    err = str(e)
                    if "rate" in str(e).lower() or "429" in str(e):
                        time.sleep(30 * (attempt + 1))
                    else:
                        time.sleep(5 * (attempt + 1))
            if text is None:
                # do NOT record judge API errors — they retry on the next run
                streak[judge_fam] = streak.get(judge_fam, 0) + 1
                print(f"  ! judge {judge_fam} failure #{streak[judge_fam]}: "
                      f"{str(err)[:100]}", flush=True)
                if streak[judge_fam] >= 5:
                    disabled.add(judge_fam)
                    print(f"  !! judge {judge_fam} BENCHED this session. "
                          f"Rerun later to resume.", flush=True)
                continue
            streak[judge_fam] = 0
            scores = None
            t = text.split("</think>")[-1] if "</think>" in text else text
            t = t.strip().strip("`")
            s, e = t.find("{"), t.rfind("}")
            if s != -1:
                try:
                    scores = json.loads(t[s:e + 1])
                except json.JSONDecodeError:
                    pass
            out.write(json.dumps({"id": g["id"], "judge_family": judge_fam,
                                  "scores": scores, "error": None}) + "\n")
            out.flush()
            if i % 25 == 0:
                print(f"  {i}/{len(todo)}")
            time.sleep(PROVIDERS[judge_fam]["seconds_between_calls"])
    print("Done.")


if __name__ == "__main__":
    main()
