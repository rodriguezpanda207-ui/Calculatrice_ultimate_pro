"""
CALCULATRICE ULTIMATE PRO
Version complète construite à partir de la version précédente.

Fonctions principales :
- Simple / Scientifique / Programmeur / Convertisseur
- DEG / RAD / GRAD
- Historique
- Mémoire MC/MR/M+/M-/MS
- sin, cos, tan, asin, acos, atan
- sinh, cosh, tanh et inverses
- log, ln, exp, sqrt, cbrt
- x², xʸ, 10ˣ, eˣ, factorielle, nCr, nPr
- π, e, %, +/- et parenthèses
- Programmeur DEC/BIN/OCT/HEX avec opérateurs bit à bit
- Convertisseurs longueur, masse, température, temps, vitesse, aire, volume
- Clavier
- Thème clair/sombre
- Gestion des erreurs sans eval() dangereux
"""

import ast
import math
import operator as op
import re
import tkinter as tk
from tkinter import ttk, messagebox


# ============================================================
# OUTILS MATHÉMATIQUES
# ============================================================

def factorial(x):
    if isinstance(x, float) and not x.is_integer():
        raise ValueError("La factorielle demande un entier.")
    x = int(x)
    if x < 0:
        raise ValueError("Factorielle impossible pour un nombre négatif.")
    if x > 170:
        raise ValueError("Nombre trop grand pour la factorielle.")
    return math.factorial(x)


def ncr(n, r):
    n, r = int(n), int(r)
    if n < 0 or r < 0 or r > n:
        raise ValueError("nCr exige 0 ≤ r ≤ n.")
    return math.comb(n, r)


def npr(n, r):
    n, r = int(n), int(r)
    if n < 0 or r < 0 or r > n:
        raise ValueError("nPr exige 0 ≤ r ≤ n.")
    return math.perm(n, r)


# ============================================================
# ÉVALUATEUR SÉCURISÉ
# ============================================================

