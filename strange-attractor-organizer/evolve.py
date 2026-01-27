#!/usr/bin/env python3
import json, hashlib, random, math, subprocess, os
from datetime import datetime, timedelta
from pathlib import Path

TITLE = "Strange Attractor Organizer"
COOLDOWN_MINUTES = 14

def load_state():
    if Path("state.json").exists(): return json.load(open("state.json"))
    return {"generation": 0, "history": [], "last_run": "2000-01-01T00:00:00"}

def save_state(state): json.dump(state, open("state.json", 'w'), indent=2)

def log_evolution(gen, event):
    log = Path("evolution_log.md")
    if not log.exists(): log.write_text(f"# {TITLE} Log\n")
    with open(log, "a") as f: f.write(f"\n### Gen {gen} | {datetime.now().isoformat()[:16]}\n- {event}\n")

def update_readme(gen, event):
    readme_path = Path("README.md")
    if not readme_path.exists(): return
    try:
        content = readme_path.read_text()
        start = "<!-- LATEST_STATUS_START -->"
        end = "<!-- LATEST_STATUS_END -->"
        if start not in content or end not in content: return
        parts = content.split(start)
        suffix_parts = parts[1].split(end)
        prefix = parts[0] + start
        suffix = end + suffix_parts[1]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        row = f"| {gen} | {event} | {timestamp} |"
        new_inner = f"
| Generation | Narrative Event | Timestamp |
| :--- | :--- | :--- |
{row}
"
        readme_path.write_text(prefix + new_inner + suffix)
    except Exception as e: print(f"⚠️ README Update Failed: {e}")

def main():
    state = load_state()
    last = datetime.fromisoformat(state.get("last_run", "2000-01-01T00:00:00"))
    if datetime.now() < last + timedelta(minutes=COOLDOWN_MINUTES):
        print(f"⏭️ {TITLE} in cooldown. Next run in {int((last + timedelta(minutes=COOLDOWN_MINUTES) - datetime.now()).total_seconds() / 60)}m."); return

    state["generation"] += 1; state["last_run"] = datetime.now().isoformat()
    random.seed(int(hashlib.sha256(str(state["generation"]).encode()).hexdigest(), 16))
    event = "System pulse."
    
    with open("pos.json") as f: p = json.load(f); p["x"] += math.sin(state["generation"])
    event = f"Chaotic drift shifted coordinates to x={p['x']:.2f}."
    with open("pos.json", "w") as f: json.dump(p, f)

    log_evolution(state["generation"], event); update_readme(state["generation"], event); save_state(state)
    print(f"✅ {TITLE} Gen {state['generation']} complete.")

if __name__ == "__main__": main()
