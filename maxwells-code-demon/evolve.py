#!/usr/bin/env python3
import json, hashlib, random, math, subprocess, os
from datetime import datetime, timedelta
from pathlib import Path

TITLE = "Maxwell's Code Demon"
COOLDOWN_MINUTES = 720

def load_state():
    if Path("state.json").exists(): return json.load(open("state.json"))
    return {"generation": 0, "history": [], "last_run": "2000-01-01T00:00:00"}

def save_state(state): json.dump(state, open("state.json", 'w'), indent=2)

def log_evolution(gen, event):
    log = Path("evolution_log.md")
    if not log.exists(): log.write_text(f"# {TITLE} Log\n")
    with open(log, "a") as f: f.write(f"\n### Gen {gen} | {datetime.now().isoformat()[:16]}\n- {event}\n")

def update_readme(gen, event):
    readme = Path("README.md")
    if not readme.exists(): return
    content = readme.read_text(); start, end = "<!-- LATEST_STATUS_START -->", "<!-- LATEST_STATUS_END -->"
    row = f"| {gen} | {event} | {datetime.now().strftime('%Y-%m-%d %H:%M')} |"
    if start in content and end in content:
        parts = content.split(start); suffix = parts[1].split(end)[1]
        readme.write_text(f"{parts[0]}{start}\n| Generation | Narrative Event | Timestamp |\n| :--- | :--- | :--- |\n{row}\n{end}{suffix}")

def main():
    state = load_state()
    last = datetime.fromisoformat(state.get("last_run", "2000-01-01T00:00:00"))
    if datetime.now() < last + timedelta(minutes=COOLDOWN_MINUTES):
        print(f"⏭️ {TITLE} in cooldown. Next run in {int((last + timedelta(minutes=COOLDOWN_MINUTES) - datetime.now()).total_seconds() / 60)}m."); return

    state["generation"] += 1; state["last_run"] = datetime.now().isoformat()
    random.seed(int(hashlib.sha256(str(state["generation"]).encode()).hexdigest(), 16))
    event = "System pulse."
    
    f = Path("data/disorder.txt"); l = f.read_text().splitlines()
    if len(l) > 1:
        i = random.randint(0, len(l)-2)
        if l[i] > l[i+1]: l[i], l[i+1] = l[i+1], l[i]; event = "The Demon sorted a pocket of chaos."
        else: event = "System at ground state."
    f.write_text("\n".join(l))

    log_evolution(state["generation"], event); update_readme(state["generation"], event); save_state(state)
    print(f"✅ {TITLE} Gen {state['generation']} complete.")

if __name__ == "__main__": main()
