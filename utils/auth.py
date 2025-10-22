
import tkinter as tk
from tkinter import ttk, messagebox
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection

class LoginWindow:
    def __init__(self, parent, callback):
        self.callback = callback
        self.top = tk.Toplevel(parent)
        self.top.title("Login")
        self.top.geometry("300x200")
        self.top.configure(bg="#D3D3D3")
        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=1)
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_rowconfigure(1, weight=1)
        self.top.grid_rowconfigure(2, weight=1)
        self.top.grid_rowconfigure(3, weight=1)

        tk.Label(self.top, text="Email:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(self.top)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Password:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.top, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self.top, text="Login", command=self.login, bg="#00FFFF", fg="#800000", font=("Arial", 12)).grid(row=2, column=0, columnspan=2, pady=10)
        self.top.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        font_size = max(10, min(14, self.top.winfo_width() // 30))
        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(font=("Arial", font_size))

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user[1], password):
                self.callback(user[0])
                self.top.destroy()
            else:
                messagebox.showerror("Error", "Invalid credentials")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class SignupWindow:
    def __init__(self, parent, callback):
        self.callback = callback
        self.top = tk.Toplevel(parent)
        self.top.title("Signup")
        self.top.geometry("300x250")
        self.top.configure(bg="#D3D3D3")
        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=1)
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_rowconfigure(1, weight=1)
        self.top.grid_rowconfigure(2, weight=1)
        self.top.grid_rowconfigure(3, weight=1)
        self.top.grid_rowconfigure(4, weight=1)

        tk.Label(self.top, text="Username:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = tk.Entry(self.top)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Email:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(self.top)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Password:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = tk.Entry(self.top, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.top, text="Signup", command=self.signup, bg="#00FFFF", fg="#800000", font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)
        self.top.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        font_size = max(10, min(14, self.top.winfo_width() // 30))
        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(font=("Arial", font_size))

    def signup(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed_password))
            conn.commit()
            self.callback(username)
            self.top.destroy()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

class ContactWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Contact Us")
        self.top.geometry("300x250")
        self.top.configure(bg="#D3D3D3")
        self.top.grid_columnconfigure(0, weight=1)
        self.top.grid_columnconfigure(1, weight=1)
        self.top.grid_rowconfigure(0, weight=1)
        self.top.grid_rowconfigure(1, weight=1)
        self.top.grid_rowconfigure(2, weight=1)
        self.top.grid_rowconfigure(3, weight=1)

        tk.Label(self.top, text="Name:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = tk.Entry(self.top)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Email:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.email_entry = tk.Entry(self.top)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Message:", bg="#D3D3D3", fg="#800000", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.message_entry = tk.Text(self.top, height=4, width=20)
        self.message_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.top, text="Submit", command=self.submit, bg="#00FFFF", fg="#800000", font=("Arial", 12)).grid(row=3, column=0, columnspan=2, pady=10)
        self.top.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        font_size = max(10, min(14, self.top.winfo_width() // 30))
        for widget in self.top.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.config(font=("Arial", font_size))

    def submit(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        message = self.message_entry.get("1.0", tk.END).strip()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
                           (name, email, message))
            conn.commit()
            messagebox.showinfo("Success", "Message sent successfully!")
            self.top.destroy()
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
