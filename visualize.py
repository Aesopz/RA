# visualize.py
"""
Route visualizer for RMFS layouts
---------------------------------
* 使用 matplotlib 將倉庫網格、揀貨目標、行走路徑與步驟序號一次呈現。
* 支援儲存 PNG / 跑完直接顯示。
"""

from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

Coord = Tuple[int, int]  # (row, col)

# -------- 1. 個別格子顏色 -------- #
_CELL_COLORS = {
    0: "#444444",  # shelf / obstacle
    1: "#e0e0e0",  # turn road
    2: "#d0d0ff",  # sub road
    3: "#c0ffc0",  # main road
    4: "#ffd080",  # picking station
    5: "#ffe0e0",  # charge station
    6: "#e0ffff",  # queue charge
    7: "#fff0c0",  # charge leave
    8: "#ffc0ff",  # queue pick
}

def _build_cmap() -> ListedColormap:
    max_code = max(_CELL_COLORS)
    colors = ["#ffffff"] * (max_code + 1)
    for code, col in _CELL_COLORS.items():
        colors[code] = col
    return ListedColormap(colors)

_CMAP = _build_cmap()

# -------- 2. 主函式 -------- #
def visualize_route(
    layout: np.ndarray,
    path: List[Coord],
    picks: Optional[List[Coord]] = None,
    title: str = "RMFS Route",
    save_path: Optional[str] = None,
    annotate_every: int = 1,
) -> None:
    """
    在 matplotlib 視窗中畫出 layout + 路徑 + (可選) picks。

    Parameters
    ----------
    layout : np.ndarray        倉庫佈局矩陣
    path   : List[Coord]       A* 或其他策略產生的完整座標序列
    picks  : List[Coord], opt  揀貨目標 (依拜訪順序)
    title  : str               圖片標題
    save_path : str, opt       若給定路徑則儲存 PNG
    annotate_every : int       多少步標一次序號 (預設 1 = 每步都標)
    """
    if not path:
        raise ValueError("path 為空，無法視覺化！")

    # ===== 1) 畫網格 =====
    plt.figure(figsize=(10, 8))
    plt.imshow(layout, cmap=_CMAP, origin="upper")
    plt.title(title)
    plt.xticks(range(layout.shape[1]))
    plt.yticks(range(layout.shape[0]))
    plt.grid(True, color="black", linewidth=0.2)

    # ===== 2) 畫路徑線 + 起終點 =====
    rows, cols = zip(*path)
    plt.plot(cols, rows, "-o", linewidth=2, markersize=4, label="route")

    # 標註步驟號碼
    for idx, (r, c) in enumerate(path):
        if idx % annotate_every == 0:
            plt.text(c, r, str(idx), color="black", fontsize=7,
                     ha="center", va="center", fontweight="bold")

    plt.scatter(cols[0], rows[0], marker="s", s=120, color="gold", edgecolors="black", label="start")
    plt.scatter(cols[-1], rows[-1], marker="P", s=140, color="red", edgecolors="black", label="end")

    # ===== 3) 標註 picks =====
    if picks:
        pr, pc = zip(*picks)
        plt.scatter(pc, pr, marker="*", s=160, color="orange",
                    edgecolors="black", label="pick (order)")
        for i, (r, c) in enumerate(picks, 1):
            plt.text(c, r, f"P{i}", color="blue", fontsize=8,
                     ha="center", va="bottom", fontweight="bold")

    plt.legend(loc="upper right", bbox_to_anchor=(1.15, 1.02))
    plt.gca().invert_yaxis()     # 讓 (0,0) 在左上 & row 往下遞增
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"[visualize] Saved to {save_path}")
    else:
        plt.show()
