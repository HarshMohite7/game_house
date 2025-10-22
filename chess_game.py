import tkinter as tk
from tkinter import messagebox
import chess
import random
import datetime
from db_config import get_db_connection
from PIL import Image, ImageTk
import os

class ChessGame:
    def __init__(self, parent, difficulty, username):
        self.parent = parent
        self.difficulty = difficulty
        self.username = username
        self.window = tk.Toplevel(parent)
        self.window.title("Chess Game")
        self.window.geometry("600x600")
        self.window.minsize(400, 400)
        self.window.configure(bg="#D3D3D3")
        
        self.board = chess.Board()
        self.square_size = 50
        self.selected_square = None
        self.legal_moves = []
        self.hovered_square = None
        self.hovered_legal_moves = []
        
        self.canvas = tk.Canvas(self.window, bg="#D3D3D3", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.piece_images = {}
        self.load_piece_images()
        
        # Timer variables (5 minutes = 300 seconds)
        self.white_time = 300
        self.black_time = 300
        self.timer_running = True
        self.timer_id = None
        
        self.window.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        self.window.bind("<KeyPress>", self.on_key_press)
        
        self.max_depth = {"easy": 1, "medium": 2, "hard": 3}[difficulty]
        
        self.draw_board()
        self.start_timer()
        if not self.board.turn:
            self.ai_move()

    def load_piece_images(self):
        pieces = {
            'P': 'wP.png',
            'N': 'wN.png',
            'B': 'wB.png',
            'R': 'wR.png',
            'Q': 'wQ.png',
            'K': 'wK.png',
            'p': 'bP.png',
            'n': 'bN.png',
            'b': 'bB.png',
            'r': 'bR.png',
            'q': 'bQ.png',
            'k': 'bK.png'
        }
        base_path = os.path.join("assets")
        for piece, filename in pieces.items():
            try:
                img_path = os.path.join(base_path, filename)
                if not os.path.exists(img_path):
                    raise FileNotFoundError(f"Image file {img_path} not found")
                img = Image.open(img_path)
                img = img.resize((self.square_size, self.square_size), Image.LANCZOS)
                self.piece_images[piece] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load image for {piece}: {e}")
                self.piece_images[piece] = None

    def start_timer(self):
        if self.timer_running:
            if self.board.turn == chess.WHITE:
                self.white_time -= 1
            else:
                self.black_time -= 1
            self.draw_board()
            if self.white_time <= 0:
                self.timer_running = False
                messagebox.showinfo("Game Over", "Time's up! Black wins")
                self.save_score(outcome="0-1")
                self.window.destroy()
                return
            if self.black_time <= 0:
                self.timer_running = False
                messagebox.showinfo("Game Over", "Time's up! White wins")
                self.save_score(outcome="1-0")
                self.window.destroy()
                return
            self.timer_id = self.window.after(1000, self.start_timer)

    def save_score(self, outcome=None):
        if not self.username:
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (self.username,))
            user_id = cursor.fetchone()
            if user_id:
                material_score = self.calculate_material_score()
                if outcome:
                    score = material_score
                else:
                    score = material_score
                cursor.execute(
                    "INSERT INTO game_scores (user_id, game_name, difficulty_level, score, played_at) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_id[0], "Chess", self.difficulty, score, datetime.datetime.now())
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to save score: {e}")

    def calculate_material_score(self):
        piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
        score = 0
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = piece_values.get(piece.symbol().lower(), 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        return score

    def on_mouse_move(self, event):
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row)
        
        if square != self.hovered_square:
            self.hovered_square = square
            piece = self.board.piece_at(square)
            self.hovered_legal_moves = []
            if piece and piece.color == chess.WHITE:
                self.hovered_legal_moves = [move for move in self.board.legal_moves if move.from_square == square]
            self.draw_board()

    def on_mouse_leave(self, event):
        self.hovered_square = None
        self.hovered_legal_moves = []
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        self.square_size = min(self.canvas.winfo_width(), self.canvas.winfo_height()) // 8
        
        for row in range(8):
            for col in range(8):
                x1, y1 = col * self.square_size, (7 - row) * self.square_size
                x2, y2 = x1 + self.square_size, y1 + self.square_size
                color = "#FFFFFF" if (row + col) % 2 == 0 else "#769656"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = 7 - chess.square_rank(square), chess.square_file(square)
                x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                if self.piece_images.get(piece.symbol()):
                    self.canvas.create_image(x, y, image=self.piece_images[piece.symbol()])
                else:
                    self.canvas.create_text(x, y, text=piece.symbol(), font=("Arial", self.square_size // 2), fill="#800000")
        
        if self.selected_square is not None:
            row, col = 7 - chess.square_rank(self.selected_square), chess.square_file(self.selected_square)
            x1, y1 = col * self.square_size, row * self.square_size
            self.canvas.create_rectangle(x1, y1, x1 + self.square_size, y1 + self.square_size, outline="#CD5C5C", width=3)
            
            for move in self.legal_moves:
                dest_square = move.to_square
                row, col = 7 - chess.square_rank(dest_square), chess.square_file(dest_square)
                x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="#00FFFF", outline="")
        
        if self.hovered_square is not None:
            row, col = 7 - chess.square_rank(self.hovered_square), chess.square_file(self.hovered_square)
            x1, y1 = col * self.square_size, row * self.square_size
            self.canvas.create_rectangle(x1, y1, x1 + self.square_size, y1 + self.square_size, outline="#00FFFF", width=2)
            for move in self.hovered_legal_moves:
                dest_square = move.to_square
                row, col = 7 - chess.square_rank(dest_square), chess.square_file(dest_square)
                x, y = col * self.square_size + self.square_size // 2, row * self.square_size + self.square_size // 2
                self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="#00FFFF", outline="")
        
        # Draw timers
        white_time_str = f"White: {self.white_time // 60}:{self.white_time % 60:02d}"
        black_time_str = f"Black: {self.black_time // 60}:{self.black_time % 60:02d}"
        self.canvas.create_text(10, 10, text=white_time_str, anchor="nw", font=("Arial", 12), fill="#800000")
        self.canvas.create_text(10, self.canvas.winfo_height() - 10, text=black_time_str, anchor="sw", font=("Arial", 12), fill="#800000")

    def on_resize(self, event):
        old_size = self.square_size
        self.square_size = min(self.canvas.winfo_width(), self.canvas.winfo_height()) // 8
        if self.square_size != old_size:
            self.load_piece_images()  # Reload images for new size
        self.draw_board()

    def on_click(self, event):
        if self.board.turn == chess.BLACK or not self.timer_running:
            return
        
        col = event.x // self.square_size
        row = 7 - (event.y // self.square_size)
        square = chess.square(col, row)
        
        if self.selected_square == square:
            self.selected_square = None
            self.legal_moves = []
            self.draw_board()
        else:
            piece = self.board.piece_at(square)
            if piece and piece.color == chess.WHITE:
                self.selected_square = square
                self.legal_moves = list(self.board.legal_moves)
                self.legal_moves = [move for move in self.legal_moves if move.from_square == square]
                self.draw_board()
            else:
                for move in self.legal_moves:
                    if move.to_square == square:
                        self.board.push(move)
                        self.selected_square = None
                        self.legal_moves = []
                        self.draw_board()
                        if self.board.is_game_over():
                            self.handle_game_over()
                        elif self.board.turn == chess.BLACK:
                            self.ai_move()

    def on_key_press(self, event):
        if event.keysym == "Escape":
            self.timer_running = False
            if self.timer_id:
                self.window.after_cancel(self.timer_id)
            self.save_score()
            self.window.destroy()

    def handle_game_over(self):
        self.timer_running = False
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        outcome = self.board.outcome()
        if outcome:
            if outcome.winner == chess.WHITE:
                message = "Checkmate! White wins"
            elif outcome.winner == chess.BLACK:
                message = "Checkmate! Black wins"
            else:
                if self.board.is_stalemate():
                    message = "Stalemate! Draw"
                elif self.board.is_insufficient_material():
                    message = "Draw by insufficient material"
                elif self.board.is_seventyfive_moves():
                    message = "Draw by 75-move rule"
                elif self.board.is_fivefold_repetition():
                    message = "Draw by fivefold repetition"
                else:
                    message = "Draw"
            messagebox.showinfo("Game Over", message)
            self.save_score(outcome=outcome.result())
        else:
            messagebox.showinfo("Game Over", "Game ended")
            self.save_score()
        self.window.destroy()

    def ai_move(self):
        if not self.timer_running:
            return
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return
        
        def evaluate_board(board):
            piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
            score = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    value = piece_values.get(piece.symbol().lower(), 0)
                    if piece.color == chess.WHITE:
                        score += value
                    else:
                        score -= value
            return score

        def minimax(board, depth, maximizing_player):
            if depth == 0 or board.is_game_over():
                return evaluate_board(board)
            
            if maximizing_player:
                max_eval = float('-inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = minimax(board, depth - 1, False)
                    board.pop()
                    max_eval = max(max_eval, eval_score)
                return max_eval
            else:
                min_eval = float('inf')
                for move in board.legal_moves:
                    board.push(move)
                    eval_score = minimax(board, depth - 1, True)
                    board.pop()
                min_eval = min(min_eval, eval_score)
                return min_eval

        best_score = float('inf')
        best_move = None
        for move in legal_moves:
            self.board.push(move)
            score = minimax(self.board, self.max_depth - 1, True)
            self.board.pop()
            if score < best_score:
                best_score = score
                best_move = move
        
        if best_move:
            self.board.push(best_move)
            self.draw_board()
            if self.board.is_game_over():
                self.handle_game_over()