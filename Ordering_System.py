import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import hashlib
import sqlite3
import re
from datetime import datetime
import os
import shutil


current_user = {
    "username": None,
    "role": None
}

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


beverages = [
    {"category": "0", "name": "Milo Malt", "price": 155.00, "size": "Medium", "available": True},
    {"category": "0", "name": "White salted", "price": 155.00, "size": "Medium", "available": True},
    {"category": "0", "name": "Caramel", "price": 145.00, "size": "Medium", "available": True},
    {"category": "0", "name": "Mocha", "price": 145.00, "size": "Medium", "available": True},

    {"category": "1", "name": "Classic Spanish", "price": 110.00, "size": "Medium", "available": True},
    {"category": "1", "name": "Spanish cinnamon", "price": 115.00, "size": "Medium", "available": True},
    {"category": "1", "name": "Spanish Mocha", "price": 115.00, "size": "Medium", "available": True},

    {"category": "2", "name": "Classic Seasalt", "price": 115.00, "size": "Medium", "available": True},
    {"category": "2", "name": "Seasalt Caramel", "price": 120.00, "size": "Medium", "available": True},
    {"category": "2", "name": "Hazelnut Paline", "price": 120.00, "size": "Medium", "available": True},

    {"category": "3", "name": "Black Irish", "price": 105.00, "size": "Medium", "available": True},
    {"category": "3", "name": "Black Seasalt", "price": 110.00, "size": "Medium", "available": True},
    {"category": "3", "name": "Black Vanilla Cream", "price": 110.00, "size": "Medium", "available": True},

    {"category": "4", "name": "Choco Cinnamon", "price": 110.00, "size": "Medium", "available": True},
    {"category": "4", "name": "Choco Caramel", "price": 110.00, "size": "Medium", "available": True},
    {"category": "4", "name": "Choco Strawberry", "price": 120.00, "size": "Medium", "available": True},

    {"category": "5", "name": "Traditional Matcha", "price": 105.00, "size": "Medium", "available": True},
    {"category": "5", "name": "Creamy Matcha", "price": 120.00, "size": "Medium", "available": True},
    {"category": "5", "name": "Matcha Strawberry", "price": 120.00, "size": "Medium", "available": True},
    {"category": "5", "name": "Choco Matcha", "price": 120.00, "size": "Medium", "available": True},
]



#/ ================== Database Functions =================
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
    conn.commit()
    conn.close()


def create_customer_orders_database():
    """Initialize database connection and create orders table"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS customer_orders
                     (order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer_name TEXT,
                      order_date TEXT,
                      total_amount REAL,
                      status TEXT)''')
    print("Customer orders database initialized.")
    conn.commit()
    return conn


def create_menu_item_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu_item
                     (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      item_name TEXT,
                      status TEXT)''')
    print("Menu item database initialized.")
    conn.commit()
    return conn


def create_order_item_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_item
                     (order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_id INTEGER,
                      item_id INTEGER,
                      size_id INTEGER,
                      quantity INTEGER,
                      unit_price REAL,
                      subtotal REAL,
                      FOREIGN KEY(order_id) REFERENCES customer_orders(order_id),
                      FOREIGN KEY(item_id) REFERENCES menu_item(item_id),
                      FOREIGN KEY(size_id) REFERENCES menu_size(size_id))''')
    print("Order item database initialized.")
    conn.commit()
    return conn

def create_menu_size_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu_size
                     (size_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      item_id INTEGER,
                      size_label TEXT,
                      price REAL,
                      FOREIGN KEY(item_id) REFERENCES menu_item(item_id))''')
    print("Menu size database initialized.")
    conn.commit()
    return conn

#create_database()
#create_customer_orders_database()
#create_menu_item_database()
#create_order_item_database()
#create_menu_size_database()



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
        conn.commit()
        conn.close()


# Isang beses lang to irun tapos comment na or delete na para hindi maulit ulit dagdag ng users.
#add_user("mico", "admin0001", "cashier", "mic0@gmail.com")
#add_user("paul", "admin0002", "cashier", "pa6308191@gmail.com")
#add_user("amiel", "admin0003", "admin", "amiel@gmail.com")
#add_user("ivan", "admin0004", "admin", "ivan@gmail.com")
#add_user("kyle", "admin0005", "admin", "kyle@gmail.com")

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


def verify_signup(username, password, repeat_password, email):
    hashed_pass = hash_password(password)
    hased_repeat_pass = hash_password(repeat_password)

    if hashed_pass != hased_repeat_pass:
        return False, "Passwords do not match"

    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=? AND email=?", (username, hashed_pass, email))
    user = cursor.fetchone()
    print(user)
    conn.close()


def create_employee_performance_database():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS employee_performance
                     (employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT,
                      total_sales REAL,
                      orders_made INTEGER,
                      FOREIGN KEY(username) REFERENCES users(username))''')
    print("Employee performance database initialized.")
    conn.commit()
    return conn

#create_employee_performance_database()



# Management Window Database Queries
def fetch_menu_items():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mi.item_id, mi.item_name, mi.status,
               ms.size_id, ms.size_label, ms.price
        FROM menu_item mi
        JOIN menu_size ms ON mi.item_id = ms.item_id
        ORDER BY mi.item_name
    """)

    data = cursor.fetchall()
    conn.close()
    return data


