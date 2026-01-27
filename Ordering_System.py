import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_login_window():
    login_window = ctk.CTk()
    login_window.geometry("400x300") # Window size
    login_window.title("Kape'Bahay Ordering System - Login") # Window Title
    login_window.iconbitmap("logo file path here") # the icon file must be in .ico format and must be placed in the same folder as the system

    label = ctk.CTkLabel(login_window, text="Hello CustomTkinter!")
    label.pack(pady=20)

loginWindow = create_login_window()

loginWindow.mainloop()