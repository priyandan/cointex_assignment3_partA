"""
Runs the agents on the levels and saves the results.

All agents get the same (level, seed) pairs so we can compare them fairly.
Results go into a csv one row at a time, and rows that are already there
get skipped, so if Colab disconnects we just run the cell again.
"""

import csv
import hashlib
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

from . import sim
from .agents.ga_task2 import GAAgent
from .agents.greedy import GreedyAgent
from .agents import proposed as _proposed
from .agents.proposed import VARIANTS, ProposedAgent

FIELDS = ["level", "seed", "agent", "hazard_speed", "won", "died", "timeout",
          "coins_total", "coins_collected", "coin_pct",
          "seconds", "completion_time", "remaining_life",
          "monster_hit_frames", "fire_hit_frames", "near_miss_pct",
          "path_length", "racr", "decisions", "mean_plan_ms", "max_plan_ms",
          "wall_seconds"]


def make_agent(name, seed, config=None):
    if name == "greedy":
        return GreedyAgent(seed)
    if name == "ga_task2":
        return GAAgent(seed)
    if config is not None:
        return ProposedAgent(seed, config)
    if name in VARIANTS:
        return ProposedAgent(seed, VARIANTS[name])
    raise KeyError(name)


def play_episode(level, seed, agent_name, config=None, record=False,
                 time_limit=sim.TIME_LIMIT_SECONDS, hazard_speed=1.0):
    # play one level until win / death / timeout and return the results
    # (record=True also keeps every frame so we can draw it or make a gif)
    env = sim.CoinTexSim(level, seed, time_limit=time_limit, hazard_speed=hazard_speed)
    agent = make_agent(agent_name, seed, config)
    trace = {"char": [env.agent.copy()], "monsters": [], "fires": [], "coins_left": [],
             "coins": [], "plans": []} if record else None
    plan_ms = []
    decisions = 0
    wall0 = time.perf_counter()
    while not env.done:
        obs = env.observe()
        t0 = time.perf_counter()
        target, wait_frames = agent.act(obs)
        plan_ms.append((time.perf_counter() - t0) * 1000.0)
        decisions += 1
        env.command(target)
        for _ in range(max(1, int(wait_frames))):
            if env.done:
                break
            env.step_frame()
            if record:
                trace["char"].append(env.agent.copy())
                trace["monsters"].append([m["pos"].copy() for m in env.monsters])
                trace["fires"].append([f["pos"].copy() for f in env.fires])
                trace["coins_left"].append(len(env.coins))
                trace["coins"].append([c.copy() for c in env.coins])
        if record and getattr(agent, "last_plan", None) is not None:
            trace["plans"].append((env.frames, list(agent.last_plan)))

    coins_collected = env.num_coins - len(env.coins)
    life = env.remaining_life_fraction()
    secs = env.seconds
    row = {
        "level": level, "seed": seed, "agent": agent_name if config is None else config.name,
        "hazard_speed": hazard_speed,
        "won": int(env.won), "died": int(env.killed), "timeout": int(env.timed_out),
        "coins_total": env.num_coins, "coins_collected": coins_collected,
        "coin_pct": round(100.0 * coins_collected / env.num_coins, 2),
        "seconds": round(secs, 3),
        "completion_time": round(secs, 3) if env.won else float("nan"),
        "remaining_life": round(100.0 * life, 2),
        "monster_hit_frames": env.monster_hit_frames,
        "fire_hit_frames": env.fire_hit_frames,
        "near_miss_pct": round(100.0 * env.near_miss_frames / max(env.frames, 1), 2),
        "path_length": round(env.path_length, 3),
        # our extra metric (RACR): coins per second x life left
        "racr": round((coins_collected / max(secs, 1e-9)) * life, 4),
        "decisions": decisions,
        "mean_plan_ms": round(float(np.mean(plan_ms)), 3) if plan_ms else 0.0,
        "max_plan_ms": round(float(np.max(plan_ms)), 3) if plan_ms else 0.0,
        "wall_seconds": round(time.perf_counter() - wall0, 3),
    }
    if record:
        trace["env"] = env
        trace["coin_times"] = list(env.coin_times)
        return row, trace
    return row