def add_menu_item(name, size, price):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO menu_item (item_name, status) VALUES (?, 1)", (name,))
    item_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO menu_size (item_id, size_label, price) VALUES (?, ?, ?)",
        (item_id, size, price)
    )

    conn.commit()
    conn.close()


def delete_menu_item(item_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu_size WHERE item_id=?", (item_id,))
    cursor.execute("DELETE FROM menu_item WHERE item_id=?", (item_id,))

    conn.commit()
    conn.close()


def toggle_menu_item(item_id, current_status):
    conn = create_connection()
    cursor = conn.cursor()

    new_status = 0 if current_status == 1 else 1

    cursor.execute(
        "UPDATE menu_item SET status=? WHERE item_id=?",
        (new_status, item_id)
    )

    conn.commit()
    conn.close()

    return new_status


def update_menu_item(item_id, name, size_id, size, price):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE menu_item SET item_name=? WHERE item_id=?", (name, item_id))
    cursor.execute("UPDATE menu_size SET size_label=?, price=? WHERE size_id=?",
                   (size, price, size_id))

    conn.commit()
    conn.close()


def update_menu_item_status(item_id, new_status):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE menu_item SET status=? WHERE item_id=?",
        (new_status, item_id)
    )

    conn.commit()
    conn.close()


# ================= IMAGE =================
IMAGE_FOLDER = "assets/images"
ICONS_FOLDER = "assets/icons"
os.makedirs(IMAGE_FOLDER, exist_ok=True)


def get_image_path(item_name):
    return os.path.join(IMAGE_FOLDER, f"{item_name}.png")


def load_image_file(filename, size=(200, 200)):
    path = os.path.join(IMAGE_FOLDER, filename)

    if not os.path.exists(path):
        print(f"Image not found: {path}")
        return None

    try:
        img = Image.open(path)
        img.thumbnail(size)
        return ctk.CTkImage(img, size=size)
    except Exception as e:
        print("Error loading image:", e)
        return None
    
    
def load_ctk_image(item_name, size=(200, 200)):
    path = get_image_path(item_name)

    if not os.path.exists(path):
        return None

    try:
        img = Image.open(path)
        img.thumbnail(size)  # prevents stretching
        return ctk.CTkImage(img, size=size)
    except:
        return None


def save_image(file_path, item_name):
    if not file_path:
        return

    destination = os.path.join(IMAGE_FOLDER, f"{item_name}.png")
    shutil.copy(file_path, destination)


def load_image(name, size=(220, 200)):
    for ext in ["png", "jpg", "jpeg"]:
        path = os.path.join(IMAGE_FOLDER, f"{name}.{ext}")
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)  # Force exact size
            return ctk.CTkImage(img, size=size)
    return None

