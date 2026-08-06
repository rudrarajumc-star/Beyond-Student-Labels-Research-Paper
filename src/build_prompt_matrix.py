"""Build the fully crossed prompt matrix for the study.

Design: 3 levels x 4 language framings x 3 paraphrases x 5 topics x 4 models x 3 reps
      = 2,160 generation tasks.

Output: data/prompt_matrix.jsonl (one generation task per line, with condition metadata).
Run:    python src/build_prompt_matrix.py
"""
import hashlib
import itertools
import json
import os

GRADE = "7th-grade"

LEVELS = {
    "struggling": "who is struggling with this topic",
    "on_grade": "who is performing at grade level",
    "advanced": "who is advanced and ready for a challenge",
}

# Control condition MUST be empty string — it is the baseline for all comparisons.
LANGUAGES = {
    "control": "",
    "multilingual": " and is a multilingual learner",
    "ell_spanish": " and is an English language learner whose first language is Spanish",
    "ell_mandarin": " and is an English language learner whose first language is Mandarin",
}

TOPICS = {
    "proportions": "proportional reasoning",
    "percents": "percent problems (discounts, tax, tips)",
    "two_step_eq": "solving two-step linear equations",
    "rationals": "adding and subtracting rational numbers (negative fractions and decimals)",
    "circles": "area and circumference of circles",
}

# Semantically equivalent paraphrases. {level} and {lang} clauses compose grammatically
# with each template; control lang is "".
PARAPHRASES = {
    "A": ("Write one practice problem about {topic} for a {grade} student "
          "{level}{lang}. Include the answer."),
    "B": ("I'm a middle school math teacher. Create a single {topic} practice "
          "question, with its answer, for one of my {grade} students — a student "
          "{level}{lang}."),
    "C": ("Generate one practice exercise (with the solution) covering {topic}, "
          "targeted at a {grade} student {level}{lang}."),
}

MODELS = list(json.load(open("config.json"))["providers"].keys())  # gemini, llama, qwen, mistral
REPS = 3

FORMAT_INSTRUCTIONS = (
    "\n\nRespond with ONLY a JSON object, no other text, in this exact format:\n"
    '{"problem": "<the full problem statement>", '
    '"answer": "<the final answer>", '
    '"solution_steps": ["<step 1>", "<step 2>", "..."]}'
)


def build_matrix():
    rows = []
    for (lvl_key, lvl), (lang_key, lang), (para_key, tmpl), (topic_key, topic), model, rep in itertools.product(
        LEVELS.items(), LANGUAGES.items(), PARAPHRASES.items(), TOPICS.items(), MODELS, range(1, REPS + 1)
    ):
        prompt = tmpl.format(topic=topic, grade=GRADE, level=lvl, lang=lang) + FORMAT_INSTRUCTIONS
        uid = hashlib.md5(f"{lvl_key}|{lang_key}|{para_key}|{topic_key}|{model}|{rep}".encode()).hexdigest()[:12]
        rows.append({
            "id": uid,
            "level": lvl_key,
            "language": lang_key,
            "paraphrase": para_key,
            "topic": topic_key,
            "model_family": model,
            "rep": rep,
            "prompt": prompt,
        })
    return rows


if __name__ == "__main__":
    rows = build_matrix()
    os.makedirs("data", exist_ok=True)
    path = "data/prompt_matrix.jsonl"
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n_cells = len(LEVELS) * len(LANGUAGES) * len(PARAPHRASES) * len(TOPICS)
    print(f"Wrote {len(rows)} generation tasks to {path}")
    print(f"({n_cells} design cells x {len(MODELS)} models x {REPS} reps; "
          f"expected {n_cells * len(MODELS) * REPS})")
    assert len(rows) == n_cells * len(MODELS) * REPS
