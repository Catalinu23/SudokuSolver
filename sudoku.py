import os
import re
import sys

DIGITS = "123456789"

UNITS = (
    [[r * 9 + c for c in range(9)] for r in range(9)]
    + [[r * 9 + c for r in range(9)] for c in range(9)]
    + [[(br + a) * 9 + bc + b for a in range(3) for b in range(3)]
       for br in (0, 3, 6) for bc in (0, 3, 6)]
)
UNITS_OF = [[u for u in UNITS if i in u] for i in range(81)]
PEERS = [sorted(set().union(*UNITS_OF[i]) - {i}) for i in range(81)]


def parse(puzzle):
    puzzle = puzzle.strip().replace(".", "0")
    if len(puzzle) != 81:
        raise ValueError(f"expected 81 characters, got {len(puzzle)}")
    if not (puzzle.isascii() and puzzle.isdigit()):
        raise ValueError("puzzle may only contain digits and '.'")
    grid = [int(ch) for ch in puzzle]
    for i, d in enumerate(grid):
        if d and any(grid[p] == d for p in PEERS[i]):
            raise ValueError(f"duplicate {d} at row {i // 9 + 1}, column {i % 9 + 1}")
    return grid


def solve_naive(puzzle):
    grid = parse(puzzle)

    def fill(i):
        while i < 81 and grid[i]:
            i += 1
        if i == 81:
            return True
        for d in range(1, 10):
            if all(grid[p] != d for p in PEERS[i]):
                grid[i] = d
                if fill(i + 1):
                    return True
        grid[i] = 0
        return False

    return "".join(map(str, grid)) if fill(0) else None


def assign(cands, i, d, propagate):
    """Make d the value of cell i by ruling out everything else."""
    if d not in cands[i]:
        return False
    if not propagate:
        cands[i] = d
        return all(eliminate(cands, p, d, False) for p in PEERS[i])
    for other in cands[i].replace(d, ""):
        if not eliminate(cands, i, other, True):
            return False
    return True


def eliminate(cands, i, d, propagate):
    """Remove candidate d from cell i, optionally propagating the consequences."""
    if d not in cands[i]:
        return True
    cands[i] = cands[i].replace(d, "")
    remaining = cands[i]
    if not remaining:
        return False
    if not propagate:
        return True

    # Cell is down to one candidate: no peer may keep it.
    if len(remaining) == 1:
        for p in PEERS[i]:
            if not eliminate(cands, p, remaining, True):
                return False

    # Each unit must still have a home for d; if only one is left, put it there.
    for unit in UNITS_OF[i]:
        homes = [j for j in unit if d in cands[j]]
        if not homes:
            return False
        if len(homes) == 1 and not assign(cands, homes[0], d, True):
            return False
    return True


def search(cands, empty, propagate):
    if not empty:
        return cands
    i = min(empty, key=lambda j: len(cands[j]))
    rest = [j for j in empty if j != i]
    for d in cands[i]:
        attempt = cands.copy()
        if assign(attempt, i, d, propagate):
            result = search(attempt, rest, propagate)
            if result:
                return result
    return None


def solve(puzzle, propagate=True):
    grid = parse(puzzle)
    cands = [DIGITS] * 81
    for i, d in enumerate(grid):
        if d and not assign(cands, i, str(d), propagate):
            return None
    empty = [i for i in range(81) if not grid[i]]
    result = search(cands, empty, propagate)
    return "".join(result) if result else None


def format_grid(solution):
    lines = []
    for r in range(9):
        if r in (3, 6):
            lines.append("------+-------+------")
        row = solution[r * 9 : r * 9 + 9]
        lines.append(" | ".join(" ".join(row[c : c + 3]) for c in (0, 3, 6)))
    return "\n".join(lines)


def read_puzzles(path):
    with open(path) as f:
        text = f.read()
    if "=" in text:
        blocks = ["".join(block.split()) for block in re.split("=+", text)]
    else:
        blocks = [line.strip() for line in text.splitlines()]
    return [b for b in blocks if b]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python sudoku.py <puzzle-string | puzzle-file>")
    arg = sys.argv[1]
    puzzles = read_puzzles(arg) if os.path.isfile(arg) else [arg]

    for n, puzzle in enumerate(puzzles):
        if n:
            print()
        try:
            solution = solve(puzzle)
        except ValueError as e:
            print(f"Invalid puzzle: {e}")
            continue
        print(format_grid(solution) if solution else "No solution")


if __name__ == "__main__":
    main()
