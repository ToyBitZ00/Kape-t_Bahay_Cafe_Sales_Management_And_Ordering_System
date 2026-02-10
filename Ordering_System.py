from email.mime import image
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

# This block of code is what displays, withdraw and hides the windows.

def show_cart_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.deiconify()  # Show the cart window


def create_login_window():
    loginwindow = ctk.CTk()
    loginwindow.geometry("900x700") # Window size
    loginwindow.title("Kape'Bahay Ordering System - Login") # Window Title
    loginwindow.minsize(1280, 720) # Disable window resizing
    loginwindow.configure(bg="#FFFFFF") # Window background color
    #loginwindow.iconbitmap("logo file path here") the icon file must be in .ico format and must be placed in the same folder as the system

    # Left Frame
    leftframe = ctk.CTkFrame(loginwindow, fg_color="#1E6F43")
    leftframe.pack(side="left",fill="both", expand=True)

    greetingLabel = ctk.CTkLabel(leftframe, 
                                 bg_color="transparent",
                                 text="Kape't Bahay", 
                                 font=ctk.CTkFont(size=40, weight="bold"))
    greetingLabel.pack(pady=(100,0))

    # Right Frame
    rightframe = ctk.CTkFrame(loginwindow, 
                              fg_color="#FFFFFF",
                              corner_radius=20)
    rightframe.pack(side="right", padx=(0, 100), pady=100, fill="both", expand=True)

    loginLabel = ctk.CTkLabel(rightframe, 
                              text="SIGN IN", 
                              font=ctk.CTkFont(size=30, weight="bold"),
                              fg_color="transparent")
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

    loginButton = ctk.CTkButton(rightframe, 
                                text="Login", 
                                font=ctk.CTkFont(size=20), 
                                width=200, 
                                height=50, 
                                fg_color="#1E6F43", 
                                hover_color="#14532D",
                                command=lambda: show_cart_window(loginwindow))
    loginButton.pack(pady=(0,10))

    signupLabel = ctk.CTkLabel(rightframe, text="Don't have an account?", font=ctk.CTkFont(size=14), fg_color="#3032AA")    
    signupLabel.pack(pady=(10,5))
    signupButton = ctk.CTkButton(rightframe, text="Sign Up", font=ctk.CTkFont(size=16), width=100, height=40, fg_color="#1E6F43", hover_color="#14532D")
    signupButton.pack()

    return loginwindow


