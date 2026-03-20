import tkinter as tk
from tkinter import font as tkfont
import math
import re

# ─── Theme Definitions ────────────────────────────────────────────────────────

THEMES = {
    "dark": {
        "bg":           "#0f1117",
        "display_bg":   "#1a1d27",
        "btn_bg":       "#1e2130",
        "btn_num":      "#252840",
        "btn_op":       "#2a2d42",
        "btn_eq":       "#5c6bc0",
        "btn_sci":      "#1e3040",
        "btn_clear":    "#3d1f2e",
        "btn_special":  "#1f2e3d",
        "text":         "#e8eaf6",
        "display_text": "#ffffff",
        "expr_text":    "#7986cb",
        "btn_fg":       "#c5cae9",
        "btn_op_fg":    "#90caf9",
        "btn_sci_fg":   "#80cbc4",
        "btn_eq_fg":    "#ffffff",
        "btn_clear_fg": "#ef9a9a",
        "btn_special_fg":"#b0bec5",
        "hover_num":    "#2e3250",
        "hover_op":     "#323552",
        "hover_eq":     "#7986cb",
        "hover_sci":    "#1e3d50",
        "hover_clear":  "#4d2535",
        "hover_special":"#263545",
        "shadow":       "#000000",
        "border":       "#2d3154",
        "status_bg":    "#161929",
        "mode_btn":     "#252840",
    },
    "light": {
        "bg":           "#f0f2fa",
        "display_bg":   "#ffffff",
        "btn_bg":       "#e8eaf6",
        "btn_num":      "#ffffff",
        "btn_op":       "#e3f2fd",
        "btn_eq":       "#5c6bc0",
        "btn_sci":      "#e0f7fa",
        "btn_clear":    "#fce4ec",
        "btn_special":  "#ede7f6",
        "text":         "#1a237e",
        "display_text": "#1a237e",
        "expr_text":    "#7986cb",
        "btn_fg":       "#37474f",
        "btn_op_fg":    "#1565c0",
        "btn_sci_fg":   "#00695c",
        "btn_eq_fg":    "#ffffff",
        "btn_clear_fg": "#c62828",
        "btn_special_fg":"#4527a0",
        "hover_num":    "#dde0f5",
        "hover_op":     "#bbdefb",
        "hover_eq":     "#7986cb",
        "hover_sci":    "#b2ebf2",
        "hover_clear":  "#f8bbd9",
        "hover_special":"#d1c4e9",
        "shadow":       "#c5cae9",
        "border":       "#c5cae9",
        "status_bg":    "#e8eaf6",
        "mode_btn":     "#dde0f5",
    }
}

ACCENT_COLORS = {
    "indigo": {"btn_eq": "#5c6bc0", "hover_eq": "#7986cb", "expr_text": "#7986cb", "btn_op_fg": "#90caf9"},
    "purple": {"btn_eq": "#8e24aa", "hover_eq": "#ab47bc", "expr_text": "#ce93d8", "btn_op_fg": "#ce93d8"},
    "red":    {"btn_eq": "#e53935", "hover_eq": "#ef5350", "expr_text": "#ef9a9a", "btn_op_fg": "#ef9a9a"},
    "blue":   {"btn_eq": "#1e88e5", "hover_eq": "#42a5f5", "expr_text": "#90caf9", "btn_op_fg": "#90caf9"},
    "green":  {"btn_eq": "#43a047", "hover_eq": "#66bb6a", "expr_text": "#a5d6a7", "btn_op_fg": "#a5d6a7"},
}

# ─── Calculator Logic ─────────────────────────────────────────────────────────

