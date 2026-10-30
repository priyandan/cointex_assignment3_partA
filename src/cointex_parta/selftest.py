"""
Quick checks we run before the experiments (notebook 00).
Run with: python -m cointex_parta.selftest
"""

import math
import random

import numpy as np

from . import sim
from .agents import greedy
from .agents.proposed import _fire_positions, nn_two_opt_tour, tour_length
from .levels import LEVEL_TABLE
from .runner import play_episode


def check_level_table():
    assert len(LEVEL_TABLE) == 24
    for n, c in LEVEL_TABLE.items():
        assert c["num_coins"] > 0 and c["num_collisions_level"] > 0, n


def check_deterministic():
    a = play_episode(18, 3, "proposed")
    b = play_episode(18, 3, "proposed")
    for k in ("won", "seconds", "remaining_life", "coins_collected"):
        assert a[k] == b[k], (k, a[k], b[k])


def check_paired_worlds():
    # same seed should give the same coins and monster moves
    e1, e2 = sim.CoinTexSim(10, 7), sim.CoinTexSim(10, 7)
    assert all(np.allclose(p, q) for p, q in zip(e1.coins, e2.coins))
    e1.command((0.9, 0.9))
    for _ in range(300):
        e1.step_frame()
        e2.step_frame()
    for m1, m2 in zip(e1.monsters, e2.monsters):
        assert np.allclose(m1["pos"], m2["pos"])


def check_fire_prediction():
    # our fire prediction should match the simulator
    worst = 0.0
    for level in (14, 18, 19, 20):
        env = sim.CoinTexSim(level, 0)
        env.run_frames(random.Random(level).randint(30, 400))
        obs = env.observe()
        future = []
        for _ in range(120):                       # 2 s ahead
            env.step_frame()
            future.append([f["pos"].copy() for f in env.fires])
        taus = np.arange(1, 121) * sim.DT
        for j, f in enumerate(obs.fires):
            pred = _fire_positions(f, taus)
            true = np.array([fr[j] for fr in future])
            worst = max(worst, float(np.abs(pred - true).max()))
    assert worst < 1e-6, worst
    return f"max error {worst:.2e}"


def check_tour():
    rng = np.random.default_rng(0)
    for _ in range(20):
        coins = [tuple(p) for p in rng.random((15, 2))]
        start = (0.1, 0.1)
        nn = nn_two_opt_tour(start, coins, two_opt=False)
        opt = nn_two_opt_tour(start, coins, two_opt=True)
        assert sorted(opt) == list(range(15))
        assert tour_length(start, coins, opt) <= tour_length(start, coins, nn) + 1e-9


def check_greedy_verbatim():
    # 2 coins, no hazards: route should visit both coins
    tsp = greedy.create_matrix([0.1, 0.1], [[0.5, 0.5], [0.2, 0.2]], [], [])
    route = greedy.findMinRoute(tsp)
    assert sorted(route[:-1]) == [2, 3], route
    # check_coin bug: coins near the monster still survive because of the pop
    coins = [[0.1 * i, 0.5] for i in range(6)]
    kept = greedy.check_coin([c[:] for c in coins], [[0.25, 0.5]], [])
    assert len(kept) > 0


def run_all():
    ok = True
    for fn in (check_level_table, check_deterministic, check_paired_worlds,
               check_fire_prediction, check_tour, check_greedy_verbatim):
        try:
            note = fn()
            print(f"PASS  {fn.__name__}" + (f"  ({note})" if note else ""))
        except Exception as exc:
            ok = False
            print(f"FAIL  {fn.__name__}: {exc!r}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if run_all() else 1)
