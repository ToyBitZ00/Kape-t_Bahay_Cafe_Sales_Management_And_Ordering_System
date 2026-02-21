import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import hashlib
import sqlite3

current_user = {
    "username": None,
    "role": None
}
#/ ================== Database Functions =================

# Database connection function
def create_connection():
    conn = sqlite3.connect("kape't_bahay_database.db")
    return conn


def create_database():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    print("Database and 'users' table created successfully.")

    conn.commit()
    conn.close()

#create_database()

# Used to hash passwords for security purposes.
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Used to add a user to the database.
def add_user(username, password, role, email):
    conn = create_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
            (username, hashed_pw, role, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        result = cursor.execute("SELECT * FROM users").fetchall()
        print(result)
        conn.commit()
        conn.close()


# Used to delete users from the users table.
def delete_user(): 
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users")
    conn.commit()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print("USERS AFTER DELETE:", rows)

    conn.commit()
    conn.close()

#add_user("mico", "admin0001", "cashier", "mic0@gmail.com")
#add_user("paul", "admin0002", "cashier", "pa6308191@gmail.com")

#add_user("amiel", "admin0003", "admin")
#add_user("ivan", "admin0004", "admin")
#add_user("kyle", "admin0005", "admin")
#delete_user()


def verify_user(username, password):
    hashed = hash_password(password)

    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = cursor.fetchone()
    print(user)
    conn.close()

    return user is not None



#/ =================== GUI Functions =====================


root = ctk.CTk()
root.withdraw()
root.title("Kape'Bahay Ordering System")


windows = {}


def lazy_create_window(name):
    if name in windows:
        return windows[name]
    
    if name == "login":
        w = create_login_window(root)
    elif name == "signup":
        w = create_signup_window(root)
    elif name == "cart":
        w = create_cart_window(root)
    elif name == "orders":
        w = create_orders_window(root)
    elif name == "management":
        w = create_management_window(root)
    elif name == "profile":
        w = create_profile_window(root)
    elif name == "sales":
        w = create_sales_report_window(root)
    else:
        raise ValueError(f"Unknown window: {name}")
    
    windows[name] = w
    w.withdraw()           
    return w


def verify_user_login(username, password):
    """
    Checks if the provided username and password match a record in the database.
    Returns (success: bool, role: str or None, error_message: str or None)
    """
    if not username.strip() or not password:
        return False, None, "Please enter both username and password"

    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Get the stored hash and role for this username
        cursor.execute("""
            SELECT password, role 
            FROM users 
            WHERE username = ?
        """, (username.strip(),))

        result = cursor.fetchone()

        conn.close()

        if result is None:
            return False, None, "Username not found"

        stored_hash, role = result

        entered_hash = hash_password(password)

        if entered_hash == stored_hash:
            return True, role, None
        else:
            return False, None, "Incorrect password"

    except sqlite3.Error as e:
        return False, None, f"Database error: {str(e)}"
    except Exception as e:
        return False, None, f"Unexpected error: {str(e)}"




# Craete your windows here. You can also create more functions for other windows you will create in the future. Just make sure to follow the same format as the functions above.
def create_login_window(master):
    loginwindow = ctk.CTkToplevel(master)
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

    businessLogoImage = ctk.CTkImage(Image.open("kape't_bahay_logo.png"), size=(400, 400))
    businessLogo = ctk.CTkLabel(leftframe, 
                                text="",
                                font=("Segoe UI", 20, "bold"),
                                text_color="#FFFFFF",
                                width=400,
                                height=400,
                                fg_color="transparent",
                                image=businessLogoImage)
    businessLogo.pack(padx=(80,0), pady=(80,0), anchor="center")
    
    
    greetingLabel = ctk.CTkLabel(leftframe, 
                                 bg_color="transparent",
                                 text="Kape't Bahay Cafe", 
                                 text_color="#FFFFFF",
                                 font=("Comic Sans MS", 40, "bold"))
    greetingLabel.pack(padx=(80,0), pady=(30,0), anchor="center")

    subGreetingLabel = ctk.CTkLabel(leftframe, 
                                 text="Ordering and Management System",
                                 text_color="#FFFFFF",
                                 font=("Comic Sans MS", 30, "bold"),
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
                                command=lambda: attempt_login())
    loginButton.pack(padx=(60,60), pady=(0,5), fill="both")

    signupButton = ctk.CTkButton(rightframe, 
                                text="Don't have an account?", 
                                font=ctk.CTkFont(size=14), 
                                fg_color="transparent", 
                                text_color="#3032AA",
                                hover_color="#FFFFFF",
                                command=lambda: open_signup_window())    
    signupButton.pack(pady=(0,5))


    def attempt_login():
        username = usernameEntry.get()
        password = passwordEntry.get()

        success, user_role, error_msg = verify_user_login(username, password)

        if success:
            current_user["username"] = username
            current_user["role"] = user_role
            messagebox.showinfo("Success", f"Welcome, {username}! ({user_role})")
            show_window("profile")  # or wherever you want to go after login
        else:
            # Shows the specific error
            messagebox.showerror("Login Failed", error_msg)
            passwordEntry.delete(0, ctk.END)
            passwordEntry.focus_set()


    def open_signup_window():
        signupWindow = lazy_create_window("signup")

        if "signup" in windows and windows["signup"].winfo_exists():
            windows["signup"].destroy()
        
        signupWindow = create_signup_window(root)
        windows["signup"] = signupWindow

        signupWindow.deiconify()
        signupWindow.lift()
        signupWindow.focus_force()

        loginwindow.grab_set()  
        signupWindow.grab_set()
        signupWindow.attributes("-topmost", True)
        
        signupWindow.wait_window()

        loginwindow.grab_release()
        loginwindow.lift()
        loginwindow.focus_force()
        
    return loginwindow


def create_signup_window(master):
    signupwindow = ctk.CTkToplevel(master)
    signupwindow.geometry("570x780")
    signupwindow.title("Kape'Bahay Ordering System - Signup")
    signupwindow.resizable(False, False)
    signupwindow.configure(fg_color="#43382F")

    boxFrame = ctk.CTkFrame(signupwindow, 
                            fg_color="#F2F1EF",
                            corner_radius=15,
                            border_width=2,
                            border_color="#dddddd")
    boxFrame.pack(padx=(40,40), pady=(40,40), fill="both", expand=True)
    boxFrame.pack_propagate(False)
    boxFrame.grid_propagate(False)

    # 10 Rows, 1 Column

    signupLabel = ctk.CTkLabel(boxFrame,
                              text="Sign Up",
                              font=("Segoe UI Light", 40, "bold"),
                              fg_color="transparent",
                              text_color="#000000")
    signupLabel.grid(row=0, column=0, padx=20, pady=(20,0), sticky="w")

    infoLabel = ctk.CTkLabel(boxFrame,
                             text="Create an account or",   
                                font=("Arial", 14),
                                fg_color="transparent",
                                text_color="#000000")
    infoLabel.grid(row=1, column=0, padx=22, pady=(0,20), sticky="w")

    signinButton = ctk.CTkButton(boxFrame, 
                                text="Sign in", 
                                font=("Arial", 14, "underline"), 
                                width=5, 
                                height=5, 
                                fg_color="transparent", 
                                text_color="#3032AA",
                                hover_color="#FFFFFF",
                                command=lambda: (signupwindow.destroy(), lazy_create_window("login").deiconify()))
    signinButton.place(x=158, y=77)
    
    emailLabel = ctk.CTkLabel(boxFrame,
                              text="Email Address",
                                font=("Arial", 14),
                                fg_color="transparent",
                                text_color="#000000")
    emailLabel.grid(row=2, column=0, padx=(28,0), pady=(0,0), sticky="w")

    emailEntry = ctk.CTkEntry(boxFrame,
                              placeholder_text="Enter your email address",
                                width=450,
                                height=60,
                                font=("Arial", 14),
                                text_color="#000000",
                                fg_color="#FFFFFF",
                                border_color="#dddddd",
                                corner_radius=10)
    emailEntry.grid(row=3, column=0, padx=20, pady=(0,10), sticky="ew")

    usernamelabel = ctk.CTkLabel(boxFrame,
                                text="Username",
                                font=("Arial", 14),
                                fg_color="transparent",
                                text_color="#000000")
    usernamelabel.grid(row=4, column=0, padx=(28,0), pady=(0,0), sticky="w")

    usernameEntry = ctk.CTkEntry(boxFrame,
                                width=400,
                                height=60,
                                placeholder_text="Enter your username",
                                font=("Arial", 14),
                                text_color="#000000",
                                fg_color="#FFFFFF",
                                border_color="#dddddd",
                                corner_radius=10,
                                show="*")
    usernameEntry.grid(row=5, column=0, padx=22, pady=(0,10), sticky="ew")

    passwordLabel = ctk.CTkLabel(boxFrame,
                                text="Password",
                                font=("Arial", 14),
                                fg_color="transparent",
                                text_color="#000000")
    passwordLabel.grid(row=6, column=0, padx=(28,0), pady=(0,0), sticky="w")

    passwordEntry = ctk.CTkEntry(boxFrame,
                                width=400,
                                height=60,
                                placeholder_text="Enter your password",
                                font=("Arial", 14),
                                text_color="#000000",
                                fg_color="#FFFFFF",
                                border_color="#dddddd",
                                corner_radius=10,
                                show="*")
    passwordEntry.grid(row=7, column=0, padx=22, pady=(0,10), sticky="ew")

    repeatPasswordLabel = ctk.CTkLabel(boxFrame,
                                text="Repeat Password",
                                font=("Arial", 14),
                                fg_color="transparent",
                                text_color="#000000")
    repeatPasswordLabel.grid(row=8, column=0, padx=(28,0), pady=(0,0), sticky="w")

    repeatPasswordEntry = ctk.CTkEntry(boxFrame,
                                width=400,
                                height=60,
                                placeholder_text="Repeat your password",
                                font=("Arial", 14),
                                text_color="#000000",
                                fg_color="#FFFFFF",
                                border_color="#dddddd",
                                corner_radius=10,
                                show="*")
    repeatPasswordEntry.grid(row=9, column=0, padx=22, pady=(0,10), sticky="ew")

    show_password_var = ctk.BooleanVar()

    def toggle_password():
        if show_password_var.get():
            passwordEntry.configure(show="")
            repeatPasswordEntry.configure(show="")
        else:
            passwordEntry.configure(show="*")
            repeatPasswordEntry.configure(show="*")

    show_password_checkbox = ctk.CTkCheckBox(boxFrame,
                                            text="Show Password",
                                            variable=show_password_var,
                                            onvalue=True,
                                            offvalue=False,
                                            checkbox_width=16,
                                            checkbox_height=16,
                                            checkmark_color="#43382F",
                                            border_width=2,
                                            hover_color="#43382F",
                                            text_color="#000000",
                                            command=toggle_password,
                                            corner_radius=2)
    show_password_checkbox.grid(row=10, column=0, padx=(28,0), pady=(0,0), sticky="ew")

    signupButton = ctk.CTkButton(boxFrame,
                                text="Sign Up",
                                font=ctk.CTkFont(size=20),
                                width=200,
                                height=50,
                                fg_color="#1E6F43",
                                hover_color="#14532D"
                                """command=lambda: attempt_signup()""")
    signupButton.grid(row=11, column=0, padx=22, pady=(20,0), sticky="ew")
    
    descriptionLabel = ctk.CTkLabel(boxFrame,
                                    text="By signing up to create an account, you agree to our \nTerms of Service and Privacy Policy.",
                                    font=("Segoe UI Light", 12),
                                    fg_color="transparent",
                                    text_color="#5E5E5E")
    descriptionLabel.grid(row=12, column=0, padx=22, pady=(20,20), sticky="ew")




    def close_signup():
        signupwindow.destroy()

    signupwindow.protocol("WM_DELETE_WINDOW", close_signup)
    signupwindow.withdraw()
    return signupwindow


def create_cart_window(master):
    cartwindow = ctk.CTkToplevel(master)
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
            command=lambda n=name, p=price: add_to_cart(n, p)  
        ).pack(pady=5)

        col += 1
        if col > 2:
            col = 0
            row += 1

    return cartwindow


