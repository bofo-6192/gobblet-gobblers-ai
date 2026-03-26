from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from game_logic import Move, Player, TicTacToe

# A terminal win must be much larger than any heuristic score so that
# guaranteed wins/losses always take priority over estimated positions.
WIN_SCORE = 10000


def ordered_moves(state: TicTacToe) -> list[Move]:
    """
    Return legal moves in a preferred search order.

    The AI searches the centre first, then corners, then edges.
    For each cell, larger pieces are considered before smaller ones.
    This ordering can improve alpha-beta pruning efficiency by exploring
    stronger candidate moves earlier.
    """
    preferred_cells = [4, 0, 2, 6, 8, 1, 3, 5, 7]
    legal = set(state.legal_moves())

    ordered: list[Move] = []
    for cell in preferred_cells:
        for size in (3, 2, 1):
            move = (cell, size)
            if move in legal:
                ordered.append(move)

    return ordered


def line_score(owners: list[Optional[str]], perspective: Player) -> int:
    """
    Evaluate a single line of three visible top pieces.

    A line contributes positively if it is favourable to the AI player,
    negatively if it is favourable to the opponent, and zero if both
    players already appear in the same line.

    Examples:
    - [X, None, None] gives a small positive score for X
    - [X, X, None] gives a larger positive score for X
    - [X, O, None] gives 0 because the line is blocked
    """
    opponent = "O" if perspective == "X" else "X"

    # A mixed line cannot become a clean winning line for either side.
    if perspective in owners and opponent in owners:
        return 0

    player_count = owners.count(perspective)
    opponent_count = owners.count(opponent)
    empty_count = owners.count(None)

    if player_count > 0 and opponent_count == 0:
        if player_count == 1 and empty_count == 2:
            return 8
        if player_count == 2 and empty_count == 1:
            return 60
        if player_count == 3:
            return 500

    if opponent_count > 0 and player_count == 0:
        if opponent_count == 1 and empty_count == 2:
            return -8
        if opponent_count == 2 and empty_count == 1:
            return -70
        if opponent_count == 3:
            return -500

    return 0


def heuristic(state: TicTacToe, perspective: Player) -> int:
    """
    Estimate the strength of a non-terminal position.

    The heuristic combines:
    1. Visible alignment potential across rows, columns, and diagonals
    2. The sizes of visible top pieces
    3. Remaining reserve pieces for both players

    Positive values favour the given perspective player.
    Negative values favour the opponent.
    """
    score = 0

    lines = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ]

    # Evaluate strategic control of each possible winning line.
    for a, b, c in lines:
        owners = [
            state.visible_owner(a),
            state.visible_owner(b),
            state.visible_owner(c),
        ]
        score += line_score(owners, perspective)

    # Reward larger visible pieces on the board because they exert
    # stronger control and are harder to cover.
    for i in range(9):
        top = state.top_piece(i)
        if top is None:
            continue

        owner, size = top
        if owner == perspective:
            score += size * 3
        else:
            score -= size * 3

    # Reward reserve advantage. Having more remaining pieces gives
    # more future options and flexibility.
    opponent = "O" if perspective == "X" else "X"
    for size in (1, 2, 3):
        score += state.reserves[perspective][size] * size
        score -= state.reserves[opponent][size] * size

    return score


def alphabeta_value(
    state: TicTacToe,
    depth: int,
    alpha: int,
    beta: int,
    perspective: Player,
    max_depth: int,
) -> int:
    """
    Compute the minimax value of a state using alpha-beta pruning.

    Parameters:
    - state: current game state
    - depth: current search depth
    - alpha: best guaranteed value for the maximizing side so far
    - beta: best guaranteed value for the minimizing side so far
    - perspective: the player for whom the evaluation is being performed
    - max_depth: depth limit for the search

    Returns:
    - A large positive value for winning states
    - A large negative value for losing states
    - A heuristic estimate for non-terminal states at the depth limit
    """
    winner = state.winner()

    # Terminal winning positions use exact scores, not heuristic values.
    # Depth is included so that faster wins and slower losses are preferred.
    if winner is not None:
        if winner == perspective:
            return WIN_SCORE - depth
        return -WIN_SCORE + depth

    # Terminal draw
    if state.is_terminal():
        return 0

    # At the depth limit, estimate the position instead of searching deeper.
    if depth >= max_depth:
        return heuristic(state, perspective)

    maximizing = state.next_player == perspective

    if maximizing:
        value = -10**9
        for move in ordered_moves(state):
            child = state.apply(move)
            value = max(
                value,
                alphabeta_value(child, depth + 1, alpha, beta, perspective, max_depth),
            )
            alpha = max(alpha, value)

            # Prune branches that cannot affect the final choice.
            if alpha >= beta:
                break

        return value

    value = 10**9
    for move in ordered_moves(state):
        child = state.apply(move)
        value = min(
            value,
            alphabeta_value(child, depth + 1, alpha, beta, perspective, max_depth),
        )
        beta = min(beta, value)

        # Prune branches that cannot improve the result.
        if alpha >= beta:
            break

    return value


def best_move_alphabeta(
    state: TicTacToe,
    player: Player,
    max_depth: int,
) -> Optional[Move]:
    """
    Return the best move for the given player using alpha-beta search.

    If the game is already over or no move exists, return None.
    """
    if state.is_terminal():
        return None

    moves = ordered_moves(state)
    if not moves:
        return None

    best_move: Optional[Move] = None
    alpha = -10**9
    beta = 10**9
    best_value = -10**9

    for move in moves:
        value = alphabeta_value(
            state.apply(move),
            1,
            alpha,
            beta,
            player,
            max_depth,
        )

        if value > best_value:
            best_value = value
            best_move = move

        alpha = max(alpha, best_value)

    return best_move


@dataclass
class AlphaBetaAI:
    """
    AI agent that chooses moves using alpha-beta pruning.

    Attributes:
    - ai_player: the side controlled by the AI ("X" or "O")
    - difficulty: search difficulty level
    """
    ai_player: Player = "X"
    difficulty: str = "medium"

    def search_depth(self) -> int:
        """
        Return the search depth based on the selected difficulty level.
        """
        return {
            "easy": 2,
            "medium": 4,
            "hard": 6,
        }.get(self.difficulty, 4)

    def choose_move(self, state: TicTacToe) -> Move:
        """
        Select and return the best move for the current game state.

        Raises:
        - ValueError if the game is already over
        - ValueError if it is not the AI's turn
        - ValueError if no legal move is found
        """
        if state.is_terminal():
            raise ValueError("Game is already over.")

        if state.next_player != self.ai_player:
            raise ValueError("It is not the AI's turn.")

        move = best_move_alphabeta(state, self.ai_player, self.search_depth())
        if move is None:
            raise ValueError("No legal move found.")

        return move