"""Run generations across 4 free-tier providers (all OpenAI-compatible endpoints).
Resumable: re-running skips completed IDs.

Env vars required (free, no credit card, all work from India):
  GEMINI_API_KEY    https://aistudio.google.com        (Gemini 2.0 Flash)
  GROQ_API_KEY      https://console.groq.com           (Llama 3.3 70B)
  CEREBRAS_API_KEY  https://cloud.cerebras.ai          (Qwen 3 32B)
  MISTRAL_API_KEY   https://console.mistral.ai         (Mistral Small)

Usage:
  python3 src/generate.py                  # run everything remaining
  python3 src/generate.py --family gemini  # one provider only
  python3 src/generate.py --limit 40       # smoke test

Output: data/generations.jsonl  (raw response + parsed JSON + parse status per row)
"""
import argparse
import json
import os
import sys
import time

CONFIG = json.load(open("config.json"))
TEMP = CONFIG["temperature"]
MAXTOK = CONFIG["max_tokens"]
PROVIDERS = CONFIG["providers"]

MATRIX = "data/prompt_matrix.jsonl"
OUT = "data/generations.jsonl"

_clients = {}


def call_provider(family, prompt):
    """All four providers speak the OpenAI chat-completions protocol."""
    from openai import OpenAI
    cfg = PROVIDERS[family]
    key = os.environ.get(cfg["api_key_env"])
    if not key:
        raise RuntimeError(f"Set {cfg['api_key_env']} first (see README).")
    if family not in _clients:
        _clients[family] = OpenAI(api_key=key, base_url=cfg["base_url"])
    r = _clients[family].chat.completions.create(
        model=cfg["model"], temperature=TEMP,
        max_tokens=cfg.get("max_tokens", MAXTOK),  # reasoning models need headroom
        messages=[{"role": "user", "content": prompt}])
    return r.choices[0].message.content


def parse_output(text):
    """Extract the JSON object; tolerate code fences and <think> blocks (Qwen).
    Returns (parsed_or_None, status)."""
    if text is None:
        return None, "empty"
    t = text.strip()
    # strip Qwen-style thinking blocks
    if "</think>" in t:
        t = t.split("</think>")[-1].strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    start, end = t.find("{"), t.rfind("}")
    if start == -1 or end == -1:
        return None, "no_json"
    try:
        obj = json.loads(t[start:end + 1])
    except json.JSONDecodeError:
        return None, "bad_json"
    if not all(k in obj for k in ("problem", "answer", "solution_steps")):
        return obj, "missing_keys"
    return obj, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", choices=list(PROVIDERS), default=None)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    tasks = [json.loads(l) for l in open(MATRIX)]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["id"] for l in open(OUT)}
    todo = [t for t in tasks if t["id"] not in done
            and not PROVIDERS[t["model_family"]].get("skip")
            and (args.family is None or t["model_family"] == args.family)]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(done)} done, {len(todo)} to run.")

    disabled, streak = set(), {}
    with open(OUT, "a") as out:
        for i, t in enumerate(todo, 1):
            fam = t["model_family"]
            if fam in disabled:
                continue
            text, err = None, None
            for attempt in range(3):
                try:
                    text = call_provider(fam, t["prompt"])
                    break
                except Exception as e:
                    err = str(e)
                    time.sleep(20 * (attempt + 1) if ("429" in err or "rate" in err.lower())
                               else 5 * (attempt + 1))
            if text is None:
                # do NOT record api errors as done — they retry on the next run
                streak[fam] = streak.get(fam, 0) + 1
                print(f"  ! {fam} API failure #{streak[fam]}: {str(err)[:100]}", flush=True)
                if streak[fam] >= 5:
                    disabled.add(fam)
                    print(f"  !! {fam} BENCHED for this session (quota exhausted?). "
                          f"Rerun later — it resumes automatically.", flush=True)
                continue
            streak[fam] = 0
            parsed, status = parse_output(text)
            row = {**t, "model_id": PROVIDERS[fam]["model"], "raw_output": text,
                   "parsed": parsed, "parse_status": status}
            out.write(json.dumps(row) + "\n")
            out.flush()
            if i % 25 == 0:
                print(f"  {i}/{len(todo)} ({fam})", flush=True)
            time.sleep(PROVIDERS[fam]["seconds_between_calls"])
    done_now = len(done) + len([1 for l in open(OUT)]) - len(done) if os.path.exists(OUT) else 0
    print(f"Done. Benched this session: {sorted(disabled) or 'none'}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
