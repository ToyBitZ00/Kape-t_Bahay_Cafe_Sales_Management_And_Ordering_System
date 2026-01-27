import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def create_login_window():
    login_window = ctk.CTk()
    login_window.geometry("900x700") # Window size
    login_window.title("Kape'Bahay Ordering System - Login") # Window Title
    #login_window.iconbitmap("logo file path here") # the icon file must be in .ico format and must be placed in the same folder as the system

    # Left Frame
    left_frame = ctk.CTkFrame(login_window, fg_color="#2A8F5C")
    left_frame.pack(side="left",fill="both", expand=True)


    # Right Frame
    right_frame = ctk.CTkFrame(login_window, fg_color="#3032AA")
    right_frame.pack(side="right", fill="both", expand=True)


    return login_window

# Also replicate this part for other windows you will create in the future.
loginWindowCreation = create_login_window()

# Do not mess with this part.
loginWindowCreation.mainloop()