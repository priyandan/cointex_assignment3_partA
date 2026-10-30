# COMP6009 Assignment Part A - CoinTex (Group 01)

Improving the greedy CoinTex agent (`main_work_greedy.py`) with a classical search algorithm, and
comparing it with the original greedy agent and our genetic algorithm from Lab Task 2.

Our agent is **RH-STA\*** (risk-aware receding-horizon space-time A\*):
- coins are visited in a nearest neighbour + 2-opt order, starting from the character's real position
- the path to the next coin is found with A\* over (x, y, time), checked against where the monsters and
  fires *will be* (fires are predicted exactly from `cointex.kv`, monsters from their velocity with a growing margin)
- only the first move is done, then we re-plan every 0.25 s

## Results

All three agents played the same 1200 worlds (24 levels x 50 seeds).

| | Original greedy | GA (Task 2) | **RH-STA\* (ours)** |
|---|---|---|---|
| Success rate | 80.2% | 100% | **100%** |
| Levels won in every seed | 4 / 24 | 24 / 24 | **24 / 24** |
| Mean time to collect all coins | 5.23 s | 6.99 s | **4.30 s** |
| Remaining life | 58.5% | 93.3% | **99.5%** |
| RACR (coins/s x life, our metric) | 1.49 | 2.06 | **3.18** |
| Near-miss time (HEI, our metric) | 7.6% | 1.6% | 3.2% |

- Ours won 238 worlds that greedy lost, and greedy never won a world ours lost (McNemar p < 0.001).
- Ours was faster than the GA in 93% of the worlds both won (Wilcoxon p < 0.001).
- Planning takes 4.8 ms per move on average (worst 44 ms), well inside the 250 ms per move.
- With monsters and fires 2x faster, ours still wins 100%, the GA 99.4% and greedy about 79%.

Full tables: [`results/results_summary.md`](results/results_summary.md). Figures for the report and slides:
[`report_assets/figures`](report_assets/figures).

## Repository layout

```
src/cointex_parta/
  levels.py          settings for all 24 levels (checked against cointex.kv)
  sim.py             headless CoinTex simulator using the game's sizes, collision rules and timings
  agents/greedy.py   original greedy agent (create_matrix / check_coin / findMinRoute copied from main_work_greedy.py)
  agents/ga_task2.py our GA from Lab Task 2 (unchanged)
  agents/proposed.py our RH-STA* agent
  runner.py          runs the experiments and saves the results
  plots.py           figures and gifs
  selftest.py        quick checks
notebooks/           Google Colab notebooks (00 setup, 01 greedy, 02 ours, 03 GA, 04 comparison)
results/             CSV results, tables and figures from our final run
report_assets/       final figures (incl. gifs) and tables used in the report and slides
```

## How to run

**Colab:** upload the notebooks, run `00_setup_and_code` first, then `01`, `02`, `03`, then `04`.
Everything is saved to `My Drive/COMP6009_Assignment-Part A/`.

**Locally:**
```bash
pip install -r requirements.txt
cd src
python -m cointex_parta.selftest
python -c "from cointex_parta import runner; print(runner.play_episode(23, 0, 'proposed'))"
```

## Notes

- Kivy can't run on Colab, so the experiments use our simulator. Fire paths and monster speeds were
  checked against `cointex.kv` for all 24 levels. Coin counts and life limits follow `main_work_greedy.py`
  from Blackboard (it differs from the CoinTex repo's `main.py` on levels 1, 17, 19 and 20).
- The same seed gives the same coins and monster moves for every agent, so the comparisons are paired.
- An episode fails if the life bar runs out or the coins are not all collected within 60 s.
- CoinTex game: https://github.com/ahmedfgad/CoinTex
