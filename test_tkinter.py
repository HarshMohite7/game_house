import tkinter as tk
print("Tkinter imported successfully")
root = tk.Tk()
root.title("Test Window")
root.geometry("200x100")
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=20)
root.mainloop()