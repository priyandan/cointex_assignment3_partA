# CoinTex Part A - results summary
Generated 2026-10-21 19:01  |  env: {'python': '3.13.15', 'numpy': '2.1.3', 'pygad': '3.3.1', 'matplotlib': '3.10.0', 'cpus': 12, 'cointex_parta': '1.0.0'}
Config: {"levels": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], "n_seeds": 50, "time_limit_s": 60.0, "stress_speeds": [1.0, 1.25, 1.5, 2.0], "stress_seeds": 20, "hard_levels": [7, 10, 11, 15, 16, 18, 21, 22, 23, 24], "sensitivity_seeds": 20}

## Table 1 - overall
|                        |   Original greedy |   GA (Task 2) |   Proposed (RH-STA*) |
|:-----------------------|------------------:|--------------:|---------------------:|
| episodes               |           1200    |       1200    |              1200    |
| success_rate           |             80.17 |        100    |               100    |
| levels_always_won      |              4    |         24    |                24    |
| levels_majority_won    |             20    |         24    |                24    |
| death_rate             |             19.83 |          0    |                 0    |
| timeout_rate           |              0    |          0    |                 0    |
| completion_time_mean   |              5.23 |          6.99 |                 4.3  |
| completion_time_median |              5.02 |          6.22 |                 4.22 |
| remaining_life_mean    |             58.51 |         93.28 |                99.52 |
| racr_mean              |              1.49 |          2.06 |                 3.18 |
| near_miss_pct_mean     |              7.62 |          1.62 |                 3.2  |
| path_length_mean       |              3.27 |          4.98 |                 3.4  |
| plan_ms_mean           |              0.03 |         16.26 |                 5.89 |