# Orders Window
def create_orders_window(master):
    orders_window = ctk.CTkToplevel(master)
    orders_window.geometry("800x600")
    orders_window.title("Kape'Bahay Ordering System - Orders")
     # Further implementation of the orders window goes here.  
    return orders_window


# Beverage management window
def create_management_window(master):
    settings_window = ctk.CTkToplevel(master)
    settings_window.geometry("800x600")
    settings_window.title("Kape'Bahay Ordering System - Settings")
     # Further implementation of the settings window goes here.  
    return settings_window

def create_profile_window(master):
    profile_window = ctk.CTkToplevel(master)
    profile_window.geometry("1020x730")
    profile_window.title("Kape'Bahay - Barista Profile")
    profile_window.resizable(False, False)
    profile_window.configure(fg_color="#120f0d")

    sales_var = ctk.DoubleVar(value=500.00)
    orders_var = ctk.IntVar(value=42)

    
    name_label = ctk.CTkLabel(profile_window, text="---", 
                              font=("Segoe UI", 54, "bold"), text_color="white")
    name_label.grid(row=0, column=0, padx=(50, 0), pady=(40, 40), sticky="w")
    
    role_badge = ctk.CTkLabel(profile_window, text="---", fg_color="#c8b591", text_color="black", 
                              corner_radius=15, font=("Segoe UI", 16, "bold"), width=110, height=35)
    role_badge.grid(row=0, column=1, padx=(10, 720), pady=(25, 20), sticky="w")

    
    profile_window.name_label = name_label
    profile_window.role_badge = role_badge


    main_box = ctk.CTkFrame(profile_window, fg_color="#6f5e4c", corner_radius=20, width=960, height=540)
    main_box.grid(row=1, column=0, columnspan=2, padx=30, pady=(0), sticky="nsew")
    main_box.grid_propagate(False)

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
                                 width=400, height=120, corner_radius=25,
                                 command=lambda: show_window("cart"))
    order_button.place(x=505, y=50)
    

    logout_button = ctk.CTkButton(main_box, text="LOGOUT", font=("Segoe UI", 32, "bold"), 
                                  fg_color="#513626", hover_color="#3d291d", 
                                  width=400, height=120, corner_radius=25, 
                                  command=lambda: show_window("login"))
    logout_button.place(x=505, y=200)

    # ================= Notifications Section with Scrollable Frame =================
    notif_title = ctk.CTkLabel(main_box, text="Notifications:", font=("Segoe UI", 22, "bold"), text_color="white")
    notif_title.place(x=35, y=390)

    notif_frame = ctk.CTkScrollableFrame(main_box, 
                                         width=870, 
                                         height=40, 
                                         fg_color="transparent", 
                                         scrollbar_button_color="#6f5e4c", 
                                         scrollbar_button_hover_color="#6f5e4c")
    notif_frame.place(x=35, y=425)

    stock_alert = ctk.CTkLabel(notif_frame, text="• Low Stock: Whole Milk (2 Boxes remaining)", 
                               font=("Segoe UI", 18), text_color="#ffd7ba", anchor="w")
    stock_alert.pack(fill="x", pady=2)

    return profile_window

def create_sales_report_window(master):
    report_window = ctk.CTkToplevel(master)
    report_window.geometry("800x600")
    report_window.title("Kape'Bahay Ordering System - Sales Report")
     # Further implementation of the sales report window goes here.  
    return report_window
 

loginWindowCreation = lazy_create_window("login")
loginWindowCreation.deiconify()
loginWindowCreation.lift()

def show_window(name):
    target = lazy_create_window(name)

    # Hide others
    for key, win in windows.items():
        if key != name and win is not None and win.winfo_exists():
            win.withdraw()

    if name == "profile" and current_user["username"]:
        # Update labels BEFORE showing
        target.name_label.configure(text=current_user["username"].upper())
        target.role_badge.configure(text=current_user["role"].upper())
        # optional: change badge color based on role
        if current_user["role"].upper() == "ADMIN":
            target.role_badge.configure(fg_color="#c8b591")
        else:
            target.role_badge.configure(fg_color="#646a77")  # gray for cashier

    target.deiconify()
    target.lift()
    target.focus_force()

root.mainloop()