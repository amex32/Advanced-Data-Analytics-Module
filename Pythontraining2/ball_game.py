import tkinter as tk
from tkinter import font as tkfont
import math

# ── Constants ──────────────────────────────────────────────────────────────────
SIZE        = 5
WIN_LENGTH  = 4
CELL_SIZE   = 90
CELL_PAD    = 12
BOARD_PAD   = 20
ANIM_STEPS  = 12
ANIM_DELAY  = 18   # ms per animation frame

COLORS = {
    "bg":           "#0d0f18",
    "board_bg":     "#141625",
    "board_border": "#252840",
    "cell_empty":   "#1c1f35",
    "cell_border":  "#2d3154",
    "cell_hover":   "#252a45",
    "p1_outer":     "#c0392b",
    "p1_inner":     "#ff6b6b",
    "p1_shine":     "#ffaaaa",
    "p2_outer":     "#1565c0",
    "p2_inner":     "#42a5f5",
    "p2_shine":     "#90caf9",
    "win_glow_p1":  "#ff4444",
    "win_glow_p2":  "#2196f3",
    "text_primary": "#e8eaf6",
    "text_muted":   "#7986cb",
    "panel_bg":     "#141625",
    "panel_border": "#252840",
    "active_p1":    "#3d1520",
    "active_p2":    "#0d2040",
    "btn_bg":       "#1e2130",
    "btn_hover":    "#2a2e4a",
    "btn_border":   "#3d4275",
}

# ── Utility ────────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

# ── Main App ───────────────────────────────────────────────────────────────────

class CircleDropGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Circle Drop — 2 Player")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        self._setup_fonts()
        self._build_ui()
        self._new_game()

    # ── Fonts ──────────────────────────────────────────────────────────────────

    def _setup_fonts(self):
        self.f_title  = tkfont.Font(family="Segoe UI",      size=18, weight="bold")
        self.f_player = tkfont.Font(family="Segoe UI",      size=13, weight="bold")
        self.f_label  = tkfont.Font(family="Segoe UI",      size=10)
        self.f_status = tkfont.Font(family="Segoe UI",      size=12, weight="bold")
        self.f_btn    = tkfont.Font(family="Segoe UI",      size=11, weight="bold")
        self.f_badge  = tkfont.Font(family="Courier New",   size=10, weight="bold")

    # ── UI Build ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = tk.Frame(self, bg=COLORS["bg"])
        outer.pack(padx=24, pady=20)

        # Title
        tk.Label(outer, text="◉  CIRCLE DROP", font=self.f_title,
                 bg=COLORS["bg"], fg=COLORS["text_primary"]).pack(pady=(0, 16))

        # Scoreboard
        self.score_frame = tk.Frame(outer, bg=COLORS["bg"])
        self.score_frame.pack(fill="x", pady=(0, 14))

        self.card1 = self._make_player_card(self.score_frame, 1)
        self.card1.pack(side="left", padx=(0, 8))

        self.turn_badge = tk.Label(self.score_frame, text="▶  Red's turn",
                                    font=self.f_badge, bg=COLORS["active_p1"],
                                    fg="#ff9999", padx=12, pady=6,
                                    relief="flat", bd=0)
        self.turn_badge.pack(side="left", expand=True, fill="x", padx=4)

        self.card2 = self._make_player_card(self.score_frame, 2)
        self.card2.pack(side="right", padx=(8, 0))

        # Canvas board
        board_w = SIZE * CELL_SIZE + (SIZE - 1) * CELL_PAD + 2 * BOARD_PAD
        board_h = board_w
        self.canvas = tk.Canvas(outer, width=board_w, height=board_h,
                                 bg=COLORS["board_bg"], bd=0, highlightthickness=2,
                                 highlightbackground=COLORS["board_border"])
        self.canvas.pack()
        self.canvas.bind("<Motion>",   self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Leave>",    self._on_mouse_leave)

        # Status
        self.status_lbl = tk.Label(outer, text="", font=self.f_status,
                                    bg=COLORS["bg"], fg=COLORS["text_muted"],
                                    pady=6)
        self.status_lbl.pack()

        # Restart button
        self.restart_btn = tk.Label(outer, text="⟳  New Game",
                                     font=self.f_btn, bg=COLORS["btn_bg"],
                                     fg=COLORS["text_primary"], padx=20, pady=8,
                                     cursor="hand2", relief="flat", bd=0)
        self.restart_btn.pack(pady=(4, 0))
        self.restart_btn.bind("<Button-1>", lambda e: self._new_game())
        self.restart_btn.bind("<Enter>",
                               lambda e: self.restart_btn.configure(bg=COLORS["btn_hover"]))
        self.restart_btn.bind("<Leave>",
                               lambda e: self.restart_btn.configure(bg=COLORS["btn_bg"]))

    def _make_player_card(self, parent, player):
        bg = COLORS["active_p1"] if player == 1 else COLORS["panel_bg"]
        card = tk.Frame(parent, bg=bg, padx=14, pady=8,
                         relief="flat", bd=0)
        # inner canvas for ball dot
        dot = tk.Canvas(card, width=22, height=22, bg=bg,
                         bd=0, highlightthickness=0)
        dot.pack(side="left", padx=(0, 8))
        outer_c = COLORS["p1_outer"] if player == 1 else COLORS["p2_outer"]
        inner_c = COLORS["p1_inner"] if player == 1 else COLORS["p2_inner"]
        dot.create_oval(1, 1, 21, 21, fill=outer_c, outline="")
        dot.create_oval(5, 5, 17, 17, fill=inner_c, outline="")
        dot.create_oval(6, 6, 10, 10, fill=COLORS["p1_shine"] if player == 1 else COLORS["p2_shine"], outline="")

        info = tk.Frame(card, bg=bg)
        info.pack(side="left")
        lbl = "Player 1" if player == 1 else "Player 2"
        clr = "Red" if player == 1 else "Blue"
        tk.Label(info, text=lbl, font=self.f_label, bg=bg,
                 fg=COLORS["text_muted"]).pack(anchor="w")
        tk.Label(info, text=clr, font=self.f_player, bg=bg,
                 fg=COLORS["p1_inner"] if player == 1 else COLORS["p2_inner"]).pack(anchor="w")

        if player == 1:
            self.dot1 = dot
            self.info_frame1 = card
        else:
            self.dot2 = dot
            self.info_frame2 = card

        return card

    # ── Game State ─────────────────────────────────────────────────────────────

    def _new_game(self):
        self.board       = [[0]*SIZE for _ in range(SIZE)]
        self.current     = 1
        self.game_over   = False
        self.animating   = False
        self.hover_col   = -1
        self.hover_row   = -1
        self.win_cells   = []
        self.win_pulse   = 0
        self.win_dir     = 1
        self.cell_ids    = {}   # (r,c) -> list of canvas item ids
        self._draw_board()
        self._update_ui()
        self.status_lbl.configure(text="Click a circle to drop your ball")

    # ── Drawing ────────────────────────────────────────────────────────────────

    def _cell_xy(self, r, c):
        """Return (cx, cy) center of cell (r,c)."""
        x = BOARD_PAD + c * (CELL_SIZE + CELL_PAD) + CELL_SIZE // 2
        y = BOARD_PAD + r * (CELL_SIZE + CELL_PAD) + CELL_SIZE // 2
        return x, y

    def _draw_board(self):
        self.canvas.delete("all")
        self.cell_ids = {}
        for r in range(SIZE):
            for c in range(SIZE):
                self._draw_cell(r, c)

    def _draw_cell(self, r, c, highlight=False, win=False):
        cx, cy = self._cell_xy(r, c)
        R = CELL_SIZE // 2 - 2
        ids = []

        # Outer ring / glow
        if win:
            p = self.board[r][c]
            glow = COLORS["win_glow_p1"] if p == 1 else COLORS["win_glow_p2"]
            ids.append(self.canvas.create_oval(
                cx-R-5, cy-R-5, cx+R+5, cy+R+5,
                fill="", outline=glow, width=3))

        # Cell background
        bg = COLORS["cell_hover"] if highlight else COLORS["cell_empty"]
        border = COLORS["cell_border"]
        if win:
            p = self.board[r][c]
            border = COLORS["win_glow_p1"] if p == 1 else COLORS["win_glow_p2"]
        ids.append(self.canvas.create_oval(
            cx-R, cy-R, cx+R, cy+R,
            fill=bg, outline=border, width=2))

        # Ball if placed
        v = self.board[r][c]
        if v != 0:
            ids += self._draw_ball(cx, cy, v, R - 6)

        self.cell_ids[(r, c)] = ids

    def _draw_ball(self, cx, cy, player, r, alpha=1.0):
        outer = COLORS["p1_outer"]  if player == 1 else COLORS["p2_outer"]
        inner = COLORS["p1_inner"]  if player == 1 else COLORS["p2_inner"]
        shine = COLORS["p1_shine"]  if player == 1 else COLORS["p2_shine"]
        ids = []
        ids.append(self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                                            fill=outer, outline=""))
        ir = int(r * 0.65)
        ids.append(self.canvas.create_oval(cx-ir, cy-ir, cx+ir, cy+ir,
                                            fill=inner, outline=""))
        sr = max(2, int(r * 0.22))
        ox, oy = cx - int(r * 0.25), cy - int(r * 0.25)
        ids.append(self.canvas.create_oval(ox-sr, oy-sr, ox+sr, oy+sr,
                                            fill=shine, outline=""))
        return ids

    def _redraw_cell(self, r, c, highlight=False, win=False):
        for iid in self.cell_ids.get((r, c), []):
            self.canvas.delete(iid)
        self._draw_cell(r, c, highlight=highlight, win=win)

    # ── Animation ─────────────────────────────────────────────────────────────

    def _animate_drop(self, r, c, player, step=0):
        """Animate a ball dropping into cell (r, c)."""
        # Remove any previous temp ball for this cell
        for iid in self.cell_ids.get(("anim", r, c), []):
            self.canvas.delete(iid)

        if step > ANIM_STEPS:
            self.animating = False
            self._redraw_cell(r, c)
            # Check win/draw
            win = self._check_win(r, c, player)
            if win:
                self.win_cells = win
                self._start_win_pulse()
                name = "Red" if player == 1 else "Blue"
                self.status_lbl.configure(
                    text=f"Player {player} ({name}) wins! 🎉",
                    fg=COLORS["p1_inner"] if player == 1 else COLORS["p2_inner"])
                self.game_over = True
                self._update_ui(game_over=True)
            elif all(self.board[rr][cc] != 0 for rr in range(SIZE) for cc in range(SIZE)):
                self.status_lbl.configure(text="It's a draw! Board is full.", fg=COLORS["text_muted"])
                self.game_over = True
                self._update_ui(game_over=True)
            else:
                self.current = 2 if player == 1 else 1
                self._update_ui()
            return

        t = step / ANIM_STEPS
        ease = ease_out_back(t)

        # Start from top of board, land at cell center
        cx, cy = self._cell_xy(r, c)
        start_y = BOARD_PAD + CELL_SIZE // 2 - int(1.2 * CELL_SIZE)
        ball_y = lerp(start_y, cy, ease)
        ball_r = int((CELL_SIZE // 2 - 8) * min(1.0, t + 0.3))
        ball_r = max(4, ball_r)

        ids = self._draw_ball(cx, int(ball_y), player, ball_r)
        self.cell_ids[("anim", r, c)] = ids

        self.after(ANIM_DELAY, lambda: self._animate_drop(r, c, player, step + 1))

    # ── Win Pulse Animation ────────────────────────────────────────────────────

    def _start_win_pulse(self):
        for r, c in self.win_cells:
            self._redraw_cell(r, c, win=True)
        self._pulse_step()

    def _pulse_step(self):
        if not self.win_cells:
            return
        self.win_pulse += self.win_dir * 0.08
        if self.win_pulse >= 1.0:
            self.win_pulse = 1.0; self.win_dir = -1
        elif self.win_pulse <= 0.0:
            self.win_pulse = 0.0; self.win_dir = 1

        for r, c in self.win_cells:
            for iid in self.cell_ids.get((r, c), []):
                self.canvas.delete(iid)
            cx, cy = self._cell_xy(r, c)
            R = CELL_SIZE // 2 - 2
            p = self.board[r][c]
            glow = COLORS["win_glow_p1"] if p == 1 else COLORS["win_glow_p2"]
            gw = int(3 + self.win_pulse * 4)
            extra = int(self.win_pulse * 7)
            ids = []
            ids.append(self.canvas.create_oval(
                cx-R-extra, cy-R-extra, cx+R+extra, cy+R+extra,
                fill="", outline=glow, width=gw))
            ids.append(self.canvas.create_oval(
                cx-R, cy-R, cx+R, cy+R,
                fill=COLORS["cell_empty"], outline=glow, width=2))
            ids += self._draw_ball(cx, cy, p, R - 6)
            self.cell_ids[(r, c)] = ids

        self.after(30, self._pulse_step)

    # ── Event Handlers ─────────────────────────────────────────────────────────

    def _hit_cell(self, x, y):
        for r in range(SIZE):
            for c in range(SIZE):
                cx, cy = self._cell_xy(r, c)
                if math.hypot(x - cx, y - cy) <= CELL_SIZE // 2 - 2:
                    return r, c
        return None, None

    def _on_mouse_move(self, event):
        if self.game_over or self.animating:
            return
        r, c = self._hit_cell(event.x, event.y)
        old_r, old_c = self.hover_row, self.hover_col
        if (r, c) != (old_r, old_c):
            if old_r >= 0:
                self._redraw_cell(old_r, old_c)
            if r is not None and self.board[r][c] == 0:
                self.hover_row, self.hover_col = r, c
                self._redraw_cell(r, c, highlight=True)
            else:
                self.hover_row, self.hover_col = -1, -1

    def _on_mouse_leave(self, event):
        if self.hover_row >= 0:
            self._redraw_cell(self.hover_row, self.hover_col)
            self.hover_row, self.hover_col = -1, -1

    def _on_click(self, event):
        if self.game_over or self.animating:
            return
        r, c = self._hit_cell(event.x, event.y)
        if r is None or self.board[r][c] != 0:
            return
        self.board[r][c] = self.current
        self.hover_row, self.hover_col = -1, -1
        self.animating = True
        self._redraw_cell(r, c)  # clear hover
        self._animate_drop(r, c, self.current)

    # ── Win Check ─────────────────────────────────────────────────────────────

    def _check_win(self, r, c, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            cells = [(r, c)]
            for s in range(1, WIN_LENGTH):
                nr, nc = r + dr*s, c + dc*s
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == player:
                    cells.append((nr, nc))
                else:
                    break
            for s in range(1, WIN_LENGTH):
                nr, nc = r - dr*s, c - dc*s
                if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == player:
                    cells.append((nr, nc))
                else:
                    break
            if len(cells) >= WIN_LENGTH:
                return cells
        return None

    # ── UI Updates ─────────────────────────────────────────────────────────────

    def _update_ui(self, game_over=False):
        p = self.current
        if game_over:
            self.turn_badge.configure(text="Game Over", bg=COLORS["panel_bg"],
                                       fg=COLORS["text_muted"])
            for card in [self.card1, self.card2]:
                card.configure(bg=COLORS["panel_bg"])
            return

        if p == 1:
            self.turn_badge.configure(text="▶  Red's turn",
                                       bg=COLORS["active_p1"], fg="#ff9999")
            self.card1.configure(bg=COLORS["active_p1"])
            self.card2.configure(bg=COLORS["panel_bg"])
            self._recolor_card(self.card1, COLORS["active_p1"])
            self._recolor_card(self.card2, COLORS["panel_bg"])
        else:
            self.turn_badge.configure(text="▶  Blue's turn",
                                       bg=COLORS["active_p2"], fg="#90caf9")
            self.card2.configure(bg=COLORS["active_p2"])
            self.card1.configure(bg=COLORS["panel_bg"])
            self._recolor_card(self.card2, COLORS["active_p2"])
            self._recolor_card(self.card1, COLORS["panel_bg"])

        self.status_lbl.configure(
            text=f"Player {p} — click a circle to drop",
            fg=COLORS["p1_inner"] if p == 1 else COLORS["p2_inner"])

    def _recolor_card(self, card, bg):
        card.configure(bg=bg)
        for child in card.winfo_children():
            try:
                child.configure(bg=bg)
                for grandchild in child.winfo_children():
                    try: grandchild.configure(bg=bg)
                    except: pass
            except: pass


# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = CircleDropGame()
    app.mainloop()