## Table 2 - per level
|   level |   success_rate|greedy |   success_rate|ga_task2 |   success_rate|proposed |   completion_time_mean|greedy |   completion_time_mean|ga_task2 |   completion_time_mean|proposed |   remaining_life_mean|greedy |   remaining_life_mean|ga_task2 |   remaining_life_mean|proposed |   racr_mean|greedy |   racr_mean|ga_task2 |   racr_mean|proposed |
|--------:|----------------------:|------------------------:|------------------------:|------------------------------:|--------------------------------:|--------------------------------:|-----------------------------:|-------------------------------:|-------------------------------:|-------------------:|---------------------:|---------------------:|
|       1 |                   100 |                     100 |                     100 |                          2.09 |                            3.42 |                            1.94 |                        96.9  |                          99.6  |                         100    |               2.49 |                 1.78 |                 2.65 |
|       2 |                   100 |                     100 |                     100 |                          3.31 |                            3.95 |                            2.77 |                        95.2  |                          99.33 |                         100    |               2.39 |                 2.24 |                 2.93 |
|       3 |                    98 |                     100 |                     100 |                          4.57 |                            4.9  |                            3.74 |                        84.67 |                          97.67 |                          99.2  |               2.23 |                 2.47 |                 3.22 |
|       4 |                    94 |                     100 |                     100 |                          4.11 |                            4.78 |                            3.32 |                        88.9  |                          97.8  |                         100    |               2.21 |                 2.27 |                 3.05 |
|       5 |                    90 |                     100 |                     100 |                          5.8  |                            5.97 |                            4.42 |                        69.3  |                          94.8  |                          98.2  |               1.8  |                 2.56 |                 3.37 |
|       6 |                    92 |                     100 |                     100 |                          4.63 |                            5.49 |                            3.72 |                        73.1  |                          96.1  |                          99.9  |               1.91 |                 2.27 |                 3.26 |
|       7 |                    72 |                     100 |                     100 |                          4.08 |                            6.64 |                            3.53 |                        49.84 |                          92    |                          99.44 |               1.23 |                 1.57 |                 2.88 |
|       8 |                    92 |                     100 |                     100 |                          5.8  |                            6.19 |                            4.57 |                        60.32 |                          95.28 |                          99.2  |               1.56 |                 2.51 |                 3.29 |
|       9 |                    90 |                     100 |                     100 |                          4.7  |                            5.82 |                            3.84 |                        64    |                          94.72 |                         100    |               1.65 |                 2.14 |                 3.16 |
|      10 |                    80 |                     100 |                     100 |                          5.4  |                            6.5  |                            4.51 |                        42.2  |                          91.67 |                          98.53 |               1.12 |                 2.09 |                 3.09 |
|      11 |                    80 |                     100 |                     100 |                          6.12 |                            7.26 |                            4.55 |                        56.4  |                          95.27 |                         100    |               1.44 |                 2.15 |                 3.34 |
|      12 |                    94 |                     100 |                     100 |                          5.04 |                            6.11 |                            3.85 |                        68.13 |                          97.13 |                          99.73 |               1.71 |                 2.1  |                 3.15 |
|      13 |                    92 |                     100 |                     100 |                          4.23 |                            5.56 |                            3.54 |                        76.7  |                          98.3  |                         100    |               1.86 |                 2    |                 2.9  |
|      14 |                   100 |                     100 |                     100 |                          5.8  |                            6.13 |                            4.28 |                        82.13 |                          98.8  |                         100    |               2.13 |                 2.53 |                 3.52 |
|      15 |                    82 |                     100 |                     100 |                          6.7  |                            7.7  |                            4.9  |                        54.4  |                          93    |                         100    |               1.37 |                 2.14 |                 3.3  |
|      16 |                    72 |                     100 |                     100 |                          6.51 |                            7.19 |                            4.88 |                        36.8  |                          89.54 |                          99.83 |               0.88 |                 2.06 |                 3.12 |
|      17 |                    98 |                     100 |                     100 |                          3.8  |                            5.63 |                            3.26 |                        83.87 |                          97.93 |                         100    |               2.21 |                 2    |                 3.09 |
|      18 |                    20 |                     100 |                     100 |                          6.93 |                           12.22 |                            5.17 |                         6.47 |                          79.93 |                          98.2  |               0.14 |                 1.11 |                 2.91 |
|      19 |                   100 |                     100 |                     100 |                          4.6  |                            9.84 |                            3.89 |                        76.53 |                          93.27 |                         100    |               2    |                 1.36 |                 3.1  |
|      20 |                    80 |                     100 |                     100 |                          5.8  |                            8.21 |                            4.53 |                        46.93 |                          92.67 |                         100    |               1.21 |                 1.83 |                 3.34 |
|      21 |                    48 |                     100 |                     100 |                          7.29 |                            9.33 |                            5.38 |                        23.53 |                          88    |                          99.2  |               0.6  |                 1.92 |                 3.36 |
|      22 |                    38 |                     100 |                     100 |                          7.74 |                            9.85 |                            5.88 |                        18.2  |                          83.93 |                          97.4  |               0.47 |                 1.82 |                 3.35 |
|      23 |                    68 |                     100 |                     100 |                          9.89 |                            8.4  |                            6.65 |                        30.87 |                          89.87 |                          99.93 |               0.79 |                 2.78 |                 3.8  |
|      24 |                    44 |                     100 |                     100 |                          8.01 |                           10.79 |                            6.2  |                        18.93 |                          82.07 |                          99.6  |               0.47 |                 1.72 |                 3.26 |

## Table 3 - paired tests
|    | comparison           |   proposed_only_wins |   other_only_wins |   mcnemar_p |   paired_episodes_both_won |   median_time_diff_s |   mean_time_diff_s |   proposed_faster_pct_of_pairs |   wilcoxon_p |
|---:|:---------------------|---------------------:|------------------:|------------:|---------------------------:|---------------------:|-------------------:|-------------------------------:|-------------:|
|  0 | proposed vs greedy   |                  238 |                 0 | 4.52784e-72 |                        962 |               -0.925 |             -1.137 |                           91.2 | 9.21422e-142 |
|  1 | proposed vs ga_task2 |                    0 |                 0 | 1           |                       1200 |               -1.734 |             -2.691 |                           93.2 | 1.26142e-183 |

## Completion-time 95% CI
|    | agent    |   mean_time |   ci95_low |   ci95_high |
|---:|:---------|------------:|-----------:|------------:|
|  0 | greedy   |       5.228 |      5.122 |       5.345 |
|  1 | ga_task2 |       6.995 |      6.818 |       7.184 |
|  2 | proposed |       4.304 |      4.239 |       4.367 |

