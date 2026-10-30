"""
Run play_live.py for every agent, level and seed and collect the results.

    python live_game/run_live_trials.py --assets PATH/TO/TutorialProject --game PATH/TO/main_work_greedy.py

Each trial runs in its own process (the game can only be started once per
process). Results go to results/05_live_game/: one JSON per trial plus
live_trials.csv and live_summary.csv. Trials that already have a JSON are
skipped, so the run can be restarted.
"""

import argparse
import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "05_live_game")
AGENTS = ["greedy", "ga_task2", "proposed"]
LEVELS = [1, 7, 14, 18, 21, 22, 23, 24]
SEEDS = [0, 1, 2]
FIELDS = ["agent", "level", "seed", "outcome", "won", "coins_collected", "coins_total",
          "coin_pct", "remaining_life", "seconds", "moves", "mean_plan_ms"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True)
    parser.add_argument("--game", required=True)
    args = parser.parse_args()
    os.makedirs(os.path.join(OUT, "trials"), exist_ok=True)

    rows = []
    for level in LEVELS:
        for seed in SEEDS:
            for agent in AGENTS:
                path = os.path.abspath(os.path.join(OUT, "trials", "%s_L%d_s%d.json" % (agent, level, seed)))
                if not os.path.exists(path):
                    subprocess.run([sys.executable, os.path.join(HERE, "play_live.py"),
                                    "--assets", args.assets, "--game", args.game,
                                    "--agent", agent, "--level", str(level), "--seed", str(seed),
                                    "--json", path],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
                if os.path.exists(path):
                    with open(path) as handle:
                        row = json.load(handle)
                else:
                    row = {"agent": agent, "level": level, "seed": seed, "outcome": "aborted", "won": False}
                rows.append(row)
                print(agent, level, seed, row.get("outcome"), row.get("seconds"), row.get("remaining_life"), flush=True)

    with open(os.path.join(OUT, "live_trials.csv"), "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    with open(os.path.join(OUT, "live_summary.csv"), "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["agent", "trials", "success_rate", "completion_time_mean", "remaining_life_mean"])
        for agent in AGENTS:
            mine = [r for r in rows if r["agent"] == agent]
            won = [r for r in mine if r.get("won")]
            life = [r["remaining_life"] for r in mine if "remaining_life" in r]
            writer.writerow([agent, len(mine), round(100.0 * len(won) / len(mine), 1),
                             round(sum(r["seconds"] for r in won) / len(won), 2) if won else "",
                             round(sum(life) / len(life), 1) if life else ""])


if __name__ == "__main__":
    main()