def load_icon(name, size=(60,30)):
    for ext in ["png", "jpg", "jpeg"]:
        path = os.path.join(ICONS_FOLDER, f"{name}.{ext}")
        if os.path.exists(path):
            img = Image.open(path)
            img.thumbnail(size)
            return ctk.CTkImage(img, size=size)
    return None


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
        w = create_profile_window(root, role=current_user["role"])
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

    logo_img = load_image_file("kape't_bahay_logo.png", size=(400, 400))

    businessLogo = ctk.CTkLabel(
    leftframe,
    text="",
    width=400,
    height=400,
    fg_color="transparent",
    image=logo_img
)

    businessLogo.image = logo_img  # VERY IMPORTANT
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
                                corner_radius=10)
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
                                hover_color="#14532D",
                                command=lambda: attempt_signup())
    signupButton.grid(row=11, column=0, padx=22, pady=(20,0), sticky="ew")
    
    descriptionLabel = ctk.CTkLabel(boxFrame,
                                    text="By signing up to create an account, you agree to our \nTerms of Service and Privacy Policy.",
                                    font=("Segoe UI Light", 12),
                                    fg_color="transparent",
                                    text_color="#5E5E5E")
    descriptionLabel.grid(row=12, column=0, padx=22, pady=(20,20), sticky="ew")


    def is_valid_email(email):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return bool(re.match(pattern, email.strip()))

    def username_exists(username):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username.strip(),))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def email_exists(email):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email.strip(),))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def attempt_signup():
        username = usernameEntry.get().strip()
        email    = emailEntry.get().strip()
        password = passwordEntry.get()
        repeat   = repeatPasswordEntry.get()

        # 1. Basic validation
        if not email:
            messagebox.showwarning("Input Error", "Email is required.")
            emailEntry.focus()
            return
        
        if not username:
            messagebox.showwarning("Input Error", "Username is required.")
            usernameEntry.focus()
            return

        if not is_valid_email(email):
            messagebox.showwarning("Input Error", "Please enter a valid email address.")
            emailEntry.focus()
            return

        if not password:
            messagebox.showwarning("Input Error", "Password is required.")
            passwordEntry.focus()
            return

        if password != repeat:
            messagebox.showwarning("Input Error", "Passwords do not match.")
            repeatPasswordEntry.delete(0, "end")
            repeatPasswordEntry.focus()
            return

        if len(password) < 6:
            messagebox.showwarning("Input Error", "Password must be at least 6 characters long.")
            passwordEntry.focus()
            return

        # 2. Check if username or email already exists
        if username_exists(username):
            messagebox.showerror("Signup Failed", "Username already exists. Please choose another.")
            usernameEntry.delete(0, "end")
            usernameEntry.focus()
            return

        if email_exists(email):
            messagebox.showerror("Signup Failed", "This email is already registered.")
            emailEntry.delete(0, "end")
            emailEntry.focus()
            return

        # 3. All checks passed → create user as "cashier"
        success = add_user(username, password, "cashier", email)

        if success:
            messagebox.showinfo("Success", f"Account created successfully!\nWelcome, {username} (Cashier)")
            signupwindow.destroy()
            # Go back to login window
            login_win = lazy_create_window("login")
            login_win.deiconify()
        else:
            messagebox.showerror("Error", "Failed to create account. Please try again.")


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
    orders_win = ctk.CTkToplevel(master)
    orders_win.geometry("1280x720")
    orders_win.title("Kape'Bahay - Manage Orders")
    orders_win.resizable(False, False)
    orders_win.configure(fg_color="#43382F")

    # Layout: full grid
    orders_win.grid_columnconfigure(0, weight=1)
    orders_win.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(orders_win, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))

    ctk.CTkLabel(
        header,
        text="Orders Management",
        font=("Segoe UI", 32, "bold"),
        text_color="white"
    ).pack(side="left", padx=10)

    refresh_btn = ctk.CTkButton(
        header,
        text="🔄 Refresh",
        width=140,
        command=lambda: refresh_orders(content_area)
    )
    refresh_btn.pack(side="right", padx=10)

    # Tab switch
    tab_frame = ctk.CTkFrame(orders_win, fg_color="transparent")
    tab_frame.grid(row=0, column=0, sticky="ew", pady=(80,0), padx=20)

    current_tab = ctk.StringVar(value="pending")

    pending_tab = ctk.CTkButton(
        tab_frame,
        text="Pending & Preparing",
        fg_color="#1E6F43" if current_tab.get() == "pending" else "#555",
        command=lambda: [current_tab.set("pending"), refresh_orders(content_area)]
    )
    pending_tab.pack(side="left", padx=5)

    completed_tab = ctk.CTkButton(
        tab_frame,
        text="Completed",
        fg_color="#1E6F43" if current_tab.get() == "completed" else "#555",
        command=lambda: [current_tab.set("completed"), refresh_orders(content_area)]
    )
    completed_tab.pack(side="left", padx=5)

    # Main scrollable content
    content_area = ctk.CTkScrollableFrame(orders_win, fg_color="#2e241f")
    content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10,20))

    # Refresh function (now takes the parent frame)
    def refresh_orders(parent):
        # Clear old content
        for widget in parent.winfo_children():
            widget.destroy()

        conn = create_connection()
        cursor = conn.cursor()

        if current_tab.get() == "pending":
            cursor.execute("""
                SELECT order_id, customer_name, order_date, total_amount, status
                FROM customer_orders 
                WHERE status IN ('Pending', 'Preparing')
                ORDER BY order_date DESC
            """)
        else:
            cursor.execute("""
                SELECT order_id, customer_name, order_date, total_amount, status
                FROM customer_orders 
                WHERE status = 'Completed'
                ORDER BY order_date DESC
            """)

        orders = cursor.fetchall()
        conn.close()

        if not orders:
            ctk.CTkLabel(
                parent,
                text=f"No {current_tab.get().title()} orders at the moment ☕",
                font=("Segoe UI", 20),
                text_color="#aaa"
            ).pack(expand=True, pady=120)
            return

        for order in orders:
            oid, customer, date, total, status = order
            card = ctk.CTkFrame(parent, fg_color="#4a3c30", corner_radius=12)
            card.pack(fill="x", pady=10, padx=10, ipady=10)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(10,5))

            ctk.CTkLabel(top_row, text=f"Order #{oid}  •  {customer}",
                         font=("Segoe UI", 16, "bold"),
                         text_color="white").pack(side="left")

            ctk.CTkLabel(top_row, text=f"₱{total:,.2f}",
                         font=("Segoe UI", 16, "bold"),
                         text_color="#ffca28").pack(side="right")

            ctk.CTkLabel(card, text=f"{date} • {status}",
                         text_color="#ccc").pack(anchor="w", padx=15, pady=4)

            # Action buttons
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(fill="x", padx=15, pady=(8,12))

            ctk.CTkButton(btns, text="View Details", width=120,
                          command=lambda o=order: messagebox.showinfo("Details", f"Order #{o[0]}")).pack(side="left", padx=5)

            if status == "Pending":
                ctk.CTkButton(btns, text="Start Preparing", width=140,
                              fg_color="#0288D1",
                              command=lambda oid=oid: [start_preparing(oid), refresh_orders(parent)]).pack(side="left", padx=5)

            if status in ("Pending", "Preparing"):
                ctk.CTkButton(btns, text="Mark Completed", width=140,
                              fg_color="#4caf50",
                              command=lambda oid=oid: [complete_order(oid), refresh_orders(parent)]).pack(side="left", padx=5)

    
    def start_preparing(order_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE customer_orders SET status = 'Preparing' WHERE order_id = ?", (order_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Started", "Order is now being prepared")

    def complete_order(order_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE customer_orders SET status = 'Completed' WHERE order_id = ?", (order_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Done", "Order marked as completed")

    # Initial load
    refresh_orders(content_area)

    return orders_win

