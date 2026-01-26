#!/usr/bin/env python3
import os
import json
import hashlib
import random
import math
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Final 19 Projects with Meta-Frequency (Cooldowns in Minutes)
PROJECTS = [
    {
        "name": "algorithmic-stone-garden",
        "title": "Algorithmic Stone Garden",
        "principle": "Wang Tiling Rules / Aperiodic Tiling",
        "trigger": "Daily placement of tiles.",
        "cooldown": 1440, # Daily
        "evolve_logic": r'''
    h = hashlib.sha256(str(state['generation']).encode()).hexdigest()
    edges = [int(h[i:i+2], 16) % 4 for i in range(0, 8, 2)]
    event = f"The garden expanded! A new mathematical tile was laid down matching its neighbors."
    Path("data").mkdir(exist_ok=True)
    (Path("data") / f"tile_{state['generation']:04d}.json").write_text(json.dumps({"edges": edges}))
'''
    },
    {
        "name": "library-of-babel",
        "title": "The Library of Babel",
        "principle": "Combinatorics / Total Information Space",
        "trigger": "Weekly exploration.",
        "cooldown": 10080, # Weekly
        "evolve_logic": r'''
    content = "".join(random.choice("abcdefghijklmnopqrstuvwxyz ") for _ in range(80))
    event = f"The librarian explored a new shelf and found the phrase: '{content[:20]}...'"
    (Path("data") / f"page_{state['generation']:04d}.txt").write_text(content)
'''
    },
    {
        "name": "digital-ecosphere",
        "title": "Digital Ecosphere",
        "principle": "Genetic Algorithms",
        "trigger": "Hourly evolution tournament.",
        "cooldown": 60,
        "evolve_logic": r'''
    import zlib
    orgs = list(Path("organisms").glob("*.bin"))
    if orgs:
        best_org = min(orgs, key=lambda p: len(zlib.compress(p.read_bytes())))
        new_data = bytearray(best_org.read_bytes())
        if new_data:
            idx = random.randint(0, len(new_data)-1)
            new_data[idx] ^= (1 << random.randint(0, 7))
        Path(f"organisms/mutant_{state['generation']}.bin").write_bytes(new_data)
        event = f"The strongest file, {best_org.name}, produced a mutated descendant."
    else: event = "Ecosystem extinct."
'''
    },
    {
        "name": "chaitins-oracle",
        "title": "Chaitin's Oracle Machine",
        "principle": "Ω approximation via sampling.",
        "trigger": "Continuous sampling (every 15m).",
        "cooldown": 14,
        "evolve_logic": r'''
    halted = random.random() > 0.5
    with open("omega.txt", "a") as f: f.write("1" if halted else "0")
    event = f"The Oracle peered into the abyss and saw a program 'halt' (1)." if halted else "The Oracle saw a program 'loop' (0)."
'''
    },
    {
        "name": "lamarckian-library",
        "title": "Lamarckian Library",
        "principle": "Verification / Self-Correction",
        "trigger": "Daily corrective push.",
        "cooldown": 1440,
        "evolve_logic": r'''
    f_p = Path("functions/f1.py")
    if "+ 1" in f_p.read_text():
        f_p.write_text("def f(x): return x")
        event = "The code corrected its identity function behavior."
    else: event = "Logic set stable; no errors found."
'''
    },
    {
        "name": "clock-of-long-now",
        "title": "The Clock of the Long Now",
        "principle": "Number Theory / Deterministic Time",
        "trigger": "Hourly cryptographic swing.",
        "cooldown": 59,
        "evolve_logic": r'''
    c_f = Path("counter.txt"); val = int(c_f.read_text())
    val += 1 if hashlib.sha256(str(val).encode()).digest()[-1] > 127 else -1
    c_f.write_text(str(val))
    event = f"The pendulum swung; current time-state: {val}."
'''
    },
    {
        "name": "maxwells-code-demon",
        "title": "Maxwell's Code Demon",
        "principle": "Entropy Balancing.",
        "trigger": "Twice daily sorting.",
        "cooldown": 720,
        "evolve_logic": r'''
    f = Path("data/disorder.txt"); l = f.read_text().splitlines()
    if len(l) > 1:
        i = random.randint(0, len(l)-2)
        if l[i] > l[i+1]: l[i], l[i+1] = l[i+1], l[i]; event = "The Demon sorted a pocket of chaos."
        else: event = "System at ground state."
    f.write_text("\n".join(l))
'''
    },
    {
        "name": "zenos-paradox",
        "title": "Zeno's Commit Paradox",
        "principle": "Infinite Series / Subdivision",
        "trigger": "Daily subdivision.",
        "cooldown": 1440,
        "evolve_logic": r'''
    f = Path("target.txt"); c = f.read_text()
    if len(c) > 1: f.write_text(c[:len(c)//2]); event = f"The paradox holds: the file vanished by half, now at {len(c)//2} bytes."
    else: event = "Zeno Limit: 1 byte remains reachable."
'''
    },
    {
        "name": "turing-tumble",
        "title": "Turing Tumble in Git",
        "principle": "Deterministic Logic Flow",
        "trigger": "Hourly signal propagation.",
        "cooldown": 60,
        "evolve_logic": r'''
    h = hashlib.sha256(Path("start.marble").read_bytes()).hexdigest()
    event = f"Signal chain reached output node {h[:8]}."
    (Path("data") / f"node_{h[:8]}.active").touch()
'''
    },
    {
        "name": "mandelbrot-explorer",
        "title": "The Mandelbrot Set Explorer",
        "principle": "Orbit escapes.",
        "trigger": "Daily fractal diving.",
        "cooldown": 1440,
        "evolve_logic": r'''
    with open("point.json") as f: p = json.load(f)
    z, c = 0j, complex(p["re"], p["im"])
    for _ in range(5): z = z*z + c
    event = f"Dived deeper into the fractal boundary; orbit magnitude: {abs(z):.2f}."
    (Path("data") / f"orbit_{state['generation']}.txt").write_text(str(z))
'''
    },
    {
        "name": "conways-fractran",
        "title": "Conway's Fractran",
        "principle": "Turing-complete prime math.",
        "trigger": "Rapid math (every 30m).",
        "cooldown": 29,
        "evolve_logic": r'''
    n = int(Path("state.txt").read_text()); fracs = [(3,2), (5,3), (1,5)]
    for num, den in fracs:
        if (n*num)%den == 0: n = (n*num)//den; break
    Path("state.txt").write_text(str(n))
    event = f"State transitioned to {n}. The prime sequence continues."
'''
    },
    {
        "name": "digital-phyllotaxis",
        "title": "Digital Phyllotaxis",
        "principle": "Golden angle packing.",
        "trigger": "Daily growth.",
        "cooldown": 1440,
        "evolve_logic": r'''
    with open("grow.json") as f: d = json.load(f); n = d["n"] + 1
    r, t = math.sqrt(n), n * 2.39996
    event = f"The project bloomed; seed {n} was placed."
    (Path("data") / f"seed_{n:04d}.txt").write_text(f"{r*math.cos(t)},{r*math.sin(t)}")
    with open("grow.json", "w") as f: json.dump({"n": n}, f)
'''
    },
    {
        "name": "busy-beaver-hunter",
        "title": "The Busy Beaver Hunter",
        "principle": "Uncomputability search.",
        "trigger": "Hourly scout missions.",
        "cooldown": 60,
        "evolve_logic": r'''
    high = int(Path("champion.txt").read_text()); curr = random.randint(0, high + 10)
    if curr > high: Path("champion.txt").write_text(str(curr)); event = f"The hunter found a new record holder: {curr} steps."
    else: event = "The hunter searched program space; record holds."
'''
    },
    {
        "name": "hash-sound",
        "title": "Hash Sound",
        "principle": "Sonification.",
        "trigger": "Hourly harmonics.",
        "cooldown": 60,
        "evolve_logic": r'''
    h = hashlib.sha256(str(state['generation']).encode()).digest(); freq = (h[0] * 4) + 200
    event = f"The project struck a new chord at {freq}Hz."
'''
    },
    {
        "name": "pi-search-engine",
        "title": "Pi Search Engine",
        "principle": "Walking pi's digits.",
        "trigger": "Rapid navigation (15m).",
        "cooldown": 14,
        "evolve_logic": r'''
    p = int(Path("pos.txt").read_text()) + random.randint(1, 42)
    Path("pos.txt").write_text(str(p)); event = f"Walked further into Pi's digits to index {p}."
'''
    },
    {
        "name": "digital-droplet",
        "title": "Digital Droplet",
        "principle": "Fluid Dynamics",
        "trigger": "Rapid simulation (15m).",
        "cooldown": 14,
        "evolve_logic": r'''
    v = state.get("vibration", 0.1); m_p = Path("mols.json"); m = json.loads(m_p.read_text())
    if len(m) > 1: m[0]["x"] += v; m[1]["x"] -= v; event = "Droplets drifted closer."
    else: event = "Merged into a stable pool."
    m_p.write_text(json.dumps(m))
'''
    },
    {
        "name": "oracle-of-ramsey",
        "title": "The Oracle of Ramsey",
        "principle": "Inevitable Graph Patterns.",
        "trigger": "Weekly graph updates.",
        "cooldown": 10080,
        "evolve_logic": r'''
    with open("graph.json") as f: g = json.load(f); g["nodes"] += 1
    event = f"Social graph grew to {g['nodes']} nodes; patterns checked."
    with open("graph.json", "w") as f: json.dump(g, f)
'''
    },
    {
        "name": "strange-attractor-organizer",
        "title": "Strange Attractor Organizer",
        "principle": "Lorenz Chaos Dynamics.",
        "trigger": "Continuous drift (15m).",
        "cooldown": 14,
        "evolve_logic": r'''
    with open("pos.json") as f: p = json.load(f); p["x"] += math.sin(state["generation"])
    event = f"Chaotic drift shifted coordinates to x={p['x']:.2f}."
    with open("pos.json", "w") as f: json.dump(p, f)
'''
    },
    {
        "name": "thermodynamic-code-simulator",
        "title": "Thermodynamic Code Simulator",
        "principle": "Entropy Equilibrium.",
        "trigger": "Continuous cooling (15m).",
        "cooldown": 14,
        "evolve_logic": r'''
    t_f = Path("temp.txt"); t = float(t_f.read_text()) * state.get("cooling_rate", 0.99)
    t_f.write_text(f"{t:.2f}"); event = f"Energy radiated into void; system at {t:.2f}K."
'''
    }
]

