from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Type aliases used throughout the project.
Player = str
Piece = Tuple[Player, int]   # (player, size)
Move = Tuple[int, int]       # (cell_index, size)


@dataclass(frozen=True)
class TicTacToe:
    """
    Represent the game state for the Gobblet Gobblers kids version.

    Rules implemented:
    - 3x3 board
    - each player has 2 small, 2 medium, and 2 large pieces
    - players place pieces only from their reserve
    - a larger piece may cover a smaller visible piece
    - once placed, pieces do not move
    """

    board: List[List[Piece]]
    next_player: Player
    reserves: Dict[Player, Dict[int, int]]

    SIZE = 3

    @staticmethod
    def new() -> "TicTacToe":
        """
        Create and return a new empty game state.
        """
        return TicTacToe(
            board=[[] for _ in range(9)],
            next_player="X",
            reserves={
                "X": {1: 2, 2: 2, 3: 2},
                "O": {1: 2, 2: 2, 3: 2},
            },
        )

    def top_piece(self, index: int) -> Optional[Piece]:
        """
        Return the visible top piece at a board cell.

        If the stack is empty, return None.
        """
        stack = self.board[index]
        return stack[-1] if stack else None

    def visible_owner(self, index: int) -> Optional[Player]:
        """
        Return the owner of the visible top piece at a cell.

        If the cell is empty, return None.
        """
        top = self.top_piece(index)
        return top[0] if top else None

    def visible_size(self, index: int) -> Optional[int]:
        """
        Return the size of the visible top piece at a cell.

        If the cell is empty, return None.
        """
        top = self.top_piece(index)
        return top[1] if top else None

    def can_place(self, size: int, cell: int) -> bool:
        """
        Return True if a piece of the given size can be placed on the cell.

        A move is legal when:
        - the target cell is inside the board
        - the cell is empty, or
        - the new piece is larger than the current visible top piece
        """
        if cell < 0 or cell >= 9:
            return False

        top = self.top_piece(cell)
        return top is None or size > top[1]

    def legal_moves(self) -> List[Move]:
        """
        Return all legal moves for the current player.

        A move is represented as:
        (cell_index, size)
        """
        moves: List[Move] = []
        stock = self.reserves[self.next_player]

        for size in (1, 2, 3):
            if stock[size] <= 0:
                continue

            for cell in range(9):
                if self.can_place(size, cell):
                    moves.append((cell, size))

        return moves

    def apply(self, move: Move) -> "TicTacToe":
        """
        Return a new game state after applying one move.

        This method does not mutate the current object. Instead, it creates
        and returns a new updated state.
        """
        cell, size = move

        if cell < 0 or cell >= 9:
            raise ValueError("Illegal move: cell out of range.")
        if size not in (1, 2, 3):
            raise ValueError("Illegal move: invalid piece size.")
        if self.reserves[self.next_player][size] <= 0:
            raise ValueError("Illegal move: no remaining piece of that size.")
        if not self.can_place(size, cell):
            raise ValueError("Illegal move: piece must be larger than the top piece.")

        # Copy the board so the current state remains unchanged.
        new_board = [stack.copy() for stack in self.board]
        new_board[cell].append((self.next_player, size))

        # Copy reserves and decrease the used piece count.
        new_reserves = {
            "X": self.reserves["X"].copy(),
            "O": self.reserves["O"].copy(),
        }
        new_reserves[self.next_player][size] -= 1

        # Switch turns after the move.
        next_turn = "O" if self.next_player == "X" else "X"

        return TicTacToe(
            board=new_board,
            next_player=next_turn,
            reserves=new_reserves,
        )

    def winning_line(self) -> Optional[Tuple[int, int, int]]:
        """
        Return the winning line if one exists.

        A player wins when the visible top pieces form a full row,
        column, or diagonal of the same owner.
        """
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

        for a, b, c in lines:
            owner_a = self.visible_owner(a)
            owner_b = self.visible_owner(b)
            owner_c = self.visible_owner(c)

            if owner_a is not None and owner_a == owner_b == owner_c:
                return (a, b, c)

        return None

    def winner(self) -> Optional[Player]:
        """
        Return the winning player if the game has been won.

        If no one has won, return None.
        """
        line = self.winning_line()
        if line is None:
            return None
        return self.visible_owner(line[0])

    def is_terminal(self) -> bool:
        """
        Return True if the game is over.

        The game ends when:
        - a player has won, or
        - no legal moves remain
        """
        return self.winner() is not None or len(self.legal_moves()) == 0