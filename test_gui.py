import tkinter as tk
from tkinter import messagebox

def test_gui():
    root = tk.Tk()
    root.withdraw() # Hide the main window
    messagebox.showinfo("Test GUI", "GUI test successful!")
    root.destroy()

if __name__ == "__main__":
    test_gui()