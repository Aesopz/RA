# largest_gap_n.py
"""
Dynamic Largest-Gap routing strategy
===================================

依照使用者最新邏輯逐步決策：
1. 先決定初始方向（上／下）。
2. 每輪選最近貨架，若不在 main road 先上下移動至最近 turn point (layout==1)。
3. 進入目標巷道後：
   * 若該巷道剩餘待撿貨物 >=2 → 依當前方向走完整巷道，
   * 否則或目標 row ∈ {2,5,8,11} → 撿完即反轉回原 turn point。
4. 重複直到所有貨架取完，再回最近的 picking station (layout==4)。

依賴：
* a_star.py  – 提供 a_star() 路徑尋徑
* layout.py – 提供網格編碼
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import numpy as np
from a_star import a_star, DEFAULT_COSTS

Coord = Tuple[int, int]
REV_ROWS = {2, 5, 8, 11}   # 撿完需反轉的 row

# ---------- 工具 ---------- #
def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def nearest_turn(layout: np.ndarray, r: int, c: int) -> Optional[int]:
    """在同 col 上下尋找最近 turn point (layout==1) 回傳 row"""
    H = layout.shape[0]
    for off in range(1, H):
        for nr in (r-off, r+off):
            if 0 <= nr < H and layout[nr, c] == 1:
                return nr
    return None


def nearest_station(layout: np.ndarray, pos: Coord) -> Coord:
    """回傳最近的 picking station (layout==4)"""
    stations = list(zip(*np.where(layout == 4)))
    return min(stations, key=lambda s: manhattan(pos, s))


# ---------- 主函式 ---------- #
def plan_route_largest_gap_n(
    layout: np.ndarray,
    start: Coord,
    picks: List[Coord],
    costs: Dict[int, float] = DEFAULT_COSTS,
) -> List[Coord]:
    """
    Parameters
    ----------
    layout : np.ndarray
    start  : Coord
    picks  : List[Coord]

    Returns
    -------
    path   : List[Coord]  完整行走路徑
    """
    remaining = picks.copy()
    path: List[Coord] = [start]
    curr = start

    # -- 決定初始方向：上(-1) or 下(+1) --
    up_exist = any(p[0] < curr[0] for p in remaining)
    direction = -1 if up_exist else 1

    while remaining:
        # 1) 找最近目標
        remaining.sort(key=lambda p: manhattan(curr, p))
        target = remaining[0]

        # 2) 若不在 main road (3)，先到最近 turn point (1)
        r, c = curr
        if layout[r, c] != 3:
            turn_r = nearest_turn(layout, r, c)
            if turn_r is None:
                raise RuntimeError("找不到 turn point！")
            segment = a_star(layout, curr, (turn_r, c), costs)
            path.extend(segment[1:])
            curr = (turn_r, c)
            r = turn_r

        # 3) 水平到目標巷道 col
        if c != target[1]:
            segment = a_star(layout, curr, (r, target[1]), costs)
            path.extend(segment[1:])
            curr = (r, target[1])

        # 4) 垂直到目標 row
        segment = a_star(layout, curr, target, costs)
        path.extend(segment[1:])
        curr = target
        remaining.remove(curr)

        # 5) 判斷巷道剩餘 item
        same_col_items = [p for p in remaining if p[1] == curr[1]]
        go_full_aisle = len(same_col_items) >= 2

        if go_full_aisle:
            # 依方向走向巷道盡頭 (到 turn point)
            turn_r = nearest_turn(layout, curr[0], curr[1])
            if turn_r is not None and (turn_r - curr[0]) * direction > 0:
                segment = a_star(layout, curr, (turn_r, curr[1]), costs)
                path.extend(segment[1:])
                curr = (turn_r, curr[1])
        else:
            # 不滿 2 件或 row 在 REV_ROWS → 原路折返
            if curr[0] in REV_ROWS or not same_col_items:
                turn_r = nearest_turn(layout, curr[0], curr[1])
                if turn_r is not None and (turn_r - curr[0]) * direction < 0:
                    segment = a_star(layout, curr, (turn_r, curr[1]), costs)
                    path.extend(segment[1:])
                    curr = (turn_r, curr[1])

        # 6) 回到 main road 以左右移動
        if layout[curr[0], curr[1]] != 3:
            # 往下方向找 main road
            main_r = curr[0]
            while 0 <= main_r < layout.shape[0] and layout[main_r, curr[1]] != 3:
                main_r += direction
            if 0 <= main_r < layout.shape[0]:
                segment = a_star(layout, curr, (main_r, curr[1]), costs)
                path.extend(segment[1:])
                curr = (main_r, curr[1])

        # 7) 更新上下方向：若上方還有貨物則 direction=-1，否則 +1
        up_exist = any(p[0] < curr[0] for p in remaining)
        down_exist = any(p[0] > curr[0] for p in remaining)
        direction = -1 if up_exist else (1 if down_exist else direction)

    # 8) 全部撿完 → 回最近 picking station
    dest = nearest_station(layout, curr)
    if dest != curr:
        segment = a_star(layout, curr, dest, costs)
        path.extend(segment[1:])

    return path


# ---------- 測試 ----------
if __name__ == "__main__":
    from layout import build_layout
    wl = build_layout()
    grid = wl.layout_matrix

    start = (13, 7)
    picks = [(5, 4), (2, 10), (8, 1), (3, 13)]
    route = plan_route_largest_gap_n(grid, start, picks)
    print("steps:", len(route)-1)
    print(" -> ".join(map(str, route)))
