from __future__ import annotations

import os
import tkinter as tk

from ai_engine import AlphaBetaAI
from game_logic import TicTacToe

# Pygame is used only for sound playback. If it is unavailable, the game
# falls back to the normal Tkinter bell sound.
try:
    import pygame

    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False


# -----------------------------
# UI colour palette
# -----------------------------
BG = "#f7f3ea"
WOOD = "#d4b06a"
BOARD_CELL = "#fffdf8"
BOARD_CELL_HOVER = "#f5ead3"
PANEL = "#efe3c7"
TEXT = "#3b2d1f"

BLUE = "#68c4ff"
BLUE_HAIR = "#ef8a38"

ORANGE = "#f4a259"
ORANGE_HAIR = "#7fc6ff"

MOUTH = "#111111"
SELECT = "#6bd6a8"
MOVE_HL = "#8de0b7"
WIN_HL = "#ffe86b"
BADGE = "#7c5a2d"


def load_sound(path: str):
    """
    Load and return a sound effect if pygame audio is available.

    If pygame is unavailable or the file does not exist, return None so the
    program can safely fall back to the standard bell sound.
    """
    if not PYGAME_AVAILABLE:
        return None
    if not os.path.exists(path):
        return None

    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None


# Load game sound effects once at startup.
CLICK_SOUND = load_sound(os.path.join("sounds", "click.wav"))
PLACE_SOUND = load_sound(os.path.join("sounds", "place.wav"))
WIN_SOUND = load_sound(os.path.join("sounds", "win.wav"))


class PieceWidget:
    """
    Visual widget representing one selectable reserve piece.

    Each piece belongs to either player X or O and has a size
    (small, medium, or large). The widget handles selection,
    hover behaviour, and drawing its visual appearance.
    """

    def __init__(self, canvas: tk.Canvas, owner: str, size: int, command):
        self.canvas = canvas
        self.owner = owner
        self.size = size
        self.command = command
        self.selected = False
        self.disabled = False

        self.canvas.bind("<Button-1>", self._click)
        self.canvas.bind("<Enter>", self._enter)
        self.canvas.bind("<Leave>", self._leave)
        self.draw()

    def _click(self, event) -> None:
        """Call the assigned command when the piece is clicked."""
        if not self.disabled:
            self.command(self.owner, self.size)

    def _enter(self, event) -> None:
        """Show a hand cursor while hovering over an active piece."""
        if not self.disabled:
            self.canvas.config(cursor="hand2")

    def _leave(self, event) -> None:
        """Restore the normal cursor when the mouse leaves the piece."""
        self.canvas.config(cursor="")

    def set_selected(self, selected: bool) -> None:
        """Update the selected state and redraw the widget."""
        self.selected = selected
        self.draw()

    def set_disabled(self, disabled: bool) -> None:
        """Update the disabled state and redraw the widget."""
        self.disabled = disabled
        self.draw()

    def draw(self) -> None:
        """
        Draw the piece as a toy-like character.

        The drawing changes depending on:
        - owner: X or O
        - size: 1, 2, or 3
        - selected/disabled state
        """
        canvas = self.canvas
        canvas.delete("all")
        canvas.configure(bg=PANEL, highlightthickness=0)

        border = SELECT if self.selected else "#d7c8a5"
        width = 4 if self.selected else 2
        fill_card = "#f8f0db" if not self.disabled else "#e8dcc0"

        canvas.create_rectangle(4, 4, 96, 136, outline=border, width=width, fill=fill_card)

        body = BLUE if self.owner == "X" else ORANGE
        hair = BLUE_HAIR if self.owner == "X" else ORANGE_HAIR

        if self.disabled:
            body = "#b9c4c9" if self.owner == "X" else "#ccb49d"
            hair = "#caa78a"

        if self.size == 1:
            x1, y1, x2, y2 = 28, 54, 72, 108
            hx1, hy1, hx2, hy2 = 44, 28, 58, 52
            eye_y = 72
            mouth_y1, mouth_y2 = 80, 99
        elif self.size == 2:
            x1, y1, x2, y2 = 22, 42, 78, 112
            hx1, hy1, hx2, hy2 = 42, 18, 58, 42
            eye_y = 65
            mouth_y1, mouth_y2 = 76, 103
        else:
            x1, y1, x2, y2 = 16, 26, 84, 116
            hx1, hy1, hx2, hy2 = 40, 8, 60, 30
            eye_y = 56
            mouth_y1, mouth_y2 = 70, 107

        # Character body
        canvas.create_oval(x1, y1, x2, y2, fill=body, outline="")
        canvas.create_rectangle(x1, (y1 + y2) / 2, x2, y2, fill=body, outline="")

        # Hair / top tuft
        canvas.create_oval(hx1, hy1, hx2, hy2, fill=hair, outline="")
        canvas.create_polygon(
            (hx1 + hx2) / 2, hy1 - 4,
            hx2 + 6, hy1 + 6,
            hx1 + 6, hy2,
            fill=hair, outline="",
        )

        # Eyes
        canvas.create_oval(35, eye_y, 58, eye_y + 16, fill="white", outline="")
        canvas.create_oval(48, eye_y - 2, 69, eye_y + 14, fill="white", outline="")
        canvas.create_oval(46, eye_y + 5, 50, eye_y + 9, fill="#333", outline="")
        canvas.create_oval(57, eye_y + 4, 61, eye_y + 8, fill="#333", outline="")

        # Mouth / teeth
        canvas.create_oval(32, mouth_y1, 68, mouth_y2, fill=MOUTH, outline="")
        canvas.create_rectangle(32, mouth_y1 - 4, 68, (mouth_y1 + mouth_y2) / 2, fill=body, outline="")
        canvas.create_rectangle(48, mouth_y2 - 8, 54, mouth_y2, fill="white", outline="")

        # Size badge
        canvas.create_text(50, 126, text=f"{self.size}", font=("Segoe UI", 12, "bold"), fill=BADGE)


