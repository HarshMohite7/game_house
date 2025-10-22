import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk
import os
from db_config import get_db_connection
import datetime
import winsound

class CarRacingGame:
    def __init__(self, parent, difficulty, username):
        self.parent = parent
        self.difficulty = difficulty
        self.username = username
        self.window = tk.Toplevel(parent)
        self.window.title("Car Racing")
        self.window.geometry("500x700")
        self.window.minsize(300, 400)
        self.window.configure(bg="#1a1a2e")  # Dark gaming theme

        self.canvas = tk.Canvas(self.window, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.width, self.height = 500, 700
        self.road_rect = [self.width // 5, 0, self.width * 3 // 5, self.height]
        self.player_car = {'x': self.width // 2 - 25, 'y': self.height - 120}
        self.opponent_cars = [{'x': random.randint(self.road_rect[0], self.road_rect[0] + self.road_rect[2] - 50), 'y': -100}]
        self.speed = {'easy': 5, 'medium': 10, 'hard': 15}[difficulty]
        self.spawn_interval = {'easy': 60, 'medium': 45, 'hard': 30}[difficulty]
        self.spawn_timer = 0
        self.score = 0
        self.state = "menu"
        self.speed_increase = 0
        self.lane_offset = 0
        self.fps = 60
        self.running = True
        self.lane_pulse = 0

        self.image_cache = {}
        self.photo_images = {}
        self.load_images()

        self.font_size = max(16, self.width // 30)

        self.window.bind("<Configure>", self.on_resize)
        self.window.bind("<KeyPress>", self.on_key_press)
        self.window.bind("<KeyRelease>", self.on_key_release)

        self.move_left = False
        self.move_right = False

        self.draw_menu()
        self.update()

    def load_images(self):
        image_paths = {
            'car_img': os.path.join('assets', 'car.png'),
            'enemy_img': os.path.join('assets', 'enemy_car.png'),
            'grass_img': os.path.join('assets', 'grass.png')
        }
        for key, path in image_paths.items():
            try:
                if os.path.exists(path):
                    img = Image.open(path)
                else:
                    raise FileNotFoundError(f"{path} not found")
                if key in ['car_img', 'enemy_img']:
                    img = img.resize((50, 100), Image.LANCZOS)
                else:
                    img = img.resize((150, 150), Image.LANCZOS)
                self.image_cache[key] = img
                self.photo_images[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load {key}: {e}")
                self.image_cache[key] = None
                self.photo_images[key] = None
        self.car_img = self.photo_images.get('car_img')
        self.enemy_img = self.photo_images.get('enemy_img')
        self.grass_img = self.photo_images.get('grass_img')

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
                    (user_id[0], "Car Racing", self.difficulty, self.score, datetime.datetime.now())
                )
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to save score: {e}")

    def on_resize(self, event):
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        self.road_rect = [self.width // 5, 0, self.width * 3 // 5, self.height]
        self.player_car['x'] = max(self.road_rect[0], min(self.player_car['x'], self.road_rect[0] + self.road_rect[2] - self.width // 10))
        self.player_car['y'] = self.height - 120
        self.font_size = max(16, self.width // 30)

        for key, img in self.image_cache.items():
            if img:
                if key in ['car_img', 'enemy_img']:
                    size = (self.width // 10, self.width // 5)
                else:
                    size = (self.width // 5, self.width // 5)
                self.photo_images[key] = ImageTk.PhotoImage(img.resize(size, Image.LANCZOS))
        self.car_img = self.photo_images.get('car_img')
        self.enemy_img = self.photo_images.get('enemy_img')
        self.grass_img = self.photo_images.get('grass_img')

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
            if event.keysym == "Left":
                self.move_left = True
            elif event.keysym == "Right":
                self.move_right = True

    def on_key_release(self, event):
        if event.keysym == "Left":
            self.move_left = False
        elif event.keysym == "Right":
            self.move_right = False

    def reset(self):
        self.player_car = {'x': self.width // 2 - self.width // 20, 'y': self.height - 120}
        self.opponent_cars = [{'x': random.randint(self.road_rect[0], self.road_rect[0] + self.road_rect[2] - self.width // 10), 'y': -100}]
        self.score = 0
        self.spawn_timer = 0
        self.spawn_interval = {'easy': 60, 'medium': 45, 'hard': 30}[self.difficulty]
        self.speed_increase = 0
        self.lane_offset = 0
        self.state = "playing"
        self.draw_game()

    def draw_road(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#646464")
        self.canvas.create_rectangle(
            self.road_rect[0], self.road_rect[1],
            self.road_rect[0] + self.road_rect[2], self.road_rect[3],
            fill="#1a1a2e", outline="#00ffcc", width=3
        )
        self.lane_offset = (self.lane_offset + 5) % 35
        self.lane_pulse = (self.lane_pulse + 1) % 20
        lane_color = "#ffffff" if self.lane_pulse < 10 else "#cccccc"
        for y in range(-int(self.lane_offset), self.height, 35):
            self.canvas.create_line(
                self.road_rect[0] + self.road_rect[2] // 2, y,
                self.road_rect[0] + self.road_rect[2] // 2, y + 20,
                fill=lane_color, width=5
            )

    def draw_grass(self):
        for y in range(0, self.height, self.width // 5):
            if self.grass_img:
                self.canvas.create_image(0, y, image=self.grass_img, anchor="nw")
                self.canvas.create_image(self.width * 4 // 5, y, image=self.grass_img, anchor="nw")
            else:
                self.canvas.create_rectangle(
                    0, y, self.width // 5, y + self.width // 5, fill="#228B22"
                )
                self.canvas.create_rectangle(
                    self.width * 4 // 5, y, self.width, y + self.width // 5, fill="#228B22"
                )
        # Add grid overlay on grass
        for x in range(0, self.width // 5, 20):
            self.canvas.create_line(x, 0, x, self.height, fill="#2e2e4e", width=1)
            self.canvas.create_line(self.width * 4 // 5 + x, 0, self.width * 4 // 5 + x, self.height, fill="#2e2e4e", width=1)
        for y in range(0, self.height, 20):
            self.canvas.create_line(0, y, self.width // 5, y, fill="#2e2e4e", width=1)
            self.canvas.create_line(self.width * 4 // 5, y, self.width, y, fill="#2e2e4e", width=1)

    def draw_ui(self):
        self.canvas.create_text(
            10, 10, text=f"Score: {self.score}", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="nw", tag="score"
        )

    def draw_menu(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")
        self.canvas.create_text(
            self.width // 2, 200, text="Car Racing Game", fill="#00ffcc",
            font=("Impact", self.font_size + 4, "bold"), anchor="center", tag="text1"
        )
        self.canvas.create_text(
            self.width // 2, 250, text="Press [SPACE] to Start", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center", tag="text2"
        )
        self.canvas.create_text(
            self.width // 2, 290, text="Press [ESC] to Quit", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center", tag="text3"
        )
        self.animate_text()

    def draw_gameover(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")
        self.canvas.create_text(
            self.width // 2, 200, text="Game Over!", fill="#ff0066",
            font=("Impact", self.font_size + 4, "bold"), anchor="center", tag="text1"
        )
        self.canvas.create_text(
            self.width // 2, 250, text=f"Score: {self.score}", fill="#00ffcc",
            font=("Arial Black", self.font_size, "bold"), anchor="center", tag="text2"
        )
        self.canvas.create_text(
            self.width // 2, 290, text="Press [R] to Retry or [ESC] to Quit", fill="#ffcc00",
            font=("Arial Black", self.font_size, "bold"), anchor="center", tag="text3"
        )
        self.animate_text()

    def animate_text(self):
        if self.state in ["menu", "gameover"]:
            colors = ["#00ffcc", "#ffcc00"]
            current_color = self.canvas.itemcget("text1", "fill") if self.canvas.find_withtag("text1") else colors[0]
            next_color = colors[1] if current_color == colors[0] else colors[0]
            for tag in ["text1", "text2", "text3"]:
                if self.canvas.find_withtag(tag):
                    self.canvas.itemconfig(tag, fill=next_color)
            self.window.after(1000, self.animate_text)

    def draw_game(self):
        self.draw_road()
        self.draw_grass()
        if self.car_img:
            self.canvas.create_image(
                self.player_car['x'] + self.width // 20, self.player_car['y'] + self.width // 10,
                image=self.car_img, anchor="center"
            )
        else:
            self.canvas.create_rectangle(
                self.player_car['x'], self.player_car['y'],
                self.player_car['x'] + self.width // 10, self.player_car['y'] + self.width // 5,
                fill="#ff0066", outline="#00ffcc"
            )
        for car in self.opponent_cars:
            if self.enemy_img:
                self.canvas.create_image(
                    car['x'] + self.width // 20, car['y'] + self.width // 10,
                    image=self.enemy_img, anchor="center"
                )
            else:
                self.canvas.create_rectangle(
                    car['x'], car['y'],
                    car['x'] + self.width // 10, car['y'] + self.width // 5,
                    fill="#ffcc00", outline="#00ffcc"
                )
        self.draw_ui()

    def spawn_enemy(self):
        lanes = [self.road_rect[0] + i * (self.road_rect[2] // 3) for i in range(3)]
        x = random.choice([l for l in lanes if all(abs(l - car['x']) > self.width // 10 for car in self.opponent_cars)])
        self.opponent_cars.append({'x': x, 'y': -100})

    def check_collision(self):
        player_rect = [self.player_car['x'], self.player_car['y'], self.width // 10, self.width // 5]
        for car in self.opponent_cars:
            enemy_rect = [car['x'], car['y'], self.width // 10, self.width // 5]
            if (abs(player_rect[0] - enemy_rect[0]) < player_rect[2] and
                abs(player_rect[1] - enemy_rect[1]) < player_rect[3]):
                try:
                    winsound.Beep(800, 200)
                except:
                    pass
                self.state = "gameover"
                self.draw_gameover()

    def update(self):
        if not self.running:
            return

        if self.state == "playing":
            if self.move_left and self.player_car['x'] > self.road_rect[0]:
                self.player_car['x'] -= 7
            if self.move_right and self.player_car['x'] < self.road_rect[0] + self.road_rect[2] - self.width // 10:
                self.player_car['x'] += 7

            for car in self.opponent_cars[:]:
                car['y'] += self.speed + self.speed_increase
                if car['y'] > self.height:
                    self.opponent_cars.remove(car)
                    self.score += {'easy': 10, 'medium': 15, 'hard': 20}[self.difficulty]
                    try:
                        winsound.Beep(1200, 100)
                    except:
                        pass

            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_enemy()
                self.spawn_timer = 0
                if self.spawn_interval > 30:
                    self.spawn_interval -= 1
                    self.speed_increase += 0.1

            self.score += 1
            self.check_collision()

            self.draw_game()

        self.window.after(1000 // self.fps, self.update)