# main.py

from typing import List, Tuple, Callable
import argparse
import numpy as np

from layout import build_layout
from s_shape_d import plan_route_s_shape_dynamic
from largest_gap_n import plan_route_largest_gap_n          # ★ 新增
from visualize import visualize_route

Coord = Tuple[int, int]


# ---------------- Demo para ---------------- #
def demo_parameters() -> tuple[np.ndarray, Coord, List[Coord], Coord]:
    wl = build_layout()
    grid = wl.layout_matrix
    start = (13, 7)
    picks = [(5, 4), (2, 10), (8, 1), (3, 13)]
    end = (2, 14)
    return grid, start, picks, end


# ---------------- process ---------------- #
def main() -> None:
    parser = argparse.ArgumentParser(description="RMFS Routing Demo")
    parser.add_argument("-s", "--strategy",
                        choices=["s-shape-dynamic", "largest_gap-n"],
                        default="s-shape-dynamic")
    parser.add_argument("-a", "--annotate-every", type=int, default=1)
    parser.add_argument("-o", "--save", type=str, default=None)
    args = parser.parse_args()

    layout, start, picks, end = demo_parameters()

    router: dict[str, Callable[..., List[Coord]]] = {
        "s-shape-dynamic": plan_route_s_shape_dynamic,
        "largest_gap-n": plan_route_largest_gap_n,           
    }

    plan_func = router[args.strategy]

    if args.strategy in {"s-shape-dynamic", "largest_gap-n"}:
        path = plan_func(layout, start, picks)
    else:
        path = plan_func(layout, start, picks, end=end)

    # result
    total_steps = len(path) - 1
    print(f"\n=== {args.strategy.upper()}  Route Summary ===")
    print(f"Total steps: {total_steps}\n")
    for idx, pos in enumerate(path):
        mark = ""
        if idx == 0:
            mark = "(start)"
        elif pos in picks:
            mark = f"(pick #{picks.index(pos)+1})"
        elif idx == len(path)-1:
            mark = "(end)"
        print(f"Step {idx:3d}: {pos} {mark}")

    # plot
    visualize_route(layout=layout,
                    path=path,
                    picks=picks,
                    title=f"{args.strategy.upper()} Route",
                    save_path=args.save,
                    annotate_every=max(1, args.annotate_every))


if __name__ == "__main__":
    main()
