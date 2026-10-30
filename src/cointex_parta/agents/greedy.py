"""
The original greedy agent from main_work_greedy.py.

create_matrix, check_coin and findMinRoute are copied from the given file
(we only took out the print statements), so the baseline behaves the same.
GreedyAgent below just replays what CollectCoinThread.run() does:
plan a nearest-neighbour route over the coins, walk to each coin with a
0.4 s sleep, then read the positions again and repeat.

Problems we found (see notebook 01):
  1. hazards are only checked when the route is planned, not while walking it
  2. check_coin pops from the list it is looping over, so it skips coins
  3. the route always starts from (0.1, 0.1), not the real position
  4. moves have no length limit, so one move can cross a monster's path
  5. 0.4 s sleep but the walk only takes 0.25 s
  6. if all coins are near a hazard the route is empty and it just waits
"""

from typing import DefaultDict

from ..sim import COIN_SIZE, FIRE_SIZE, MONSTER_SIZE, FPS

INT_MAX = 2147483647
SLEEP_SECONDS = 0.4


# ---- copied from main_work_greedy.py ----
def create_matrix(start_pos, coin_pos, monsters_pos, fires_pos):
    coin_pos = check_coin(coin_pos, monsters_pos, fires_pos)

    tem_pos = coin_pos
    tem_pos.insert(0, start_pos)
    tem_dif_y = []
    for i in range(len(coin_pos)):
        tem_dif_x = []
        for j in range(len(coin_pos)):
            if (i == j):
                tem_dif_x.append(-1)
            else:
                tem_dif_x.append(abs(coin_pos[i][0] - coin_pos[j][0]) + abs(coin_pos[i][1] - coin_pos[j][1]))
        tem_dif_y.append(tem_dif_x)
    return tem_dif_y


def check_coin(coin_pos, monsters_pos, fires_pos):
    monsters_pos.append([-10, -10])
    fires_pos.append([-10, -10])

    tem_coin_pos = coin_pos
    p = 0.3  # parameter to adjust the closeness between coin to monster (or fire)
    for i in range(len(coin_pos)):
        for j in range(len(monsters_pos)):
            for k in range(len(fires_pos)):
                try:
                    if ((abs(coin_pos[i][0] - monsters_pos[j][0]) + abs(coin_pos[i][1] - monsters_pos[j][1])) < p) \
                            or ((abs(coin_pos[i][0] - fires_pos[k][0]) + abs(coin_pos[i][1] - fires_pos[k][1])) < p):
                        tem_coin_pos.pop(i)
                except:  # noqa: E722  (kept as in the original)
                    None
    return tem_coin_pos


def findMinRoute(tsp):
    sum = 0
    counter = 0
    j = 0
    i = 0
    min = INT_MAX
    visitedRouteList = DefaultDict(int)

    visitedRouteList[0] = 1
    route = [0] * len(tsp)

    while i < len(tsp) and j < len(tsp[i]):
        if counter >= len(tsp[i]) - 1:
            break
        if j != i and (visitedRouteList[j] == 0):
            if tsp[i][j] < min:
                min = tsp[i][j]
                route[counter] = j + 1
        j += 1
        if j == len(tsp[i]):
            sum += min
            min = INT_MAX
            visitedRouteList[route[counter] - 1] = 1
            j = 0
            i = route[counter] - 1
            counter += 1

    i = route[counter - 1] - 1
    for j in range(len(tsp)):
        if (i != j) and tsp[i][j] < min:
            min = tsp[i][j]
            route[counter] = j + 1
    sum += min
    return route
# ---- end of copied code ----


def _corners(obs):
    # position_func_v3 gives pos_hint (bottom-left corner), not the centre
    coin_pos = [[x - COIN_SIZE / 2.0, y - COIN_SIZE / 2.0] for x, y in obs.coins]
    monsters_pos = [[m[0] - MONSTER_SIZE / 2.0, m[1] - MONSTER_SIZE / 2.0] for m in obs.monsters]
    fires_pos = [[f.x - FIRE_SIZE / 2.0, f.y - FIRE_SIZE / 2.0] for f in obs.fires]
    return coin_pos, monsters_pos, fires_pos


class GreedyAgent:
    # same steps as CollectCoinThread.run()
    # act() returns (where to walk, how many frames to wait)

    name = "greedy"

    def __init__(self, seed=0):
        self._plan = None          # remaining stops of the current tour
        self._started = False

    def act(self, obs):
        if not self._started:
            # the original moves to start_pos first but doesn't sleep,
            # so the first coin move replaces it straight away
            self._started = True
        while True:
            if self._plan:
                target = self._plan.pop(0)
                return (float(target[0]), float(target[1])), int(round(SLEEP_SECONDS * FPS))
            if not obs.coins:
                return None, 1
            coin_pos, monsters_pos, fires_pos = _corners(obs)
            start_pos = [0.1, 0.1]
            tsp = create_matrix(start_pos, coin_pos, monsters_pos, fires_pos)
            route = findMinRoute(tsp)
            # create_matrix inserted start_pos into coin_pos, same as the original
            stops = [coin_pos[route[i] - 1] for i in range(0, len(route) - 1)]
            if not stops:
                # original just loops without moving until the hazards move away
                return None, 1
            self._plan = stops