def _job(args):
    level, seed, agent_name, config, speed = args
    return play_episode(level, seed, agent_name, config=config, hazard_speed=speed)


def _done_keys(path):
    # which runs are already in the csv
    if not os.path.exists(path):
        return set()
    with open(path, newline="") as f:
        return {(int(r["level"]), int(r["seed"]), r["agent"], float(r["hazard_speed"]))
                for r in csv.DictReader(f)}


def run_sweep(csv_path, levels, seeds, agents, configs=None, workers=None, verbose=True,
              hazard_speeds=(1.0,)):
    # agents  = list of agent names ("greedy", "ga_task2", "proposed", ...)
    # configs = extra proposed settings to try, {name: Config} (for the sensitivity test)
    configs = configs or {}
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    done = _done_keys(csv_path)
    jobs = []
    for speed in hazard_speeds:
        speed = float(speed)
        for level in levels:
            for seed in seeds:
                for name in agents:
                    if (level, seed, name, speed) not in done:
                        jobs.append((level, seed, name, None, speed))
                for name, cfg in configs.items():
                    if (level, seed, name, speed) not in done:
                        jobs.append((level, seed, name, cfg, speed))
    total = len(jobs)
    if verbose:
        print(f"{len(done)} episodes already in {os.path.basename(csv_path)}; running {total} more")
    if not total:
        return
    new_file = not os.path.exists(csv_path)
    workers = workers or max(1, (os.cpu_count() or 1))
    t0 = time.time()
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        finished = 0

        def report(row):
            nonlocal finished
            writer.writerow(row)
            f.flush()
            finished += 1
            if verbose and (finished % max(1, total // 20) == 0 or finished == total):
                rate = finished / max(time.time() - t0, 1e-9)
                eta = (total - finished) / max(rate, 1e-9)
                print(f"  {finished}/{total} episodes  ({rate:.2f}/s, ETA {eta/60:.1f} min)")

        # run in parallel on all cpu cores
        if workers == 1:
            for job in jobs:
                report(_job(job))
        else:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_job, job) for job in jobs]
                for fut in as_completed(futures):
                    report(fut.result())


def summarise(df, by=("agent",)):
    # averages per agent (or per agent + level) for the tables
    import pandas as pd
    g = df.groupby(list(by))
    out = pd.DataFrame({
        "episodes": g.size(),
        "success_rate": 100.0 * g["won"].mean(),
        "death_rate": 100.0 * g["died"].mean(),
        "timeout_rate": 100.0 * g["timeout"].mean(),
        "avg_coin_pct": g["coin_pct"].mean(),
        "completion_time_mean": g["completion_time"].mean(),
        "completion_time_median": g["completion_time"].median(),
        "episode_time_mean": g["seconds"].mean(),
        "remaining_life_mean": g["remaining_life"].mean(),
        "near_miss_pct_mean": g["near_miss_pct"].mean(),
        "racr_mean": g["racr"].mean(),
        "path_length_mean": g["path_length"].mean(),
        "plan_ms_mean": g["mean_plan_ms"].mean(),
    })
    return out.reset_index()


def proposed_code_tag():
    # changes whenever proposed.py changes
    with open(_proposed.__file__, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def reset_if_changed(csv_path, tag):
    # if the csv was made with an older version of our agent, move it to *_old_<tag>.csv
    # so the sweep runs again instead of reusing old rows
    tag_file = csv_path + ".tag"
    old = open(tag_file).read().strip() if os.path.exists(tag_file) else None
    if os.path.exists(csv_path) and old != tag:
        backup = csv_path.replace(".csv", f"_old_{old or 'v1'}.csv")
        shutil.move(csv_path, backup)
        print("agent code changed - old results moved to", os.path.basename(backup))
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(tag_file, "w") as f:
        f.write(tag)