# README and MASTER TEMPLATES remain similar but with link improvements
README_TEMPLATE = """# {title}

![Autonomous System Status](https://github.com/Abhisheksinha1506/autonomous-deepseek/actions/workflows/deepseek-autonomous.yml/badge.svg)

## ⬅️ [Back to Master Dashboard](../README.md)

## 📢 Latest Status
<!-- LATEST_STATUS_START -->
| Generation | Narrative Event | Timestamp |
| :--- | :--- | :--- |
| 0 | Project Initialized | {now} |
<!-- LATEST_STATUS_END -->

## 📖 Pro-Link Discovery
- **State**: [[state.json]](state.json)
- **Engine**: [[evolve.py]](evolve.py)
- **Manifest**: [[data/]] directory

## 🧠 Autonomous Principle
**{principle}**

---
**Trigger**: {trigger} | **Status**: 🟢 Active | **Output**: Narrative.
"""

MASTER_README_TEMPLATE = """# Autonomous Deepseek Project Suite

This directory contains {count} entities evolving via high-frequency GitHub Actions.

## 🕹️ Central Command
- **Master Trigger**: [*/15 * * * *](../.github/workflows/deepseek-autonomous.yml)

## 🧬 Project Census
| Project | Concept | Frequency |
| :--- | :--- | :--- |
{table_rows}
"""