class CalcEngine:
    def __init__(self):
        self.reset()
        self.deg_mode = True

    def reset(self):
        self.expr = ""
        self.result = "0"
        self.just_evaluated = False
        self.error = False

    def to_rad(self, x):
        return math.radians(x) if self.deg_mode else x

    def safe_eval(self, expr):
        expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        expr = expr.replace("π", str(math.pi)).replace("e", str(math.e))
        allowed = {
            "sin": lambda x: math.sin(self.to_rad(x)),
            "cos": lambda x: math.cos(self.to_rad(x)),
            "tan": lambda x: math.tan(self.to_rad(x)),
            "asin": lambda x: math.degrees(math.asin(x)) if self.deg_mode else math.asin(x),
            "acos": lambda x: math.degrees(math.acos(x)) if self.deg_mode else math.acos(x),
            "atan": lambda x: math.degrees(math.atan(x)) if self.deg_mode else math.atan(x),
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "log": math.log10, "ln": math.log, "log2": math.log2,
            "sqrt": math.sqrt, "cbrt": lambda x: x**(1/3),
            "abs": abs, "factorial": math.factorial,
            "ceil": math.ceil, "floor": math.floor,
            "exp": math.exp, "pi": math.pi, "e": math.e,
        }
        try:
            result = eval(expr, {"__builtins__": {}}, allowed)
            if isinstance(result, complex):
                return "Complex number"
            if math.isinf(result): return "Infinity"
            if math.isnan(result): return "Undefined"
            if isinstance(result, float):
                if result == int(result) and abs(result) < 1e15:
                    return str(int(result))
                return f"{result:.10g}"
            return str(result)
        except ZeroDivisionError:
            return "Division by zero"
        except (ValueError, OverflowError) as ex:
            return f"Error: {ex}"
        except Exception:
            return "Syntax Error"

# ─── Main Application ─────────────────────────────────────────────────────────

class ScientificCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.engine = CalcEngine()
        self.mode = "dark"
        self.accent = "indigo"
        self.theme = self._build_theme()
        self.btn_refs = []
        self.anim_id = None

        self.title("Sci Calc Pro")
        self.resizable(False, False)
        self.configure(bg=self.theme["bg"])

        self._setup_fonts()
        self._build_ui()
        self._apply_theme()
        self._bind_keys()

    def _build_theme(self):
        t = dict(THEMES[self.mode])
        t.update(ACCENT_COLORS[self.accent])
        return t

    def _setup_fonts(self):
        self.f_display  = tkfont.Font(family="Courier New", size=32, weight="bold")
        self.f_expr     = tkfont.Font(family="Courier New", size=11)
        self.f_btn      = tkfont.Font(family="Segoe UI",    size=13, weight="bold")
        self.f_sci      = tkfont.Font(family="Segoe UI",    size=11, weight="bold")
        self.f_tiny     = tkfont.Font(family="Segoe UI",    size=9)
        self.f_status   = tkfont.Font(family="Segoe UI",    size=9, weight="bold")
        self.f_icon     = tkfont.Font(family="Segoe UI",    size=12, weight="bold")

    def _build_ui(self):
        # ── Outer shell ──
        self.outer = tk.Frame(self, bd=0, relief="flat")
        self.outer.pack(padx=12, pady=12)

        # ── Top bar ──
        top = tk.Frame(self.outer, height=36)
        top.pack(fill="x", pady=(0, 6))

        self.title_lbl = tk.Label(top, text="SCI CALC PRO",
                                   font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
                                   pady=4)
        self.title_lbl.pack(side="left", padx=6)

        # Accent color buttons
        self.accent_frame = tk.Frame(top)
        self.accent_frame.pack(side="right", padx=(0, 6))

        self.accent_btns = {}
        accent_icons = {"indigo":"●","purple":"●","red":"●","blue":"●","green":"●"}
        accent_clrs   = {"indigo":"#7986cb","purple":"#ab47bc","red":"#ef5350","blue":"#42a5f5","green":"#66bb6a"}
        for name in ["indigo","purple","red","blue","green"]:
            b = tk.Label(self.accent_frame, text=accent_icons[name],
                         font=tkfont.Font(family="Segoe UI", size=16),
                         fg=accent_clrs[name], cursor="hand2", width=2)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, n=name: self._set_accent(n))
            self.accent_btns[name] = b

        # Mode toggle
        self.mode_btn = tk.Label(top, text="☀", font=self.f_icon,
                                  cursor="hand2", padx=8, pady=2, relief="flat", bd=0)
        self.mode_btn.pack(side="right", padx=4)
        self.mode_btn.bind("<Button-1>", lambda e: self._toggle_mode())

        # ── Display ──
        disp_frame = tk.Frame(self.outer, bd=0, relief="flat")
        disp_frame.pack(fill="x", pady=(0, 8))

        self.expr_lbl = tk.Label(disp_frame, text="", anchor="e",
                                  font=self.f_expr, height=1, padx=14)
        self.expr_lbl.pack(fill="x")

        self.disp_lbl = tk.Label(disp_frame, text="0", anchor="e",
                                  font=self.f_display, height=2, padx=14)
        self.disp_lbl.pack(fill="x")

        # ── Status bar ──
        self.status_bar = tk.Frame(self.outer, height=24)
        self.status_bar.pack(fill="x", pady=(0, 8))

        self.deg_btn = tk.Label(self.status_bar, text="DEG", font=self.f_status,
                                 padx=8, pady=2, cursor="hand2", relief="flat")
        self.deg_btn.pack(side="left", padx=4)
        self.deg_btn.bind("<Button-1>", lambda e: self._toggle_deg())

        self.inv_btn = tk.Label(self.status_bar, text="INV", font=self.f_status,
                                 padx=8, pady=2, cursor="hand2", relief="flat")
        self.inv_btn.pack(side="left", padx=2)
        self.inv_btn.bind("<Button-1>", lambda e: self._toggle_inv())
        self.inv_mode = False

        self.mem_lbl = tk.Label(self.status_bar, text="M: 0", font=self.f_status,
                                 padx=8, pady=2)
        self.mem_lbl.pack(side="right", padx=4)
        self.memory = 0

        # ── Button grid ──
        grid = tk.Frame(self.outer)
        grid.pack()

        # Layout: (label, col, row, colspan, type, action)
        # Types: num, op, eq, sci, clear, special
        layout = [
            # Row 0 – sci
            ("sin",  0,0,1,"sci","sin("),  ("cos",  1,0,1,"sci","cos("),
            ("tan",  2,0,1,"sci","tan("),  ("ln",   3,0,1,"sci","ln("),
            ("log",  4,0,1,"sci","log("),  ("√",    5,0,1,"sci","sqrt("),

            # Row 1 – sci
            ("x²",  0,1,1,"sci","^2"),     ("x³",  1,1,1,"sci","^3"),
            ("xⁿ",  2,1,1,"sci","^"),      ("eˣ",  3,1,1,"sci","exp("),
            ("π",   4,1,1,"sci","π"),      ("e",   5,1,1,"sci","e"),

            # Row 2 – sci
            ("⌈x⌉", 0,2,1,"sci","ceil("), ("⌊x⌋", 1,2,1,"sci","floor("),
            ("|x|",  2,2,1,"sci","abs("),  ("n!",  3,2,1,"sci","factorial("),
            ("1/x",  4,2,1,"sci","1/("),   ("cbrt",5,2,1,"sci","cbrt("),

            # Row 3 – control
            ("AC",   0,3,1,"clear","AC"),  ("⌫",   1,3,1,"clear","DEL"),
            ("(",    2,3,1,"special","("), (")",   3,3,1,"special",")"),
            ("%",    4,3,1,"special","%"), ("÷",   5,3,1,"op","÷"),

            # Row 4 – nums
            ("7",    0,4,1,"num","7"),     ("8",   1,4,1,"num","8"),
            ("9",    2,4,1,"num","9"),     ("×",   3,4,1,"op","×"),
            ("M+",   4,4,1,"special","M+"),("MR",  5,4,1,"special","MR"),

            # Row 5
            ("4",    0,5,1,"num","4"),     ("5",   1,5,1,"num","5"),
            ("6",    2,5,1,"num","6"),     ("−",   3,5,1,"op","−"),
            ("MC",   4,5,1,"special","MC"),("MS",  5,5,1,"special","MS"),

            # Row 6
            ("1",    0,6,1,"num","1"),     ("2",   1,6,1,"num","2"),
            ("3",    2,6,1,"num","3"),     ("+",   3,6,1,"op","+"),
            ("=",    4,6,2,"eq","="),

            # Row 7
            ("0",    0,7,2,"num","0"),     (".",   2,7,1,"num","."),
            ("±",    3,7,1,"special","±"),
        ]

        BW, BH = 68, 52
        PAD = 4

        for (lbl, c, r, cs, typ, act) in layout:
            frame = tk.Frame(grid, width=BW*cs + PAD*(cs-1), height=BH)
            frame.grid(row=r, column=c, columnspan=cs,
                       padx=PAD//2, pady=PAD//2, sticky="nsew")
            frame.pack_propagate(False)

            btn = tk.Label(frame, text=lbl, cursor="hand2",
                           relief="flat", bd=0,
                           font=self.f_sci if typ=="sci" else self.f_btn)
            btn.pack(fill="both", expand=True)

            btn.bind("<Button-1>",   lambda e, a=act, t=typ, b=btn: self._on_click(a, t, b))
            btn.bind("<Enter>",      lambda e, t=typ, b=btn: self._on_hover(b, t, True))
            btn.bind("<Leave>",      lambda e, t=typ, b=btn: self._on_hover(b, t, False))

            self.btn_refs.append((btn, typ, frame))

    # ─── Theme & Color ────────────────────────────────────────────────────────

    def _apply_theme(self):
        t = self.theme
        self.configure(bg=t["bg"])
        self.outer.configure(bg=t["bg"])

        self.title_lbl.configure(bg=t["bg"], fg=t["expr_text"])

        for w in [self.accent_frame, self.status_bar]:
            w.configure(bg=t["bg"])
        for _, b in self.accent_btns.items():
            b.configure(bg=t["bg"])

        self.mode_btn.configure(
            bg=t["mode_btn"], fg=t["text"],
            text="☀" if self.mode == "dark" else "🌙"
        )

        self.expr_lbl.configure(bg=t["display_bg"], fg=t["expr_text"])
        self.disp_lbl.configure(bg=t["display_bg"], fg=t["display_text"])
        self.disp_lbl.master.configure(bg=t["display_bg"])

        self.status_bar.configure(bg=t["status_bg"])
        active_deg = t["btn_eq"] if self.engine.deg_mode else t["btn_bg"]
        active_inv = t["btn_clear"] if self.inv_mode else t["btn_bg"]
        self.deg_btn.configure(bg=active_deg,
                                fg="#ffffff" if self.engine.deg_mode else t["btn_fg"])
        self.inv_btn.configure(bg=active_inv,
                                fg=t["btn_clear_fg"] if self.inv_mode else t["btn_fg"])
        self.mem_lbl.configure(bg=t["status_bg"], fg=t["expr_text"])

        color_map = {
            "num":     (t["btn_num"],    t["btn_fg"]),
            "op":      (t["btn_op"],     t["btn_op_fg"]),
            "eq":      (t["btn_eq"],     t["btn_eq_fg"]),
            "sci":     (t["btn_sci"],    t["btn_sci_fg"]),
            "clear":   (t["btn_clear"],  t["btn_clear_fg"]),
            "special": (t["btn_special"],t["btn_special_fg"]),
        }
        for (btn, typ, frame) in self.btn_refs:
            bg, fg = color_map[typ]
            btn.configure(bg=bg, fg=fg)
            frame.configure(bg=bg)

        # grid frame bg
        for w in self.outer.winfo_children():
            if isinstance(w, tk.Frame) and w not in [
                self.status_bar, self.accent_frame
            ]:
                try: w.configure(bg=t["bg"])
                except: pass

    def _toggle_mode(self):
        self.mode = "light" if self.mode == "dark" else "dark"
        self.theme = self._build_theme()
        self._apply_theme()

    def _set_accent(self, name):
        self.accent = name
        self.theme = self._build_theme()
        self._apply_theme()

    def _on_hover(self, btn, typ, entering):
        t = self.theme
        hover_map = {
            "num":     t["hover_num"],
            "op":      t["hover_op"],
            "eq":      t["hover_eq"],
            "sci":     t["hover_sci"],
            "clear":   t["hover_clear"],
            "special": t["hover_special"],
        }
        normal_map = {
            "num":     t["btn_num"],
            "op":      t["btn_op"],
            "eq":      t["btn_eq"],
            "sci":     t["btn_sci"],
            "clear":   t["btn_clear"],
            "special": t["btn_special"],
        }
        bg = hover_map[typ] if entering else normal_map[typ]
        btn.configure(bg=bg)
        # update parent frame too
        try: btn.master.configure(bg=bg)
        except: pass

    # ─── Input Handling ───────────────────────────────────────────────────────

    def _on_click(self, action, typ, btn=None):
        self._flash(btn, typ)
        e = self.engine

        if action == "AC":
            e.reset()
        elif action == "DEL":
            if e.just_evaluated:
                e.reset()
            elif e.expr:
                e.expr = e.expr[:-1]
        elif action == "=":
            if e.expr:
                e.result = e.safe_eval(e.expr)
                e.just_evaluated = True
        elif action == "M+":
            try: self.memory += float(e.result); self._update_mem()
            except: pass
        elif action == "MS":
            try: self.memory = float(e.result); self._update_mem()
            except: pass
        elif action == "MR":
            val = f"{self.memory:g}"
            if e.just_evaluated: e.expr = ""
            e.expr += val; e.just_evaluated = False
        elif action == "MC":
            self.memory = 0; self._update_mem()
        elif action == "±":
            if e.just_evaluated:
                try:
                    v = float(e.result)
                    e.result = f"{-v:g}"
                    e.expr = ""; return
                except: pass
            else:
                if e.expr and e.expr[0] == "-":
                    e.expr = e.expr[1:]
                else:
                    e.expr = "-" + e.expr
        else:
            if e.just_evaluated and action not in "+-×÷^%":
                e.expr = ""
            e.just_evaluated = False
            # Inverse trig
            if self.inv_mode and action in ["sin(","cos(","tan("]:
                action = "a" + action
            e.expr += action

        self._refresh_display()

    def _flash(self, btn, typ):
        if not btn: return
        t = self.theme
        flash_map = {"num":"#ffffff","op":"#bbdefb","eq":"#ffffff",
                     "sci":"#b2dfdb","clear":"#ffcdd2","special":"#d1c4e9"}
        orig_map  = {"num":t["btn_num"],"op":t["btn_op"],"eq":t["btn_eq"],
                     "sci":t["btn_sci"],"clear":t["btn_clear"],"special":t["btn_special"]}
        flash = flash_map.get(typ, "#ffffff")
        orig  = orig_map.get(typ, t["btn_num"])
        btn.configure(bg=flash)
        self.after(80, lambda: btn.configure(bg=orig))

    def _refresh_display(self):
        e = self.engine
        if e.just_evaluated:
            self.expr_lbl.configure(text=e.expr + " =")
            self.disp_lbl.configure(text=e.result)
        else:
            self.expr_lbl.configure(text=e.expr[-40:] if len(e.expr) > 40 else e.expr)
            # Live preview
            if e.expr:
                preview = e.safe_eval(e.expr)
                if "Error" not in preview and "Syntax" not in preview:
                    self.disp_lbl.configure(text=preview)
                else:
                    self.disp_lbl.configure(text=e.expr[-14:] if len(e.expr)>14 else e.expr)
            else:
                self.disp_lbl.configure(text="0")

    def _update_mem(self):
        self.mem_lbl.configure(text=f"M: {self.memory:g}")

    def _toggle_deg(self):
        self.engine.deg_mode = not self.engine.deg_mode
        lbl = "DEG" if self.engine.deg_mode else "RAD"
        self.deg_btn.configure(text=lbl)
        self._apply_theme()

    def _toggle_inv(self):
        self.inv_mode = not self.inv_mode
        self._apply_theme()

    # ─── Keyboard ─────────────────────────────────────────────────────────────

    def _bind_keys(self):
        key_map = {
            "0":"0","1":"1","2":"2","3":"3","4":"4",
            "5":"5","6":"6","7":"7","8":"8","9":"9",
            ".":".", "+":"+", "-":"−", "*":"×", "/":"÷",
            "^":"^", "(":"(", ")":")", "%":"%",
            "Return":"=", "equal":"=",
            "BackSpace":"DEL", "Escape":"AC",
        }
        for k, v in key_map.items():
            self.bind(f"<Key-{k}>", lambda e, a=v: self._on_click(a, "num"))
        self.bind("<Key-s>", lambda e: self._on_click("sin(", "sci"))
        self.bind("<Key-c>", lambda e: self._on_click("cos(", "sci"))
        self.bind("<Key-t>", lambda e: self._on_click("tan(", "sci"))
        self.bind("<Key-l>", lambda e: self._on_click("log(", "sci"))
        self.bind("<Key-r>", lambda e: self._on_click("sqrt(", "sci"))
        self.bind("<Key-p>", lambda e: self._on_click("π", "sci"))


if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()

    