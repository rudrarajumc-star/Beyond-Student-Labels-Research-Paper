"""One-command driver: loads keys from .env, self-heals the config, cleans the
data file, verifies every provider, then runs the full generation.

Usage (from the project folder):
  caffeinate -i python3 src/run_study.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)


def load_env():
    if not os.path.exists(".env"):
        sys.exit("No .env file found.")
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    print("[1/5] Keys loaded from .env")


def client_for(cfg):
    from openai import OpenAI
    return OpenAI(api_key=os.environ[cfg["api_key_env"]], base_url=cfg["base_url"])


def try_model(cfg, model_id):
    try:
        # generous budget: reasoning models (gpt-oss) burn tokens thinking first
        r = client_for(cfg).chat.completions.create(
            model=model_id, max_tokens=max(cfg.get("max_tokens", 0), 500),
            messages=[{"role": "user", "content": "Say hi"}])
        r.choices[0].message  # a completed call without exception = provider works
        return True
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print(f"      {model_id}: rate-limited/quota (model is valid; will "
                  f"retry during the run or after quota resets)")
            return True
        print(f"      {model_id}: {str(e)[:110]}")
        return False


def heal_gemini(config):
    """Find a Gemini model this key can actually use; pin it in config.json."""
    cfg = config["providers"]["gemini"]
    candidates = [cfg["model"], "gemini-2.5-flash", "gemini-2.5-flash-lite",
                  "gemini-flash-latest"]
    # also ask the API what exists
    try:
        listed = [m.id for m in client_for(cfg).models.list().data]
        candidates += [m for m in listed if "flash" in m and "image" not in m
                       and "tts" not in m and "live" not in m]
    except Exception as e:
        print(f"      (model list unavailable: {str(e)[:80]})")
    seen = set()
    for m in [c for c in candidates if not (c in seen or seen.add(c))]:
        print(f"      trying {m} ...")
        if try_model(cfg, m):
            if m != cfg["model"]:
                cfg["model"] = m
                json.dump(config, open("config.json", "w"), indent=2)
            print(f"[2/5] Gemini OK -> pinned {m}")
            return True
    print("[2/5] FAILED: no working Gemini model. Get an AIza... key from "
          "aistudio.google.com, put it in .env, rerun.")
    return False


def verify_others(config):
    ok = True
    for fam, cfg in config["providers"].items():
        if fam == "gemini":
            continue
        good = try_model(cfg, cfg["model"])
        print(f"      {fam} ({cfg['model']}): {'OK' if good else 'FAILED'}")
        ok = ok and good
    print(f"[3/5] Provider check {'passed' if ok else 'FAILED'}")
    return ok


def clean_data():
    path = "data/generations.jsonl"
    if not os.path.exists(path):
        print("[4/5] No existing data — starting fresh")
        return
    rows = [json.loads(l) for l in open(path) if l.strip()]
    seen, keep = set(), []
    for r in rows:
        if str(r.get("parse_status", "")).startswith("api_error"):
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        keep.append(r)
    with open(path, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in keep)
    print(f"[4/5] Data cleaned: kept {len(keep)} good rows "
          f"(removed {len(rows) - len(keep)} errors/duplicates)")


if __name__ == "__main__":
    load_env()
    config = json.load(open("config.json"))
    if config["providers"]["gemini"].get("skip"):
        print("[2/5] Gemini SKIPPED (dropped from study per DESIGN.md amendment)")
    elif not heal_gemini(config):
        sys.exit(1)
    if not verify_others(config):
        sys.exit("Fix the failed provider key in .env, then rerun.")
    clean_data()
    if not os.path.exists("data/prompt_matrix.jsonl"):
        subprocess.run([sys.executable, "src/build_prompt_matrix.py"], check=True)
    print("[5/5] Launching full generation run (interrupt-safe; rerun to resume)\n")
    subprocess.run([sys.executable, "src/generate.py"])