def cart_window():
    cartwindow = ctk.CTkToplevel()
    cartwindow.geometry("800x600")
    cartwindow.title("Kape'Bahay Ordering System - Cart")
     # Further implementation of the cart window goes here.  

    # ================== MAIN LAYOUT ==================
    cartwindow.grid_columnconfigure(0, weight=3)
    cartwindow.grid_columnconfigure(1, weight=1)
    cartwindow.grid_rowconfigure(0, weight=1)

    # ================== LEFT: ITEMS SECTION ==================
    items_frame = ctk.CTkScrollableFrame(cartwindow, 
                                         width=500,
                                         height=600,
                                         corner_radius=15)
    items_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

    items_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

    # Header
    title = ctk.CTkLabel(items_frame, text="COFFEES", font=("Arial", 22, "bold"))
    title.grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))


    # Category buttons

    category_var = ctk.StringVar()

    categories = ["FAVORITES", "SPANISH SERIES", "SAESALT SERIES", "BLACK SERIES", "CHOCO SERIES", "MATCHA SERIES"]

    categories_Combo = ctk.CTkComboBox(items_frame,
                                       font=("Arial",12, "bold"),
                                       variable=category_var,
                                       values=list(categories),
                                       state="readonly",
                                       width=170,
                                       height=30,
                                       )
    categories_Combo.grid(row=1, column=0, padx=10, pady=10, sticky="w")




    # Sample product cards
    products = [
        ("0", "Milo Malt", "₱155.00"),
        ("0", "White salted", "₱155.00"),
        ("0", "Caramel", "₱145.00"),
        ("0","Mocha", "₱145.00"),
        ("1","Classic Spanish", "₱110.00"),
        ("1","Spanish cinnamon", "₱115.00"),
        ("1","Spanish Mocha", "₱115.00"),\
        ("2","Classic Seasalt", "₱115.00"),
        ("2","Seasalt Caramel", "₱120.00"),
        ("2","Hazelnut Paline", "₱120.00"),
        ("3","Black Irish", "₱105.00"),
        ("3","Black Seasalt", "₱110.00"),
        ("3","Black Vanilla Cream", "₱110.00"),
        ("4","Choco Cinnamon", "₱110.00"),
        ("4","Choco Caramel", "₱110.00"),
        ("4","Choco Strawberry", "₱120.00"),
        ("5","Traditional Matcha", "₱105.00"),
        ("5","Creamy Matcha", "₱120.00"),
        ("5","Matcha Strawberry", "₱120.00"),
        ("5","Choco Matcha", "₱120.00"),
    
    ]

    row_index = 2
    col_index = 0

    for id, name, price in products:
        card = ctk.CTkFrame(items_frame, 
                            fg_color="#505050", corner_radius=10)
        card.grid(row=row_index, column=col_index, padx=10, pady=10, sticky="nsew")

        img_placeholder = ctk.CTkLabel(card, text="Image", width=140, height=30, fg_color="#444")
        img_placeholder.pack(padx=10, pady=10)

        lbl_name = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"))
        lbl_name.pack(pady=(0, 2))

        lbl_price = ctk.CTkLabel(card, text=price, font=("Arial", 12))
        lbl_price.pack()

        add_btn = ctk.CTkButton(card, text="+", width=32, height=32, corner_radius=16)
        add_btn.pack(pady=8)

        col_index += 1
        if col_index > 2:
            col_index = 0
            row_index += 1

    # ================== RIGHT: CART SUMMARY ==================
    cart_frame = ctk.CTkFrame(cartwindow, corner_radius=15)
    cart_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

    cart_frame.grid_columnconfigure(0, weight=1)

    cart_title = ctk.CTkLabel(cart_frame, text="Current Order", font=("Arial", 20, "bold"))
    cart_title.pack(pady=10)

    # Order items
    order_items = [
        ("Raspberry Tart", "₱120.00"),
        ("Lemon Tart", "₱90.00"),
    ]

    for item, price in order_items:
        item_frame = ctk.CTkFrame(cart_frame, fg_color="#2b2b2b", corner_radius=10)
        item_frame.pack(fill="x", padx=10, pady=5)

        name_lbl = ctk.CTkLabel(item_frame, text=item)
        name_lbl.pack(side="left", padx=10)

        price_lbl = ctk.CTkLabel(item_frame, text=price)
        price_lbl.pack(side="right", padx=10)

    # Summary
    summary_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
    summary_frame.pack(fill="x", padx=10, pady=15)

    ctk.CTkLabel(summary_frame, text="Subtotal: ₱210.00").pack(anchor="w")
    ctk.CTkLabel(summary_frame, text="Service Charge: 20%").pack(anchor="w")
    ctk.CTkLabel(summary_frame, text="Tax: ₱15.00").pack(anchor="w")

    total_lbl = ctk.CTkLabel(
        summary_frame,
        text="Total: ₱225.00",
        font=("Arial", 16, "bold")
    )
    total_lbl.pack(anchor="w", pady=(10, 0))

    # Continue Button
    continue_btn = ctk.CTkButton(
        cart_frame,
        text="Continue",
        height=45,
        corner_radius=20
    )
    continue_btn.pack(fill="x", padx=15, pady=15)

    return cartwindow

# Also replicate this part for other windows you will create in the future.
loginWindowCreation = create_login_window()
cartWIndowCreation = cart_window()


# Hides other window at the startup of the program.
cartWIndowCreation.withdraw()  


# Do not mess with this part.
loginWindowCreation.mainloop()