## Stress test
|    | agent    |   hazard_speed |   success |   time |   life |   racr |
|---:|:---------|---------------:|----------:|-------:|-------:|-------:|
|  0 | ga_task2 |           1    |    100    |   7.14 |  93.12 |   2.03 |
|  1 | ga_task2 |           1.25 |     99.79 |   6.79 |  92.23 |   2.07 |
|  2 | ga_task2 |           1.5  |    100    |   6.54 |  91.18 |   2.08 |
|  3 | ga_task2 |           2    |     99.38 |   6.39 |  87.67 |   2    |
|  4 | greedy   |           1    |     79.58 |   5.17 |  59.23 |   1.53 |
|  5 | greedy   |           1.25 |     80.42 |   5.19 |  57    |   1.47 |
|  6 | greedy   |           1.5  |     80.42 |   5.09 |  55.4  |   1.43 |
|  7 | greedy   |           2    |     78.54 |   5.01 |  50.77 |   1.33 |
|  8 | proposed |           1    |    100    |   4.32 |  99.58 |   3.19 |
|  9 | proposed |           1.25 |    100    |   4.27 |  99.37 |   3.2  |
| 10 | proposed |           1.5  |    100    |   4.35 |  98.69 |   3.14 |
| 11 | proposed |           2    |    100    |   4.36 |  97.45 |   3.09 |

## Ablation
|    | agent                  |   episodes |   success_rate |   death_rate |   timeout_rate |   avg_coin_pct |   completion_time_mean |   completion_time_median |   episode_time_mean |   remaining_life_mean |   near_miss_pct_mean |   racr_mean |   path_length_mean |   plan_ms_mean |
|---:|:-----------------------|-----------:|---------------:|-------------:|---------------:|---------------:|-----------------------:|-------------------------:|--------------------:|----------------------:|---------------------:|------------:|-------------------:|---------------:|
|  0 | proposed               |       1200 |         100    |         0    |              0 |         100    |                   4.3  |                     4.22 |                4.3  |                 99.52 |                 3.2  |        3.18 |               3.4  |           5.89 |
|  1 | proposed_no_hazard     |       1200 |          92.08 |         7.92 |              0 |          97.79 |                   3.88 |                     3.93 |                3.84 |                 67.71 |                 7.36 |        2.31 |               2.89 |           1.84 |
|  2 | proposed_static_hazard |       1200 |          99.75 |         0.25 |              0 |          99.94 |                   4.41 |                     4.23 |                4.41 |                 92.67 |                 4.9  |        2.91 |               3.54 |           6.87 |
|  3 | proposed_no_tour       |       1200 |         100    |         0    |              0 |         100    |                   4.43 |                     4.23 |                4.43 |                 99.63 |                 3.5  |        3.1  |               3.49 |           6.53 |

## Sensitivity (hard levels)
|    | param          |   value |   success |   time |   life |
|---:|:---------------|--------:|----------:|-------:|-------:|
|  0 | horizon        |    2    |       100 |   5.22 |  99.38 |
|  1 | horizon        |    4    |       100 |   5.22 |  99.2  |
|  2 | horizon        |    8    |       100 |   5.22 |  99.2  |
|  3 | horizon        |   12    |       100 |   5.22 |  99.2  |
|  4 | max_expansions |   25    |       100 |   5.35 |  99.4  |
|  5 | max_expansions |   50    |       100 |   5.27 |  99.31 |
|  6 | max_expansions |  100    |       100 |   5.22 |  99.2  |
|  7 | max_expansions |  250    |       100 |   5.14 |  99.22 |
|  8 | max_step       |    0.15 |       100 |   7.81 |  98.76 |
|  9 | max_step       |    0.2  |       100 |   6.37 |  99.07 |
| 10 | max_step       |    0.25 |       100 |   5.6  |  99.48 |
| 11 | max_step       |    0.3  |       100 |   5.22 |  99.2  |
| 12 | max_step       |    0.4  |       100 |   4.72 |  99.4  |
| 13 | max_step       |    0.5  |       100 |   4.63 |  99.4  |
| 14 | monster_sigma  |    0    |       100 |   5.11 |  98.99 |
| 15 | monster_sigma  |    0.05 |       100 |   5.17 |  99.22 |
| 16 | monster_sigma  |    0.1  |       100 |   5.22 |  99.2  |
| 17 | monster_sigma  |    0.2  |       100 |   5.27 |  99.31 |
| 18 | risk_weight    |    0    |       100 |   5.08 |  97.84 |
| 19 | risk_weight    |    1    |       100 |   5.04 |  99.15 |
| 20 | risk_weight    |    4    |       100 |   5.22 |  99.2  |
| 21 | risk_weight    |    8    |       100 |   5.38 |  99    |
| 22 | risk_weight    |   16    |       100 |   5.63 |  99.65 |

