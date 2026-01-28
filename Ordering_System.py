import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def create_login_window():
    loginwindow = ctk.CTk()
    loginwindow.geometry("900x700") # Window size
    loginwindow.title("Kape'Bahay Ordering System - Login") # Window Title
    #loginwindow.iconbitmap("logo file path here") # the icon file must be in .ico format and must be placed in the same folder as the system

    # Left Frame
    leftframe = ctk.CTkFrame(loginwindow, fg_color="#2A8F5C")
    leftframe.pack(side="left",fill="both", expand=True)

    greetingLabel = ctk.CTkLabel(leftframe, text="Kape'Bahay", font=ctk.CTkFont(size=40, weight="bold"), fg_color="#2A8F5C")
    greetingLabel.pack(pady=(100,10))

    createOrderButton = ctk.CTkButton(leftframe, text="Create Order", font=ctk.CTkFont(size=20), width=200, height=50, fg_color="#1E6F43", hover_color="#14532D")
    createOrderButton.pack(pady=(0, 200), side="bottom")

    # Right Frame
    rightframe = ctk.CTkFrame(loginwindow, fg_color="#3032AA")
    rightframe.pack(side="right", fill="both", expand=True)

    loginLabel = ctk.CTkLabel(rightframe, text="SIGN IN", font=ctk.CTkFont(size=30, weight="bold"), fg_color="#3032AA")
    loginLabel.pack(pady=(100,10))

    usernameEntry = ctk.CTkEntry(rightframe, placeholder_text="Username", width=200, height=40, font=ctk.CTkFont(size=16))
    usernameEntry.pack(pady=(150,10))

    passwordEntry = ctk.CTkEntry(rightframe, placeholder_text="Password", width=200, height=40, font=ctk.CTkFont(size=16), show="*")
    passwordEntry.pack(pady=(10,5))

    showpasswordvar = ctk.BooleanVar()

    def toggle_password():
        if showpasswordvar.get():
            passwordEntry.configure(show="")
        else:
            passwordEntry.configure(show="*")

    showpasswordcheckbox = ctk.CTkCheckBox(rightframe, 
                                           text="Show Password", 
                                           variable=showpasswordvar, 
                                           onvalue=True, 
                                           offvalue=False,
                                           checkbox_width=12,
                                           checkbox_height=12,
                                           checkmark_color="#1E6F43",
                                           border_width=1,
                                           hover_color="#1E6F43",
                                           text_color="#FFFFFF",
                                           command=toggle_password)
    showpasswordcheckbox.pack(padx=(0,80), pady=(0,20))


    return loginwindow
# Also replicate this part for other windows you will create in the future.
loginWindowCreation = create_login_window()

# Do not mess with this part.
loginWindowCreation.mainloop()