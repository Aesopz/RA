# s_shape_dynamic.py

from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import numpy as np
from a_star import a_star, DEFAULT_COSTS

Coord = Tuple[int, int]


def find_nearest(layout: np.ndarray, start_r: int, col: int, target_codes: set[int]) -> Optional[int]:
    """上下找最近符合指定 cell_code 的 row"""
    for offset in range(1, layout.shape[0]):
        for r in [start_r - offset, start_r + offset]:
            if 0 <= r < layout.shape[0] and layout[r, col] in target_codes:
                return r
    return None


def find_nearest_station(curr: Coord, stations: List[Coord]) -> Coord:
    """從當前座標找最近的 picking station"""
    return min(stations, key=lambda p: abs(p[0]-curr[0]) + abs(p[1]-curr[1]))


def plan_route_s_shape_dynamic(
    layout: np.ndarray,
    start: Coord,
    picks: List[Coord],
    stations: Optional[List[Coord]] = None,
    costs: Optional[Dict[int, float]] = None
) -> List[Coord]:
    """
    動態 S-shape 導航（步驟式決策），根據貨架相對位置決定方向與移動方式。
    
    Parameters
    ----------
    layout : np.ndarray
    start : Coord
    picks : List[Coord]
    stations : List[Coord], optional
    costs : dict, optional

    Returns
    -------
    List[Coord] : 完整走訪路徑
    """
    if costs is None:
        costs = DEFAULT_COSTS
    remaining = picks.copy()
    path: List[Coord] = [start]
    current = start

    # ===== 1) 判斷初始方向（up or down）=====
    up_exists = any(p[0] < current[0] for p in remaining)
    down_exists = any(p[0] > current[0] for p in remaining)
    direction = -1 if up_exists else (1 if down_exists else 0)
    if direction == 0:
        return path  # 無貨可撿

    # ===== 2) 開始迴圈撿貨 =====
    while remaining:
        curr_r, curr_c = current

        # ---- 判斷下一個最近可撿貨物 ----
        remaining.sort(key=lambda p: abs(p[0]-curr_r) + abs(p[1]-curr_c))
        for target in remaining:
            target_r, target_c = target
            if (direction == -1 and target_r < curr_r) or (direction == 1 and target_r > curr_r):
                break
        else:
            # 該方向沒貨了 → 換方向
            direction *= -1
            continue

        # ---- 移動到目標 col：前提是必須站在可左右移動的 cell ----
        if layout[curr_r, curr_c] not in (1, 3):  # 不是 turn / main road
            nearest_r = find_nearest(layout, curr_r, curr_c, {1})
            if nearest_r is None:
                raise RuntimeError("找不到任何 turn point！")
            segment = a_star(layout, (curr_r, curr_c), (nearest_r, curr_c), costs)
            path.extend(segment[1:])
            curr_r = nearest_r
            current = (curr_r, curr_c)

        # ---- 水平移動到目標 col ----
        if curr_c != target_c:
            segment = a_star(layout, current, (curr_r, target_c), costs)
            path.extend(segment[1:])
            curr_c = target_c
            current = (curr_r, curr_c)

        # ---- 垂直移動到目標 row ----
        if curr_r != target_r:
            segment = a_star(layout, current, (target_r, curr_c), costs)
            path.extend(segment[1:])
            curr_r = target_r
            current = (curr_r, curr_c)

        # ---- 撿取完成 ----
        remaining.remove(current)

        # ---- 繼續直行（往 turn point） ----
        next_r = find_nearest(layout, curr_r, curr_c, {1})  # turn point
        if next_r is not None and (direction * (next_r - curr_r) > 0):
            segment = a_star(layout, current, (next_r, curr_c), costs)
            path.extend(segment[1:])
            current = (next_r, curr_c)
        else:
            # 無法繼續延伸，回主幹道調整方向
            direction *= -1

    # ===== 3) 回到最近的 picking station =====
    if stations is None:
        stations = list(zip(*np.where(layout == 4)))
    end_station = find_nearest_station(current, stations)
    segment = a_star(layout, current, end_station, costs)
    path.extend(segment[1:])

    return path
