import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os
from db_config import get_db_connection
import datetime
import winsound

class SnakeGame:
    def __init__(self, parent, difficulty, username):
        self.parent = parent
        self.difficulty = difficulty
        self.username = username
        self.window = tk.Toplevel(parent)
        self.window.title("Snake Game")
        self.window.geometry("800x600")
        self.window.minsize(400, 400)
        self.window.configure(bg="#1a1a2e")  # Dark gaming theme

        self.canvas = tk.Canvas(self.window, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.width, self.height = 800, 600
        self.grid_size = 20
        self.snake = [(10, 10)]
        self.fruit = self.spawn_fruit()
        self.direction = 'right'
        self.next_direction = 'right'
        self.fps = {'easy': 10, 'medium': 15, 'hard': 20}[difficulty]
        self.running = True
        self.score = 0
        self.state = "menu"
        self.image_cache = {}
        self.photo_images = {}
        self.load_images()

        self.font_size = max(16, self.width // 30)

        self.window.bind("<KeyPress>", self.on_key_press)
        self.window.bind("<Configure>", self.on_resize)

        self.draw_menu()
        self.update()

    def load_images(self):
        image_paths = {
            'bg_image': os.path.join('assets', 'grass.png'),
            'snake_image': os.path.join('assets', 'snake.png'),
            'fruit_image': os.path.join('assets', 'fruit.png')
        }
        for key, path in image_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                else:
                    raise FileNotFoundError(f"{path} not found")
                if key == 'bg_image':
                    img = img.resize((self.width, self.height), Image.LANCZOS)
                else:
                    img = img.resize((self.grid_size, self.grid_size), Image.LANCZOS)
                self.image_cache[key] = img
                self.photo_images[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load {key}: {e}")
                self.image_cache[key] = None
                self.photo_images[key] = None
        self.bg_image = self.photo_images.get('bg_image')
        self.snake_image = self.photo_images.get('snake_image')
        self.fruit_image = self.photo_images.get('fruit_image')

    def save_score(self):
        if not self.username:
            return
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (self.username,))
            user_id = cursor.fetchone()
            if user_id:
                cursor.execute(
                    "INSERT INTO game_scores (user_id, game_name, difficulty_level, score, played_at) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (user_id[0], "Snake", self.difficulty, self.score, datetime.datetime.now())
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to save score: {e}")

    def spawn_fruit(self):
        while True:
            fruit = (random.randint(0, self.width // self.grid_size - 1),
                     random.randint(0, self.height // self.grid_size - 1))
            if fruit not in self.snake:
                return fruit

    def on_resize(self, event):
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.grid_size = min(self.width, self.height) // 20
        self.font_size = max(16, self.width // 30)
        if self.image_cache.get('bg_image'):
            self.photo_images['bg_image'] = ImageTk.PhotoImage(
                self.image_cache['bg_image'].resize((self.width, self.height), Image.LANCZOS)
            )
            self.bg_image = self.photo_images['bg_image']
        if self.image_cache.get('snake_image'):
            self.photo_images['snake_image'] = ImageTk.PhotoImage(
                self.image_cache['snake_image'].resize((self.grid_size, self.grid_size), Image.LANCZOS)
            )
            self.snake_image = self.photo_images['snake_image']
        if self.image_cache.get('fruit_image'):
            self.photo_images['fruit_image'] = ImageTk.PhotoImage(
                self.image_cache['fruit_image'].resize((self.grid_size, self.grid_size), Image.LANCZOS)
            )
            self.fruit_image = self.photo_images['fruit_image']
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_gameover()

    def on_key_press(self, event):
        if event.keysym == "Escape":
            self.running = False
            self.save_score()
            self.window.destroy()
        elif self.state == "menu":
            if event.keysym == "space":
                try:
                    winsound.Beep(1000, 100)
                except:
                    pass
                self.state = "playing"
                self.draw_game()
        elif self.state == "gameover":
            if event.keysym == "r":
                try:
                    winsound.Beep(1000, 100)
                except:
                    pass
                self.reset()
        elif self.state == "playing":
            if event.keysym == "Up" and self.direction != 'down':
                self.next_direction = 'up'
            elif event.keysym == "Down" and self.direction != 'up':
                self.next_direction = 'down'
            elif event.keysym == "Left" and self.direction != 'right':
                self.next_direction = 'left'
            elif event.keysym == "Right" and self.direction != 'left':
                self.next_direction = 'right'

    def reset(self):
        self.snake = [(10, 10)]
        self.fruit = self.spawn_fruit()
        self.direction = 'right'
        self.next_direction = 'right'
        self.score = 0
        self.state = "playing"
        self.draw_game()

    def draw_menu(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")
        self.canvas.create_text(
            self.width // 2, 200, text="Snake Game", fill="#00ffcc",
            font=("Impact", self.font_size + 4, "bold"), anchor="center"
        )
        self.canvas.create_text(
            self.width // 2, 250, text="Press [SPACE] to Start", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center"
        )
        self.canvas.create_text(
            self.width // 2, 290, text="Press [ESC] to Quit", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center"
        )
        self.animate_text()  # Start text animation

    def draw_gameover(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")
        self.canvas.create_text(
            self.width // 2, 200, text="Game Over!", fill="#ff0066",
            font=("Impact", self.font_size + 4, "bold"), anchor="center"
        )
        self.canvas.create_text(
            self.width // 2, 250, text=f"Score: {self.score}", fill="#00ffcc",
            font=("Arial Black", self.font_size, "bold"), anchor="center"
        )
        self.canvas.create_text(
            self.width // 2, 290, text="Press [R] to Retry or [ESC] to Quit", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center"
        )
        self.animate_text()

    def animate_text(self):
        colors = ["#00ffcc", "#ffcc00"]
        current_color = self.canvas.itemcget("text1", "fill") if self.canvas.find_withtag("text1") else colors[0]
        next_color = colors[1] if current_color == colors[0] else colors[0]
        for tag in ["text1", "text2", "text3"]:
            if self.canvas.find_withtag(tag):
                self.canvas.itemconfig(tag, fill=next_color)
        if self.state in ["menu", "gameover"]:
            self.window.after(1000, self.animate_text)

    def draw_game(self):
        self.canvas.delete("all")
        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")

        # Draw grid overlay
        for x in range(0, self.width, self.grid_size):
            self.canvas.create_line(x, 0, x, self.height, fill="#2e2e4e", width=1)
        for y in range(0, self.height, self.grid_size):
            self.canvas.create_line(0, y, self.width, y, fill="#2e2e4e", width=1)

        for segment in self.snake:
            x, y = segment[0] * self.grid_size, segment[1] * self.grid_size
            if self.snake_image:
                self.canvas.create_image(x + self.grid_size // 2, y + self.grid_size // 2,
                                        image=self.snake_image, anchor="center")
            else:
                self.canvas.create_rectangle(x, y, x + self.grid_size, y + self.grid_size,
                                            fill="#00ffcc", outline="#ff0066")

        fx, fy = self.fruit[0] * self.grid_size, self.fruit[1] * self.grid_size
        if self.fruit_image:
            self.canvas.create_image(fx + self.grid_size // 2, fy + self.grid_size // 2,
                                    image=self.fruit_image, anchor="center")
        else:
            self.canvas.create_rectangle(fx, fy, fx + self.grid_size, fy + self.grid_size,
                                        fill="#ff0066", outline="#ffffff")

        self.canvas.create_text(
            10, 10, text=f"Score: {self.score}", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="nw", tag="score"
        )

    def update(self):
        if not self.running:
            return

        if self.state == "playing":
            self.direction = self.next_direction
            head = list(self.snake[0])
            if self.direction == 'up':
                head[1] -= 1
            elif self.direction == 'down':
                head[1] += 1
            elif self.direction == 'left':
                head[0] -= 1
            elif self.direction == 'right':
                head[0] += 1

            head[0] = head[0] % (self.width // self.grid_size)
            head[1] = head[1] % (self.height // self.grid_size)
            self.snake.insert(0, tuple(head))

            if tuple(head) == self.fruit:
                try:
                    winsound.Beep(1200, 100)
                except:
                    pass
                self.score += 10
                self.fruit = self.spawn_fruit()
            else:
                self.snake.pop()

            if tuple(head) in self.snake[1:]:
                self.running = False
                self.state = "gameover"
                self.save_score()
                self.draw_gameover()
                return

            self.draw_game()

        self.window.after(1000 // self.fps, self.update)