"""
Settings for all 24 levels.

- num_coins and num_collisions_level: from the LevelN classes in main_work_greedy.py
- monster speeds and fire paths: from the <LevelN> parts of cointex.kv

Note: level 20 has 10 fires in the kv file but num_fires = 8, and level 22 has
4 monsters but num_monsters = 2, so only the first ones move in the game.
We do the same here.

parse_level_table() reads the table back from the game files so we can check it
(notebook 00).
"""

import re

NUM_LEVELS = 24

# monsters: list of (anim_duration_low, anim_duration_high)
# fires:    list of ((start_x, start_y), (end_x, end_y), leg_duration) in pos_hint units
LEVEL_TABLE = {
    1: dict(num_coins=5, num_collisions_level=20,
         monsters=[(3.5, 4.5)],
         fires=[]),
    2: dict(num_coins=8, num_collisions_level=30,
         monsters=[(2.5, 3.5)],
         fires=[]),
    3: dict(num_coins=12, num_collisions_level=30,
         monsters=[(1.0, 1.5)],
         fires=[]),
    4: dict(num_coins=10, num_collisions_level=20,
         monsters=[(2.5, 3.5)],
         fires=[((1.5, 0.5), (-0.5, 0.5), 2.5)]),
    5: dict(num_coins=15, num_collisions_level=20,
         monsters=[(1.0, 1.5)],
         fires=[((1.5, 0.7), (-0.5, 0.7), 3.0), ((1.5, 0.3), (-0.5, 0.3), 2.0)]),
    6: dict(num_coins=12, num_collisions_level=20,
         monsters=[(2.5, 3.0)],
         fires=[((1.5, 0.8), (-0.5, 0.8), 2.5), ((1.5, 0.2), (-0.5, 0.2), 2.0), ((0.5, 1.5), (0.5, -0.5), 3.5)]),
    7: dict(num_coins=10, num_collisions_level=25,
         monsters=[(1.0, 1.5), (1.5, 2.5), (1.5, 2.5)],
         fires=[]),
    8: dict(num_coins=15, num_collisions_level=25,
         monsters=[(1.5, 2.5), (1.0, 1.5)],
         fires=[]),
    9: dict(num_coins=12, num_collisions_level=25,
         monsters=[(2.5, 3.5), (1.2, 1.7)],
         fires=[]),
    10: dict(num_coins=14, num_collisions_level=30,
         monsters=[(1.5, 2.5), (0.8, 1.2), (1.0, 1.5)],
         fires=[]),
    11: dict(num_coins=15, num_collisions_level=30,
         monsters=[(2.5, 3.5), (2.0, 2.5)],
         fires=[((1.5, 0.5), (-0.5, 0.5), 3.5)]),
    12: dict(num_coins=12, num_collisions_level=30,
         monsters=[(2.5, 3.5), (1.5, 2.0)],
         fires=[((1.5, 0.5), (-0.5, 0.5), 2.5)]),
    13: dict(num_coins=10, num_collisions_level=20,
         monsters=[(2.5, 3.5), (2.5, 3.0)],
         fires=[((1.5, 0.5), (-0.5, 0.5), 2.5), ((0.5, 1.5), (0.5, -0.5), 3.5)]),
    14: dict(num_coins=15, num_collisions_level=30,
         monsters=[],
         fires=[((1.5, 0.2), (-0.5, 0.2), 2.5), ((1.5, 0.8), (-0.5, 0.8), 3.5), ((-1.5, 0.5), (-0.5, 0.5), 3.5), ((0.8, 1.5), (0.8, -0.5), 2.5), ((0.2, 1.5), (0.2, -0.5), 3.5), ((0.5, 1.5), (0.5, -0.5), 2.5)]),
    15: dict(num_coins=16, num_collisions_level=30,
         monsters=[(3.0, 3.5), (3.0, 3.5)],
         fires=[((1.2, 0.2), (-0.5, 0.2), 2.5), ((1.5, 0.7), (-0.5, 0.7), 3.5), ((0.5, 1.5), (0.5, -0.5), 2.5)]),
    16: dict(num_coins=15, num_collisions_level=35,
         monsters=[(2.0, 3.5), (3.0, 3.5), (1.0, 1.5)],
         fires=[((1.5, 0.2), (-0.5, 0.2), 2.5), ((1.5, 0.7), (-0.5, 0.7), 1.5)]),
    17: dict(num_coins=10, num_collisions_level=30,
         monsters=[],
         fires=[((1.0, 0.3), (0.0, 0.3), 2.5), ((1.0, 0.8), (0.0, 0.8), 2.0), ((0.8, 1.0), (0.8, 0.0), 3.5), ((0.3, 0.0), (0.3, 1.0), 3.0)]),
    18: dict(num_coins=15, num_collisions_level=30,
         monsters=[(1.0, 1.6), (1.0, 2.0), (1.0, 1.2)],
         fires=[((0.8, 0.3), (0.2, 0.3), 3.2), ((0.3, 0.8), (0.7, 0.8), 2.3), ((0.8, 0.3), (0.8, 0.7), 3.2), ((0.3, 0.8), (0.3, 0.2), 2.5)]),
    19: dict(num_coins=12, num_collisions_level=30,
         monsters=[],
         fires=[((0.8, 0.3), (0.2, 0.3), 2.2), ((0.3, 0.8), (0.7, 0.8), 3.0), ((-1.5, 0.5), (1.5, 0.5), 2.5), ((0.8, 0.3), (0.8, 0.7), 3.2), ((0.3, 0.8), (0.3, 0.2), 2.3), ((0.5, -1.5), (0.5, 1.5), 2.4)]),
    20: dict(num_coins=15, num_collisions_level=30,
         monsters=[],
         fires=[((0.9, 0.1), (0.1, 0.1), 2.5), ((0.0, 0.3), (1.0, 0.3), 2.6), ((0.1, 0.5), (0.9, 0.5), 2.5), ((0.1, 0.9), (0.9, 0.9), 3.3), ((0.2, 0.1), (0.2, 0.9), 2.5), ((0.5, 0.9), (0.5, 0.1), 3.3), ((0.7, -1.5), (0.7, 1.5), 2.6), ((0.9, 0.1), (0.9, 0.9), 3.3)]),
    21: dict(num_coins=18, num_collisions_level=30,
         monsters=[(1.0, 1.3), (1.0, 1.5)],
         fires=[((0.8, 0.3), (0.2, 0.3), 1.8), ((0.3, 0.8), (0.7, 0.8), 2.5), ((-1.5, 0.5), (1.5, 0.5), 3.0), ((0.1, 0.3), (0.9, 0.3), 2.5)]),
    22: dict(num_coins=20, num_collisions_level=30,
         monsters=[(1.0, 1.8), (1.0, 2.0)],
         fires=[((0.8, 0.3), (0.2, 0.3), 2.9), ((0.3, 0.8), (0.7, 0.8), 2.5), ((-1.5, 0.5), (1.5, 0.5), 2.3), ((0.1, 0.3), (0.9, 0.3), 2.8)]),
    23: dict(num_coins=25, num_collisions_level=30,
         monsters=[(1.5, 2.0), (1.5, 2.5)],
         fires=[((-1.5, 0.3), (1.0, 0.3), 2.8), ((1.5, 0.8), (-0.5, 0.8), 2.0)]),
    24: dict(num_coins=20, num_collisions_level=30,
         monsters=[(1.5, 1.7), (1.8, 2.5), (1.5, 2.0)],
         fires=[((0.8, 0.3), (0.2, 0.3), 2.8), ((0.3, 0.8), (0.7, 0.8), 2.5)]),
}


