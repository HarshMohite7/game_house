import tkinter as tk
from tkinter import ttk, messagebox
from utils.auth import LoginWindow, SignupWindow, ContactWindow
from db_config import get_db_connection
from tic_tac_toe import TicTacToeGame
from snake_game import SnakeGame
from car_racing import CarRacingGame
from chess_game import ChessGame
import traceback

print("Starting main.py...")

try:
    class GamePortal:
        def __init__(self, root):
            print("Initializing GamePortal...")
            self.root = root
            self.root.title("GameZone Portal")
            self.root.geometry("800x600")
            self.root.minsize(600, 400)
            self.root.configure(bg="#1a1a2e")  # Dark gaming theme background
            self.username = None  # Initialize username as None

            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_rowconfigure(1, weight=1)
            self.root.grid_rowconfigure(2, weight=1)
            self.root.grid_rowconfigure(3, weight=1)
            self.root.grid_rowconfigure(4, weight=1)

            # Title label with gaming font and neon glow effect
            self.title_label = tk.Label(
                self.root,
                text="GameZone Portal",
                font=("Impact", 30, "bold"),
                bg="#1a1a2e",
                fg="#00ffcc",  # Neon cyan for text
                pady=10,
                relief="flat",
                highlightthickness=2,
                highlightbackground="#ff0066"  # Neon pink border
            )
            self.title_label.grid(row=0, column=0, pady=20, sticky="n")

            # Welcome label with glowing effect
            self.welcome_label = tk.Label(
                self.root,
                text="",
                font=("Arial Black", 16, "bold"),
                bg="#1a1a2e",
                fg="#ffcc00",  # Neon yellow for welcome text
                pady=5
            )
            self.welcome_label.grid(row=1, column=0, sticky="n")

            # Custom style for dropdowns
            style = ttk.Style()
            style.theme_use("clam")  # Use 'clam' theme for better customization
            style.configure(
                "TCombobox",
                fieldbackground="#2e2e4e",  # Darker field background
                background="#00ffcc",  # Neon cyan background
                foreground="#ffffff",  # White text
                arrowcolor="#ff0066",  # Neon pink arrow
                font=("Arial Black", 12)
            )
            style.map(
                "TCombobox",
                fieldbackground=[("readonly", "#2e2e4e")],
                selectbackground=[("readonly", "#ff0066")],  # Neon pink selection
                selectforeground=[("readonly", "#ffffff")]
            )

            # Game selection dropdown
            self.game_var = tk.StringVar(value="Tic Tac Toe")
            self.game_dropdown = ttk.Combobox(
                self.root,
                textvariable=self.game_var,
                values=["Tic Tac Toe", "Snake", "Car Racing", "Chess"],
                state="readonly",
                font=("Arial Black", 12),
                width=15
            )
            self.game_dropdown.grid(row=2, column=0, pady=15, sticky="n")
            self.game_dropdown.bind("<<ComboboxSelected>>", self.update_dropdown_style)

            # Difficulty selection dropdown
            self.difficulty_var = tk.StringVar(value="Easy")
            self.difficulty_dropdown = ttk.Combobox(
                self.root,
                textvariable=self.difficulty_var,
                values=["Easy", "Medium", "Hard"],
                state="readonly",
                font=("Arial Black", 12),
                width=15
            )
            self.difficulty_dropdown.grid(row=3, column=0, pady=15, sticky="n")
            self.difficulty_dropdown.bind("<<ComboboxSelected>>", self.update_dropdown_style)

            # Button frame
            self.button_frame = tk.Frame(self.root, bg="#1a1a2e")
            self.button_frame.grid(row=4, column=0, pady=20, sticky="n")
            self.button_frame.grid_columnconfigure(0, weight=1)
            self.button_frame.grid_columnconfigure(1, weight=1)
            self.button_frame.grid_columnconfigure(2, weight=1)
            self.button_frame.grid_columnconfigure(3, weight=1)

            # Button style helper
            def create_button(text, command, col):
                btn = tk.Button(
                    self.button_frame,
                    text=text,
                    command=command,
                    bg="#ff0066",  # Neon pink background
                    fg="#ffffff",  # White text
                    font=("Arial Black", 12, "bold"),
                    width=12,
                    relief="flat",
                    activebackground="#00ffcc",  # Neon cyan on click
                    activeforeground="#ffffff",
                    bd=0,
                    highlightthickness=2,
                    highlightbackground="#00ffcc"  # Neon cyan border
                )
                btn.grid(row=0, column=col, padx=10)
                # Hover effect
                btn.bind("<Enter>", lambda e: btn.config(bg="#ff3399"))  # Lighter pink on hover
                btn.bind("<Leave>", lambda e: btn.config(bg="#ff0066"))  # Back to original
                return btn

            # Create buttons
            self.play_button = create_button("Play", self.start_game, 0)
            self.login_button = create_button("Login", self.open_login, 1)
            self.signup_button = create_button("Signup", self.open_signup, 2)
            self.contact_button = create_button("Contact Us", self.open_contact, 3)

            self.root.bind("<Configure>", self.on_resize)

        def update_dropdown_style(self, event=None):
            style = ttk.Style()
            style.configure(
                "TCombobox",
                fieldbackground="#2e2e4e",
                background="#00ffcc",
                foreground="#ffffff",
                arrowcolor="#ff0066",
                font=("Arial Black", 12)
            )

        def on_resize(self, event):
            width = self.root.winfo_width()
            font_size = max(14, min(30, width // 35))
            self.title_label.config(font=("Impact", font_size, "bold"))
            self.welcome_label.config(font=("Arial Black", font_size // 2, "bold"))
            self.game_dropdown.config(font=("Arial Black", font_size // 2))
            self.difficulty_dropdown.config(font=("Arial Black", font_size // 2))
            self.play_button.config(font=("Arial Black", font_size // 2, "bold"))
            self.login_button.config(font=("Arial Black", font_size // 2, "bold"))
            self.signup_button.config(font=("Arial Black", font_size // 2, "bold"))
            self.contact_button.config(font=("Arial Black", font_size // 2, "bold"))

        def set_user(self, username):
            self.username = username
            self.welcome_label.config(text=f"Welcome, {username}" if username else "")
            self.login_button.grid_remove()
            self.signup_button.grid_remove()
            if username:
                self.logout_button = tk.Button(
                    self.button_frame,
                    text="Logout",
                    command=self.logout,
                    bg="#ff0066",
                    fg="#ffffff",
                    font=("Arial Black", 12, "bold"),
                    width=12,
                    relief="flat",
                    activebackground="#00ffcc",
                    activeforeground="#ffffff",
                    bd=0,
                    highlightthickness=2,
                    highlightbackground="#00ffcc"
                )
                self.logout_button.grid(row=0, column=1, padx=10)
                self.logout_button.bind("<Enter>", lambda e: self.logout_button.config(bg="#ff3399"))
                self.logout_button.bind("<Leave>", lambda e: self.logout_button.config(bg="#ff0066"))
            else:
                self.login_button.grid()
                self.signup_button.grid()

        def logout(self):
            self.username = None
            self.welcome_label.config(text="")
            self.logout_button.grid_remove()
            self.login_button.grid()
            self.signup_button.grid()

        def open_login(self):
            LoginWindow(self.root, self.set_user)

        def open_signup(self):
            SignupWindow(self.root, self.set_user)

        def open_contact(self):
            ContactWindow(self.root)

        def start_game(self):
            print("Starting game:", self.game_var.get(), "Difficulty:", self.difficulty_var.get())
            game = self.game_var.get()
            difficulty = self.difficulty_var.get().lower()
            if game == "Tic Tac Toe":
                TicTacToeGame(self.root, difficulty, self.username)
            elif game == "Snake":
                SnakeGame(self.root, difficulty, self.username)
            elif game == "Car Racing":
                CarRacingGame(self.root, difficulty, self.username)
            elif game == "Chess":
                ChessGame(self.root, difficulty, self.username)

    if __name__ == "__main__":
        print("Creating Tkinter root...")
        root = tk.Tk()
        app = GamePortal(root)
        print("Entering mainloop...")
        root.mainloop()
except Exception as e:
    print("Error in main.py:", str(e))
    traceback.print_exc()