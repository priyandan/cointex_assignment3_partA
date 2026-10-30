"""
Play one level of the real CoinTex game (Kivy) with one of our agents.

The agents themselves are not changed. This file only connects them to the game:
every 0.25 s it reads the character, coins, monsters and fires from the Kivy
widgets, builds the same Observation the simulator gives (sim.Observation),
asks the agent for a move and calls app.start_char_animation with it.

  greedy    -> the supplied CollectCoinThread.run() is used exactly as given
  ga_task2  -> our Lab Task 2 GA (agents/ga_task2.py)
  proposed  -> RH-STA* (agents/proposed.py)

Needs the TutorialProject folder of the CoinTex repo with main_work_greedy.py
inside it (Part 1 of the assignment):

    python live_game/play_live.py --assets PATH/TO/TutorialProject --agent proposed --level 18 --seed 0 --headless

Prints the result as JSON (same fields as the Lab 2 real-game trials) and exits
0 if the level was won.
"""

import argparse
import json
import math
import os
import random
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", required=True, help="path to the game's TutorialProject folder")
    parser.add_argument("--agent", default="proposed", choices=["greedy", "ga_task2", "proposed"])
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--headless", action="store_true", help="no visible window")
    parser.add_argument("--game", help="path to main_work_greedy.py (default: inside --assets)")
    parser.add_argument("--json", help="also write the result to this file (absolute path)")
    return parser.parse_args()


def load_game(path):
    # main_work_greedy.py ends with app.run(), so run everything except that line
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    lines = source.rstrip().splitlines()
    if lines and lines[-1].strip() == "app.run()":
        lines = lines[:-1]
    game = {"__name__": "main_work_greedy", "__file__": path}
    exec(compile("\n".join(lines) + "\n", path, "exec"), game)
    return game


