"""
Plotting functions for the notebooks and report.
Each agent always has the same colour.
"""

import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from . import sim

AGENT_COLORS = {
    "proposed": "#2a78d6",                 # blue
    "greedy": "#eb6834",                   # orange
    "ga_task2": "#1baf7a",                 # aqua
    "proposed_no_hazard": "#eda100",       # yellow
    "proposed_static_hazard": "#e87ba4",   # magenta
    "proposed_no_tour": "#6250d6",         # violet
}
AGENT_LABELS = {
    "proposed": "Proposed (RH-STA*)",
    "greedy": "Original greedy",
    "ga_task2": "GA (Task 2)",
    "proposed_no_hazard": "RH-STA* w/o hazards",
    "proposed_static_hazard": "RH-STA* static hazards",
    "proposed_no_tour": "RH-STA* w/o 2-opt tour",
}
INK, MUTED, GRID = "#1f2328", "#59636e", "#d0d7de"


def style():
    matplotlib.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "axes.edgecolor": GRID, "axes.labelcolor": INK, "axes.titleweight": "bold",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
        "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
        "legend.frameon": False, "font.size": 10,
    })


def color(agent):
    return AGENT_COLORS.get(agent, "#59636e")


def label(agent):
    return AGENT_LABELS.get(agent, agent)


def save(fig, folder, name):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    fig.savefig(path)
    return path


def per_level_bars(df, metric, agents, ylabel, title, agg="mean", ylim=None, fmt="%.0f",
                   scale=1.0, figsize=(14, 4.6)):
    # bars per level, one bar per agent
    levels = sorted(df["level"].unique())
    x = np.arange(len(levels))
    width = 0.84 / len(agents)
    fig, ax = plt.subplots(figsize=figsize)
    for i, agent in enumerate(agents):
        sub = df[df["agent"] == agent].groupby("level")[metric].agg(agg).reindex(levels) * scale
        ax.bar(x + (i - (len(agents) - 1) / 2) * width, sub.values, width * 0.92,
               color=color(agent), label=label(agent), edgecolor="white", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([f"L{lv}" for lv in levels])
    ax.set_xlabel("Level")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    if ylim:
        ax.set_ylim(*ylim)
    ax.grid(axis="x", visible=False)
    ax.legend(ncol=len(agents), loc="upper center", bbox_to_anchor=(0.5, -0.14))
    fig.tight_layout()
    return fig


def overall_bars(summary, metrics, agents, titles, fmts=None, figsize=None):
    # one small chart per metric with the value on each bar
    fmts = fmts or ["%.1f"] * len(metrics)
    figsize = figsize or (3.4 * len(metrics), 3.6)
    fig, axes = plt.subplots(1, len(metrics), figsize=figsize)
    axes = np.atleast_1d(axes)
    s = summary.set_index("agent").reindex(agents)
    for ax, metric, title, fmt in zip(axes, metrics, titles, fmts):
        vals = s[metric].values
        bars = ax.bar(range(len(agents)), vals, 0.7, color=[color(a) for a in agents],
                      edgecolor="white", linewidth=0.6)
        ax.bar_label(bars, fmt=fmt, padding=2, fontsize=9, color=INK)
        ax.set_xticks(range(len(agents)))
        ax.set_xticklabels([label(a).replace(" (", "\n(") for a in agents], fontsize=8)
        ax.set_title(title, loc="left", fontsize=10)
        ax.grid(axis="x", visible=False)
        top = np.nanmax(vals) if np.isfinite(vals).any() else 1
        ax.set_ylim(0, top * 1.18 if top > 0 else 1)
    fig.tight_layout()
    return fig


def success_heatmap(df, agents, title="Success rate (%) by level"):
    levels = sorted(df["level"].unique())
    mat = np.array([[100 * df[(df.agent == a) & (df.level == lv)]["won"].mean() for lv in levels]
                    for a in agents])
    fig, ax = plt.subplots(figsize=(14, 0.55 * len(agents) + 1.4))
    im = ax.imshow(mat, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    for i in range(len(agents)):
        for j in range(len(levels)):
            v = mat[i, j]
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if v > 60 else INK)
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"L{lv}" for lv in levels])
    ax.set_yticks(range(len(agents)))
    ax.set_yticklabels([label(a) for a in agents])
    ax.grid(False)
    ax.set_title(title, loc="left")
    fig.colorbar(im, ax=ax, fraction=0.015, pad=0.01)
    fig.tight_layout()
    return fig


def completion_box(df, agents, title="Completion time of won episodes"):
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [df[(df.agent == a) & (df.won == 1)]["completion_time"].dropna().values for a in agents]
    bp = ax.boxplot(data, patch_artist=True, widths=0.5, showfliers=False,
                    medianprops=dict(color=INK, linewidth=1.5))
    for patch, a in zip(bp["boxes"], agents):
        patch.set_facecolor(color(a))
        patch.set_alpha(0.85)
        patch.set_edgecolor("white")
    ax.set_xticks(range(1, len(agents) + 1))
    ax.set_xticklabels([label(a) for a in agents])
    ax.set_ylabel("Seconds")
    ax.set_title(title, loc="left")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    return fig


