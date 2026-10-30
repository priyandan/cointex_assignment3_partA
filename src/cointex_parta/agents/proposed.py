"""
Our improved agent: RH-STA* (risk-aware receding-horizon space-time A*).

The idea:
1. Coin order - nearest neighbour tour + 2-opt, starting from where the
   character actually is (the original always started from (0.1, 0.1)).
2. Path - A* over (x, y, t). t = number of 0.25 s moves ahead. From each
   state we can move in 16 directions with 3 step sizes, step onto the goal
   coin, or wait. Every move is checked against where the hazards WILL be:
     - fires move on fixed paths (from cointex.kv) so we can predict them exactly
     - monsters are predicted with their current velocity, plus a safety
       margin that grows the further ahead we look (they can turn at any time)
   If a move hits a hazard in the first few steps we don't allow it. Later
   hits and near misses just add cost.
3. We only do the first move of the plan, then look again and re-plan
   (every 0.25 s).

Because time is part of the state, A* can choose to wait for a fire to pass
and then grab the coin. Greedy and the GA can't do that.

cost = 1 per move + 0.2 * distance + risk_weight * near-miss risk
h    = distance left / max step  (number of moves still needed)
"""

import heapq
import math
import time
from dataclasses import dataclass, replace

import numpy as np

from ..sim import COIN_GAB, FIRE_GAB, MONSTER_GAB, MONSTER_SIZE, MOVE_FRAMES, MOVE_SECONDS

SQRT2 = math.sqrt(2.0)


@dataclass(frozen=True)
class Config:
    name: str = "proposed"
    # moves
    max_step: float = 0.30          # longest move in one 0.25 s step
    step_fracs: tuple = (1.0, 0.5, 0.25)
    n_dirs: int = 16
    # search
    horizon: int = 8                # how many moves ahead (8 x 0.25 = 2 s)
    max_expansions: int = 100      # total for one move, shared by all the goals we try
    heuristic_weight: float = 1.2   # a bit greedy so A* is faster
    samples: int = 8                # points checked along each move
    grid: float = 0.02              # for the closed set
    # hazards
    use_hazards: bool = True
    predict_motion: bool = True
    monster_margin: float = 0.05
    fire_margin: float = 0.035
    monster_sigma: float = 0.10     # extra margin per second we look ahead
    contact_buffer: float = 0.01
    hard_steps: int = 3             # no predicted contact allowed in the first 3 moves
    late_contact_penalty: float = 3.0
    risk_weight: float = 4.0
    dist_weight: float = 0.2
    # goals
    use_tour: bool = True
    two_opt: bool = True
    alt_goals: int = 3
    defer_seconds: float = 1.0
    # if we're stuck (no coin for a while) we accept more risk
    stuck_seconds: float = 4.0
    stagnation_relax: float = 0.25


DEFAULT = Config()

# versions with one part turned off, for the ablation test
VARIANTS = {
    "proposed": DEFAULT,
    "proposed_no_hazard": replace(DEFAULT, name="proposed_no_hazard", use_hazards=False),
    "proposed_static_hazard": replace(DEFAULT, name="proposed_static_hazard", predict_motion=False),
    "proposed_no_tour": replace(DEFAULT, name="proposed_no_tour", use_tour=False),
}


def nn_two_opt_tour(start, coins, two_opt=True):
    # nearest neighbour tour from start, then 2-opt to remove crossings.
    # open path (we don't come back to the start). returns coin indexes in order
    n = len(coins)
    if n <= 1:
        return list(range(n))
    pts = np.vstack([np.asarray(start)[None, :], np.asarray(coins)])
    dist = np.hypot(*(pts[:, None, :] - pts[None, :, :]).transpose(2, 0, 1))
    order = [0]
    unvisited = set(range(1, n + 1))
    while unvisited:
        last = order[-1]
        nxt = min(unvisited, key=lambda j: dist[last, j])
        order.append(nxt)
        unvisited.remove(nxt)
    if two_opt:
        improved = True
        while improved:
            improved = False
            for i in range(1, n):
                for j in range(i + 1, n + 1):
                    a, b = order[i - 1], order[i]
                    c = order[j]
                    d = order[j + 1] if j + 1 <= n else None
                    before = dist[a, b] + (dist[c, d] if d is not None else 0.0)
                    after = dist[a, c] + (dist[b, d] if d is not None else 0.0)
                    if after < before - 1e-9:
                        order[i:j + 1] = order[i:j + 1][::-1]
                        improved = True
    return [k - 1 for k in order[1:]]


def tour_length(start, coins, order):
    pts = [np.asarray(start)] + [np.asarray(coins[k]) for k in order]
    return float(sum(np.hypot(*(pts[i + 1] - pts[i])) for i in range(len(pts) - 1)))


