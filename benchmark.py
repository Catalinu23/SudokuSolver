import os
import signal
import statistics
import time
from functools import partial

from sudoku import read_puzzles, solve, solve_naive

FILES = ["easy50.txt", "top95.txt", "hardest.txt"]
TIMEOUT = 5.0
SOLVERS = {
    "naive": solve_naive,
    "MRV only": partial(solve, propagate=False),
    "propagation": solve,
}


def on_alarm(signum, frame):
    raise TimeoutError


def timed(solver, puzzle):
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    start = time.perf_counter()
    try:
        solver(puzzle)
        return time.perf_counter() - start
    except TimeoutError:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    signal.signal(signal.SIGALRM, on_alarm)
    here = os.path.dirname(os.path.abspath(__file__))
    print("| Puzzle set | Solver | Avg (ms) | Median (ms) | Max (ms) | Timeouts |")
    print("|---|---|---:|---:|---:|---:|")
    for name in FILES:
        path = os.path.join(here, name)
        if not os.path.isfile(path):
            print(f"| {name} | missing, see the top of benchmark.py | | | | |")
            continue
        puzzles = read_puzzles(path)
        for label, solver in SOLVERS.items():
            times = [timed(solver, p) for p in puzzles]
            ms = [TIMEOUT * 1000 if t is None else t * 1000 for t in times]
            print(
                f"| {name} ({len(puzzles)}) | {label} | {statistics.mean(ms):.1f} "
                f"| {statistics.median(ms):.1f} | {max(ms):.1f} | {times.count(None)} |",
                flush=True,
            )


if __name__ == "__main__":
    main()
