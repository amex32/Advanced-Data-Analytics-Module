import tkinter as tk
from tkinter import messagebox

# Create window
root = tk.Tk()
root.title("Tic Tac Toe ❌⭕")
root.geometry("300x350")

current_player = "X"
buttons = []

# Check winner
def check_winner():
    for row in range(3):
        if buttons[row][0]["text"] == buttons[row][1]["text"] == buttons[row][2]["text"] != "":
            return True

    for col in range(3):
        if buttons[0][col]["text"] == buttons[1][col]["text"] == buttons[2][col]["text"] != "":
            return True

    if buttons[0][0]["text"] == buttons[1][1]["text"] == buttons[2][2]["text"] != "":
        return True

    if buttons[0][2]["text"] == buttons[1][1]["text"] == buttons[2][0]["text"] != "":
        return True

    return False

# Check draw
def check_draw():
    for row in buttons:
        for btn in row:
            if btn["text"] == "":
                return False
    return True

# Button click
def on_click(row, col):
    global current_player

    if buttons[row][col]["text"] == "":
        buttons[row][col]["text"] = current_player

        if check_winner():
            messagebox.showinfo("Game Over", f"Player {current_player} wins! 🎉")
            reset_game()
        elif check_draw():
            messagebox.showinfo("Game Over", "It's a draw! 🤝")
            reset_game()
        else:
            current_player = "O" if current_player == "X" else "X"

# Reset game
def reset_game():
    global current_player
    current_player = "X"
    for row in buttons:
        for btn in row:
            btn["text"] = ""

# Create grid
frame = tk.Frame(root)
frame.pack(pady=20)

for i in range(3):
    row = []
    for j in range(3):
        btn = tk.Button(frame, text="", font=("Arial", 20), width=5, height=2,
                        command=lambda r=i, c=j: on_click(r, c))
        btn.grid(row=i, column=j)
        row.append(btn)
    buttons.append(row)

# Restart button
restart_btn = tk.Button(root, text="Restart 🔄", command=reset_game)
restart_btn.pack(pady=10)

# Run app
root.mainloop()