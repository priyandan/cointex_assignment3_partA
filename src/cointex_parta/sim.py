"""
Headless version of the CoinTex game so we can run lots of episodes without
Kivy (Kivy needs a window, so it won't run on Colab).

We copied the numbers from the game files:
- sprite sizes from cointex.kv (character/monster 0.15, fire 0.03, coin 0.05)
- collision checks from main_work_greedy.py (coin and fire use width/3,
  monster uses width/2), counted every frame at 60 fps
- the character always takes 0.25 s to walk to its target
- monsters walk to random points, fires sweep back and forth on fixed paths

Positions are sprite centres (the game uses pos_hint = bottom-left corner).
Same seed = same coins and same monster moves, so every agent gets the
exact same world.
"""

import collections
import random

import numpy as np

from .levels import LEVEL_TABLE

FPS = 60
DT = 1.0 / FPS
MOVE_SECONDS = 0.25          # char_anim_duration, same for all levels
MOVE_FRAMES = int(round(MOVE_SECONDS * FPS))

CHAR_SIZE = 0.15
MONSTER_SIZE = 0.15
FIRE_SIZE = 0.03
COIN_SIZE = 0.05

CHAR_HALF = CHAR_SIZE / 2.0
MONSTER_GAB = CHAR_SIZE / 2.0    # width/2 in monst_pos_hint
COIN_GAB = CHAR_SIZE / 3.0       # width/3 in char_pos_hint
FIRE_GAB = CHAR_SIZE / 3.0       # width/3 in fire_pos_hint

# coins can be right at the edge, so the character has to be allowed there too
EDGE_MARGIN = COIN_SIZE / 2.0

FIRE_PARK = (1.1, 1.1)       # where screen_on_pre_enter puts the fires
MONSTER_PARK = (0.8, 0.8)    # monster start position in the kv file

TIME_LIMIT_SECONDS = 60.0

# for our near-miss metric: close to a hazard but not touching it
NEAR_MISS_BAND = 0.05

FireState = collections.namedtuple(
    "FireState", "x y vx vy tx ty remaining ox oy leg_duration")
Observation = collections.namedtuple(
    "Observation",
    "level frame time char coins monsters fires margin stagnation life")