class LiveWorld:
    """Builds sim.Observation objects from the Kivy widgets of one level."""

    def __init__(self, app, level, sim):
        self.app = app
        self.level = level
        self.sim = sim
        self.t0 = time.monotonic()
        self.prev_monsters = None
        self.prev_time = None
        self.coins_left = None
        self.last_coin_time = self.t0
        self.frame = 0

    def screen(self):
        return self.app.root.screens[self.level]

    @staticmethod
    def centre(widget):
        return (widget.pos_hint["x"] + widget.size_hint[0] / 2.0,
                widget.pos_hint["y"] + widget.size_hint[1] / 2.0)

    def _fire_state(self, fire, now):
        # the game animates park -> start -> end -> start -> ... with fire_anim_duration per leg
        sim = self.sim
        d = float(fire.fire_anim_duration)
        half = (fire.size_hint[0] / 2.0, fire.size_hint[1] / 2.0)
        p0 = (fire.fire_start_pos_hint["x"] + half[0], fire.fire_start_pos_hint["y"] + half[1])
        p1 = (fire.fire_end_pos_hint["x"] + half[0], fire.fire_end_pos_hint["y"] + half[1])
        t = now - self.t0
        leg = int(t // d)
        remaining = d - (t - leg * d)
        to, nxt = (p0, p1) if leg % 2 == 0 else (p1, p0)
        x, y = self.centre(fire)
        return sim.FireState(x, y, 0.0, 0.0, to[0], to[1], remaining, nxt[0], nxt[1], d)

    def observe(self):
        sim = self.sim
        scr = self.screen()
        now = time.monotonic()
        lvl = self.level
        char = self.centre(scr.ids["character_image_lvl%d" % lvl])
        coins = tuple(self.centre(c) for c in list(scr.coins_ids.values()))
        monsters_now = [self.centre(scr.ids["monster%d_image_lvl%d" % (i + 1, lvl)])
                        for i in range(scr.num_monsters)]
        if self.prev_monsters is None or now - self.prev_time < 1e-3:
            vel = [(0.0, 0.0)] * len(monsters_now)
        else:
            dt = now - self.prev_time
            vel = [((m[0] - p[0]) / dt, (m[1] - p[1]) / dt)
                   for m, p in zip(monsters_now, self.prev_monsters)]
        self.prev_monsters, self.prev_time = monsters_now, now
        monsters = tuple((m[0], m[1], v[0], v[1]) for m, v in zip(monsters_now, vel))
        fires = tuple(self._fire_state(scr.ids["fire%d_lvl%d" % (i + 1, lvl)], now)
                      for i in range(scr.num_fires))
        if self.coins_left is None or len(coins) < self.coins_left:
            self.last_coin_time = now
        self.coins_left = len(coins)
        self.frame += 1
        life = max(0.0, 1.0 - scr.num_collisions_hit / scr.num_collisions_level)
        return sim.Observation(level=lvl, frame=self.frame, time=now - self.t0, char=char,
                               coins=coins, monsters=monsters, fires=fires,
                               margin=sim.EDGE_MARGIN, stagnation=now - self.last_coin_time,
                               life=life)


def main():
    args = parse_args()
    if args.headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ.setdefault("KIVY_NO_ARGS", "1")

    assets = os.path.abspath(args.assets)
    game_file = os.path.abspath(args.game) if args.game else os.path.join(assets, "main_work_greedy.py")
    os.chdir(assets)        # the game loads images, sounds and cointex.kv from here

    from cointex_parta import sim
    from cointex_parta.runner import make_agent

    game = load_game(game_file)
    import kivy.clock

    random.seed(args.seed)  # same coin layout for every agent on this seed
    app = game["app"]
    state = {"outcome": "timeout", "started": None, "stop": threading.Event(),
             "plan_ms": [], "moves": 0}

    if args.agent != "greedy":
        agent = make_agent(args.agent, args.seed)

        def agent_run(thread):
            world = LiveWorld(app, game["lvl_num"], sim)
            while not state["stop"].is_set():
                scr = world.screen()
                if scr.character_killed or not scr.coins_ids:
                    break
                obs = world.observe()
                t0 = time.perf_counter()
                target, wait_frames = agent.act(obs)
                state["plan_ms"].append((time.perf_counter() - t0) * 1000.0)
                # The game only checks coin pickups when the character moves (char_pos_hint),
                # the simulator checks every frame. So if the agent stays put while a coin is
                # already inside its pickup box, step onto that coin so the game registers it.
                if target is not None and math.hypot(target[0] - obs.char[0], target[1] - obs.char[1]) < 1e-3:
                    for cx, cy in obs.coins:
                        if abs(cx - obs.char[0]) <= sim.COIN_GAB and abs(cy - obs.char[1]) <= sim.COIN_GAB:
                            target = (cx, cy)
                            break
                if os.environ.get("LIVE_TRACE"):
                    state.setdefault("trace", []).append(
                        {"t": round(obs.time, 2), "char": [round(v, 3) for v in obs.char],
                         "target": None if target is None else [round(float(v), 3) for v in target],
                         "coins": [[round(v, 3) for v in c] for c in obs.coins[:4]], "n": len(obs.coins)})
                if target is not None:
                    state["moves"] += 1
                    kivy.clock.Clock.schedule_once(
                        lambda _dt, tg=target: app.start_char_animation(world.level, tg), 0)
                time.sleep(max(1, int(wait_frames)) / sim.FPS)

        game["CollectCoinThread"].run = agent_run

    def enter_level(_dt):
        state["started"] = time.monotonic()
        app.root.current = "level%d" % args.level

    def poll(_dt):
        if state["started"] is None:
            return
        scr = app.root.screens[args.level]
        elapsed = time.monotonic() - state["started"]
        if scr.num_coins_collected >= scr.num_coins:
            state["outcome"] = "won"
        elif scr.character_killed:
            state["outcome"] = "died"
        elif elapsed < args.timeout:
            return
        kivy.clock.Clock.unschedule(poll)
        state["stop"].set()
        plan = state["plan_ms"]
        state["result"] = {
            "agent": args.agent, "level": args.level, "seed": args.seed,
            "outcome": state["outcome"], "won": state["outcome"] == "won",
            "coins_collected": scr.num_coins_collected, "coins_total": scr.num_coins,
            "coin_pct": round(100.0 * scr.num_coins_collected / scr.num_coins, 2),
            "remaining_life": round(100.0 * max(0.0, 1.0 - scr.num_collisions_hit / scr.num_collisions_level), 2),
            "seconds": round(elapsed, 2),
            "moves": state["moves"],
            "mean_plan_ms": round(sum(plan) / len(plan), 2) if plan else None,
        }
        if "trace" in state:
            state["result"]["trace"] = state["trace"]
        app.stop()

    kivy.clock.Clock.schedule_once(enter_level, 1.0)
    kivy.clock.Clock.schedule_interval(poll, 0.05)
    app.run()

    result = state.get("result", {"agent": args.agent, "level": args.level, "seed": args.seed,
                                  "outcome": "aborted", "won": False})
    print(json.dumps(result, indent=2))
    if args.json:
        with open(args.json, "w") as handle:
            json.dump(result, handle, indent=2)
    sys.stdout.flush()
    os._exit(0 if result.get("won") else 1)   # the greedy thread is not a daemon


if __name__ == "__main__":
    main()