class SafeEvaluator:
    BIN_OPS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
        ast.FloorDiv: op.floordiv,
    }

    UNARY_OPS = {
        ast.UAdd: op.pos,
        ast.USub: op.neg,
    }

    FUNCTIONS = {
        "sqrt": math.sqrt,
        "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "factorial": factorial,
        "ncr": ncr,
        "npr": npr,
        "exp": math.exp,
        "log": math.log10,
        "ln": math.log,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def evaluate(self, expression):
        tree = ast.parse(expression, mode="eval")
        return self._eval(tree.body)

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            raise ValueError("Constante interdite.")

        if isinstance(node, ast.BinOp) and type(node.op) in self.BIN_OPS:
            left = self._eval(node.left)
            right = self._eval(node.right)
            return self.BIN_OPS[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self.UNARY_OPS:
            return self.UNARY_OPS[type(node.op)](self._eval(node.operand))

        if isinstance(node, ast.Name):
            if node.id in self.CONSTANTS:
                return self.CONSTANTS[node.id]
            raise ValueError(f"Nom inconnu : {node.id}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Fonction interdite.")
            name = node.func.id.lower()
            if name not in self.FUNCTIONS:
                raise ValueError(f"Fonction inconnue : {name}")
            if node.keywords:
                raise ValueError("Arguments nommés interdits.")
            args = [self._eval(a) for a in node.args]
            return self.FUNCTIONS[name](*args)

        raise ValueError("Expression non autorisée.")


# ============================================================
# CALCULATRICE
# ============================================================

class UltimateCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculatrice Ultimate Pro")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        self.mode = "Simple"
        self.angle_mode = "DEG"
        self.theme = "dark"

        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.mode_var = tk.StringVar(value="Simple")
        self.angle_var = tk.StringVar(value="DEG")

        self.memory = 0.0
        self.last_answer = 0.0
        self.history = []

        self.programmer_base = "DEC"
        self.converter_category = "Longueur"

        self.evaluator = SafeEvaluator()

        self.colors = {}
        self.configure_theme()
        self.build_interface()
        self.bind_keyboard()
        self.set_mode("Simple")

    # --------------------------------------------------------
    # THÈME
    # --------------------------------------------------------

    def configure_theme(self):
        if self.theme == "dark":
            self.colors = {
                "bg": "#101114",
                "panel": "#181a20",
                "display": "#0b0c0f",
                "text": "#f3f4f6",
                "muted": "#9ca3af",
                "button": "#242832",
                "button2": "#303641",
                "accent": "#7c3aed",
                "accent2": "#2563eb",
                "danger": "#b91c1c",
                "success": "#15803d",
                "border": "#363b45",
            }
        else:
            self.colors = {
                "bg": "#f3f4f6",
                "panel": "#ffffff",
                "display": "#ffffff",
                "text": "#111827",
                "muted": "#6b7280",
                "button": "#e5e7eb",
                "button2": "#d1d5db",
                "accent": "#7c3aed",
                "accent2": "#2563eb",
                "danger": "#dc2626",
                "success": "#16a34a",
                "border": "#cbd5e1",
            }

    def apply_theme(self):
        self.configure_theme()
        self.root.configure(bg=self.colors["bg"])
        self.refresh_ui_colors()

    def refresh_ui_colors(self):
        if not hasattr(self, "widgets"):
            return

        for widget in self.widgets:
            try:
                cls = widget.winfo_class()
                if cls == "Button":
                    widget.configure(
                        bg=self.colors["button"],
                        fg=self.colors["text"],
                        activebackground=self.colors["button2"],
                        activeforeground=self.colors["text"],
                    )
                elif cls == "Label":
                    widget.configure(bg=self.colors["panel"], fg=self.colors["text"])
            except tk.TclError:
                pass

        self.display.configure(
            bg=self.colors["display"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
        )
        self.result_label.configure(
            bg=self.colors["display"], fg=self.colors["muted"]
        )

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------

    def build_interface(self):
        self.widgets = []

        self.main = tk.Frame(self.root, bg=self.colors["bg"])
        self.main.pack(fill="both", expand=True, padx=12, pady=12)

        self.top = tk.Frame(self.main, bg=self.colors["bg"])
        self.top.pack(fill="x")

        tk.Label(
            self.top,
            text="CALCULATRICE ULTIMATE PRO",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
        ).pack(side="left")

        self.mode_menu = ttk.Combobox(
            self.top,
            textvariable=self.mode_var,
            values=["Simple", "Scientifique", "Programmeur", "Convertisseur"],
            state="readonly",
            width=18,
        )
        self.mode_menu.pack(side="right", padx=5)
        self.mode_menu.bind("<<ComboboxSelected>>",
                            lambda e: self.set_mode(self.mode_var.get()))

        self.theme_btn = tk.Button(
            self.top, text="☀ / ☾", command=self.toggle_theme,
            bd=0, padx=12, pady=6,
            bg=self.colors["button"], fg=self.colors["text"]
        )
        self.theme_btn.pack(side="right", padx=5)
        self.widgets.append(self.theme_btn)

        # Affichage
        self.display_frame = tk.Frame(
            self.main, bg=self.colors["display"], bd=1,
            highlightthickness=1, highlightbackground=self.colors["border"]
        )
        self.display_frame.pack(fill="x", pady=(12, 8))

        self.result_label = tk.Label(
            self.display_frame,
            textvariable=self.result,
            anchor="e",
            font=("Consolas", 14),
            bg=self.colors["display"],
            fg=self.colors["muted"],
            padx=14,
            pady=8,
        )
        self.result_label.pack(fill="x")

        self.display = tk.Entry(
            self.display_frame,
            textvariable=self.expression,
            justify="right",
            font=("Consolas", 28, "bold"),
            bg=self.colors["display"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
            bd=0,
        )
        self.display.pack(fill="x", padx=14, pady=(0, 14), ipady=8)

        self.content = tk.Frame(self.main, bg=self.colors["bg"])
        self.content.pack(fill="both", expand=True)

        self.button_area = tk.Frame(self.content, bg=self.colors["bg"])
        self.button_area.pack(side="left", fill="both", expand=True)

        self.side = tk.Frame(
            self.content, bg=self.colors["panel"], width=280
        )
        self.side.pack(side="right", fill="y", padx=(10, 0))
        self.side.pack_propagate(False)

        self.build_side_panel()

    def build_side_panel(self):
        for w in self.side.winfo_children():
            w.destroy()

        tk.Label(
            self.side, text="Historique",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["panel"], fg=self.colors["text"]
        ).pack(anchor="w", padx=12, pady=(12, 5))

        self.history_list = tk.Listbox(
            self.side,
            bg=self.colors["display"],
            fg=self.colors["text"],
            selectbackground=self.colors["accent"],
            relief="flat",
            font=("Consolas", 10),
        )
        self.history_list.pack(fill="both", expand=True, padx=12, pady=5)
        self.history_list.bind("<Double-Button-1>", self.use_history)

        buttons = tk.Frame(self.side, bg=self.colors["panel"])
        buttons.pack(fill="x", padx=12, pady=12)

        for text, cmd in [
            ("Réutiliser", self.use_history),
            ("Effacer historique", self.clear_history),
        ]:
            b = tk.Button(
                buttons, text=text, command=cmd,
                bg=self.colors["button"], fg=self.colors["text"],
                activebackground=self.colors["button2"],
                relief="flat", padx=8, pady=7
            )
            b.pack(fill="x", pady=3)

        self.refresh_history()

    # --------------------------------------------------------
    # MODES
    # --------------------------------------------------------

    def set_mode(self, mode):
        self.mode = mode
        self.mode_var.set(mode)
        self.expression.set("")
        self.result.set("0")

        for w in self.button_area.winfo_children():
            w.destroy()

        if mode == "Simple":
            self.build_simple()
        elif mode == "Scientifique":
            self.build_scientific()
        elif mode == "Programmeur":
            self.build_programmer()
        else:
            self.build_converter()

    def make_button(self, parent, text, command, row, col, colspan=1,
                    bg=None, fg=None, fontsize=12):
        if bg is None:
            bg = self.colors["button"]
        if fg is None:
            fg = self.colors["text"]

        b = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", fontsize, "bold"),
            bg=bg,
            fg=fg,
            activebackground=self.colors["button2"],
            activeforeground=self.colors["text"],
            relief="flat",
            bd=0,
            padx=5,
            pady=5,
        )
        b.grid(
            row=row, column=col, columnspan=colspan,
            sticky="nsew", padx=3, pady=3
        )
        self.widgets.append(b)
        return b

    def configure_grid(self, frame, rows, cols):
        for r in range(rows):
            frame.rowconfigure(r, weight=1)
        for c in range(cols):
            frame.columnconfigure(c, weight=1)

    def build_simple(self):
        f = tk.Frame(self.button_area, bg=self.colors["bg"])
        f.pack(fill="both", expand=True)
        self.configure_grid(f, 6, 4)

        keys = [
            ("MC", self.memory_clear), ("MR", self.memory_recall),
            ("M+", self.memory_add), ("M-", self.memory_sub),
            ("MS", self.memory_store), ("⌫", self.backspace),
            ("C", self.clear), ("÷", lambda: self.insert("/")),
            ("7", lambda: self.insert("7")), ("8", lambda: self.insert("8")),
            ("9", lambda: self.insert("9")), ("×", lambda: self.insert("*")),
            ("4", lambda: self.insert("4")), ("5", lambda: self.insert("5")),
            ("6", lambda: self.insert("6")), ("−", lambda: self.insert("-")),
            ("1", lambda: self.insert("1")), ("2", lambda: self.insert("2")),
            ("3", lambda: self.insert("3")), ("+", lambda: self.insert("+")),
            ("±", self.toggle_sign), ("0", lambda: self.insert("0")),
            (".", lambda: self.insert(".")), ("=", self.calculate),
        ]

        for i, (text, cmd) in enumerate(keys):
            r, c = divmod(i, 4)
            bg = self.colors["button"]
            if text == "=":
                bg = self.colors["accent"]
            elif text == "C":
                bg = self.colors["danger"]
            elif text in ("+", "−", "×", "÷"):
                bg = self.colors["button2"]
            self.make_button(f, text, cmd, r, c, bg=bg)

    def build_scientific(self):
        outer = tk.Frame(self.button_area, bg=self.colors["bg"])
        outer.pack(fill="both", expand=True)

        # Zone fonctions
        funcs_frame = tk.Frame(outer, bg=self.colors["bg"])
        funcs_frame.pack(fill="both", expand=True)

        self.configure_grid(funcs_frame, 5, 6)

        top = [
            (self.angle_mode, self.cycle_angle_mode),
            ("(", lambda: self.insert("(")),
            (")", lambda: self.insert(")")),
            ("C", self.clear),
            ("⌫", self.backspace),
            ("=", self.calculate),
        ]
        for c, (text, cmd) in enumerate(top):
            bg = self.colors["accent"] if text == "=" else self.colors["button"]
            if text == "C":
                bg = self.colors["danger"]
            self.make_button(funcs_frame, text, cmd, 0, c, bg=bg)

        funcs = [
            ("sin", lambda: self.insert_function("sin")),
            ("cos", lambda: self.insert_function("cos")),
            ("tan", lambda: self.insert_function("tan")),
            ("asin", lambda: self.insert_function("asin")),
            ("acos", lambda: self.insert_function("acos")),
            ("atan", lambda: self.insert_function("atan")),
            ("sinh", lambda: self.insert_function("sinh")),
            ("cosh", lambda: self.insert_function("cosh")),
            ("tanh", lambda: self.insert_function("tanh")),
            ("asinh", lambda: self.insert_function("asinh")),
            ("acosh", lambda: self.insert_function("acosh")),
            ("atanh", lambda: self.insert_function("atanh")),
            ("log", lambda: self.insert_function("log")),
            ("ln", lambda: self.insert_function("ln")),
            ("√", lambda: self.insert_function("sqrt")),
            ("∛", lambda: self.insert_function("cbrt")),
            ("x²", lambda: self.insert("^2")),
            ("xʸ", lambda: self.insert("^")),
            ("10ˣ", lambda: self.insert("10**")),
            ("eˣ", lambda: self.insert("exp(")),
            ("x!", self.factorial_current),
            ("nCr", lambda: self.insert_function("ncr")),
            ("nPr", lambda: self.insert_function("npr")),
            ("π", lambda: self.insert("pi")),
            ("e", lambda: self.insert("e")),
            ("%", lambda: self.insert("%")),
            ("±", self.toggle_sign),
        ]

        for i, (text, cmd) in enumerate(funcs):
            r = 1 + i // 6
            c = i % 6
            self.make_button(funcs_frame, text, cmd, r, c, fontsize=10)

        # Pavé numérique séparé : aucun chevauchement avec les fonctions.
        num_frame = tk.Frame(outer, bg=self.colors["bg"])
        num_frame.pack(fill="both", expand=True, pady=(5, 0))
        self.configure_grid(num_frame, 4, 6)

        nums = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("/", 0, 3), ("(", 0, 4), (")", 0, 5),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("*", 1, 3), ("+", 1, 4), ("-", 1, 5),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            ("0", 2, 3), (".", 2, 4), ("±", 2, 5),
            ("MC", 3, 0), ("MR", 3, 1), ("M+", 3, 2),
            ("M-", 3, 3), ("MS", 3, 4), ("=", 3, 5),
        ]
        for text, r, c in nums:
            if text == "=":
                cmd = self.calculate
                bg = self.colors["accent"]
            elif text == "±":
                cmd = self.toggle_sign
                bg = self.colors["button2"]
            elif text in ("MC", "MR", "M+", "M-", "MS"):
                cmd = getattr(self, {
                    "MC": "memory_clear", "MR": "memory_recall",
                    "M+": "memory_add", "M-": "memory_sub",
                    "MS": "memory_store"
                }[text])
                bg = self.colors["button2"]
            else:
                cmd = lambda x=text: self.insert(x)
                bg = self.colors["button"]
            self.make_button(num_frame, text, cmd, r, c, bg=bg, fontsize=10)

    def build_programmer(self):
        f = tk.Frame(self.button_area, bg=self.colors["bg"])
        f.pack(fill="both", expand=True)

        top = tk.Frame(f, bg=self.colors["bg"])
        top.pack(fill="x", pady=(0, 8))

        for base in ["DEC", "BIN", "OCT", "HEX"]:
            b = tk.Button(
                top, text=base,
                command=lambda x=base: self.change_programmer_base(x),
                bg=self.colors["accent"] if base == self.programmer_base
                else self.colors["button"],
                fg=self.colors["text"],
                relief="flat", padx=15, pady=7
            )
            b.pack(side="left", padx=3)

        grid = tk.Frame(f, bg=self.colors["bg"])
        grid.pack(fill="both", expand=True)
        self.configure_grid(grid, 7, 6)

        buttons = [
            ("AND", "&"), ("OR", "|"), ("XOR", "^"), ("NOT", "~"),
            ("<<", "<<"), (">>", ">>"),
            ("7","7"),("8","8"),("9","9"),("A","A"),("B","B"),("C","C"),
            ("4","4"),("5","5"),("6","6"),("D","D"),("E","E"),("F","F"),
            ("1","1"),("2","2"),("3","3"),("(","("),(")",")"),("⌫","BACK"),
            ("0","0"),("+","+"),("-","-"),("*","*"),("/","/"),("=","="),
            ("C","CLEAR"),("MC","MC"),("MR","MR"),("M+","M+"),("M-","M-"),("MS","MS"),
        ]

        for i, (label, value) in enumerate(buttons):
            r, c = divmod(i, 6)
            if value == "=":
                cmd = self.calculate_programmer
                bg = self.colors["accent"]
            elif value == "CLEAR":
                cmd = self.clear
                bg = self.colors["danger"]
            elif value == "BACK":
                cmd = self.backspace
                bg = self.colors["button2"]
            elif value in ("MC","MR","M+","M-","MS"):
                cmd = getattr(self, {
                    "MC":"memory_clear","MR":"memory_recall",
                    "M+":"memory_add","M-":"memory_sub","MS":"memory_store"
                }[value])
                bg = self.colors["button2"]
            else:
                cmd = lambda x=value: self.insert_programmer(x)
                bg = self.colors["button"]
            self.make_button(grid, label, cmd, r, c, bg=bg, fontsize=10)

    # --------------------------------------------------------
    # CONVERTISSEUR
    # --------------------------------------------------------

    def build_converter(self):
        outer = tk.Frame(self.button_area, bg=self.colors["bg"])
        outer.pack(fill="both", expand=True)

        categories = [
            "Longueur", "Masse", "Température", "Temps",
            "Vitesse", "Aire", "Volume"
        ]

        cat_frame = tk.Frame(outer, bg=self.colors["bg"])
        cat_frame.pack(fill="x", pady=(0, 10))

        self.converter_category_var = tk.StringVar(value=self.converter_category)
        combo = ttk.Combobox(
            cat_frame,
            textvariable=self.converter_category_var,
            values=categories,
            state="readonly",
            width=22
        )
        combo.pack(side="left")
        combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_converter())

        self.converter_value = tk.Entry(
            cat_frame, font=("Consolas", 14),
            bg=self.colors["display"], fg=self.colors["text"],
            insertbackground=self.colors["text"], relief="flat"
        )
        self.converter_value.pack(
            side="left", fill="x", expand=True, padx=8, ipady=8
        )

        body = tk.Frame(outer, bg=self.colors["bg"])
        body.pack(fill="x", pady=10)

        self.converter_from = ttk.Combobox(body, state="readonly", width=14)
        self.converter_from.pack(side="left", padx=5)

        tk.Label(
            body, text="→", font=("Segoe UI", 20, "bold"),
            bg=self.colors["bg"], fg=self.colors["text"]
        ).pack(side="left", padx=5)

        self.converter_to = ttk.Combobox(body, state="readonly", width=14)
        self.converter_to.pack(side="left", padx=5)

        self.converter_result = tk.StringVar(value="Résultat : —")
        tk.Label(
            outer, textvariable=self.converter_result,
            font=("Consolas", 18, "bold"),
            bg=self.colors["panel"], fg=self.colors["text"],
            anchor="w", padx=15, pady=15
        ).pack(fill="x", pady=10)

        convert_btn = tk.Button(
            outer, text="CONVERTIR", command=self.convert_units,
            bg=self.colors["accent"], fg=self.colors["text"],
            activebackground=self.colors["accent2"],
            relief="flat", font=("Segoe UI", 13, "bold"),
            padx=12, pady=10
        )
        convert_btn.pack(fill="x", pady=5)
        self.widgets.append(convert_btn)

        self.refresh_converter()

    def converter_data(self):
        return {
            "Longueur": {
                "m": 1, "km": 1000, "cm": .01, "mm": .001,
                "µm": 1e-6, "mile": 1609.344, "yard": .9144,
                "foot": .3048, "inch": .0254
            },
            "Masse": {
                "kg": 1, "g": .001, "mg": 1e-6,
                "tonne": 1000, "lb": .45359237, "oz": .028349523125
            },
            "Temps": {
                "s": 1, "ms": .001, "min": 60,
                "h": 3600, "jour": 86400, "semaine": 604800
            },
            "Vitesse": {
                "m/s": 1, "km/h": 1000/3600,
                "mph": 1609.344/3600, "knot": 1852/3600
            },
            "Aire": {
                "m²": 1, "km²": 1e6, "cm²": 1e-4,
                "ha": 10000, "acre": 4046.8564224
            },
            "Volume": {
                "m³": 1, "L": .001, "mL": 1e-6,
                "cm³": 1e-6, "gal US": .003785411784
            },
        }

    def refresh_converter(self):
        self.converter_category = self.converter_category_var.get()
        if self.converter_category == "Température":
            units = ["°C", "°F", "K"]
        else:
            units = list(self.converter_data()[self.converter_category].keys())

        self.converter_from["values"] = units
        self.converter_to["values"] = units

        if units:
            self.converter_from.set(units[0])
            self.converter_to.set(units[1] if len(units) > 1 else units[0])

    def convert_units(self):
        try:
            value = float(self.converter_value.get().replace(",", "."))
            category = self.converter_category
            src = self.converter_from.get()
            dst = self.converter_to.get()

            if category == "Température":
                result = self.convert_temperature(value, src, dst)
            else:
                data = self.converter_data()[category]
                base_value = value * data[src]
                result = base_value / data[dst]

            self.converter_result.set(
                f"Résultat : {self.format_number(result)} {dst}"
            )
            self.result.set(self.format_number(result))
            self.add_history(
                f"{value:g} {src} → {self.format_number(result)} {dst}"
            )
        except Exception as exc:
            self.show_error(str(exc))

    def convert_temperature(self, value, src, dst):
        if src == "°C":
            c = value
        elif src == "°F":
            c = (value - 32) * 5 / 9
        else:
            c = value - 273.15

        if dst == "°C":
            return c
        if dst == "°F":
            return c * 9 / 5 + 32
        return c + 273.15

    # --------------------------------------------------------
    # INSERTION / AFFICHAGE
    # --------------------------------------------------------

    def insert(self, text):
        self.display.insert(tk.INSERT, text)

    def insert_function(self, name):
        self.display.insert(tk.INSERT, f"{name}(")

    def clear(self):
        self.expression.set("")
        self.result.set("0")

    def backspace(self):
        pos = self.display.index(tk.INSERT)
        text = self.expression.get()
        if pos > 0:
            self.expression.set(text[:pos-1] + text[pos:])
            self.display.icursor(pos-1)

    def toggle_sign(self):
        text = self.expression.get().strip()
        if not text:
            return
        if text.startswith("-(") and text.endswith(")"):
            self.expression.set(text[2:-1])
        else:
            self.expression.set(f"-({text})")

    def factorial_current(self):
        text = self.expression.get().strip()
        if text:
            self.expression.set(f"factorial({text})")

    # --------------------------------------------------------
    # ANGLES
    # --------------------------------------------------------

    def cycle_angle_mode(self):
        order = ["DEG", "RAD", "GRAD"]
        self.angle_mode = order[(order.index(self.angle_mode) + 1) % 3]
        self.angle_var.set(self.angle_mode)
        self.set_mode("Scientifique")

    def angle_to_rad(self, x):
        if self.angle_mode == "DEG":
            return math.radians(x)
        if self.angle_mode == "GRAD":
            return x * math.pi / 200
        return x

    def rad_to_angle(self, x):
        if self.angle_mode == "DEG":
            return math.degrees(x)
        if self.angle_mode == "GRAD":
            return x * 200 / math.pi
        return x

    def build_angle_functions(self):
        funcs = self.evaluator.FUNCTIONS
        return funcs

    # --------------------------------------------------------
    # CALCUL
    # --------------------------------------------------------

    def preprocess_expression(self, expr):
        expr = expr.replace("×", "*").replace("÷", "/")
        expr = expr.replace("−", "-")
        expr = expr.replace("^", "**")
        expr = expr.replace("π", "pi")

        # Pourcentage simple : 50% devient 0.5.
        expr = re.sub(
            r"(?<![A-Za-z0-9_.])(\d+(?:\.\d+)?)%",
            r"(\1/100)",
            expr
        )

        # Factorielle postfixe : 5! -> factorial(5)
        while re.search(r"(\d+(?:\.\d+)?|\([^()]+\))!", expr):
            expr = re.sub(
                r"(\d+(?:\.\d+)?|\([^()]+\))!",
                r"factorial(\1)",
                expr,
                count=1
            )
        return expr

    def calculate(self):
        expr = self.expression.get().strip()
        if not expr:
            return

        try:
            prepared = self.preprocess_expression(expr)

            # Fonctions trigonométriques adaptées au mode d'angle.
            result = self.evaluate_with_angles(prepared)
            self.last_answer = result
            self.result.set(self.format_number(result))
            self.add_history(f"{expr} = {self.format_number(result)}")
        except Exception as exc:
            self.result.set("Erreur")
            self.show_error(self.friendly_error(exc))

    def evaluate_with_angles(self, expression):
        # Conversion contrôlée des appels trigonométriques.
        funcs = {
            "sin": lambda x: math.sin(self.angle_to_rad(x)),
            "cos": lambda x: math.cos(self.angle_to_rad(x)),
            "tan": lambda x: math.tan(self.angle_to_rad(x)),
            "asin": lambda x: self.rad_to_angle(math.asin(x)),
            "acos": lambda x: self.rad_to_angle(math.acos(x)),
            "atan": lambda x: self.rad_to_angle(math.atan(x)),
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "asinh": math.asinh,
            "acosh": math.acosh,
            "atanh": math.atanh,
        }

        # Évalue récursivement les appels trigonométriques avant
        # l'évaluation générale. Les autres fonctions restent dans
        # SafeEvaluator.
        tree = ast.parse(expression, mode="eval")

        def ev(node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id.lower()
                if name in funcs:
                    args = [ev(a) for a in node.args]
                    return funcs[name](*args)
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                    return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in SafeEvaluator.BIN_OPS:
                return SafeEvaluator.BIN_OPS[type(node.op)](ev(node.left), ev(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in SafeEvaluator.UNARY_OPS:
                return SafeEvaluator.UNARY_OPS[type(node.op)](ev(node.operand))
            if isinstance(node, ast.Name):
                if node.id in ("pi", "e"):
                    return SafeEvaluator.CONSTANTS[node.id]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id.lower()
                if name not in funcs and name in SafeEvaluator.FUNCTIONS:
                    return SafeEvaluator.FUNCTIONS[name](*[ev(a) for a in node.args])
            raise ValueError("Expression non autorisée.")

        return ev(tree.body)

    def friendly_error(self, exc):
        msg = str(exc)
        if isinstance(exc, ZeroDivisionError):
            return "Division par zéro impossible."
        if "math domain error" in msg:
            return "Valeur hors domaine mathématique."
        if "maximum recursion" in msg.lower():
            return "Expression trop complexe."
        return msg or "Calcul impossible."

    def format_number(self, value):
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, int):
            return str(value)
        if abs(value) < 1e-12:
            value = 0.0
        if float(value).is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"

    # --------------------------------------------------------
    # PROGRAMMEUR
    # --------------------------------------------------------

    def insert_programmer(self, text):
        base = self.programmer_base
        if text in "ABCDEF" and base != "HEX":
            return
        if text == "~":
            self.insert("~")
        else:
            self.insert(text)

    def parse_programmer_expression(self, expression, base):
        # Convertit les nombres écrits dans la base choisie vers des
        # nombres décimaux avant de laisser l'AST sécurisé les calculer.
        if not expression.strip():
            raise ValueError("Expression vide.")

        patterns = {
            "DEC": r"\d+",
            "BIN": r"[01]+",
            "OCT": r"[0-7]+",
            "HEX": r"(?:0x)?[0-9A-Fa-f]+",
        }
        token = patterns[base]

        def repl(match):
            s = match.group(0)
            if base == "HEX" and s.lower().startswith("0x"):
                return str(int(s, 16))
            return str(int(s, {"DEC":10, "BIN":2, "OCT":8, "HEX":16}[base]))

        return re.sub(token, repl, expression)

    def calculate_programmer(self):
        expr = self.expression.get().strip()
        if not expr:
            return
        try:
            prepared = expr.replace("AND", "&").replace("OR", "|").replace("XOR", "^")
            prepared = self.parse_programmer_expression(prepared, self.programmer_base)
            value = self.evaluate_integer_ast(prepared)
            self.last_answer = value
            self.result.set(self.format_programmer(value))
            self.add_history(
                f"[{self.programmer_base}] {expr} = {self.format_programmer(value)}"
            )
        except Exception as exc:
            self.result.set("Erreur")
            self.show_error(self.friendly_error(exc))

    def evaluate_integer_ast(self, expression):
        tree = ast.parse(expression, mode="eval")

        binary = {
            ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
            ast.FloorDiv: op.floordiv, ast.Mod: op.mod,
            ast.BitAnd: op.and_, ast.BitOr: op.or_,
            ast.BitXor: op.xor, ast.LShift: op.lshift,
            ast.RShift: op.rshift,
        }
        unary = {ast.UAdd: op.pos, ast.USub: op.neg, ast.Invert: op.invert}

        def ev(n):
            if isinstance(n, ast.Constant) and isinstance(n.value, int) and not isinstance(n.value, bool):
                return n.value
            if isinstance(n, ast.BinOp) and type(n.op) in binary:
                return binary[type(n.op)](ev(n.left), ev(n.right))
            if isinstance(n, ast.UnaryOp) and type(n.op) in unary:
                return unary[type(n.op)](ev(n.operand))
            raise ValueError("Opération programmeur non autorisée.")

        return ev(tree.body)

    def format_programmer(self, value):
        if self.programmer_base == "DEC":
            return str(value)
        if self.programmer_base == "BIN":
            return ("-" if value < 0 else "") + bin(abs(value))[2:]
        if self.programmer_base == "OCT":
            return ("-" if value < 0 else "") + oct(abs(value))[2:]
        return ("-" if value < 0 else "") + format(abs(value), "X")

    def change_programmer_base(self, base):
        try:
            current = self.expression.get().strip()
            if current:
                prepared = self.parse_programmer_expression(
                    current, self.programmer_base
                )
                value = self.evaluate_integer_ast(prepared)
                self.expression.set(self.format_for_base(value, base))
            self.programmer_base = base
            self.set_mode("Programmeur")
        except Exception:
            self.programmer_base = base
            self.set_mode("Programmeur")

    def format_for_base(self, value, base):
        if base == "DEC":
            return str(value)
        if base == "BIN":
            return bin(value)[2:] if value >= 0 else "-" + bin(-value)[2:]
        if base == "OCT":
            return oct(value)[2:] if value >= 0 else "-" + oct(-value)[2:]
        return format(value, "X") if value >= 0 else "-" + format(-value, "X")

    # --------------------------------------------------------
    # MÉMOIRE
    # --------------------------------------------------------

    def current_numeric_value(self):
        text = self.result.get()
        if text in ("Erreur", "0"):
            expr = self.expression.get().strip()
            if expr:
                try:
                    return float(self.evaluate_with_angles(self.preprocess_expression(expr)))
                except Exception:
                    pass
        return float(text)

    def memory_clear(self):
        self.memory = 0.0
        self.result.set("MC")

    def memory_recall(self):
        self.expression.set(self.format_number(self.memory))
        self.result.set(self.format_number(self.memory))

    def memory_store(self):
        self.memory = self.current_numeric_value()
        self.result.set("MS")

    def memory_add(self):
        self.memory += self.current_numeric_value()
        self.result.set("M+")

    def memory_sub(self):
        self.memory -= self.current_numeric_value()
        self.result.set("M-")

    # --------------------------------------------------------
    # HISTORIQUE
    # --------------------------------------------------------

    def add_history(self, text):
        self.history.insert(0, text)
        self.history = self.history[:100]
        if hasattr(self, "history_list"):
            self.refresh_history()

    def refresh_history(self):
        if not hasattr(self, "history_list"):
            return
        self.history_list.delete(0, tk.END)
        for item in self.history:
            self.history_list.insert(tk.END, item)

    def use_history(self, event=None):
        if not hasattr(self, "history_list"):
            return
        selection = self.history_list.curselection()
        if not selection:
            return
        item = self.history[selection[0]]
        if " = " in item:
            expr = item.split(" = ", 1)[0]
            if expr.startswith("[") and "] " in expr:
                expr = expr.split("] ", 1)[1]
            self.expression.set(expr)

    def clear_history(self):
        self.history.clear()
        self.refresh_history()

    # --------------------------------------------------------
    # CLAVIER / THÈME / ERREURS
    # --------------------------------------------------------

    def bind_keyboard(self):
        self.root.bind("<Return>", lambda e: self.calculate())
        self.root.bind("<KP_Enter>", lambda e: self.calculate())
        self.root.bind("<Escape>", lambda e: self.clear())
        self.root.bind("<BackSpace>", lambda e: self.backspace())

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()
        self.set_mode(self.mode)
        self.build_side_panel()

    def show_error(self, message):
        messagebox.showerror("Calculatrice Ultimate Pro", message)


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateCalculator(root)
    root.mainloop()
