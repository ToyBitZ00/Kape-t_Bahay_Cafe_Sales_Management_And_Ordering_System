import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

window = ctk.CTk()
window.geometry("400x300")
window.title("CustomTkinter Test")

label = ctk.CTkLabel(window, text="Hello CustomTkinter!")
label.pack(pady=20)

window.mainloop()