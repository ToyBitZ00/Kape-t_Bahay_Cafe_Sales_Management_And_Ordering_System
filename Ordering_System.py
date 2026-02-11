import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk


# This block of code is what displays, withdraw and hides the windows.
def show_login_window(current=None):
    loginWindowCreation.deiconify()  # Show the login window
    cartWIndowCreation.withdraw()  # Hide the cart window
    orderWindowCreation.withdraw()  # Hide the orders window
    managementWindowCreation.withdraw()  # Hide the management window
    profileWindowCreation.withdraw()  # Hide the profile window
    salesReportWindowCreation.withdraw()  # Hide the sales report window



def show_cart_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.deiconify()  # Show the cart window
    orderWindowCreation.withdraw()  # Hide the orders window
    managementWindowCreation.withdraw()  # Hide the management window
    profileWindowCreation.withdraw()  # Hide the profile window
    salesReportWindowCreation.withdraw()  # Hide the sales report window


def show_orders_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.withdraw()  # Hide the cart window
    orderWindowCreation.deiconify()  # Show the orders window
    managementWindowCreation.withdraw()  # Hide the management window
    profileWindowCreation.withdraw()  # Hide the profile window
    salesReportWindowCreation.withdraw()  # Hide the sales report window


def show_management_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.withdraw()  # Hide the cart window
    orderWindowCreation.withdraw()  # Hide the orders window
    managementWindowCreation.deiconify()  # Show the management window
    profileWindowCreation.withdraw()  # Hide the profile window
    salesReportWindowCreation.withdraw()  # Hide the sales report window


def show_profile_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.withdraw()  # Hide the cart window
    orderWindowCreation.withdraw()  # Hide the orders window
    managementWindowCreation.withdraw()  # Hide the management window
    profileWindowCreation.deiconify()  # Show the profile window
    salesReportWindowCreation.withdraw()  # Hide the sales report window


def show_sales_report_window(current=None):
    loginWindowCreation.withdraw()  # Hide the current window
    cartWIndowCreation.withdraw()  # Hide the cart window
    orderWindowCreation.withdraw()  # Hide the orders window
    managementWindowCreation.withdraw()  # Hide the management window
    profileWindowCreation.withdraw()  # Hide the profile window
    salesReportWindowCreation.deiconify()  # Show the sales report window


def create_login_window():
    loginwindow = ctk.CTk()
    loginwindow.geometry("1280x720") # Window size
    loginwindow.title("Kape'Bahay Ordering System - Login") # Window Title
    loginwindow.resizable(False, False) # Disable window resizing
    loginwindow.configure(fg_color="#c3955b") # Window background color
    #loginwindow.iconbitmap("logo file path here") the icon file must be in .ico format and must be placed in the same folder as the system

    loginwindow.grid_columnconfigure(0, weight=1)
    loginwindow.grid_columnconfigure(1, weight=1)
    loginwindow.grid_rowconfigure(0, weight=1)


    # Left Frame
    leftframe = ctk.CTkFrame(loginwindow, 
                             fg_color="transparent")
    leftframe.grid(row=0, column=0, sticky="nesw")

    greetingLabel = ctk.CTkLabel(leftframe, 
                                 bg_color="transparent",
                                 text="WELCOME", 
                                 font=("Segoe UI", 40, "bold"))
    greetingLabel.pack(padx=(0,0), pady=(150,0), anchor="center")

    headlineLabel = ctk.CTkLabel(leftframe, 
                                 text="to Kape'Bahay",
                                 font=("Segoe UI", 20, "bold"),
                                 bg_color="transparent")
    headlineLabel.pack(padx=(0,0), pady=(10,0), anchor="center")
    
    right_container = ctk.CTkFrame(loginwindow, 
                                   fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew")
    right_container.grid_rowconfigure(0, weight=1)
    right_container.grid_columnconfigure(0, weight=1)


    # Right Frame
    rightframe = ctk.CTkFrame(right_container, 
                              fg_color="#FFFFFF",
                              corner_radius=25,
                              width=460,
                              height=560,
                              border_width=2,
                              border_color="#dddddd")
    rightframe.place(relx=0.5, rely=0.5, anchor="center")
    rightframe.pack_propagate(False)
    rightframe.grid_propagate(False)

    loginLabel = ctk.CTkLabel(rightframe, 
                              text="Sign in", 
                              font=("Segoe UI",50,"bold"),
                              fg_color="#FFFFFF",
                              text_color="#000000")
    loginLabel.pack(side="top", padx=(60,0), pady=(50,0), anchor="w")

    descriptionLabel = ctk.CTkLabel(rightframe,
                                    text="Please enter your credentials to continue",
                                    font=("Segoe UI", 14),
                                    fg_color="#FFFFFF",
                                    text_color="#000000")
    descriptionLabel.pack(side="top", padx=(60,0), pady=(10,20), anchor="w")

    usernameEntry = ctk.CTkEntry(rightframe, 
                                 placeholder_text="Username", 
                                 placeholder_text_color="#000000",
                                 width=345, 
                                 height=60, 
                                 font=("Segoe UI", 16),
                                 fg_color="#FFFFFF",
                                 border_color="#dddddd")
    usernameEntry.pack(pady=(10,10))

    passwordEntry = ctk.CTkEntry(rightframe, 
                                 placeholder_text="Password", 
                                 placeholder_text_color="#000000",
                                 width=345, 
                                 height=60, 
                                 font=("Segoe UI", 16), 
                                 fg_color="#FFFFFF",
                                 show="*",
                                 border_color="#dddddd")
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
                                           border_width=2,
                                           hover_color="#1E6F43",
                                           text_color="#000000",
                                           command=toggle_password,
                                           corner_radius=3)
    showpasswordcheckbox.pack(padx=(65,0), pady=(0,20), anchor="w")

    loginButton = ctk.CTkButton(rightframe, 
                                text="Login", 
                                font=ctk.CTkFont(size=20), 
                                width=200, 
                                height=50, 
                                fg_color="#1E6F43", 
                                hover_color="#14532D",
                                command=lambda: show_cart_window(loginwindow))
    loginButton.pack(padx=(60,60), pady=(0,5), fill="both")

    signupLabel = ctk.CTkButton(rightframe, 
                                text="Don't have an account?", 
                                font=ctk.CTkFont(size=14), 
                                fg_color="transparent", 
                                text_color="#3032AA",
                                hover_color="FFFFFF")    
    signupLabel.pack(pady=(0,5))

    return loginwindow


