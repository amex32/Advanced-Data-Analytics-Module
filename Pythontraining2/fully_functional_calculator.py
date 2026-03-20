import tkinter as tk
from tkinter import ttk
import math

class ScientificCalculator:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Scientific Calculator")
        self.root.geometry("420x620")
        self.dark_mode = True

        self.expression = ""

        self.display = tk.Entry(root, font=("Arial", 22), bd=10, relief=tk.RIDGE, justify="right")
        self.display.pack(fill="both", padx=10, pady=10)

        self.history = tk.Text(root, height=4, font=("Arial", 10))
        self.history.pack(fill="both", padx=10)

        self.create_buttons()

        toggle_btn = tk.Button(root, text="Toggle Dark/Light Mode", command=self.toggle_mode)
        toggle_btn.pack(fill="x", padx=10, pady=5)

        self.apply_theme()

    def press(self, value):
        self.expression += str(value)
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

    def clear(self):
        self.expression = ""
        self.display.delete(0, tk.END)

    def delete(self):
        self.expression = self.expression[:-1]
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

    def evaluate(self):
        try:
            expr = self.expression

            expr = expr.replace("π", str(math.pi))
            expr = expr.replace("e", str(math.e))
            expr = expr.replace("^", "**")

            result = eval(expr, {"__builtins__": None}, math.__dict__)

            self.history.insert(tk.END, f"{self.expression} = {result}\n")
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, str(result))
            self.expression = str(result)

        except:
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, "Error")
            self.expression = ""

    def create_buttons(self):

        frame = tk.Frame(self.root)
        frame.pack()

        buttons = [
            ('7','8','9','/','sin'),
            ('4','5','6','*','cos'),
            ('1','2','3','-','tan'),
            ('0','.','+','=','sqrt'),
            ('(',')','^','log','ln'),
            ('π','e','!','DEL','C')
        ]

        for r,row in enumerate(buttons):
            for c,btn in enumerate(row):

                action = lambda x=btn:self.button_action(x)

                tk.Button(frame,
                          text=btn,
                          width=7,
                          height=3,
                          font=("Arial",14),
                          command=action).grid(row=r,column=c,padx=3,pady=3)

    def button_action(self,btn):

        if btn == "=":
            self.evaluate()

        elif btn == "C":
            self.clear()

        elif btn == "DEL":
            self.delete()

        elif btn == "sqrt":
            self.press("math.sqrt(")

        elif btn == "sin":
            self.press("math.sin(")

        elif btn == "cos":
            self.press("math.cos(")

        elif btn == "tan":
            self.press("math.tan(")

        elif btn == "log":
            self.press("math.log10(")

        elif btn == "ln":
            self.press("math.log(")

        elif btn == "!":
            self.press("math.factorial(")

        else:
            self.press(btn)

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):

        if self.dark_mode:

            bg = "#1e1e1e"
            fg = "white"
            entry_bg = "#2d2d2d"

        else:

            bg = "white"
            fg = "black"
            entry_bg = "#f4f4f4"

        self.root.configure(bg=bg)
        self.display.configure(bg=entry_bg, fg=fg, insertbackground=fg)
        self.history.configure(bg=entry_bg, fg=fg)

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg)
                for child in widget.winfo_children():
                    child.configure(bg=entry_bg, fg=fg, activebackground=bg)


if __name__ == "__main__":
    root = tk.Tk()
    app = ScientificCalculator(root)
    root.mainloop()