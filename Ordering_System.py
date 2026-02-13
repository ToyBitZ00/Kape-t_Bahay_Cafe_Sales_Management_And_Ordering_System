import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os


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

# Craete your windows here. You can also create more functions for other windows you will create in the future. Just make sure to follow the same format as the functions above.
def create_login_window():
    loginwindow = ctk.CTk()
    loginwindow.geometry("1280x720") # Window size
    loginwindow.title("Kape'Bahay Ordering System - Login") # Window Title
    loginwindow.resizable(False, False) # Disable window resizing
    loginwindow.configure(fg_color="#43382F") # Window background color
    #loginwindow.iconbitmap("logo file path here") the icon file must be in .ico format and must be placed in the same folder as the system

    loginwindow.grid_columnconfigure(0, minsize=640)
    loginwindow.grid_columnconfigure(1, minsize=640)
    loginwindow.grid_rowconfigure(0, weight=1)


    # Left Frame
    leftframe = ctk.CTkFrame(loginwindow, 
                             fg_color="transparent",
                             width=640)
    leftframe.grid(row=0, column=0, sticky="news")
    leftframe.grid_propagate(False)

    businessLogo = ctk.CTkLabel(leftframe, 
                                text="Logo Image",
                                font=("Segoe UI", 20, "bold"),
                                text_color="#000000",
                                width=400,
                                height=400,
                                fg_color="#FFFFFF")
    businessLogo.pack(padx=(80,0), pady=(80,0), anchor="center")
    #businessLogoImage = ctk.CTkImage(Image.open("kape't bahay logo.png"), size=(200, 200))
    #businessLogo.configure(image=businessLogoImage)
    greetingLabel = ctk.CTkLabel(leftframe, 
                                 bg_color="transparent",
                                 text="Kape't Bahay Cafe", 
                                 font=("Segoe UI", 40, "bold"))
    greetingLabel.pack(padx=(80,0), pady=(30,0), anchor="center")

    subGreetingLabel = ctk.CTkLabel(leftframe, 
                                 text="Ordering and Management System",
                                 font=("Segoe UI", 30, "bold"),
                                 bg_color="transparent")
    subGreetingLabel.pack(padx=(85,0), pady=(0,0), anchor="center")
    
    right_container = ctk.CTkFrame(loginwindow, 
                                   fg_color="transparent")
    right_container.grid(row=0, column=1, sticky="nsew")
    right_container.grid_rowconfigure(0, weight=1)
    right_container.grid_columnconfigure(0, weight=1)


    # Right Frame
    rightframe = ctk.CTkFrame(right_container, 
                              fg_color="#F2F1EF",
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
    descriptionLabel.pack(side="top", padx=(60,0), pady=(0,20), anchor="w")

    usernameEntry = ctk.CTkEntry(rightframe, 
                                 placeholder_text="Username", 
                                 placeholder_text_color="#888888",
                                 width=345, 
                                 height=60, 
                                 font=("Segoe UI", 16),
                                 text_color="#000000",
                                 fg_color="#FFFFFF",
                                 border_color="#dddddd")
    usernameEntry.pack(pady=(40,10))

    passwordEntry = ctk.CTkEntry(rightframe, 
                                 placeholder_text="Password", 
                                 placeholder_text_color="#888888",
                                 width=345, 
                                 height=60, 
                                 font=("Segoe UI", 16), 
                                 text_color="#000000",
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
                                command=lambda: show_profile_window(loginwindow))
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
    cartwindow.geometry("1280x720")
    cartwindow.title("Kape'Bahay Ordering System - Cart")

    cartwindow.grid_columnconfigure(0, weight=3)
    cartwindow.grid_columnconfigure(1, weight=1)
    cartwindow.grid_rowconfigure(0, weight=0) 
    cartwindow.grid_rowconfigure(1, weight=1)  

    # ================= DATA =================
    cart_items = []
    products = [
            ("0", "Milo Malt", 155.00),
            ("0", "White salted", 155.00),
            ("0", "Caramel", 145.00),
            ("0","Mocha", 145.00),
            ("1","Classic Spanish", 110.00),
            ("1","Spanish cinnamon", 115.00),
            ("1","Spanish Mocha", 115.00),
            ("2","Classic Seasalt", 115.00),
            ("2","Seasalt Caramel", 120.00),
            ("2","Hazelnut Paline", 120.00),
            ("3","Black Irish", 105.00),
            ("3","Black Seasalt", 110.00),
            ("3","Black Vanilla Cream", 110.00),
            ("4","Choco Cinnamon", 110.00),
            ("4","Choco Caramel", 110.00),
            ("4","Choco Strawberry", 120.00),
            ("5","Traditional Matcha", 105.00),
            ("5","Creamy Matcha", 120.00),
            ("5","Matcha Strawberry", 120.00),
            ("5","Choco Matcha", 120.00),
    ]

    # ================= LEFT SIDE =================
    headerFrame = ctk.CTkFrame(cartwindow, 
                               fg_color="transparent",
                               width=592,
                               height=115) 
    headerFrame.grid(row=0, column=0, columnspan=3, padx=15, pady=(0, 0), sticky="nw")
    headerFrame.grid_columnconfigure((0, 1, 2), weight=1)
    headerFrame.grid_propagate(False)
    headerFrame.pack_propagate(False)

    items_frame = ctk.CTkScrollableFrame(cartwindow, 
                                         corner_radius=15)
    items_frame.grid(row=1, column=0, padx=15, pady=(15, 15), sticky="nsew")

    items_frame.grid_columnconfigure((0, 1, 2), weight=1)

    # ── Categories list (used for both index and display)
    categories = [
        "FAVORITES",
        "SPANISH SERIES",
        "SEASALT SERIES",      
        "BLACK SERIES",
        "CHOCO SERIES",
        "MATCHA SERIES"
    ]

    def filter_products(choice):
        if choice == "All":
            display_products(None)
        else:
            category_index = categories.index(choice)
            display_products(str(category_index))

    category_var = ctk.StringVar(value="All")   # default shows everything

    # ── Header
    CoffeeHeaderLabel = ctk.CTkLabel(
        headerFrame,
        text="COFFEE MENU",
        font=("Segoe UI", 40, "bold"))
    CoffeeHeaderLabel.pack(pady=15, anchor="w", side="top")
    # ── ComboBox – full width, centered look
    categories_Combo = ctk.CTkComboBox(
        headerFrame,
        values=["All"] + categories,           
        variable=category_var,
        font=("Segoe UI", 18, "bold"),
        state="readonly",
        width=280,                             
        height=70,
        command=filter_products
    )
    categories_Combo.pack(pady=(0, 0), anchor="w", side="top")
    # ── Product display function
    def display_products(selected_category=None):
        # Remove only product cards (rows >= 2)
        for widget in items_frame.winfo_children():
            info = widget.grid_info()
            if info and int(info.get("row", 0)) >= 2:
                widget.destroy()

        row_index = 2
        col_index = 0

        for cat_id, name, price in products:
            if selected_category is None or cat_id == selected_category:

                card = ctk.CTkFrame(items_frame, fg_color="#505050", corner_radius=10)
                card.grid(row=row_index, column=col_index, padx=10, pady=10, sticky="nsew")

                img_placeholder = ctk.CTkLabel(card, text="Image", width=140, height=30, fg_color="#444")
                img_placeholder.pack(padx=10, pady=10)

                lbl_name = ctk.CTkLabel(card, text=name, font=("Arial", 14, "bold"))
                lbl_name.pack(pady=(0, 2))

                lbl_price = ctk.CTkLabel(card, text=price)
                lbl_price.pack()

                add_btn = ctk.CTkButton(card, text="+", width=32, height=32)
                # Tip: connect button later with lambda or partial if needed
                add_btn.pack(pady=8)

                col_index += 1
                if col_index > 2:
                    col_index = 0
                    row_index += 1

    # Show all products initially
    display_products()

    

    

    # ================= RIGHT SIDE =================
    cart_frame = ctk.CTkFrame(cartwindow, 
                              corner_radius=15)
    cart_frame.grid(row=0, column=1, rowspan=2, padx=(0, 15), pady=15, sticky="nsew")

    cart_frame.grid_columnconfigure(0, weight=1)

    current_order_label = ctk.CTkLabel(cart_frame, 
                 text="Current Order",
                 font=("Arial", 20, "bold"))
    current_order_label.pack(pady=(10, 0))

    cart_items_container = ctk.CTkScrollableFrame(cart_frame, height=300)
    cart_items_container.pack(fill="both", expand=True, padx=15, pady=10)

    subtotal_label = ctk.CTkLabel(cart_frame, 
                                  text="Subtotal: ₱0.00",
                                  font=("Arial", 16, "bold"))
    subtotal_label.pack(pady=10)

    create_order_button = ctk.CTkButton(cart_frame, 
                                        text="Create Order", 
                                        font=("Segoe UI", 18, "bold"), 
                                        width=200, 
                                        height=50, 
                                        fg_color="#1E6F43", 
                                        hover_color="#14532D")
    create_order_button.pack(pady=(0, 20), fill="both", padx=15)

    

    # ================= FUNCTIONS =================

    def update_cart_display():
        # Clear previous items
        for widget in cart_items_container.winfo_children():
            widget.destroy()

        subtotal = 0

        for item in cart_items:
            subtotal += item["price"]

            item_frame = ctk.CTkFrame(cart_items_container, fg_color="#2b2b2b")
            item_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(item_frame, text=item["name"]).pack(side="left", padx=10)
            ctk.CTkLabel(item_frame,
                         text=f"₱{item['price']:.2f}").pack(side="right", padx=10)

        subtotal_label.configure(text=f"Subtotal: ₱{subtotal:.2f}")

    def add_to_cart(name, price):
        cart_items.append({"name": name, "price": price})
        update_cart_display()

    # ================= DISPLAY PRODUCTS =================

    row = 1
    col = 0

    for id, name, price in products:

        card = ctk.CTkFrame(items_frame, fg_color="#505050", corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(card, text="Image", width=140,
                     height=30, fg_color="#444").pack(pady=10)

        ctk.CTkLabel(card, text=name,
                     font=("Arial", 14, "bold")).pack()

        ctk.CTkLabel(card,
                     text=f"₱{price:.2f}").pack()

        ctk.CTkButton(
            card,
            text="+",
            width=30,
            command=lambda n=name, p=price: add_to_cart(n, p)  # ✅ FIXED LAMBDA
        ).pack(pady=5)

        col += 1
        if col > 2:
            col = 0
            row += 1

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
    profile_window.geometry("1280x720")
    profile_window.title("Kape'Bahay - Barista Profile")
    profile_window.resizable(False, False)
    profile_window.configure(fg_color="#120f0d")

    sales_var = ctk.DoubleVar(value=500.00)
    orders_var = ctk.IntVar(value=42)

    name_label = ctk.CTkLabel(profile_window, text="Cashier Name", 
                              font=("Segoe UI", 54, "bold"), text_color="white")
    name_label.place(x=60, y=40)
    
    
    user_role = ctk.StringVar()
    roles_label = ctk.StringVar(value="CASHIER")


    def get_user_role(user_role):
          # Change to "Cashier" to test the other role badge

        if roles_label.get() == "ADMIN":
            user_role.set("ADMIN")
        elif roles_label.get() == "CASHIER":
            user_role.set("CASHIER")
            
        return user_role

    role_badge = ctk.CTkLabel(profile_window, textvariable=get_user_role(user_role), fg_color="#c8b591", text_color="black", 
                              corner_radius=15, font=("Segoe UI", 16, "bold"), width=110, height=35)
    role_badge.place(x=500, y=55)

    main_box = ctk.CTkFrame(profile_window, fg_color="#6f5e4c", corner_radius=25, width=1160, height=500)
    main_box.place(relx=0.5, rely=0.6, anchor="center")

    v_divider = ctk.CTkFrame(main_box, width=2, height=380, fg_color="#9e8d7a")
    v_divider.place(x=450, y=0)

    h_divider = ctk.CTkFrame(main_box, width=1160, height=2, fg_color="#9e8d7a")
    h_divider.place(x=0, y=380)

    shift_title = ctk.CTkLabel(main_box, text="My Shift", font=("Segoe UI", 30, "bold"), text_color="white")
    shift_title.place(x=40, y=30)

    status_label = ctk.CTkLabel(main_box, text="Status:", font=("Segoe UI", 24), text_color="white")
    status_label.place(x=40, y=100)
    
    status_menu = ctk.CTkOptionMenu(main_box, values=["On Shift", "Off Shift"], 
                                     fg_color="#4a3f35", button_color="#4a3f35", 
                                     width=160, height=40, font=("Segoe UI", 18))
    status_menu.place(x=130, y=100)

    sales_display = ctk.CTkLabel(main_box, text=f"Total Sales: PHP {sales_var.get():.2f}", 
                                  font=("Segoe UI", 24), text_color="white")
    sales_display.place(x=40, y=180)

    orders_display = ctk.CTkLabel(main_box, text=f"Total Orders: {orders_var.get()}", 
                                   font=("Segoe UI", 24), text_color="white")
    orders_display.place(x=40, y=260)

    order_button = ctk.CTkButton(main_box, text="Create Order", font=("Segoe UI", 32, "bold"), 
                                 fg_color="#e59a6d", hover_color="#c98359", 
                                 width=400, height=120, corner_radius=25)
    order_button.place(x=600, y=50)
    
    logout_button = ctk.CTkButton(main_box, text="LOGOUT", font=("Segoe UI", 32, "bold"), 
                                  fg_color="#513626", hover_color="#3d291d", 
                                  width=400, height=120, corner_radius=25, 
                                  command=lambda: show_login_window(profile_window))
    logout_button.place(x=600, y=200)

    # ================= Notifications Section with Scrollable Frame =================
    notif_title = ctk.CTkLabel(main_box, text="Notifications:", font=("Segoe UI", 22, "bold"), text_color="white")
    notif_title.place(x=40, y=390)

    notif_frame = ctk.CTkScrollableFrame(main_box, width=1060, height=60, fg_color="transparent", 
                                         scrollbar_button_color="#9e8d7a", scrollbar_button_hover_color="#c8b591")
    notif_frame.place(x=40, y=425)

    stock_alert = ctk.CTkLabel(notif_frame, text="• Low Stock: Whole Milk (2 Boxes remaining)", 
                               font=("Segoe UI", 18), text_color="#ffd7ba", anchor="w")
    stock_alert.pack(fill="x", pady=2)

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