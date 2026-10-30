"""
Our GA agent from Lab Task 2 (Group 01), not changed.

Same fitness (evaluate_target), same move limit (feasible_target), same GA
settings as our submitted main_updated.py. Every 0.25 s pygad evolves a
target (x, y) for 8 generations and keeps the population for the next move.
The only difference is the input: the game made a WorldSnapshot from the
Kivy widgets, here we make it from the simulator.
"""

import collections
import math

import pygad

COIN_CLUSTER_K = 3
COIN_REWARD_SCALE = 1.0
COIN_DIST_OFFSET = 0.1
TRAVEL_PENALTY = 0.8

MONSTER_PENALTY = 15.0
MONSTER_DANGER_RADIUS = 0.40
FIRE_PENALTY = 15.0
FIRE_DANGER_RADIUS = 0.35

MOVE_SECONDS = 0.25
MAX_STEP = 0.25
PATH_SAMPLES = 8

STAGNATION_GAIN = 0.6
STAGNATION_CAP = 6.0
OUT_OF_BOUNDS_PENALTY = 5.0

POPULATION = 20
PLAN_GENERATIONS = 8
MUTATION_STEP = 0.2

WorldSnapshot = collections.namedtuple(
    "WorldSnapshot", "level token char coins monsters fires margin stagnation")


def _manhattan(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by)


def feasible_target(tx, ty, snapshot):
    half_w, half_h = snapshot.margin
    tx = min(max(tx, half_w), 1.0 - half_w)
    ty = min(max(ty, half_h), 1.0 - half_h)
    char_x, char_y = snapshot.char
    dx, dy = tx - char_x, ty - char_y
    length = math.hypot(dx, dy)
    if length > MAX_STEP:
        scale = MAX_STEP / length
        tx, ty = char_x + dx * scale, char_y + dy * scale
    return tx, ty


def _path_hazard_penalty(snapshot, tx, ty, hazards, penalty, radius):
    if not hazards:
        return 0.0
    char_x, char_y = snapshot.char
    total = 0.0
    for step in range(1, PATH_SAMPLES + 1):
        fraction = step / float(PATH_SAMPLES)
        px = char_x + (tx - char_x) * fraction
        py = char_y + (ty - char_y) * fraction
        moment = MOVE_SECONDS * fraction
        for hx, hy, vx, vy in hazards:
            distance = _manhattan(px, py, hx + vx * moment, hy + vy * moment)
            if distance < radius:
                total += penalty * (radius - distance) / radius
    return total / PATH_SAMPLES


def evaluate_target(tx, ty, snapshot):
    coins = snapshot.coins
    if not coins:
        return 0.0
    fx, fy = feasible_target(tx, ty, snapshot)
    distances = sorted(_manhattan(fx, fy, cx, cy) for cx, cy in coins)
    reward = 0.0
    for distance in distances[:COIN_CLUSTER_K]:
        reward += COIN_REWARD_SCALE / (distance + COIN_DIST_OFFSET)
    reward *= min(1.0 + STAGNATION_GAIN * snapshot.stagnation, STAGNATION_CAP)
    char_x, char_y = snapshot.char
    score = reward - TRAVEL_PENALTY * _manhattan(fx, fy, char_x, char_y)
    score -= _path_hazard_penalty(snapshot, fx, fy, snapshot.monsters,
                                  MONSTER_PENALTY, MONSTER_DANGER_RADIUS)
    score -= _path_hazard_penalty(snapshot, fx, fy, snapshot.fires,
                                  FIRE_PENALTY, FIRE_DANGER_RADIUS)
    half_w, half_h = snapshot.margin
    for value, low, high in ((tx, half_w, 1.0 - half_w), (ty, half_h, 1.0 - half_h)):
        if value < low:
            score -= OUT_OF_BOUNDS_PENALTY * (low - value)
        elif value > high:
            score -= OUT_OF_BOUNDS_PENALTY * (value - high)
    return score


def to_snapshot(obs):
    return WorldSnapshot(
        level=obs.level, token=obs.frame, char=obs.char, coins=obs.coins,
        monsters=obs.monsters,
        fires=tuple((f.x, f.y, f.vx, f.vy) for f in obs.fires),
        margin=(obs.margin, obs.margin), stagnation=obs.stagnation)


class GAAgent:
    # same as CollectCoinThread.plan() in Task 2

    name = "ga_task2"

    def __init__(self, seed=0):
        self.seed = int(seed)
        self.steps = 0
        self.population = None

    def act(self, obs):
        from ..sim import MOVE_FRAMES
        snapshot = to_snapshot(obs)
        if not snapshot.coins:
            return None, 1

        def fitness_func(ga_instance, solution, solution_idx):
            return evaluate_target(float(solution[0]), float(solution[1]), snapshot)

        # seed each step so runs can be repeated
        seed = (self.seed * 7919 + self.steps) % (2 ** 31 - 1)
        self.steps += 1
        kwargs = dict(num_generations=PLAN_GENERATIONS,
                      num_parents_mating=4,
                      fitness_func=fitness_func,
                      parent_selection_type="tournament",
                      K_tournament=3,
                      keep_elitism=2,
                      sol_per_pop=POPULATION,
                      num_genes=2,
                      gene_space={'low': 0.0, 'high': 1.0},
                      init_range_low=0.0,
                      init_range_high=1.0,
                      crossover_type="single_point",
                      mutation_type="random",
                      mutation_percent_genes=50,
                      random_mutation_min_val=-MUTATION_STEP,
                      random_mutation_max_val=MUTATION_STEP,
                      mutation_by_replacement=False,
                      random_seed=seed,
                      suppress_warnings=True,
                      save_solutions=False,
                      save_best_solutions=False)
        if self.population is not None:
            kwargs["initial_population"] = self.population
        ga_instance = pygad.GA(**kwargs)
        ga_instance.run()
        self.population = ga_instance.population
        best, _, _ = ga_instance.best_solution(ga_instance.last_generation_fitness)
        return feasible_target(float(best[0]), float(best[1]), snapshot), MOVE_FRAMES