## Greedy failure causes by level
|    |   level |   fire |   monster |
|---:|--------:|-------:|----------:|
|  0 |       3 |      0 |         1 |
|  1 |       4 |      0 |         3 |
|  2 |       5 |      0 |         5 |
|  3 |       6 |      0 |         4 |
|  4 |       7 |      0 |        14 |
|  5 |       8 |      0 |         4 |
|  6 |       9 |      0 |         5 |
|  7 |      10 |      0 |        10 |
|  8 |      11 |      0 |        10 |
|  9 |      12 |      0 |         3 |
| 10 |      13 |      0 |         4 |
| 11 |      15 |      0 |         9 |
| 12 |      16 |      0 |        14 |
| 13 |      17 |      1 |         0 |
| 14 |      18 |      9 |        31 |
| 15 |      20 |     10 |         0 |
| 16 |      21 |      5 |        21 |
| 17 |      22 |     14 |        17 |
| 18 |      23 |      0 |        16 |
| 19 |      24 |      6 |        22 |

## Headlines
```json
{
 "greedy": {
  "agent": "greedy",
  "episodes": 1200,
  "success_rate_pct": 80.17,
  "death_rate_pct": 19.83,
  "timeout_rate_pct": 0.0,
  "levels_always_won": 4,
  "completion_time_mean_s": 5.23,
  "remaining_life_mean_pct": 58.51,
  "worst_levels": [
   {
    "level": 18,
    "success_rate": 20.0
   },
   {
    "level": 22,
    "success_rate": 38.0
   },
   {
    "level": 24,
    "success_rate": 44.0
   },
   {
    "level": 21,
    "success_rate": 48.0
   },
   {
    "level": 23,
    "success_rate": 68.0
   }
  ]
 },
 "proposed": {
  "agent": "proposed",
  "config": {
   "name": "proposed",
   "max_step": 0.3,
   "step_fracs": [
    1.0,
    0.5,
    0.25
   ],
   "n_dirs": 16,
   "horizon": 8,
   "max_expansions": 100,
   "heuristic_weight": 1.2,
   "samples": 8,
   "grid": 0.02,
   "use_hazards": true,
   "predict_motion": true,
   "monster_margin": 0.05,
   "fire_margin": 0.035,
   "monster_sigma": 0.1,
   "contact_buffer": 0.01,
   "hard_steps": 3,
   "late_contact_penalty": 3.0,
   "risk_weight": 4.0,
   "dist_weight": 0.2,
   "use_tour": true,
   "two_opt": true,
   "alt_goals": 3,
   "defer_seconds": 1.0,
   "stuck_seconds": 4.0,
   "stagnation_relax": 0.25
  },
  "episodes": 1200,
  "success_rate_pct": 100.0,
  "levels_always_won": 24,
  "completion_time_mean_s": 4.3,
  "remaining_life_mean_pct": 99.52,
  "plan_ms_mean": 5.89,
  "plan_ms_max": 191.55,
  "ablation": [
   {
    "agent": "proposed",
    "success_rate": 100.0,
    "completion_time_mean": 4.3,
    "remaining_life_mean": 99.52
   },
   {
    "agent": "proposed_no_hazard",
    "success_rate": 92.08,
    "completion_time_mean": 3.88,
    "remaining_life_mean": 67.71
   },
   {
    "agent": "proposed_static_hazard",
    "success_rate": 99.75,
    "completion_time_mean": 4.41,
    "remaining_life_mean": 92.67
   },
   {
    "agent": "proposed_no_tour",
    "success_rate": 100.0,
    "completion_time_mean": 4.43,
    "remaining_life_mean": 99.63
   }
  ]
 },
 "ga_task2": {
  "agent": "ga_task2",
  "episodes": 1200,
  "success_rate_pct": 100.0,
  "levels_always_won": 24,
  "completion_time_mean_s": 6.99,
  "remaining_life_mean_pct": 93.28,
  "plan_ms_mean": 16.26
 }
}
```