def _fire_positions(f, taus):
    # where a fire will be after each time in taus: finish the current sweep,
    # then go back and forth between the two end points
    a = np.array([f.x, f.y])
    b = np.array([f.tx, f.ty])
    c = np.array([f.ox, f.oy])
    r, D = max(f.remaining, 1e-9), f.leg_duration
    t = taus[..., None]
    first = a + (b - a) * np.clip(t / r, 0.0, 1.0)
    tp = np.maximum(t - r, 0.0)
    n = np.floor(tp / D)
    ph = (tp - n * D) / D
    forward = (n % 2 == 0)
    later = np.where(forward, b + (c - b) * ph, c + (b - c) * ph)
    return np.where(t <= r, first, later)


class ProposedAgent:
    def __init__(self, seed=0, config=DEFAULT):
        self.cfg = config
        self.name = config.name
        self._tour = []
        self._tour_key = None
        self._deferred = {}         # coin -> time we skip it until
        self.plan_ms = []
        self.last_plan = None       # kept so we can draw the plan
        c = config
        angles = np.arange(c.n_dirs) * (2 * math.pi / c.n_dirs)
        unit = np.stack([np.cos(angles), np.sin(angles)], axis=1)
        # all the moves we try, last row is "wait"
        self._moves = np.concatenate([unit * (c.max_step * s) for s in c.step_fracs]
                                     + [np.zeros((1, 2))])
        self._fracs = np.arange(1, c.samples + 1) / c.samples

    def _predict(self, obs):
        # predict all hazard positions for every move and sample point up to the horizon
        c = self.cfg
        taus = (np.arange(c.horizon)[:, None] + self._fracs[None, :]) * MOVE_SECONDS   # (H, S)
        pos, gab, margin = [], [], []
        if c.use_hazards:
            lo, hi = MONSTER_SIZE / 2.0, 1.0 - MONSTER_SIZE / 4.0 + MONSTER_SIZE / 2.0
            for x, y, vx, vy in obs.monsters:
                if c.predict_motion:
                    p = np.stack([np.clip(x + vx * taus, lo, hi), np.clip(y + vy * taus, lo, hi)], -1)
                else:
                    p = np.broadcast_to(np.array([x, y]), taus.shape + (2,))
                pos.append(p)
                gab.append(MONSTER_GAB)
                margin.append(c.monster_margin + c.monster_sigma * taus)
            for f in obs.fires:
                if c.predict_motion:
                    p = _fire_positions(f, taus)
                else:
                    p = np.broadcast_to(np.array([f.x, f.y]), taus.shape + (2,))
                pos.append(p)
                gab.append(FIRE_GAB)
                margin.append(np.full(taus.shape, c.fire_margin))
        if pos:
            self._hz = np.stack(pos, axis=2)     # (H, S, M, 2)
            self._gab = np.array(gab)            # (M,)
            self._mg = np.stack(margin, axis=2)  # (H, S, M)
        else:
            self._hz = None

    def _edges(self, p, succ, k):
        # risk + contact for every move p -> succ during move number k
        # (numpy so we check all moves at once)
        pts = p[None, None, :] + (succ - p)[:, None, :] * self._fracs[None, :, None]   # (A, S, 2)
        if self._hz is None:
            zeros = np.zeros(len(succ))
            return zeros, zeros.astype(bool), pts
        # same box-style distance the game uses for collisions
        d = np.abs(pts[:, :, None, :] - self._hz[k][None]).max(-1)
        clearance = d - self._gab[None, None, :]
        contact = (clearance <= self.cfg.contact_buffer).any(axis=(1, 2))
        risk = np.clip(1.0 - clearance / self._mg[k][None], 0.0, 1.0).sum(axis=(1, 2)) / self.cfg.samples
        return risk, contact, pts

    def _successors(self, p, goal, margin):
        c = self.cfg
        to_goal = goal - p
        dist = math.hypot(*to_goal)
        direct = goal if dist <= c.max_step else p + to_goal * (c.max_step / dist)
        succ = np.vstack([p + self._moves, direct[None, :]])
        return np.clip(succ, margin, 1.0 - margin)

    def _astar(self, obs, start, goal, risk_weight, hard_steps, budget):
        c = self.cfg
        H = c.horizon
        reach = COIN_GAB * 0.9
        h0 = max(0.0, math.hypot(*(goal - start)) - COIN_GAB * SQRT2) / c.max_step
        # node info stored in lists, index = node id
        xs, ys, ks, gs, parents, hs = [start[0]], [start[1]], [0], [0.0], [-1], [h0]
        heap = [(c.heuristic_weight * h0, 0.0, 0, False)]
        closed = set()
        best, best_key = None, None
        expansions = 0
        tie = 0
        while heap and expansions < budget:
            _, _, i, reached = heapq.heappop(heap)
            if reached:
                return self._path(i, parents, xs, ys), gs[i], True, expansions
            k = ks[i]
            key = (int(round(xs[i] / c.grid)), int(round(ys[i] / c.grid)), k)
            if key in closed:
                continue
            closed.add(key)
            expansions += 1
            # remember the node closest to the goal in case we don't reach it
            if i != 0:
                score = (hs[i], gs[i])
                if best_key is None or score < best_key:
                    best, best_key = i, score
            if k >= H:
                continue
            p = np.array([xs[i], ys[i]])
            succ = self._successors(p, goal, obs.margin)
            risk, contact, pts = self._edges(p, succ, k)
            lengths = np.hypot(*(succ - p).T)
            cost = 1.0 + c.dist_weight * lengths + risk_weight * risk
            if k >= hard_steps:
                cost = cost + c.late_contact_penalty * contact
                allowed = np.ones(len(succ), dtype=bool)
            else:
                allowed = ~contact
            hit_goal = (np.abs(pts - goal[None, None, :]).max(-1) <= reach).any(axis=1)
            dist_goal = np.hypot(*(succ - goal).T)
            hvals = np.where(hit_goal, 0.0, np.maximum(0.0, dist_goal - COIN_GAB * SQRT2) / c.max_step)
            g0 = gs[i]
            for a in np.nonzero(allowed)[0]:
                j = len(xs)
                xs.append(float(succ[a, 0]))
                ys.append(float(succ[a, 1]))
                ks.append(k + 1)
                g = g0 + float(cost[a])
                gs.append(g)
                parents.append(i)
                hs.append(float(hvals[a]))
                tie += 1
                heapq.heappush(heap, (g + c.heuristic_weight * hvals[a], tie, j, bool(hit_goal[a])))
        if best is None:
            return None, math.inf, False, expansions
        return self._path(best, parents, xs, ys), gs[best], False, expansions

    @staticmethod
    def _path(i, parents, xs, ys):
        path = []
        while i > 0:
            path.append((xs[i], ys[i]))
            i = parents[i]
        return path[::-1]

    def _escape(self, obs, start, goal):
        # every move is dangerous: pick the one that keeps us furthest from hazards
        succ = self._successors(start, goal, obs.margin)
        if self._hz is None:
            return tuple(succ[-1])
        pts = start[None, None, :] + (succ - start)[:, None, :] * self._fracs[None, :, None]
        d = np.abs(pts[:, :, None, :] - self._hz[0][None]).max(-1) - self._gab[None, None, :]
        worst = d.min(axis=(1, 2))
        progress = -np.hypot(*(succ - goal).T) * 1e-3
        return tuple(succ[int(np.argmax(worst + progress))])

    def _goal_order(self, obs):
        coins = obs.coins
        now = obs.time
        self._deferred = {k: t for k, t in self._deferred.items() if t > now and k in coins}
        if not self.cfg.use_tour:
            cx, cy = obs.char
            order = sorted(range(len(coins)), key=lambda j: math.hypot(coins[j][0] - cx, coins[j][1] - cy))
        else:
            # only rebuild the tour when the coins change
            key = (coins, tuple(sorted(self._deferred)))
            if key != self._tour_key:
                order = nn_two_opt_tour(obs.char, coins, self.cfg.two_opt)
                self._tour = [coins[j] for j in order]
                self._tour_key = key
            order = [coins.index(cn) for cn in self._tour]
        # skipped coins go to the back
        free = [j for j in order if coins[j] not in self._deferred]
        late = [j for j in order if coins[j] in self._deferred]
        return free + late

    def act(self, obs):
        if not obs.coins:
            return None, 1
        t0 = time.perf_counter()
        c = self.cfg
        self._predict(obs)
        start = np.array(obs.char)
        stuck = max(0.0, obs.stagnation - c.stuck_seconds)
        risk_weight = c.risk_weight / (1.0 + c.stagnation_relax * stuck)
        hard_steps = c.hard_steps if (stuck < c.stuck_seconds or obs.life < 0.5) else 1

        order = self._goal_order(obs)
        best_partial = None
        target = None
        # try the next coin in the tour, if blocked try the next 2
        # all tries share one search budget so a move never takes too long
        budget = c.max_expansions
        for rank, j in enumerate(order[:max(1, c.alt_goals)]):
            if rank > 0 and budget < 20:
                break
            goal = np.array(obs.coins[j])
            path, cost, reached, used = self._astar(obs, start, goal, risk_weight, hard_steps, budget)
            budget -= used
            if reached and path:
                target, self.last_plan = path[0], path
                break
            if rank == 0 and path:
                best_partial = path
            if c.use_tour and rank == 0:
                self._deferred[obs.coins[j]] = obs.time + c.defer_seconds
        if target is None:
            if best_partial:
                target, self.last_plan = best_partial[0], best_partial
            else:
                target = self._escape(obs, start, np.array(obs.coins[order[0]]))
                self.last_plan = [target]
        self.plan_ms.append((time.perf_counter() - t0) * 1000.0)
        return (float(target[0]), float(target[1])), MOVE_FRAMES
