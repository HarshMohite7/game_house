
import tkinter as tk
from tkinter import messagebox
import random
from db_config import get_db_connection
import datetime

class TicTacToeGame:
    def __init__(self, parent, difficulty, username):
        self.parent = parent
        self.difficulty = difficulty
        self.username = username
        self.window = tk.Toplevel(parent)
        self.window.title("Tic Tac Toe")
        self.window.geometry("400x400")
        self.window.minsize(300, 300)
        self.window.configure(bg="#D3D3D3")
        
        self.board = [""] * 9
        self.current_player = "X"
        self.buttons = []
        self.window.grid_columnconfigure(tuple(range(3)), weight=1)
        self.window.grid_rowconfigure(tuple(range(3)), weight=1)
        self.window.grid_rowconfigure(3, weight=1)
        
        self.font_size = 16
        for i in range(3):
            row = []
            for j in range(3):
                button = tk.Button(
                    self.window,
                    text="",
                    font=("Arial", self.font_size),
                    bg="#eeeed2",
                    activebackground="#00FFFF",
                    command=lambda x=i, y=j: self.button_click(x, y)
                )
                button.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)
                row.append(button)
            self.buttons.append(row)
        
        self.status_label = tk.Label(
            self.window,
            text="Your turn (X)",
            bg="#D3D3D3",
            fg="#800000",
            font=("Arial", 12)
        )
        self.status_label.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.window.bind("<Configure>", self.on_resize)
        if self.difficulty == 'easy' and random.choice([True, False]):
            self.ai_move()

    def save_score(self):
        if not self.username:
            return
        score = 100 if self.check_winner("X") else 50 if self.check_winner("O") else 0
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (self.username,))
            user_id = cursor.fetchone()
            if user_id:
                cursor.execute(
                    "INSERT INTO game_scores (user_id, game_name, difficulty_level, score, played_at) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_id[0], "Tic Tac Toe", self.difficulty, score, datetime.datetime.now())
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to save score: {e}")

    def on_resize(self, event):
        self.font_size = max(12, min(20, self.window.winfo_width() // 20))
        for row in self.buttons:
            for button in row:
                button.config(font=("Arial", self.font_size))
        self.status_label.config(font=("Arial", self.font_size // 2))

    def button_click(self, row, col):
        if self.board[row * 3 + col] == "":
            self.board[row * 3 + col] = self.current_player
            self.buttons[row][col].config(text=self.current_player, fg="#800000" if self.current_player == "X" else "#CD5C5C")
            if self.check_winner(self.current_player):
                self.save_score()
                messagebox.showinfo("Game Over", f"Player {self.current_player} wins!")
                self.window.destroy()
                return
            if "" not in self.board:
                self.save_score()
                messagebox.showinfo("Game Over", "It's a tie!")
                self.window.destroy()
                return
            self.current_player = "O" if self.current_player == "X" else "X"
            self.status_label.config(text=f"{'Your turn (X)' if self.current_player == 'X' else 'AI turn (O)'}")
            if self.current_player == "O":
                self.ai_move()

    def ai_move(self):
        moves = [i for i, x in enumerate(self.board) if x == ""]
        if not moves:
            return
        if self.difficulty == "easy":
            move = random.choice(moves)
        elif self.difficulty == "medium":
            move = self.best_move(3) or random.choice(moves)
        else:
            move = self.best_move(9) or random.choice(moves)
        self.board[move] = "O"
        row, col = divmod(move, 3)
        self.buttons[row][col].config(text="O", fg="#CD5C5C")
        if self.check_winner("O"):
            self.save_score()
            messagebox.showinfo("Game Over", "AI (O) wins!")
            self.window.destroy()
            return
        if "" not in self.board:
            self.save_score()
            messagebox.showinfo("Game Over", "It's a tie!")
            self.window.destroy()
            return
        self.current_player = "X"
        self.status_label.config(text="Your turn (X)")

    def check_winner(self, player):
        win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        return any(self.board[a] == self.board[b] == self.board[c] == player for a, b, c in win_conditions)

    def best_move(self, depth):
        best_score = float('-inf')
        best_move = None
        for move in [i for i, x in enumerate(self.board) if x == ""]:
            self.board[move] = "O"
            score = self.minimax(depth - 1, False)
            self.board[move] = ""
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, depth, is_maximizing):
        if self.check_winner("O"):
            return 1
        if self.check_winner("X"):
            return -1
        if "" not in self.board or depth == 0:
            return 0
        if is_maximizing:
            best_score = float('-inf')
            for move in [i for i, x in enumerate(self.board) if x == ""]:
                self.board[move] = "O"
                score = self.minimax(depth - 1, False)
                self.board[move] = ""
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for move in [i for i, x in enumerate(self.board) if x == ""]:
                self.board[move] = "X"
                score = self.minimax(depth - 1, True)
                self.board[move] = ""
                best_score = min(best_score, score)
            return best_score