def difficulty_curve(df, agents, metric="won", ylabel="Success rate (%)", scale=100.0,
                     title="Success rate vs level"):
    levels = sorted(df["level"].unique())
    fig, ax = plt.subplots(figsize=(11, 4))
    for a in agents:
        s = df[df.agent == a].groupby("level")[metric].mean().reindex(levels) * scale
        ax.plot(levels, s.values, "-o", color=color(a), lw=2, ms=5, label=label(a))
    ax.set_xticks(levels)
    ax.set_xlabel("Level")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left")
    ax.legend(ncol=len(agents), loc="upper center", bbox_to_anchor=(0.5, -0.16))
    fig.tight_layout()
    return fig


def _outcome(env):
    return "WON" if env.won else ("DIED" if env.killed else "TIMEOUT")


def draw_trajectory(ax, trace, agent, frame=None):
    # character path + where the hazards ended + coins not collected
    env = trace["env"]
    path = np.array(trace["char"] if frame is None else trace["char"][:frame + 1])
    ax.plot(path[:, 0], path[:, 1], "-", color=color(agent), lw=1.6, zorder=2)
    ax.scatter(*path[0], c=INK, s=30, zorder=4)
    for coin in env.coins:
        ax.scatter(*coin, marker="o", c="#eda100", edgecolors=INK, s=60, zorder=3)
    for m in env.monsters:
        ax.add_patch(plt.Rectangle(m["pos"] - sim.MONSTER_GAB, 2 * sim.MONSTER_GAB, 2 * sim.MONSTER_GAB,
                                   color="#6250d6", alpha=0.25, zorder=1))
    for f in env.fires:
        ax.scatter(*f["pos"], marker="^", c="#e34948", s=70, zorder=3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_title(f"{label(agent)} - {_outcome(env)}\n"
                 f"{env.num_coins - len(env.coins)}/{env.num_coins} coins, "
                 f"life {env.remaining_life_fraction() * 100:.0f}%, {env.seconds:.1f}s", fontsize=10)


def trajectory_grid(traces, agents, suptitle):
    fig, axes = plt.subplots(1, len(agents), figsize=(5 * len(agents), 5.4))
    for ax, a in zip(np.atleast_1d(axes), agents):
        draw_trajectory(ax, traces[a], a)
    handles = [
        plt.Line2D([], [], marker="o", ls="", mfc="#eda100", mec=INK, label="coin left"),
        plt.Line2D([], [], marker="s", ls="", c="#6250d6", alpha=0.4, ms=10, label="monster (final)"),
        plt.Line2D([], [], marker="^", ls="", c="#e34948", label="fire (final)"),
        plt.Line2D([], [], marker="o", ls="", c=INK, label="start"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4)
    fig.suptitle(suptitle, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    return fig


def animate_episode(trace, agent, path, fps=20, every=3, tail=90):
    # save a gif of one episode (draws every 3rd frame)
    from matplotlib.animation import FuncAnimation, PillowWriter
    env = trace["env"]
    chars = np.array(trace["char"])
    n = len(trace["monsters"])
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    line, = ax.plot([], [], "-", color=color(agent), lw=1.4)
    char = ax.add_patch(plt.Rectangle((0, 0), sim.COIN_GAB * 2, sim.COIN_GAB * 2,
                                      color=color(agent), alpha=0.9))
    mons = [ax.add_patch(plt.Rectangle((0, 0), 2 * sim.MONSTER_GAB, 2 * sim.MONSTER_GAB,
                                       color="#6250d6", alpha=0.3)) for _ in env.monsters]
    coins = ax.scatter([], [], marker="o", c="#eda100", edgecolors=INK, s=40)
    fires = ax.scatter([], [], marker="^", c="#e34948", s=60)
    title = ax.set_title("")
    frames = list(range(0, n, every))

    def update(i):
        c = chars[i + 1]
        lo = max(0, i + 1 - tail)
        line.set_data(chars[lo:i + 2, 0], chars[lo:i + 2, 1])
        char.set_xy(c - sim.COIN_GAB)
        for patch, m in zip(mons, trace["monsters"][i]):
            patch.set_xy(m - sim.MONSTER_GAB)
        coins.set_offsets(np.array(trace["coins"][i]).reshape(-1, 2))
        if trace["fires"][i]:
            fires.set_offsets(np.array(trace["fires"][i]))
        title.set_text(f"{label(agent)}  L{env.level_num}  t={i / sim.FPS:.1f}s  "
                       f"coins left {trace['coins_left'][i]}")
        return [line, char, coins, fires, title] + mons

    anim = FuncAnimation(fig, update, frames=frames, blit=False)
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return path