EVOLVE_TEMPLATE = r'''#!/usr/bin/env python3
import json, hashlib, random, math, subprocess, os
from datetime import datetime, timedelta
from pathlib import Path

TITLE = "__TITLE__"
COOLDOWN_MINUTES = __COOLDOWN__

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
    __LOGIC__
    log_evolution(state["generation"], event); update_readme(state["generation"], event); save_state(state)
    print(f"✅ {TITLE} Gen {state['generation']} complete.")

if __name__ == "__main__": main()
'''

def main():
    base_dir = Path("/Users/abhisheksinha/Desktop/Autogit/autonomous-deepseek")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    table_rows = []
    
    for p in PROJECTS:
        p_dir = base_dir / p["name"]; p_dir.mkdir(parents=True, exist_ok=True); (p_dir / "data").mkdir(exist_ok=True)
        (p_dir / "README.md").write_text(README_TEMPLATE.format(now=now_str, **p))
        
        logic = p["evolve_logic"]
        content = EVOLVE_TEMPLATE.replace("__TITLE__", p["title"]).replace("__COOLDOWN__", str(p["cooldown"])).replace("__LOGIC__", logic)
        (p_dir / "evolve.py").write_text(content); (p_dir / "evolve.py").chmod(0o755)
        
        if not (p_dir / "state.json").exists(): (p_dir / "state.json").write_text(json.dumps({"generation": 0, "last_run": "2000-01-01T00:00:00"}, indent=2))
        table_rows.append(f"| [{p['title']}]({p['name']}/README.md) | {p['principle']} | {p['trigger']} |")
        print(f"Cooldown Scaffolding: {p['name']}")

    (base_dir / "README.md").write_text(MASTER_README_TEMPLATE.format(count=len(PROJECTS), table_rows="\n".join(table_rows)))
    print(f"\n🎉 Frequency Optimizations Complete!")

if __name__ == "__main__": main()