class CoinTexSim:
    """One level of the game."""

    def __init__(self, level_num, seed, time_limit=TIME_LIMIT_SECONDS, hazard_speed=1.0):
        # hazard_speed > 1 speeds up monsters and fires (only used for the stress test)
        cfg = LEVEL_TABLE[level_num]
        self.hazard_speed = float(hazard_speed)
        self.level_num = level_num
        self.seed = seed
        self.num_coins = cfg["num_coins"]
        self.num_collisions_level = cfg["num_collisions_level"]
        self.time_limit = time_limit
        self.rng = random.Random(seed)

        self.frames = 0
        self.collisions_hit = 0
        self.monster_hit_frames = 0
        self.fire_hit_frames = 0
        self.near_miss_frames = 0
        self.path_length = 0.0
        self.killed = False
        self.frames_since_coin = 0
        self.coin_times = []

        # character starts at pos_hint (0, 0)
        self.agent = np.array([CHAR_HALF, CHAR_HALF])
        self._anim = None
        self._build_layout(cfg)

    def _build_layout(self, cfg):
        # coins: one per vertical strip, same as screen_on_pre_enter
        self.coins = []
        section_width = 1.0 / self.num_coins
        for k in range(self.num_coins):
            x = self.rng.uniform(section_width * k, section_width * (k + 1) - COIN_SIZE)
            y = self.rng.uniform(0.0, 1.0 - COIN_SIZE)
            self.coins.append(np.array([x + COIN_SIZE / 2.0, y + COIN_SIZE / 2.0]))

        self.monsters = []
        for low, high in cfg["monsters"]:
            low, high = low / self.hazard_speed, high / self.hazard_speed
            start = np.array([MONSTER_PARK[0] + MONSTER_SIZE / 2.0,
                              MONSTER_PARK[1] + MONSTER_SIZE / 2.0])
            monster = {"pos": start, "prev": start.copy(), "low": low, "high": high}
            self._retarget_monster(monster)
            self.monsters.append(monster)

        half = FIRE_SIZE / 2.0
        self.fires = []
        for start, end, duration in cfg["fires"]:
            duration = duration / self.hazard_speed
            p0 = np.array([start[0] + half, start[1] + half])
            p1 = np.array([end[0] + half, end[1] + half])
            park = np.array([FIRE_PARK[0] + half, FIRE_PARK[1] + half])
            # first the fire moves from the park spot to its start point
            self.fires.append({"p0": p0, "p1": p1, "duration": duration,
                               "pos": park.copy(), "prev": park.copy(),
                               "leg_from": park.copy(), "leg_to": p0.copy(),
                               "next": p1.copy(), "elapsed": 0.0})

    def _retarget_monster(self, monster):
        # same as monst_animation_completed in the game
        pos_hint = (self.rng.uniform(0.0, 1 - MONSTER_SIZE / 4),
                    self.rng.uniform(0.0, 1 - MONSTER_SIZE / 4))
        monster["target"] = np.array([pos_hint[0] + MONSTER_SIZE / 2.0,
                                      pos_hint[1] + MONSTER_SIZE / 2.0])
        monster["duration"] = self.rng.uniform(monster["low"], monster["high"])
        monster["elapsed"] = 0.0
        monster["origin"] = monster["pos"].copy()

    def command(self, target):
        # start walking to target (cancels the current walk)
        if target is None:
            return
        self._anim = {"start": self.agent.copy(),
                      "target": np.array(target, dtype=float),
                      "elapsed": 0.0}

    def _advance_character(self):
        if self._anim is None:
            return
        self._anim["elapsed"] += DT
        fraction = min(1.0, self._anim["elapsed"] / MOVE_SECONDS)
        new = self._anim["start"] + (self._anim["target"] - self._anim["start"]) * fraction
        self.path_length += float(np.hypot(*(new - self.agent)))
        self.agent = new
        if fraction >= 1.0:
            self._anim = None

    def _advance_monsters(self):
        for monster in self.monsters:
            monster["prev"] = monster["pos"].copy()
            monster["elapsed"] += DT
            fraction = min(1.0, monster["elapsed"] / monster["duration"])
            monster["pos"] = monster["origin"] + (monster["target"] - monster["origin"]) * fraction
            if fraction >= 1.0 - 1e-9:
                self._retarget_monster(monster)

    def _advance_fires(self):
        for fire in self.fires:
            fire["prev"] = fire["pos"].copy()
            fire["elapsed"] += DT
            if fire["elapsed"] >= fire["duration"] - 1e-9:
                # end of a sweep, turn around. keep the leftover time so the
                # timing doesn't drift (we found this when testing the predictor)
                fire["elapsed"] = max(0.0, fire["elapsed"] - fire["duration"])
                fire["leg_from"], fire["leg_to"], fire["next"] = (
                    fire["leg_to"].copy(), fire["next"].copy(), fire["leg_to"].copy())
            fraction = min(1.0, fire["elapsed"] / fire["duration"])
            fire["pos"] = fire["leg_from"] + (fire["leg_to"] - fire["leg_from"]) * fraction

    def _collect_coins(self):
        before = len(self.coins)
        self.coins = [c for c in self.coins
                      if not (abs(self.agent[0] - c[0]) <= COIN_GAB
                              and abs(self.agent[1] - c[1]) <= COIN_GAB)]
        collected = before - len(self.coins)
        if collected:
            self.coin_times.extend([self.frames * DT] * collected)
            self.frames_since_coin = 0
        else:
            self.frames_since_coin += 1

    def _check_hazards(self):
        # one hit per frame of contact, like the game
        near = False
        for monster in self.monsters:
            d = np.abs(self.agent - monster["pos"])
            if d[0] <= MONSTER_GAB and d[1] <= MONSTER_GAB:
                self.collisions_hit += 1
                self.monster_hit_frames += 1
            elif max(d) <= MONSTER_GAB + NEAR_MISS_BAND:
                near = True
        for fire in self.fires:
            d = np.abs(self.agent - fire["pos"])
            if d[0] <= FIRE_GAB and d[1] <= FIRE_GAB:
                self.collisions_hit += 1
                self.fire_hit_frames += 1
            elif max(d) <= FIRE_GAB + NEAR_MISS_BAND:
                near = True
        if near:
            self.near_miss_frames += 1
        if self.collisions_hit >= self.num_collisions_level:
            self.killed = True

    def step_frame(self):
        self.frames += 1
        self._advance_character()
        self._advance_monsters()
        self._advance_fires()
        self._collect_coins()
        self._check_hazards()

    def run_frames(self, n):
        for _ in range(int(n)):
            if self.done:
                return
            self.step_frame()

    def observe(self):
        # what the agent can see. velocity = change since last frame, which is
        # something you could also measure in the real game
        monsters = tuple(
            (float(m["pos"][0]), float(m["pos"][1]),
             float((m["pos"][0] - m["prev"][0]) * FPS), float((m["pos"][1] - m["prev"][1]) * FPS))
            for m in self.monsters)
        fires = []
        for f in self.fires:
            remaining = max(f["duration"] - f["elapsed"], 0.0)
            fires.append(FireState(
                float(f["pos"][0]), float(f["pos"][1]),
                float((f["pos"][0] - f["prev"][0]) * FPS), float((f["pos"][1] - f["prev"][1]) * FPS),
                float(f["leg_to"][0]), float(f["leg_to"][1]), remaining,
                float(f["next"][0]), float(f["next"][1]), f["duration"]))
        return Observation(
            level=self.level_num, frame=self.frames, time=self.frames * DT,
            char=(float(self.agent[0]), float(self.agent[1])),
            coins=tuple((float(c[0]), float(c[1])) for c in self.coins),
            monsters=monsters, fires=tuple(fires),
            margin=EDGE_MARGIN, stagnation=self.frames_since_coin * DT,
            life=self.remaining_life_fraction())

    @property
    def seconds(self):
        return self.frames * DT

    @property
    def won(self):
        return len(self.coins) == 0

    @property
    def timed_out(self):
        return not self.won and not self.killed and self.seconds >= self.time_limit

    @property
    def done(self):
        return self.won or self.killed or self.seconds >= self.time_limit

    def remaining_life_fraction(self):
        return max(0.0, 1.0 - self.collisions_hit / self.num_collisions_level)