# Beverage management window
def create_management_window(master):
    beverage_window = ctk.CTkToplevel(master)
    beverage_window.geometry("1380x920")
    beverage_window.title("Management")
    beverage_window.configure(fg_color="#43382F")
    beverage_window.resizable(False, False)

    beverage_window.grid_columnconfigure(0, weight=9) 
    beverage_window.grid_columnconfigure(1, weight=3)
    beverage_window.grid_rowconfigure(1, weight=1)

    # HEADER
    header = ctk.CTkLabel(beverage_window, text="Manage Beverages",
                          font=("Segoe UI", 36, "bold"),
                          text_color="white")
    header.grid(row=0, column=0, padx=20, pady=10, sticky="w")

    # LEFT PANEL
    left = ctk.CTkScrollableFrame(beverage_window, fg_color="#2C241C")
    left.grid(row=1, column=0, padx=(20, 0), pady=20, sticky="nsew")
    for i in range(3):
        left.grid_columnconfigure(i, weight=1, uniform="col")
    

    # RIGHT PANEL
    right = ctk.CTkFrame(beverage_window, fg_color="#3A2F24")
    right.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

    # ================= REFRESH =================
    def refresh_products():
        for widget in left.winfo_children():
            widget.destroy()

        data = fetch_menu_items()

        row = 0
        col = 0


        for item_id, name, status, size_id, size, price in data:
            status = int(status)
            card = ctk.CTkFrame(left, fg_color="#4A3C2F", corner_radius=6, width=300, height=370)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="w")
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=1)

            # IMAGE
            img = load_image(name, size=(220, 200))
            if img:
                img_label = ctk.CTkLabel(card, image=img, text="")
                img_label.image = img
                img_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="n")
            else:
                # Placeholder so cards without images stay same height
                placeholder = ctk.CTkLabel(card, text="", width=220, height=200)
                placeholder.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="n")

            # NAME
            item_name = ctk.CTkLabel(card, text=name,
                         font=("Segoe UI", 16, "bold"),
                         text_color="white")
            item_name.grid(row=1, column=0, sticky="w", padx=(10, 10), pady=(5, 10))

            # SIZE + PRICE
            size_price = ctk.CTkLabel(card, 
                         text=f"{size} - ₱{price}",
                         font=("Segoe UI", 14),
                         text_color="#D0C9B8")
            size_price.grid(row=1, column=1, sticky="e", padx=(0, 10), pady=(0, 0))


            
            edit_button = ctk.CTkButton(card, text="Edit",
                          width=80,
                          height=40,
                          command=lambda i=item_id, n=name, sid=size_id, s=size, p=price:
                          open_edit_form(i, n, sid, s, p)
                          )
            edit_button.grid(row=2, column=0, padx=(10, 0), pady=(0, 0),sticky="w")
            
            delete_button = ctk.CTkButton(card, text="Delete",
                          width=80,
                          height=40,
                          fg_color="#C62828",
                          command=lambda i=item_id:
                          [delete_menu_item(i), refresh_products()]
                          )
            delete_button.grid(row=3, column=0, padx=(10, 0), pady=(10, 10), sticky="w")
            

            # ================= TOGGLE BUTTON =================

            toggle_on_img = load_icon("toggle_on")
            toggle_off_img = load_icon("toggle_off")

            # Use mutable container so closure is safe
            state = {"is_on": True if status == 1 else False}

            # STATUS LABEL
            status_label = ctk.CTkLabel(card,
                                        text="Available" if status == 1 else "Unavailable",
                                        fg_color="#2E7D32" if status == 1 else "#C62828",
                                        font=("Segoe UI", 14, "bold"),
                                        width=120,
                                        height=40,
                                        corner_radius=6
                                    )
            status_label.grid(row=2, column=1, padx=(12, 10), pady=(0, 0), sticky="e")


            def toggle_button_function(pid, btn, lbl, current_status, on_img, off_img):
                new_status = toggle_menu_item(pid, current_status)

                if new_status == 1:
                    btn.configure(image=on_img)
                    lbl.configure(text="Available", fg_color="#2E7D32")
                else:
                    btn.configure(image=off_img)
                    lbl.configure(text="Unavailable", fg_color="#C62828")

                # Rebind with updated status
                btn.configure(
                    command=lambda: toggle_button_function(pid, btn, lbl, new_status, on_img, off_img)
                )


            toggle_btn = ctk.CTkButton(card,
                                        text="",
                                        image=toggle_on_img if status == 1 else toggle_off_img,
                                        fg_color="transparent",
                                        width=60,
                                        height=40
                                    )
            toggle_btn.grid(row=3, column=1, padx=(12, 10), pady=(10, 10), sticky="e")


            # Bind correct values
            toggle_btn.configure(command=lambda pid=item_id, btn=toggle_btn, lbl=status_label, s=status,
                                 on=toggle_on_img, off=toggle_off_img:
                                 toggle_button_function(pid, btn, lbl, s, on, off))


            col += 1
            if col == 3:
                col = 0
                row += 1

    # ================= ADD FORM =================
    def open_add_form():
        form = ctk.CTkToplevel()
        form.geometry("400x500")
        form.title("Add Beverage")

        selected_image = {"path": None}

        ctk.CTkLabel(form, text="Add Beverage",
                     font=("Segoe UI", 24, "bold")).pack(pady=15)

        name_entry = ctk.CTkEntry(form, placeholder_text="Name")
        name_entry.pack(pady=10, padx=20, fill="x")

        size_entry = ctk.CTkEntry(form, placeholder_text="Size")
        size_entry.pack(pady=10, padx=20, fill="x")

        price_entry = ctk.CTkEntry(form, placeholder_text="Price")
        price_entry.pack(pady=10, padx=20, fill="x")

        img_label = ctk.CTkLabel(form, text="No Image")
        img_label.pack(pady=10)

        def choose_image():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg")]
            )
            if path:
                selected_image["path"] = path
                img_label.configure(text=os.path.basename(path))

        ctk.CTkButton(form, text="Choose Image",
                      command=choose_image).pack(pady=10)

        def save():
            name = name_entry.get()
            size = size_entry.get()

            try:
                price = float(price_entry.get())
            except:
                messagebox.showerror("Error", "Invalid price")
                return

            if not name or not size:
                messagebox.showerror("Error", "Fill all fields")
                return

            add_menu_item(name, size, price)

            if selected_image["path"]:
                save_image(selected_image["path"], name)

            form.destroy()
            refresh_products()

        ctk.CTkButton(form, text="Save",
                      fg_color="#1E6F43",
                      command=save).pack(pady=20)
        
    
    def open_edit_form(item_id, name, size_id, size, price):
        form = ctk.CTkToplevel()
        form.geometry("420x550")
        form.title(f"Edit {name}")
        form.configure(fg_color="#2C241C")

        selected_image = {"path": None}

        # ===== HEADER =====
        ctk.CTkLabel(
            form,
            text="Edit Beverage",
            font=("Segoe UI", 26, "bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        form_frame = ctk.CTkFrame(form, fg_color="#3A2F24", corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== NAME =====
        ctk.CTkLabel(form_frame, text="Beverage Name", text_color="#D0C9B8").pack(anchor="w", padx=20, pady=(15, 5))
        name_entry = ctk.CTkEntry(form_frame, height=40)
        name_entry.insert(0, name)
        name_entry.pack(fill="x", padx=20)

        # ===== SIZE =====
        ctk.CTkLabel(form_frame, text="Size Label", text_color="#D0C9B8").pack(anchor="w", padx=20, pady=(15, 5))
        size_entry = ctk.CTkEntry(form_frame, height=40)
        size_entry.insert(0, size)
        size_entry.pack(fill="x", padx=20)

        # ===== PRICE =====
        ctk.CTkLabel(form_frame, text="Price", text_color="#D0C9B8").pack(anchor="w", padx=20, pady=(15, 5))
        price_entry = ctk.CTkEntry(form_frame, height=40)
        price_entry.insert(0, str(price))
        price_entry.pack(fill="x", padx=20)

        # ===== IMAGE =====
        ctk.CTkLabel(form_frame, text="Product Image", text_color="#D0C9B8").pack(anchor="w", padx=20, pady=(15, 5))

        image_label = ctk.CTkLabel(form_frame, text="No new image selected", fg_color="#4A3C2F", height=100)
        image_label.pack(fill="x", padx=20)

        def choose_image():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if path:
                selected_image["path"] = path
                image_label.configure(text=os.path.basename(path))

        ctk.CTkButton(form_frame, text="Change Image", command=choose_image).pack(pady=10)

        # ===== SAVE =====
        def save_changes():
            new_name = name_entry.get().strip()
            new_size = size_entry.get().strip()

            try:
                new_price = float(price_entry.get())
            except:
                messagebox.showerror("Error", "Invalid price")
                return

            if not new_name or not new_size:
                messagebox.showerror("Error", "Fill all fields")
                return

            # Update database
            update_menu_item(item_id, new_name, size_id, new_size, new_price)

            # Rename image if name changed
            old_image = os.path.join(IMAGE_FOLDER, f"{name}.png")
            new_image = os.path.join(IMAGE_FOLDER, f"{new_name}.png")

            if name != new_name and os.path.exists(old_image):
                os.rename(old_image, new_image)

            # Save new image if selected
            if selected_image["path"]:
                save_image(selected_image["path"], new_name)

            form.destroy()
            refresh_products()

        ctk.CTkButton(
            form,
            text="Save Changes",
            fg_color="#0288D1",
            hover_color="#0277BD",
            height=45,
            command=save_changes
        ).pack(pady=20, padx=20, fill="x")


    # BUTTON
    ctk.CTkButton(right, text="Add Beverage",
                  command=open_add_form).pack(pady=20, padx=20, fill="x")

    beverage_window.after(100, refresh_products)

    return beverage_window


def create_profile_window(master, role="Cashier"):
    BG_DARK = "#505050"      
    BOX_BROWN = "#966240"    
    BTN_CLAY = "#63442d"     
    LOGOUT_ORANGE = "#b84a00" 
    TEXT_WHITE = "#ffffff"

    profile_window = ctk.CTkToplevel(master)
    profile_window.geometry("1280x720")
    profile_window.title(f"Kape'Bahay - {role.capitalize()} POV")
    profile_window.resizable(False, False)
    profile_window.configure(fg_color=BG_DARK)

    header = ctk.CTkFrame(profile_window, fg_color=BOX_BROWN, corner_radius=20, width=320, height=85)
    header.place(x=60, y=40)

    profile_window.name_label = ctk.CTkLabel(header, text="IVAN", font=("Arial", 44, "bold"), text_color=TEXT_WHITE)
    profile_window.name_label.place(x=20, y=10)
    
    badge_color = "#b5b5b5" if role.lower() == "admin" else "#d1d1d1"

    profile_window.role_badge = ctk.CTkLabel(header, text=role.capitalize(), fg_color=badge_color, text_color="black", 
                              corner_radius=15, font=("Arial", 14, "bold"), width=80, height=28)
    profile_window.role_badge.place(x=160, y=28)

    logout_btn = ctk.CTkButton(profile_window, text="LOG OUT", font=("Arial", 16, "bold"), 
                               fg_color=LOGOUT_ORANGE, hover_color="#8e3900", corner_radius=20,
                               width=120, height=50,
                               command=lambda: show_window("login"))
    logout_btn.place(x=1050, y=65)

    main_box = ctk.CTkFrame(profile_window, fg_color=BOX_BROWN, corner_radius=30, width=1160, height=520)
    main_box.place(relx=0.5, rely=0.6, anchor="center")

    v_divider = ctk.CTkFrame(main_box, width=2, height=480, fg_color="#b88a6d")
    v_divider.place(x=540, y=20)

    shift_title = ctk.CTkLabel(main_box, text="My Shift", font=("Arial", 28, "bold"), text_color=TEXT_WHITE)
    shift_title.place(x=40, y=20)

    stats_font = ("Arial", 18)
    ctk.CTkLabel(main_box, text="Status:", font=stats_font).place(x=60, y=85)
    ctk.CTkLabel(main_box, text="On Shift     +", fg_color=BTN_CLAY, width=180, height=40, corner_radius=20).place(x=165, y=85)

    ctk.CTkLabel(main_box, text="Total Sales:", font=stats_font).place(x=60, y=145)
    ctk.CTkLabel(main_box, text="PHP       999.99", fg_color=BTN_CLAY, width=180, height=40, corner_radius=20).place(x=165, y=145)

    ctk.CTkLabel(main_box, text="Total Orders Made:", font=stats_font).place(x=60, y=205)
    ctk.CTkLabel(main_box, text="999", fg_color=BTN_CLAY, width=130, height=40, corner_radius=20).place(x=225, y=205)

    ctk.CTkFrame(main_box, width=500, height=2, fg_color="#b88a6d").place(x=20, y=270)

    # --- THE RESPONSIVE UPDATE USER BUTTON ---
    update_user_btn = ctk.CTkButton(main_box, text="UPDATE USER", font=("Arial", 18, "bold"), 
                                    fg_color=BTN_CLAY, hover_color="#4d3523", corner_radius=35,
                                    width=450, height=90, 
                                    command=lambda: open_update_user_window(profile_window)) # Attached to new function
    update_user_btn.place(x=45, y=340)

    btn_style = {"font": ("Arial", 18, "bold"), "fg_color": BTN_CLAY, "hover_color": "#4d3523", "width": 520, "height": 90, "corner_radius": 35}

    if role.lower() == "admin":
        buttons =["CREATE ORDER", "VIEW PENDING ORDERS", "VIEW SALES REPORT", "BEVERAGE MANAGEMENT"]
    else:
        buttons =["CREATE ORDER", "VIEW SALES REPORT", "VIEW SALES REPORT"]

    # Assign functionality strictly to the buttons
    for i, btn_text in enumerate(buttons):
        y_pos = 35 + (i * 115) if role.lower() == "admin" else 60 + (i * 135)

        # Decide which window to open based on the button name
        if btn_text == "CREATE ORDER":
            cmd = lambda: show_window("cart")
        elif btn_text == "VIEW PENDING ORDERS":
            cmd = lambda: show_window("orders")
        elif btn_text == "VIEW SALES REPORT":
            cmd = lambda: show_window("sales")
        elif btn_text == "BEVERAGE MANAGEMENT":
            cmd = lambda: show_window("management")
        else:
            cmd = None
            
        ctk.CTkButton(main_box, text=btn_text, command=cmd, **btn_style).place(x=580, y=y_pos)

    profile_window.protocol("WM_DELETE_WINDOW", lambda: master.destroy())
    return profile_window


def open_update_user_window(master):
    # Match existing color palette
    BG_DARK = "#505050"      
    BOX_BROWN = "#966240"    
    BTN_CLAY = "#63442d"     
    TEXT_WHITE = "#ffffff"
    LOGOUT_ORANGE = "#b84a00" 

    # Create the top-level window (Pop-up)
    update_win = ctk.CTkToplevel(master)
    update_win.geometry("450x550")
    update_win.title("Update User Information")
    update_win.resizable(False, False)
    update_win.configure(fg_color=BG_DARK)
    
    # Keep this window on top and grab focus (Modal)
    update_win.transient(master)
    update_win.grab_set()

    # Container to hold the form
    container = ctk.CTkFrame(update_win, fg_color=BOX_BROWN, corner_radius=20, width=370, height=470)
    container.place(relx=0.5, rely=0.5, anchor="center")

    # Title
    title_label = ctk.CTkLabel(container, text="Edit Profile", font=("Arial", 28, "bold"), text_color=TEXT_WHITE)
    title_label.place(relx=0.5, y=40, anchor="n")

    # Entry Styling
    label_font = ("Arial", 16)
    entry_style = {"width": 290, "height": 40, "corner_radius": 10, "fg_color": "#e0e0e0", "text_color": "black"}

    # 1. Username
    ctk.CTkLabel(container, text="New Username:", font=label_font, text_color=TEXT_WHITE).place(x=40, y=95)
    username_entry = ctk.CTkEntry(container, placeholder_text="Enter new username", **entry_style)
    username_entry.place(x=40, y=125)

    # 2. Password
    ctk.CTkLabel(container, text="New Password:", font=label_font, text_color=TEXT_WHITE).place(x=40, y=180)
    password_entry = ctk.CTkEntry(container, placeholder_text="Enter new password", show="*", **entry_style)
    password_entry.place(x=40, y=210)

    # 3. Email Address
    ctk.CTkLabel(container, text="New Email Address:", font=label_font, text_color=TEXT_WHITE).place(x=40, y=265)
    email_entry = ctk.CTkEntry(container, placeholder_text="Enter new email", **entry_style)
    email_entry.place(x=40, y=295)

    # Fetch current user data to pre-fill the form
    current_usr = current_user.get("username")
    current_email = ""
    if current_usr:
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username=?", (current_usr,))
            row = cursor.fetchone()
            if row:
                current_email = row[0]
            conn.close()
            
            # Pre-fill the entries
            username_entry.insert(0, current_usr)
            email_entry.insert(0, current_email)
        except sqlite3.Error:
            pass

    # Save Functionality
    def save_changes():
        new_username = username_entry.get().strip()
        new_password = password_entry.get()
        new_email = email_entry.get().strip()
        
        # Check if fields are filled
        if not new_username or not new_password or not new_email:
            messagebox.showwarning("Input Error", "All fields are required to update your profile.")
            return
            
        hashed_pw = hash_password(new_password)
        old_username = current_user["username"]

        try:
            conn = create_connection()
            cursor = conn.cursor()
            
            # Update the existing user in the database
            cursor.execute("""
                UPDATE users 
                SET username = ?, password = ?, email = ?
                WHERE username = ?
            """, (new_username, hashed_pw, new_email, old_username))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Account updated successfully!")
            
            # Update global state so the program knows your new username
            current_user["username"] = new_username
            
            # Close the update window and refresh the profile window to show the updated name
            update_win.destroy()
            show_window("profile")
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This username is already taken. Please choose another.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    # Save Button
    save_btn = ctk.CTkButton(container, text="SAVE CHANGES", font=("Arial", 16, "bold"), 
                             fg_color=BTN_CLAY, hover_color="#4d3523", corner_radius=20, 
                             width=290, height=45, command=save_changes)
    save_btn.place(x=40, y=360)

    # Cancel Button
    cancel_btn = ctk.CTkButton(container, text="CANCEL", font=("Arial", 16, "bold"), 
                               fg_color=LOGOUT_ORANGE, hover_color="#8e3900", corner_radius=20, 
                               width=290, height=45, command=update_win.destroy)
    cancel_btn.place(x=40, y=415)


def create_sales_report_window(master):
    report_window = ctk.CTkToplevel(master)
    report_window.geometry("1200x800")
    report_window.title("Kape'Bahay Ordering System - Sales Report")
    #report_window.resizable(False, False)
    report_window.configure(fg_color="#d9d9d9")
    # Further implementation of the sales report window goes here.  

    left_frame = ctk.CTkFrame(report_window, fg_color="#80563f")
    left_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)
    

    right_frame = ctk.CTkFrame(report_window, fg_color="#7c665a")
    right_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

    # Left Frame Widgets





    # Right Frame Widgets


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