def level_summary(level):
    cfg = LEVEL_TABLE[level]
    return {"level": level, "coins": cfg["num_coins"],
            "monsters": len(cfg["monsters"]), "fires": len(cfg["fires"]),
            "life_frames": cfg["num_collisions_level"]}


def parse_level_table(kv_text, game_py_text):
    # read the level settings from cointex.kv and the game .py file
    levels = {}
    blocks = re.split(r"\n<Level(\d+)>:", kv_text)
    for i in range(1, len(blocks), 2):
        n = int(blocks[i])
        body = blocks[i + 1].split("\n<")[0]
        mons = [(int(k), float(a), float(b)) for k, a, b in re.findall(
            r"id:\s*monster(\d+)_image_lvl\d+\s*\n\s*monst_anim_duration_low:\s*([\d.]+)"
            r"\s*\n\s*monst_anim_duration_high:\s*([\d.]+)", body)]
        fires = [(int(k), (float(sx), float(sy)), (float(ex), float(ey)), float(d))
                 for k, sx, sy, ex, ey, d in re.findall(
            r"id:\s*fire(\d+)_lvl\d+\s*\n\s*fire_start_pos_hint:\s*\{'x':\s*([-\d.]+),\s*'y':\s*([-\d.]+)\}"
            r"\s*\n\s*fire_end_pos_hint:\s*\{'x':\s*([-\d.]+),\s*'y':\s*([-\d.]+)\}"
            r"\s*\n\s*fire_anim_duration:\s*([\d.]+)", body)]
        levels[n] = {"monsters": mons, "fires": fires}

    for m in re.finditer(r"class Level(\d+)\(.*?\):(.*?)(?=\nclass |\napp = )", game_py_text, re.S):
        n, body = int(m.group(1)), m.group(2)

        def grab(key):
            return float(re.search(key + r"\s*=\s*([\d.]+)", body).group(1))
        levels[n]["num_coins"] = int(grab("num_coins"))
        levels[n]["num_collisions_level"] = int(grab("num_collisions_level"))
        n_mon, n_fire = int(grab("num_monsters")), int(grab("num_fires"))
        levels[n]["monsters"] = [x[1:] for x in sorted(levels[n]["monsters"]) if x[0] <= n_mon]
        levels[n]["fires"] = [x[1:] for x in sorted(levels[n]["fires"]) if x[0] <= n_fire]
    return levels


def diff_against(parsed):
    # list of differences between LEVEL_TABLE and the parsed table (empty = same)
    problems = []
    for n in range(1, NUM_LEVELS + 1):
        a, b = LEVEL_TABLE[n], parsed.get(n)
        if b is None:
            problems.append(f"level {n} missing from parsed table")
            continue
        for key in ("num_coins", "num_collisions_level", "monsters", "fires"):
            if a[key] != b[key]:
                problems.append(f"level {n} {key}: embedded={a[key]} parsed={b[key]}")
    return problems


def verify_kv(kv_text):
    # check the monster/fire settings against cointex.kv only.
    # we can't use the repo's main.py for the coin counts because it is different
    # from main_work_greedy.py (levels 1, 17, 19, 20 have other coin counts)
    stub = "\n".join(
        f"class Level{n}(Screen):\n    num_coins = {c['num_coins']}\n"
        f"    num_collisions_level = {c['num_collisions_level']}\n"
        f"    num_monsters = {len(c['monsters'])}\n    num_fires = {len(c['fires'])}\n"
        for n, c in LEVEL_TABLE.items()) + "\napp = None\n"
    return diff_against(parse_level_table(kv_text, stub))