def create_cart_window():
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


    def filter_products(choice):
        category_index = categories.index(choice)
        display_products(str(category_index))

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
                                       command=filter_products
                                       )
    categories_Combo.grid(row=1, column=0, padx=10, pady=10, sticky="w")

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

    


    def display_products(selected_category=None):

        for widget in items_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) >= 2:
                widget.destroy()

        row_index = 2
        col_index = 0




        for id, name, price in products:
            if selected_category is None or id == selected_category:

                card = ctk.CTkFrame(items_frame, fg_color="#505050", corner_radius=10)
                card.grid(row=row_index, column=col_index, padx=10, pady=10, sticky="nsew")

                img_placeholder = ctk.CTkLabel(card, text="Image", width=140, height=30, fg_color="#444")
                img_placeholder.pack(padx=10, pady=10)

                lbl_name = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"))
                lbl_name.pack(pady=(0, 2))

                lbl_price = ctk.CTkLabel(card, text=price)
                lbl_price.pack()

                add_btn = ctk.CTkButton(card, text="+", width=32, height=32)
                add_btn.pack(pady=8)

                col_index += 1
                if col_index > 2:
                    col_index = 0
                    row_index += 1

    display_products() 

    # ================== RIGHT: CART SUMMARY ==================
    cart_frame = ctk.CTkFrame(cartwindow, corner_radius=15)
    cart_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

    cart_frame.grid_columnconfigure(0, weight=1)

    cart_title = ctk.CTkLabel(cart_frame, text="Current Order", font=("Arial", 20, "bold"))
    cart_title.pack(pady=10)

    order_items_label = ctk.CTkLabel(cart_frame, text="Items in Cart:", font=("Arial", 14, "bold"))
    order_items_label.pack(anchor="w", padx=10, pady=(10, 5))

    # Order items
    order_items = [
        ("", ""),
        ("", ""),
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
    summary_frame.pack(side="bottom",fill="x", padx=10, pady=15)

    summary_label = ctk.CTkLabel(summary_frame, text="Subtotal: ₱215.00")
    summary_label.pack(anchor="sw")

    total_lbl = ctk.CTkLabel(
        summary_frame,
        text="Total: ₱215.00",
        font=("Arial", 16, "bold")
    )
    total_lbl.pack(anchor="sw", pady=(10, 0))

    # Continue Button
    continue_btn = ctk.CTkButton(
        summary_frame,
        text="Continue",
        height=45,
        corner_radius=20
    )
    continue_btn.pack(fill="x", padx=15, pady=15)

    return cartwindow


# Orders Window
def create_orders_window():
    orders_window = ctk.CTkToplevel()
    orders_window.geometry("800x600")
    orders_window.title("Kape'Bahay Ordering System - Orders")
     # Further implementation of the orders window goes here.  
    return orders_window

# Beverage management window
def create_management_window():
    settings_window = ctk.CTkToplevel()
    settings_window.geometry("800x600")
    settings_window.title("Kape'Bahay Ordering System - Settings")
     # Further implementation of the settings window goes here.  
    return settings_window

def create_profile_window():
    profile_window = ctk.CTkToplevel()
    profile_window.geometry("800x600")
    profile_window.title("Kape'Bahay Ordering System - Admin Profile")
     # Further implementation of the admin profile window goes here.  
    return profile_window

def create_sales_report_window():
    report_window = ctk.CTkToplevel()
    report_window.geometry("800x600")
    report_window.title("Kape'Bahay Ordering System - Sales Report")
     # Further implementation of the sales report window goes here.  
    return report_window



# Also replicate this part for other windows you will create in the future.
loginWindowCreation = create_login_window()
cartWIndowCreation = create_cart_window()
orderWindowCreation = create_orders_window()
managementWindowCreation = create_management_window()
profileWindowCreation = create_profile_window()
salesReportWindowCreation = create_sales_report_window()

# Hides other window at the startup of the program.
cartWIndowCreation.withdraw()  
orderWindowCreation.withdraw()
managementWindowCreation.withdraw()
profileWindowCreation.withdraw()
salesReportWindowCreation.withdraw()


# Do not mess with this part.
loginWindowCreation.mainloop()