class GameUI:
    """
    Main graphical application for Gobblet Gobblers.

    Responsibilities:
    - build menus and game screens
    - handle player interaction
    - coordinate AI turns
    - animate placed pieces
    - play sounds and update scores
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Gobblet Gobblers")
        self.root.state("zoomed")
        self.root.configure(bg=BG)
        self.root.minsize(1260, 780)

        # Load a custom application icon if available.
        if os.path.exists("icon.png"):
            try:
                icon = tk.PhotoImage(file="icon.png")
                self.root.iconphoto(True, icon)
                self.root._icon_ref = icon  # Keep a reference so Tk does not discard it.
            except Exception:
                pass

        self.mode = "AI"
        self.human = "X"
        self.difficulty = "medium"
        self.ai = AlphaBetaAI("O", self.difficulty)

        self.state = TicTacToe.new()
        self.selected_piece: tuple[str, int] | None = None
        self.game_over = False
        self.fullscreen = False

        # Scoreboard across games in the same session.
        self.score = {"X": 0, "O": 0, "Draw": 0}

        # Board drawing metadata.
        self.board_piece_items: list[list[int] | None] = [None] * 9
        self.cell_rect_ids: list[int] = []
        self.cell_centers: list[tuple[int, int]] = []
        self.cell_index_by_rect: dict[int, int] = {}

        self.root.bind("<Escape>", self.toggle_fullscreen)
        self.show_menu()

    def toggle_fullscreen(self, event=None) -> None:
        """Toggle fullscreen mode when Escape is pressed."""
        self.fullscreen = not self.fullscreen
        try:
            self.root.attributes("-fullscreen", self.fullscreen)
        except Exception:
            pass

    def play_sound(self, snd) -> None:
        """
        Play a sound effect if available.

        Falls back to the standard window bell if no external sound
        could be loaded.
        """
        if snd is not None:
            try:
                snd.play()
                return
            except Exception:
                pass

        try:
            self.root.bell()
        except Exception:
            pass

    def clear(self) -> None:
        """Remove all current widgets from the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def button(self, parent, text, command, bg="#8d6e3f", width=16):
        """
        Create a consistently styled button used throughout the app.
        """
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 14, "bold"),
            bg=bg,
            fg="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
            width=width,
            activebackground=bg,
            activeforeground="white",
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.lighten_color(bg)))
        btn.bind("<Leave>", lambda e, b=btn, color=bg: b.config(bg=color))
        return btn

    def lighten_color(self, color: str) -> str:
        """Return a lighter hover version of predefined button colours."""
        table = {
            "#8d6e3f": "#a37a47",
            "#6d8f52": "#7ea55f",
            "#cf7a44": "#df8850",
            "#9b4d4d": "#af5b5b",
            "#5ab2e8": "#71c0f0",
            "#ef9652": "#f4a86e",
        }
        return table.get(color, color)

    def show_menu(self) -> None:
        """Display the main menu screen."""
        self.clear()

        box = tk.Frame(self.root, bg=BG)
        box.pack(expand=True)

        tk.Label(
            box,
            text="Gobblet Gobblers",
            font=("Segoe UI", 38, "bold"),
            bg=BG,
            fg="#2b2115",
        ).pack(pady=(20, 8))

        tk.Label(
            box,
            text="Pick a side piece, then place it on the board. Bigger pieces can cover smaller ones.",
            font=("Segoe UI", 15),
            bg=BG,
            fg="#6b5b47",
        ).pack(pady=(0, 28))

        card = tk.Frame(box, bg=PANEL, padx=30, pady=30)
        card.pack()

        self.button(card, "Play vs AI", self.show_ai_menu, bg="#6d8f52", width=18).pack(pady=8)
        self.button(card, "Play vs Friend", self.start_pvp, bg="#cf7a44", width=18).pack(pady=8)
        self.button(card, "Exit", self.root.destroy, bg="#9b4d4d", width=18).pack(pady=8)

    def show_ai_menu(self) -> None:
        """Display the menu used to configure AI side and difficulty."""
        self.clear()

        box = tk.Frame(self.root, bg=BG)
        box.pack(expand=True)

        tk.Label(
            box,
            text="AI Settings",
            font=("Segoe UI", 34, "bold"),
            bg=BG,
            fg=TEXT,
        ).pack(pady=(20, 10))

        tk.Label(
            box,
            text="Choose your side and difficulty.",
            font=("Segoe UI", 15),
            bg=BG,
            fg="#6b5b47",
        ).pack(pady=(0, 24))

        side_frame = tk.Frame(box, bg=BG)
        side_frame.pack(pady=10)

        self.button(side_frame, "Play Blue (X)", lambda: self.choose_side("X"), bg="#5ab2e8").pack(side="left", padx=10)
        self.button(side_frame, "Play Orange (O)", lambda: self.choose_side("O"), bg="#ef9652").pack(side="left", padx=10)

        diff_card = tk.Frame(box, bg=PANEL, padx=22, pady=18)
        diff_card.pack(pady=20)

        tk.Label(
            diff_card,
            text="Difficulty",
            font=("Segoe UI", 18, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).pack(pady=(0, 10))

        diff_row = tk.Frame(diff_card, bg=PANEL)
        diff_row.pack()

        for diff in ("easy", "medium", "hard"):
            bg = "#6d8f52" if self.difficulty == diff else "#8d6e3f"
            self.button(
                diff_row,
                diff.title(),
                lambda d=diff: self.set_difficulty(d),
                bg=bg,
                width=10,
            ).pack(side="left", padx=6)

        self.button(box, "Back", self.show_menu, bg="#8d6e3f", width=12).pack(pady=16)

    def set_difficulty(self, difficulty: str) -> None:
        """Update difficulty and refresh the AI setup screen."""
        self.difficulty = difficulty
        self.show_ai_menu()

    def choose_side(self, side: str) -> None:
        """Start AI mode and assign the human and AI sides."""
        self.mode = "AI"
        self.human = side
        self.ai = AlphaBetaAI("O" if side == "X" else "X", self.difficulty)
        self.start_game()

    def start_pvp(self) -> None:
        """Start player-versus-player mode."""
        self.mode = "PVP"
        self.start_game()

    def start_game(self) -> None:
        """Create a fresh game board and display the main gameplay screen."""
        self.state = TicTacToe.new()
        self.selected_piece = None
        self.game_over = False
        self.clear()

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=20, pady=12)

        left = tk.Frame(top, bg=BG)
        left.pack(side="left")

        tk.Label(
            left,
            text="Gobblet Gobblers",
            font=("Segoe UI", 30, "bold"),
            bg=BG,
            fg="#2b2115",
        ).pack(anchor="w")

        self.status_label = tk.Label(
            left,
            text="",
            font=("Segoe UI", 14),
            bg=BG,
            fg="#6b5b47",
        )
        self.status_label.pack(anchor="w")

        self.score_label = tk.Label(
            left,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg=BG,
            fg="#7a5f2f",
        )
        self.score_label.pack(anchor="w", pady=(4, 0))

        right = tk.Frame(top, bg=BG)
        right.pack(side="right")

        self.button(right, "New Game", self.start_game, bg="#6d8f52", width=10).pack(side="left", padx=5)
        self.button(right, "Menu", self.show_menu, bg="#8d6e3f", width=10).pack(side="left", padx=5)

        body = tk.Frame(self.root, bg=BG)
        body.pack(expand=True, fill="both", padx=18, pady=8)

        self.left_panel = tk.Frame(body, bg=PANEL, padx=14, pady=14)
        self.left_panel.pack(side="left", fill="y", padx=(0, 15))

        center = tk.Frame(body, bg=BG)
        center.pack(side="left", expand=True)

        self.right_panel = tk.Frame(body, bg=PANEL, padx=14, pady=14)
        self.right_panel.pack(side="left", fill="y", padx=(15, 0))

        self.build_side_panel(self.left_panel, "X", "Blue Pieces")
        self.build_board(center)
        self.build_side_panel(self.right_panel, "O", "Orange Pieces")

        self.info_label = tk.Label(
            center,
            text="Pick a piece from the current player's side.",
            font=("Segoe UI", 13),
            bg=BG,
            fg="#6b5b47",
        )
        self.info_label.pack(pady=(10, 0))

        self.update_ui()

        # If the AI starts, schedule its opening move.
        if self.mode == "AI" and self.state.next_player == self.ai.ai_player:
            self.root.after(450, self.ai_move)

    def build_side_panel(self, parent: tk.Frame, owner: str, title: str) -> None:
        """
        Build the reserve-piece panel for one player.

        This panel shows the available small, medium, and large pieces,
        along with how many remain.
        """
        tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 18, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).pack(pady=(0, 6))

        tk.Label(
            parent,
            text="Click one to pick it up",
            font=("Segoe UI", 11),
            bg=PANEL,
            fg="#7a694f",
        ).pack(pady=(0, 10))

        container = tk.Frame(parent, bg=PANEL)
        container.pack()

        widgets = {}
        counts = {}

        for size in (3, 2, 1):
            row = tk.Frame(container, bg=PANEL)
            row.pack(pady=10)

            tk.Label(
                row,
                text={1: "Small", 2: "Medium", 3: "Large"}[size],
                font=("Segoe UI", 12, "bold"),
                bg=PANEL,
                fg=TEXT,
                width=8,
            ).pack()

            pieces_row = tk.Frame(row, bg=PANEL)
            pieces_row.pack()

            widgets[size] = []
            for _ in range(2):
                canvas = tk.Canvas(pieces_row, width=100, height=140, bg=PANEL, highlightthickness=0)
                canvas.pack(side="left", padx=4)
                piece_widget = PieceWidget(canvas, owner, size, self.select_piece_from_side)
                widgets[size].append(piece_widget)

            count_label = tk.Label(
                row,
                text="2 left",
                font=("Segoe UI", 11),
                bg=PANEL,
                fg="#7a694f",
            )
            count_label.pack(pady=(4, 0))
            counts[size] = count_label

        if owner == "X":
            self.left_piece_widgets = widgets
            self.left_count_labels = counts
        else:
            self.right_piece_widgets = widgets
            self.right_count_labels = counts

    def build_board(self, parent: tk.Frame) -> None:
        """
        Build the central 3x3 game board using a Canvas.
        """
        wrap = tk.Frame(parent, bg=BG)
        wrap.pack(expand=True)

        self.board_canvas = tk.Canvas(wrap, width=640, height=640, bg=BG, highlightthickness=0)
        self.board_canvas.pack()

        self.cell_rect_ids = []
        self.cell_centers = []
        self.cell_index_by_rect = {}
        self.board_piece_items = [None] * 9

        x0, y0, size = 80, 80, 480
        cell = size // 3

        self.board_canvas.create_rectangle(x0, y0, x0 + size, y0 + size, width=8, outline=WOOD)
        for i in range(1, 3):
            self.board_canvas.create_line(x0 + i * cell, y0, x0 + i * cell, y0 + size, width=8, fill=WOOD)
            self.board_canvas.create_line(x0, y0 + i * cell, x0 + size, y0 + i * cell, width=8, fill=WOOD)

        for r in range(3):
            for c in range(3):
                cx = x0 + c * cell + cell // 2
                cy = y0 + r * cell + cell // 2
                idx = r * 3 + c

                rect = self.board_canvas.create_rectangle(
                    x0 + c * cell + 8,
                    y0 + r * cell + 8,
                    x0 + (c + 1) * cell - 8,
                    y0 + (r + 1) * cell - 8,
                    fill=BOARD_CELL,
                    outline="",
                    width=0,
                )
                self.cell_rect_ids.append(rect)
                self.cell_centers.append((cx, cy))
                self.cell_index_by_rect[rect] = idx

                self.board_canvas.tag_bind(rect, "<Button-1>", lambda e, i=idx: self.on_board_click(i))
                self.board_canvas.tag_bind(rect, "<Enter>", lambda e, rect_id=rect: self.on_cell_enter(rect_id))
                self.board_canvas.tag_bind(rect, "<Leave>", lambda e, rect_id=rect: self.on_cell_leave(rect_id))

    def on_cell_enter(self, rect_id: int) -> None:
        """Highlight a playable cell while the mouse hovers over it."""
        if self.game_over:
            return

        index = self.cell_index_by_rect[rect_id]
        self.board_canvas.config(cursor="hand2")

        if self.selected_piece is not None:
            size = self.selected_piece[1]
            if (index, size) in self.state.legal_moves():
                self.board_canvas.itemconfig(rect_id, fill=BOARD_CELL_HOVER)

    def on_cell_leave(self, rect_id: int) -> None:
        """Restore the normal board cell appearance after hover."""
        self.board_canvas.config(cursor="")
        self.board_canvas.itemconfig(rect_id, fill=BOARD_CELL)

    def player_name(self, player: str) -> str:
        """Return the display name used in the UI for each player."""
        return "Blue" if player == "X" else "Orange"

    def select_piece_from_side(self, owner: str, size: int) -> None:
        """
        Select a reserve piece for placement.

        Selection is allowed only if:
        - the game is still running
        - it is that player's turn
        - the piece still exists in reserve
        - the human is selecting their own piece in AI mode
        """
        if self.game_over:
            return
        if owner != self.state.next_player:
            return
        if self.mode == "AI" and owner != self.human:
            return
        if self.state.reserves[owner][size] <= 0:
            return

        self.selected_piece = (owner, size)
        self.play_sound(CLICK_SOUND)
        self.update_ui()

    def on_board_click(self, index: int) -> None:
        """
        Attempt to place the currently selected reserve piece on the board.
        """
        if self.game_over:
            return
        if self.selected_piece is None:
            return
        if self.mode == "AI" and self.state.next_player != self.human:
            return

        owner, size = self.selected_piece
        if owner != self.state.next_player:
            return

        move = (index, size)
        if move not in self.state.legal_moves():
            self.play_sound(CLICK_SOUND)
            self.info_label.config(text="That piece cannot go there. Bigger pieces only.")
            return

        old_state = self.state
        new_state = self.state.apply(move)

        self.play_sound(PLACE_SOUND)
        self.selected_piece = None
        self.animate_placement(old_state, new_state, index)

    def animate_placement(self, old_state: TicTacToe, new_state: TicTacToe, target: int) -> None:
        """
        Animate a newly placed piece by scaling it into view.
        """
        self.state = old_state
        self.redraw_board(skip_cell=target)
        self.highlight_cells()

        owner, size = new_state.top_piece(target)
        cx, cy = self.cell_centers[target]
        steps = 12

        def draw_step(step: int) -> None:
            self.redraw_board(skip_cell=target)
            scale = 0.50 + (0.50 * step / steps)
            temp_items = self.draw_piece_on_board(cx, cy, owner, size, 0, scale_override=scale)

            if step < steps:
                self.root.after(20, lambda: draw_step(step + 1))
            else:
                for item in temp_items:
                    self.board_canvas.delete(item)
                self.state = new_state
                self.after_move()

        draw_step(1)

    def after_move(self) -> None:
        """
        Handle all post-move updates:
        - check for winner
        - check for draw
        - update scoreboard
        - pass control to AI if needed
        """
        winner = self.state.winner()
        if winner is not None:
            self.game_over = True
            self.score[winner] += 1
            self.play_sound(WIN_SOUND)
            self.update_ui()
            self.show_end_dialog(f"{self.player_name(winner)} wins!")
            return

        if self.state.is_terminal():
            self.game_over = True
            self.score["Draw"] += 1
            self.play_sound(CLICK_SOUND)
            self.update_ui()
            self.show_end_dialog("Draw!")
            return

        self.update_ui()

        if self.mode == "AI" and self.state.next_player == self.ai.ai_player:
            self.root.after(450, self.ai_move)

    def ai_move(self) -> None:
        """Ask the AI to choose and play its move."""
        if self.game_over:
            return
        if self.state.next_player != self.ai.ai_player:
            return

        self.status_label.config(
            text=f"{self.player_name(self.ai.ai_player)} is thinking... ({self.difficulty.title()})"
        )
        self.root.update_idletasks()

        old_state = self.state
        move = self.ai.choose_move(self.state)
        new_state = self.state.apply(move)
        target, _size = move

        self.play_sound(PLACE_SOUND)
        self.animate_placement(old_state, new_state, target)

    def update_piece_panel(self, owner: str, widgets_map, counts_map) -> None:
        """
        Update reserve piece widgets and remaining-piece counters.
        """
        reserves = self.state.reserves[owner]
        active_turn = self.state.next_player == owner and not self.game_over
        selected_size = self.selected_piece[1] if self.selected_piece and self.selected_piece[0] == owner else None

        for size in (1, 2, 3):
            remaining = reserves[size]
            counts_map[size].config(text=f"{remaining} left")

            for i, widget in enumerate(widgets_map[size]):
                widget.set_disabled(i >= remaining or not active_turn)
                widget.set_selected(active_turn and selected_size == size and i == 0 and remaining > 0)

    def draw_piece_on_board(
        self,
        cx: int,
        cy: int,
        owner: str,
        size: int,
        hidden_count: int,
        scale_override: float = 1.0,
    ) -> list[int]:
        """
        Draw a board piece at the given position and return the canvas item ids.
        """
        body = BLUE if owner == "X" else ORANGE
        hair = BLUE_HAIR if owner == "X" else ORANGE_HAIR

        if size == 1:
            w, h = 52, 72
            eye_y = cy - 6
            mouth_top = cy + 8
            hair_top = cy - 52
            hair_size = 14
        elif size == 2:
            w, h = 72, 98
            eye_y = cy - 10
            mouth_top = cy + 14
            hair_top = cy - 66
            hair_size = 17
        else:
            w, h = 92, 124
            eye_y = cy - 14
            mouth_top = cy + 20
            hair_top = cy - 82
            hair_size = 20

        w *= scale_override
        h *= scale_override
        hair_size *= scale_override

        items: list[int] = []

        items.append(self.board_canvas.create_oval(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=body, outline=""))
        items.append(self.board_canvas.create_rectangle(cx - w / 2, cy, cx + w / 2, cy + h / 2, fill=body, outline=""))

        hair_top_scaled = hair_top * scale_override + cy * (1 - scale_override)
        eye_y_scaled = eye_y * scale_override + cy * (1 - scale_override)
        mouth_top_scaled = mouth_top * scale_override + cy * (1 - scale_override)

        items.append(self.board_canvas.create_oval(
            cx - 8 * scale_override, hair_top_scaled,
            cx + 8 * scale_override, hair_top_scaled + hair_size,
            fill=hair, outline=""
        ))
        items.append(self.board_canvas.create_polygon(
            cx, hair_top_scaled - 6 * scale_override,
            cx + 12 * scale_override, hair_top_scaled + 4 * scale_override,
            cx + 2 * scale_override, hair_top_scaled + hair_size,
            fill=hair, outline=""
        ))

        items.append(self.board_canvas.create_oval(
            cx - 18 * scale_override, eye_y_scaled,
            cx + 4 * scale_override, eye_y_scaled + 16 * scale_override,
            fill="white", outline=""
        ))
        items.append(self.board_canvas.create_oval(
            cx - 2 * scale_override, eye_y_scaled - 2 * scale_override,
            cx + 20 * scale_override, eye_y_scaled + 14 * scale_override,
            fill="white", outline=""
        ))
        items.append(self.board_canvas.create_oval(
            cx - 8 * scale_override, eye_y_scaled + 5 * scale_override,
            cx - 3 * scale_override, eye_y_scaled + 10 * scale_override,
            fill="#333", outline=""
        ))
        items.append(self.board_canvas.create_oval(
            cx + 4 * scale_override, eye_y_scaled + 4 * scale_override,
            cx + 9 * scale_override, eye_y_scaled + 9 * scale_override,
            fill="#333", outline=""
        ))

        items.append(self.board_canvas.create_oval(
            cx - 22 * scale_override, mouth_top_scaled,
            cx + 22 * scale_override, mouth_top_scaled + 32 * scale_override,
            fill=MOUTH, outline=""
        ))
        items.append(self.board_canvas.create_rectangle(
            cx - 22 * scale_override, mouth_top_scaled - 5 * scale_override,
            cx + 22 * scale_override, mouth_top_scaled + 12 * scale_override,
            fill=body, outline=""
        ))
        items.append(self.board_canvas.create_rectangle(
            cx - 3 * scale_override, mouth_top_scaled + 24 * scale_override,
            cx + 3 * scale_override, mouth_top_scaled + 32 * scale_override,
            fill="white", outline=""
        ))

        if hidden_count > 0 and scale_override >= 0.95:
            items.append(self.board_canvas.create_text(
                cx, cy + h / 2 + 14,
                text=f"{hidden_count} under",
                font=("Segoe UI", 10, "bold"),
                fill="#8a7140",
            ))

        return items

    def redraw_board(self, skip_cell: int | None = None) -> None:
        """
        Redraw all visible top pieces on the board.

        The optional skip_cell parameter is used during placement animation
        so the animated piece can be drawn separately.
        """
        for items in self.board_piece_items:
            if items:
                for item in items:
                    self.board_canvas.delete(item)

        self.board_piece_items = [None] * 9

        for i in range(9):
            if skip_cell is not None and i == skip_cell:
                continue

            top = self.state.top_piece(i)
            if top is None:
                continue

            owner, size = top
            hidden_count = len(self.state.board[i]) - 1
            cx, cy = self.cell_centers[i]
            self.board_piece_items[i] = self.draw_piece_on_board(cx, cy, owner, size, hidden_count)

    def highlight_cells(self) -> None:
        """
        Highlight:
        - the winning line, if one exists
        - or the currently valid target cells for the selected piece
        """
        legal = set(self.state.legal_moves())
        selected_size = self.selected_piece[1] if self.selected_piece else None
        win_line = self.state.winning_line()

        for i, rect in enumerate(self.cell_rect_ids):
            outline = ""
            width = 0

            if win_line is not None and i in win_line:
                outline = WIN_HL
                width = 6
            elif selected_size is not None and (i, selected_size) in legal:
                outline = MOVE_HL
                width = 4

            self.board_canvas.itemconfig(rect, outline=outline, width=width)

    def update_ui(self) -> None:
        """
        Refresh all dynamic UI elements:
        - status text
        - score text
        - selection text
        - reserve panels
        - board pieces
        - cell highlights
        """
        if self.mode == "PVP":
            self.status_label.config(text=f"Turn: {self.player_name(self.state.next_player)}")
        else:
            if self.state.next_player == self.human:
                self.status_label.config(
                    text=f"Your turn: {self.player_name(self.human)} ({self.difficulty.title()})"
                )
            else:
                self.status_label.config(
                    text=f"AI turn: {self.player_name(self.ai.ai_player)} ({self.difficulty.title()})"
                )

        self.score_label.config(
            text=f"Score  Blue: {self.score['X']}   Orange: {self.score['O']}   Draws: {self.score['Draw']}"
        )

        if self.selected_piece is None:
            self.info_label.config(text="Pick a piece from the current player's side.")
        else:
            owner, size = self.selected_piece
            label = ["", "Small", "Medium", "Large"][size]
            self.info_label.config(text=f"Selected: {self.player_name(owner)} {label}")

        self.update_piece_panel("X", self.left_piece_widgets, self.left_count_labels)
        self.update_piece_panel("O", self.right_piece_widgets, self.right_count_labels)
        self.redraw_board()
        self.highlight_cells()

    def show_end_dialog(self, message: str) -> None:
        """
        Display the end-of-game popup window with score summary.
        """
        win = tk.Toplevel(self.root)
        win.title("Game Over")
        win.transient(self.root)
        win.grab_set()
        win.configure(bg=BG)
        win.resizable(False, False)

        card = tk.Frame(win, bg=PANEL, padx=28, pady=28)
        card.pack(padx=14, pady=14)

        tk.Label(
            card,
            text=message,
            font=("Segoe UI", 26, "bold"),
            bg=PANEL,
            fg=TEXT,
        ).pack(pady=(0, 10))

        tk.Label(
            card,
            text=f"Blue: {self.score['X']}   Orange: {self.score['O']}   Draws: {self.score['Draw']}",
            font=("Segoe UI", 13, "bold"),
            bg=PANEL,
            fg="#7a5f2f",
        ).pack(pady=(0, 16))

        row = tk.Frame(card, bg=PANEL)
        row.pack()

        self.button(row, "Play Again", lambda: [win.destroy(), self.start_game()], bg="#6d8f52", width=12).pack(side="left", padx=6)
        self.button(row, "Menu", lambda: [win.destroy(), self.show_menu()], bg="#8d6e3f", width=12).pack(side="left", padx=6)


def main() -> None:
    """Application entry point."""
    root = tk.Tk()
    GameUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    