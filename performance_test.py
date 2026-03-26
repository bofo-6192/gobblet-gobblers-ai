from __future__ import annotations

import time

from ai_engine import AlphaBetaAI
from game_logic import TicTacToe


def time_ai(ai: AlphaBetaAI, n: int = 50) -> float:
    """
    Measure the average time taken by the AI to select a move.

    The benchmark uses the same initial empty board repeatedly so that
    timing remains consistent across runs.
    """
    state = TicTacToe.new()

    start = time.perf_counter()
    for _ in range(n):
        _ = ai.choose_move(state)
    end = time.perf_counter()

    return (end - start) / n


def main() -> None:
    """
    Run a simple benchmark for the alpha-beta AI and print the result.
    """
    n = 20
    ai = AlphaBetaAI(ai_player="X")
    average_time = time_ai(ai, n=n)

    print(f"Average time per AI move over {n} runs:")
    print(f"  Alpha-beta: {average_time:.6f} s")


if __name__ == "__main__":
    main()