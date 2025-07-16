# warehouse_layout.py

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class WarehouseLayout:
    layout_matrix: np.ndarray
    picking_stations: List[Tuple[int, int]]
    charge_stations: List[Tuple[int, int]]
    que_charge: List[Tuple[int, int]]
    charge_leave: List[Tuple[int, int]]
    que_pick: List[Tuple[int, int]]

def build_layout() -> WarehouseLayout:
    num_rows, num_cols = 14, 15
    vertical_aisles = [0, 1, 4, 7, 10, 13, 14]
    horizontal_aisles = [0, 1, 6, 7, 12, 13]

    layout = np.zeros((num_rows, num_cols), dtype=int)

    for r in range(num_rows):
        for c in range(num_cols):
            if c in vertical_aisles and r in horizontal_aisles:
                layout[r, c] = 1  # turn road
            elif c in vertical_aisles:
                layout[r, c] = 2  # subroad
            elif r in horizontal_aisles:
                layout[r, c] = 3  # main road
            else:
                layout[r, c] = 0  # shelf block

    picking_stations = [(14, 2), (14, 11)]
    charge_stations  = [(14, 0), (14, 13)]
    que_charge       = [(13, 0), (13, 13)]
    charge_leave     = [(14, 1), (14, 12)]
    que_pick         = [(14, 8), (14, 9), (14, 10), (14, 3), (14, 4), (14, 5)]

    for x, y in picking_stations:
        layout[y, x] = 4
    for x, y in charge_stations:
        layout[y, x] = 5
    for x, y in que_charge:
        layout[y, x] = 6
    for x, y in charge_leave:
        layout[y, x] = 7
    for x, y in que_pick:
        layout[y, x] = 8

    return WarehouseLayout(
        layout_matrix=layout,
        picking_stations=picking_stations,
        charge_stations=charge_stations,
        que_charge=que_charge,
        charge_leave=charge_leave,
        que_pick=que_pick
    )