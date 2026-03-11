import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import hashlib
import sqlite3
import re
from datetime import datetime
import os
import shutil
import threading


current_user = {
    "username": None,
    "role": None
}

CATEGORIES = ["All", "Favorites", "Spanish Series", "Seasalt Series", "Black Series", "Choco Series", "Matcha Series"]


#/ ================== Database Functions =================
def create_connection():
    conn = sqlite3.connect("kape't_bahay_database.db")
    return conn

# Used to hash passwords for security purposes.
def hash_password(data):
    return hashlib.sha256(data.encode()).hexdigest()

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
        user_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO employee_performance (employee_id, username, total_sales, orders_made, on_shift) VALUES (?, ?, 0, 0)",
            (user_id, username)
        )

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # username already exists
    finally:
        conn.close()

#add_user("mico", "cashier0001", "cashier", "mico@gmail.com")
#add_user("paul", "cashier0002", "cashier", "paul@gmail.com")
#add_user("amiel", "admin0001", "admin", "amiel@gmail.com")
#add_user("ivan", "admin0002", "superAdmin", "ivan@gmail.com")
#add_user("kyle", "admin0003", "admin", "kyle@gmail.com")
# delete all orders in order items table
def delete_all_orders():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_item")
    conn.commit()
    conn.close()

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer_orders")
    conn.commit()
    conn.close()

#delete_all_orders()

# Used to delete users from the users table.
def delete_user(): 
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users")
    conn.commit()

    cursor.execute("DELETE FROM employee_performance")

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print("USERS AFTER DELETE:", rows)

    conn.commit()
    conn.close()


#elete_user()

# Used to add recovery questions to the database
def add_recovery_questions(user_id, question_number, recovery_question, answer):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO recovery_questions (user_id, question_number, recovery_question, answer) VALUES (?, ?, ?, ?)", (user_id, question_number, recovery_question, answer))
    conn.commit()
    conn.close()

# Used to verify users
def verify_user(username, password):
    hashed = hash_password(password)

    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed))
    user = cursor.fetchone()
    print(user)
    conn.close()

    return user is not None

# Used to verify signups
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

# Center Every Window
def center_window(win, width, height):
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


# -- Orders Window Database Queries --
def fetch_order_details(order_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mi.item_name, oi.quantity, oi.subtotal
        FROM order_item oi
        JOIN menu_item mi ON oi.item_id = mi.item_id
        WHERE oi.order_id = ?
    """, (order_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# -- Cart Window Database Queries --
def fetch_available_menu_items(category_filter=None):
    conn = create_connection()
    cursor = conn.cursor()
    if category_filter and category_filter != "All":
        cursor.execute("""
            SELECT item_id, item_name, category, price
            FROM menu_item
            WHERE status = 1 AND category = ?
            ORDER BY item_name
        """, (category_filter,))
    else:
        cursor.execute("""
            SELECT item_id, item_name, category, price
            FROM menu_item
            WHERE status = 1
            ORDER BY item_name
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_order(customer_name, cart_items):
    conn = create_connection()
    cursor = conn.cursor()
    total = sum(i["price"] * i["quantity"] for i in cart_items)
    cursor.execute("""
        INSERT INTO customer_orders (customer_name, order_date, total_amount, status)
        VALUES (?, datetime('now', 'localtime'), ?, 'Pending')
    """, (customer_name, total))
    order_id = cursor.lastrowid
    for item in cart_items:
        subtotal = item["price"] * item["quantity"]
        cursor.execute("""
            INSERT INTO order_item (order_id, item_id, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, item["item_id"], item["quantity"], item["price"], subtotal))
    conn.commit()
    conn.close()
    return order_id

# -- Profile Window Database Queries --
def fetch_employee_performance(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT total_sales, orders_made, on_shift
        FROM employee_performance
        WHERE username = ?
    """, (username,))
    data = cursor.fetchone()
    conn.close()
    return data

def toggle_employee_shift(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT on_shift FROM employee_performance WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    if row is None:
        conn.close()
        return 0

    new_shift = 0 if row[0] == 1 else 1
    cursor.execute(
        "UPDATE employee_performance SET on_shift = ? WHERE username = ?",
        (new_shift, username)
    )
    conn.commit()
    conn.close()
    return new_shift


def set_employee_shift_off(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE employee_performance SET on_shift = 0 WHERE username = ?",
        (username,)
    )
    conn.commit()
    conn.close()


# -- Management Window Database Queries --
def fetch_menu_items(category_filter=None):
    conn = create_connection()
    cursor = conn.cursor()

    if category_filter and category_filter != "All":
        cursor.execute("""
            SELECT item_id, item_name, status, category, price
            FROM menu_item
            WHERE category = ?
            ORDER BY item_name
        """, (category_filter,))
    else:
        cursor.execute("""
            SELECT item_id, item_name, status, category, price
            FROM menu_item
            ORDER BY item_name
        """)

    data = cursor.fetchall()
    conn.close()
    return data


def add_menu_item(name, category, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO menu_item (item_name, status, category, price)
        VALUES (?, 1, ?, ?)
    """, (name, category, price))
    conn.commit()
    conn.close()


def delete_menu_item(item_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu_item WHERE item_id = ?", (item_id,))
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


def update_menu_item(item_id, name, category, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE menu_item
        SET item_name = ?, category = ?, price = ?
        WHERE item_id = ?
    """, (name, category, price, item_id))
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


def beverage_exists(name, exclude_id=None):
    conn = create_connection()
    cursor = conn.cursor()

    if exclude_id:
        cursor.execute("""
            SELECT 1 FROM menu_item
            WHERE LOWER(item_name) = LOWER(?) AND item_id != ?
        """, (name, exclude_id))
    else:
        cursor.execute("""
            SELECT 1 FROM menu_item
            WHERE LOWER(item_name) = LOWER(?)
        """, (name,))

    result = cursor.fetchone()
    conn.close()

    return result is not None

# IMAGE FUNCTIONS 
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
        img.thumbnail(size) 
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
            img = img.resize(size, Image.LANCZOS)  
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




# -- GUI Functions --
root = ctk.CTk()
root.withdraw()
root.title("Kape'Bahay Ordering System")

windows = {}


def lazy_create_window(name):
    if name in windows:
        return windows[name]
    
    if name == "login":
        w = create_login_window(root)
    elif name == "cart":
        w = create_cart_window(root)
    elif name == "orders":
        w = create_orders_window(root)
    elif name == "management":
        w = create_management_window(root)
    elif name == "profile":
        w = create_profile_window(root, username=current_user["username"], role=current_user["role"])
    elif name == "manage_employees":
        w = create_employees_window(root)
    elif name == "sales":
        w = create_sales_report_window(root)
    else:
        raise ValueError(f"Unknown window: {name}")
    
    windows[name] = w
    w.withdraw()           
    return w

# -- Authentication Functions --
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




# Craete your windows here. You can also create more functions for other windows you will create in the future. 
def create_login_window(master):
    loginwindow = ctk.CTkToplevel(master)
    center_window(loginwindow, 1280, 720)
    loginwindow.after(100, loginwindow.lift)      # brings window to front
    loginwindow.after(100, loginwindow.focus)     # focuses the window
    loginwindow.title("Kape'Bahay Ordering System - Login") # Window Title
    loginwindow.resizable(False, False) # Disable window resizing
    loginwindow.configure(fg_color="#43382F") # Window background color
    #loginwindow.iconbitmap("assets/icons/kapebahay_icon.ico") the icon file must be in .ico format and must be placed in the same folder as the system


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

    businessLogo.image = logo_img 
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

    forgotPasswordButton = ctk.CTkButton(rightframe, 
                                text="Forgot Password?", 
                                font=ctk.CTkFont(size=14), 
                                fg_color="transparent", 
                                text_color="#3032AA",
                                hover_color="#FFFFFF",
                                command=lambda: open_forgot_password_window(loginwindow))    
    forgotPasswordButton.pack(pady=(0,5))


    def attempt_login():
        username = usernameEntry.get()
        password = passwordEntry.get()

        success, user_role, error_msg = verify_user_login(username, password)

        if success:
            current_user["username"] = username
            current_user["role"] = user_role
            messagebox.showinfo("Success", f"Welcome, {username}! ({user_role})")
            show_window("profile")  
        else:
            messagebox.showerror("Login Failed", error_msg)
            passwordEntry.delete(0, ctk.END)
            passwordEntry.focus_set()

        usernameEntry.delete(0, ctk.END)
        passwordEntry.delete(0, ctk.END)
        
    return loginwindow


def open_forgot_password_window(master):
    forgot_window = ctk.CTkToplevel(master)
    center_window(forgot_window, 500, 420)
    forgot_window.transient(master)
    forgot_window.grab_set()
    forgot_window.after(150, lambda: [forgot_window.lift(), forgot_window.focus_force()])
    forgot_window.title("Forgot Password")
    forgot_window.configure(fg_color="#43382F")
    forgot_window.resizable(False, False)

    # State
    state = {"step": 1, "user_id": None, "questions": []}

    # Header
    ctk.CTkFrame(forgot_window, fg_color="#2C241C", height=6, corner_radius=0).pack(fill="x")
    header = ctk.CTkFrame(forgot_window, fg_color="#2C241C", corner_radius=0)
    header.pack(fill="x")
    title_label = ctk.CTkLabel(header, text="Account Recovery",
                               font=("Segoe UI", 22, "bold"),
                               text_color="#F5E6D0")
    title_label.pack(anchor="w", padx=24, pady=16)

    # Body 
    body = ctk.CTkFrame(forgot_window, fg_color="#43382F", corner_radius=0)
    body.pack(fill="both", expand=True, padx=24, pady=16)

    status_label = ctk.CTkLabel(body, text="",
                                font=("Segoe UI", 13),
                                text_color="#EF5350",
                                wraplength=420)
    status_label.pack(pady=(0, 8))

    # Enter username
    def show_step1():
        for w in body.winfo_children():
            if w != status_label:
                w.destroy()

        ctk.CTkLabel(body, text="Enter your username to begin:",
                     font=("Segoe UI", 14),
                     text_color="#D0C0A0").pack(anchor="w", pady=(0, 6))

        uname_entry = ctk.CTkEntry(body, height=44,
                                   fg_color="#2C241C",
                                   border_color="#6B5540", border_width=2,
                                   text_color="#F0E6D3",
                                   corner_radius=8,
                                   font=("Segoe UI", 14))
        uname_entry.pack(fill="x")

        def submit_username():
            uname = uname_entry.get().strip()
            if not uname:
                status_label.configure(text="Please enter your username.")
                return

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, rq.recovery_question, rq.answer
                FROM users u
                JOIN recovery_questions rq ON u.id = rq.user_id
                WHERE u.username = ?
                ORDER BY rq.question_number ASC
            """, (uname,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                status_label.configure(text="Username not found or no recovery questions set.")
                return
            if len(rows) < 2:
                status_label.configure(text="This account does not have 2 recovery questions set.")
                return

            state["user_id"] = rows[0][0]
            state["questions"] = [(r[1], r[2]) for r in rows] 
            status_label.configure(text="")
            show_step2()

        ctk.CTkButton(body, text="Continue",
                      height=44, corner_radius=8,
                      fg_color="#5C4A35", hover_color="#43382F",
                      text_color="#F0E6D3",
                      font=("Segoe UI", 14, "bold"),
                      command=submit_username).pack(fill="x", pady=(12, 0))

    # Answer recovery questions 
    def show_step2():
        for w in body.winfo_children():
            if w != status_label:
                w.destroy()

        q1_text, _ = state["questions"][0]
        q2_text, _ = state["questions"][1]

        ctk.CTkLabel(body, text=f"Q1: {q1_text}",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#D0C0A0",
                     wraplength=420,
                     justify="left").pack(anchor="w", pady=(0, 4))

        a1_entry = ctk.CTkEntry(body, height=40,
                                fg_color="#2C241C",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                font=("Segoe UI", 13))
        a1_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(body, text=f"Q2: {q2_text}",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#D0C0A0",
                     wraplength=420,
                     justify="left").pack(anchor="w", pady=(0, 4))

        a2_entry = ctk.CTkEntry(body, height=40,
                                fg_color="#2C241C",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                font=("Segoe UI", 13))
        a2_entry.pack(fill="x", pady=(0, 12))

        def verify_answers():
            a1 = hash_password(a1_entry.get().strip().lower())
            a2 = hash_password(a2_entry.get().strip().lower())

            if a1 == state["questions"][0][1] and a2 == state["questions"][1][1]:
                status_label.configure(text="")
                show_step3()
            else:
                status_label.configure(text="One or both answers are incorrect. Please try again.")

        ctk.CTkButton(body, text="Verify Answers",
                      height=44, corner_radius=8,
                      fg_color="#5C4A35", hover_color="#43382F",
                      text_color="#F0E6D3",
                      font=("Segoe UI", 14, "bold"),
                      command=verify_answers).pack(fill="x")

    # Set new password
    def show_step3():
        for w in body.winfo_children():
            if w != status_label:
                w.destroy()

        ctk.CTkLabel(body, text="✔  Identity verified. Set your new password.",
                     font=("Segoe UI", 13, "bold"),
                     text_color="#66BB6A").pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(body, text="New Password:",
                     font=("Segoe UI", 13),
                     text_color="#D0C0A0").pack(anchor="w")

        pw_entry = ctk.CTkEntry(body, height=44, show="•",
                                fg_color="#2C241C",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                font=("Segoe UI", 14))
        pw_entry.pack(fill="x", pady=(4, 10))

        ctk.CTkLabel(body, text="Confirm Password:",
                     font=("Segoe UI", 13),
                     text_color="#D0C0A0").pack(anchor="w")

        cpw_entry = ctk.CTkEntry(body, height=44, show="•",
                                 fg_color="#2C241C",
                                 border_color="#6B5540", border_width=2,
                                 text_color="#F0E6D3",
                                 corner_radius=8,
                                 font=("Segoe UI", 14))
        cpw_entry.pack(fill="x", pady=(4, 12))

        def save_new_password():
            pw  = pw_entry.get()
            cpw = cpw_entry.get()

            if not pw:
                status_label.configure(text="Password cannot be empty.")
                return
            if len(pw) < 6:
                status_label.configure(text="Password must be at least 6 characters.")
                return
            if pw != cpw:
                status_label.configure(text="Passwords do not match.")
                return

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=? WHERE id=?",
                           (hash_password(pw), state["user_id"]))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Password updated successfully! Please log in.")
            forgot_window.destroy()

        ctk.CTkButton(body, text="Save New Password",
                      height=44, corner_radius=8,
                      fg_color="#2E7D32", hover_color="#1B5E20",
                      text_color="white",
                      font=("Segoe UI", 14, "bold"),
                      command=save_new_password).pack(fill="x")

    show_step1()

def create_cart_window(master):
    cart_win = ctk.CTkToplevel(master)
    center_window(cart_win, 1380, 920)
    cart_win.after(100, cart_win.lift)      
    cart_win.after(100, cart_win.focus)    
    cart_win.title("Kape't Bahay - Order")
    cart_win.configure(fg_color="#43382F")
    cart_win.resizable(False, False)

    cart_win.grid_columnconfigure(0, weight=7)
    cart_win.grid_columnconfigure(1, weight=3)
    cart_win.grid_rowconfigure(1, weight=1)

    # STATE
    cart_items = []

    # HEADER
    ctk.CTkLabel(cart_win, text="Place an Order",
                 font=("Segoe UI", 36, "bold"),
                 text_color="white").grid(row=0, column=0, padx=20, pady=10, sticky="w")

    ctk.CTkButton(cart_win, text="Return to Menu",
                  font=("Segoe UI", 14, "bold"),
                  fg_color="#5C4A35", hover_color="#43382F",
                  text_color="white", width=200, height=40,
                  command=lambda: show_window("profile")
                  ).grid(row=0, column=1, padx=20, pady=(20, 0), sticky="e")

    # LEFT PANEL
    left_container = ctk.CTkFrame(cart_win, fg_color="#2C241C", corner_radius=6)
    left_container.grid(row=1, column=0, padx=(20, 0), pady=20, sticky="nsew")
    left_container.grid_columnconfigure(0, weight=1)
    left_container.grid_rowconfigure(1, weight=1)

    # Filter bar
    filter_bar = ctk.CTkFrame(left_container, fg_color="#2C241C")
    filter_bar.grid(row=0, column=0, sticky="w", padx=0, pady=(15, 0))

    ctk.CTkLabel(filter_bar, text="Category:",
                 font=("Segoe UI", 18, "bold"),
                 text_color="white").grid(row=0, column=0, padx=(10, 8))

    category_var = ctk.StringVar(value="All")
    ctk.CTkComboBox(filter_bar,
                    font=("Segoe UI", 16),
                    values=["All"] + CATEGORIES[1:],
                    variable=category_var,
                    state="readonly",
                    width=220, height=32,
                    command=lambda _: refresh_products()
                    ).grid(row=0, column=1, sticky="w", pady=(2, 0))

    ctk.CTkButton(filter_bar, text="↺ Reset",
                  width=90, height=32,
                  fg_color="#5C4A35", hover_color="#43382F",
                  font=("Segoe UI", 13, "bold"),
                  command=lambda: [category_var.set("All"), refresh_products()]
                  ).grid(row=0, column=2, padx=(10, 0), pady=(2, 0))

    canvas_container = ctk.CTkFrame(left_container, fg_color="#2C241C", corner_radius=0)
    canvas_container.grid(row=1, column=0, sticky="nsew", padx=2, pady=(8, 0))
    canvas_container.grid_columnconfigure(0, weight=1)
    canvas_container.grid_rowconfigure(0, weight=1)

    canvas = tk.Canvas(canvas_container, bg="#2C241C", highlightthickness=0, bd=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar = ctk.CTkScrollbar(canvas_container, orientation="vertical",
                                  command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Inner frame that holds all the cards — sits inside the canvas
    left = ctk.CTkFrame(canvas, fg_color="#2C241C", corner_radius=0)
    canvas_window = canvas.create_window((0, 0), window=left, anchor="nw")

    # Keep inner frame width in sync with canvas width
    def _on_canvas_resize(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", _on_canvas_resize)

    # Update scroll region whenever inner frame changes size
    def _on_frame_resize(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    left.bind("<Configure>", _on_frame_resize)

    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<MouseWheel>", _on_mousewheel)
    left.bind("<MouseWheel>", _on_mousewheel)

    # Bind mousewheel to all child widgets recursively
    def _bind_mousewheel(widget):
        widget.bind("<MouseWheel>", _on_mousewheel)
        for child in widget.winfo_children():
            _bind_mousewheel(child)

    # RIGHT PANEL
    right = ctk.CTkFrame(cart_win, fg_color="#3A2F24", corner_radius=6)
    right.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(right, text="Current Order",
                 font=("Segoe UI", 22, "bold"),
                 text_color="white").grid(row=0, column=0, pady=(16, 0), padx=16, sticky="w")

    cart_scroll = ctk.CTkScrollableFrame(right, fg_color="#2C241C", corner_radius=6)
    cart_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(10, 0))
    cart_scroll.grid_columnconfigure(0, weight=1)

    totals_frame = ctk.CTkFrame(right, fg_color="#2C241C", corner_radius=6)
    totals_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(8, 0))
    totals_frame.grid_columnconfigure(0, weight=1)

    items_count_label = ctk.CTkLabel(totals_frame, text="Items: 0",
                                     font=("Segoe UI", 13), text_color="#D0C9B8")
    items_count_label.grid(row=0, column=0, sticky="w", padx=14, pady=(10, 2))

    subtotal_label = ctk.CTkLabel(totals_frame, text="Total:  ₱0.00",
                                  font=("Segoe UI", 18, "bold"), text_color="white")
    subtotal_label.grid(row=1, column=0, sticky="w", padx=14, pady=(2, 10))

    ctk.CTkLabel(right, text="Customer Name",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#D0C0A0").grid(row=3, column=0, sticky="w", padx=16, pady=(10, 4))

    customer_entry = ctk.CTkEntry(right, height=40,
                                  fg_color="#43382F",
                                  border_color="#6B5540", border_width=2,
                                  text_color="#F0E6D3", corner_radius=8,
                                  font=("Segoe UI", 14))
    customer_entry.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 10))

    ctk.CTkButton(right, text="Place Order",
                  height=46, corner_radius=8,
                  fg_color="#2E7D32", hover_color="#1B5E20",
                  text_color="white", font=("Segoe UI", 15, "bold"),
                  command=lambda: place_order()
                  ).grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))

    ctk.CTkButton(right, text="Clear Cart",
                  height=38, corner_radius=8,
                  fg_color="#5C4A35", hover_color="#43382F",
                  text_color="#F0E6D3", font=("Segoe UI", 13, "bold"),
                  command=lambda: clear_cart()
                  ).grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 16))

    # ── CART FUNCTIONS ──
    def update_cart_display():
        for widget in cart_scroll.winfo_children():
            widget.destroy()

        total = 0
        total_qty = 0

        if not cart_items:
            ctk.CTkLabel(cart_scroll, text="☕",
                         font=("Segoe UI", 40), text_color="#5C4A35").pack(pady=(40, 8))
            ctk.CTkLabel(cart_scroll, text="Your cart is empty",
                         font=("Segoe UI", 15, "bold"), text_color="#A09080").pack()
            ctk.CTkLabel(cart_scroll,
                         text="Add beverages from the\nmenu to get started",
                         font=("Segoe UI", 13), text_color="#6B5540",
                         justify="center").pack(pady=(6, 0))
            items_count_label.configure(text="Items: 0")
            subtotal_label.configure(text="Total:  ₱0.00")
            return

        for item in cart_items:
            line_total = item["price"] * item["quantity"]
            total += line_total
            total_qty += item["quantity"]

            row_frame = ctk.CTkFrame(cart_scroll, fg_color="#43382F", corner_radius=6)
            row_frame.pack(fill="x", pady=4)
            row_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row_frame,
                         text=f"{item['name']}  ({item['size']})",
                         font=("Segoe UI", 13, "bold"),
                         text_color="white", anchor="w"
                         ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

            detail_row = ctk.CTkFrame(row_frame, fg_color="transparent")
            detail_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
            detail_row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(detail_row,
                         text=f"₱{item['price']:.2f} × {item['quantity']}",
                         font=("Segoe UI", 12), text_color="#D0C9B8"
                         ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(detail_row,
                         text=f"₱{line_total:.2f}",
                         font=("Segoe UI", 13, "bold"), text_color="#F5D8A8"
                         ).grid(row=0, column=1, sticky="e")
            ctk.CTkButton(detail_row, text="✕",
                          width=28, height=28,
                          fg_color="#C62828", hover_color="#922B21",
                          text_color="white", font=("Segoe UI", 12, "bold"),
                          corner_radius=6,
                          command=lambda n=item["name"]: remove_from_cart(n)
                          ).grid(row=0, column=2, padx=(8, 0))

        items_count_label.configure(text=f"Items: {total_qty}")
        subtotal_label.configure(text=f"Total:  ₱{total:.2f}")

    def add_to_cart(item_id, name, price, quantity):
        for item in cart_items:
            if item["item_id"] == item_id:
                item["quantity"] += quantity
                update_cart_display()
                return
        cart_items.append({
            "item_id": item_id,
            "name": name,
            "size": "Regular 16oz", 
            "price": price,
            "quantity": quantity
        })
        update_cart_display()

    def remove_from_cart(name):
        cart_items[:] = [i for i in cart_items if i["name"] != name]
        update_cart_display()

    def clear_cart():
        cart_items.clear()
        update_cart_display()

    def place_order():
        if not cart_items:
            messagebox.showwarning("Empty Cart", "Please add items before placing an order.")
            return
        customer = customer_entry.get().strip()
        if not customer:
            messagebox.showwarning("Missing Name", "Please enter a customer name.")
            return

        order_id = create_order(customer, cart_items)
        order_total = sum(item["price"] * item["quantity"] for item in cart_items)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE employee_performance
            SET total_sales = total_sales + ?,
                orders_made = orders_made + 1
            WHERE username = ?
        """, (order_total, current_user["username"]))
        conn.commit()
        conn.close()

        messagebox.showinfo("Order Placed",
                            f"Order #{order_id} placed successfully for {customer}!")
        clear_cart()
        customer_entry.delete(0, "end")

    # ── PRODUCT DISPLAY ──
    # Cache images so they aren't reloaded on every refresh
    _image_cache = {}

    def get_cached_image(name):
        if name not in _image_cache:
            _image_cache[name] = load_image(name, size=(200, 165))
        return _image_cache[name]

    def refresh_products():
        for widget in left.winfo_children():
            widget.destroy()

        selected_category = category_var.get()
        data = fetch_available_menu_items(
            category_filter=selected_category if selected_category != "All" else None
        )

        if not data:
            ctk.CTkLabel(left, text="No available beverages ☕",
                         font=("Segoe UI", 18), text_color="#A09080"
                         ).pack(pady=60)
            _bind_mousewheel(left)
            return

        chunks = [data[i:i+3] for i in range(0, len(data), 3)]

        for chunk in chunks:
            row_frame = ctk.CTkFrame(left, fg_color="transparent")
            row_frame.pack(fill="x", padx=6, pady=4)
            for col_i in range(3):
                row_frame.grid_columnconfigure(col_i, weight=1, uniform="card_col")

            for col_i, (item_id, name, category, price) in enumerate(chunk):
                card = ctk.CTkFrame(row_frame, fg_color="#4A3C2F", corner_radius=6)
                card.grid(row=0, column=col_i, padx=8, pady=4, sticky="n")
                card.grid_columnconfigure(0, weight=1)
                card.grid_columnconfigure(1, weight=1)

                img = get_cached_image(name)
                if img:
                    img_label = ctk.CTkLabel(card, image=img, text="",
                                             width=200, height=165)
                    img_label.image = img
                    img_label.grid(row=0, column=0, columnspan=2, pady=(14, 6), padx=10)
                else:
                    ctk.CTkLabel(card, text="", width=200, height=165
                                 ).grid(row=0, column=0, columnspan=2, pady=(14, 6))

                ctk.CTkLabel(card, text=name,
                             font=("Segoe UI", 14, "bold"),
                             text_color="white",
                             wraplength=180, justify="left"
                             ).grid(row=1, column=0, columnspan=2,
                                    sticky="w", padx=10, pady=(2, 0))
                size = "Large 220z" if category == "Favorites" else "Regular 16oz"
                ctk.CTkLabel(card, text=f"{size}  ₱{price:.2f}",
                             font=("Segoe UI", 12), text_color="#D0C9B8"
                             ).grid(row=2, column=0, columnspan=2,
                                    sticky="w", padx=10, pady=(0, 4))

                qty_var = ctk.IntVar(value=1)
                qty_frame = ctk.CTkFrame(card, fg_color="transparent")
                qty_frame.grid(row=3, column=0, columnspan=2,
                               sticky="ew", padx=10, pady=(4, 12))
                qty_frame.grid_columnconfigure(1, weight=1)

                ctk.CTkButton(qty_frame, text="−", width=30, height=30,
                              fg_color="#5C4A35", hover_color="#43382F",
                              text_color="white", font=("Segoe UI", 15, "bold"),
                              corner_radius=6,
                              command=lambda q=qty_var: q.set(max(1, q.get() - 1))
                              ).grid(row=0, column=0)

                ctk.CTkLabel(qty_frame, textvariable=qty_var,
                             font=("Segoe UI", 13, "bold"),
                             text_color="white", width=30
                             ).grid(row=0, column=1)

                ctk.CTkButton(qty_frame, text="+", width=30, height=30,
                              fg_color="#5C4A35", hover_color="#43382F",
                              text_color="white", font=("Segoe UI", 16, "bold"),
                              corner_radius=6,
                              command=lambda q=qty_var: q.set(q.get() + 1)
                              ).grid(row=0, column=2)

                ctk.CTkButton(qty_frame, text="Add to Cart",
                              height=30, corner_radius=6,
                              fg_color="#2E7D32", hover_color="#1B5E20",
                              text_color="white", font=("Segoe UI", 12, "bold"),
                              command=lambda iid=item_id, n=name, p=price, q=qty_var:
                                  add_to_cart(iid, n, p, q.get())
                              ).grid(row=0, column=3, padx=(6, 0))

            for empty_col in range(len(chunk), 3):
                ctk.CTkFrame(row_frame, fg_color="transparent"
                             ).grid(row=0, column=empty_col, padx=8, sticky="n")

        # Rebind mousewheel to all newly created widgets
        _bind_mousewheel(left)
        # Force scroll region update
        left.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    # ── Delayed load with one-shot configure fallback ──
    cart_win.after(200, refresh_products)
    cart_win.after(10, update_cart_display)

    def _on_first_configure(event):
        left.unbind("<Configure>", _cid_ref[0])
        cart_win.after(50, refresh_products)
    _cid_ref = [None]
    _cid_ref[0] = left.bind("<Configure>", _on_first_configure)

    return cart_win


# Orders Window
def create_orders_window(master):
    orders_win = ctk.CTkToplevel(master)
    center_window(orders_win, 1280, 720)
    orders_win.after(100, orders_win.lift)      # brings window to front
    orders_win.after(100, orders_win.focus)     # focuses the window
    orders_win.title("Kape'Bahay - Manage Orders")
    orders_win.resizable(False, False)
    orders_win.configure(fg_color="#43382F")

    orders_win.grid_columnconfigure(0, weight=1)
    orders_win.grid_rowconfigure(0, weight=0)
    orders_win.grid_rowconfigure(1, weight=1)
    orders_win.grid_rowconfigure(2, weight=0)

    # ================= HEADER =================
    header = ctk.CTkFrame(orders_win, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(header, text="Orders Management",
                 font=("Segoe UI", 32, "bold"),
                 text_color="white").grid(row=0, column=0, sticky="w", padx=10)

    ctk.CTkButton(header, text="⟳  Refresh",
                  width=140, height=38,
                  fg_color="#5C4A35", hover_color="#43382F",
                  font=("Segoe UI", 13, "bold"),
                  command=lambda: refresh_orders()).grid(row=1, column=1, sticky="e", padx=10)

    # ================= TABS =================
    tab_frame = ctk.CTkFrame(orders_win, fg_color="transparent")
    tab_frame.grid(row=0, column=0, sticky="w", pady=(70, 0), padx=30)

    current_tab = ctk.StringVar(value="pending")

    def update_tab_colors():
        pending_tab.configure(fg_color="#2E7D32" if current_tab.get() == "pending" else "#5C4A35")
        completed_tab.configure(fg_color="#2E7D32" if current_tab.get() == "completed" else "#5C4A35")

    def switch_tab(tab):
        current_tab.set(tab)
        update_tab_colors()
        refresh_orders()

    pending_tab = ctk.CTkButton(tab_frame, text="Pending & Preparing",
                                width=180, height=36,
                                fg_color="#2E7D32", hover_color="#1B5E20",
                                font=("Segoe UI", 13, "bold"),
                                command=lambda: switch_tab("pending"))
    pending_tab.pack(side="left", padx=(0, 6))

    completed_tab = ctk.CTkButton(tab_frame, text="Completed",
                                  width=140, height=36,
                                  fg_color="#5C4A35", hover_color="#43382F",
                                  font=("Segoe UI", 13, "bold"),
                                  command=lambda: switch_tab("completed"))
    completed_tab.pack(side="left")

    # ================= CONTENT AREA =================
    content_area = ctk.CTkScrollableFrame(orders_win, fg_color="#2C241C", corner_radius=6)
    content_area.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 0))


    # ================= DETAILS POPUP =================
    def open_details_popup(order): 
        oid, customer, date, total, status = order

        popup = ctk.CTkToplevel(orders_win)
        center_window(popup, 420, 600)
        popup.transient(orders_win)
        popup.grab_set()
        popup.after(150, lambda: [popup.lift(), popup.focus_force()])
        popup.title(f"Order #{oid}")
        popup.configure(fg_color="#2C241C")
        popup.resizable(False, False)

        # ── Title ──
        ctk.CTkLabel(popup, text=f"Order #{oid} - {customer}",
                 font=("Segoe UI", 27, "bold"),
                 text_color="white").pack(pady=(20, 16))

        # ── Info boxes row (DATE, TOTAL, STATUS) ──
        info_frame = ctk.CTkFrame(popup, fg_color="#3A2A1A", corner_radius=8, height=100)
        info_frame.pack(fill="x", padx=20, pady=(0, 16))
        info_frame.pack_propagate(False)
        info_frame.grid_columnconfigure((0,1,2), weight=1)
        info_frame.grid_rowconfigure((0,1), weight=1, pad=8)

        # Format date to two lines
        date_parts = date.replace("T", " ").split(" ")
        date_display = f"{date_parts[0]}\n{date_parts[1][:8] if len(date_parts) > 1 else ''}"

        status_color = ("#2E7D32" if status == "Completed"
                        else "#0288D1" if status == "Preparing"
                        else "#E67E22")

        def info_box(parent, col, label, value, value_color="white"):
            ctk.CTkLabel(
                parent,
                text=label,
                font=("Segoe UI", 16, "bold"),
                text_color="#B8A890"
            ).grid(row=0, column=col, pady=(10,4), padx=6, sticky="n")
            ctk.CTkLabel(
                parent,
                text=value,
                font=("Segoe UI", 14, "bold"),
                text_color=value_color
            ).grid(row=1, column=col, pady=(4,10), padx=6, sticky="n")

        info_box(info_frame, 0, "DATE", date_display)
        info_box(info_frame, 1, "TOTAL", f"₱{total:,.2f}", "#F5D8A8")
        info_box(info_frame, 2, "STATUS", status, status_color)

        # ── Items label ──
        ctk.CTkLabel(popup, text="Items:",
                     font=("Segoe UI", 20, "bold"),
                     text_color="#D0C0A0").pack(anchor="w", padx=20, pady=(0, 0))

        # ── Items scroll ──
        items_scroll = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        items_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        items_scroll.grid_columnconfigure(0, weight=1)

        details = fetch_order_details(oid)

        if not details:
            ctk.CTkLabel(items_scroll, text="No items found for this order.",
                         font=("Segoe UI", 13),
                         text_color="#A09080").pack(pady=30)
        else:
            for i, (item_name, quantity, subtotal) in enumerate(details):
                # Individual item frame with dark background
                item_box = ctk.CTkFrame(items_scroll, fg_color="#1A1410", corner_radius=6)
                item_box.pack(fill="x", pady=6)
                item_box.grid_columnconfigure(0, weight=1)

                # Left: icon + name
                left = ctk.CTkFrame(item_box, fg_color="transparent")
                left.grid(row=0, column=0, sticky="w", padx=12, pady=10)

                ctk.CTkLabel(left, text="●",
                             font=("Segoe UI", 14),
                             text_color="#E67E22").pack(side="left", padx=(0, 8))

                ctk.CTkLabel(left,
                             text=f"{item_name}",
                             font=("Segoe UI", 16, "bold"),
                             text_color="#F0E6D3").pack(side="left", anchor="w")

                # Right: quantity + price
                ctk.CTkLabel(item_box,
                             text=f"{quantity}x",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#F5D8A8").grid(row=0, column=1,
                                                        sticky="e", padx=12, pady=10)
                
                ctk.CTkLabel(item_box,
                             text=f"₱{subtotal:.2f}",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#F5D8A8").grid(row=0, column=2,
                                                        sticky="e", padx=12, pady=10)

        # ── Footer buttons ──
        footer = ctk.CTkFrame(popup, fg_color="#3A2A1A", corner_radius=0, height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        # COMPLETED ORDERS → only show Close
        if status == "Completed":

            footer.grid_columnconfigure(0, weight=1)

            ctk.CTkButton(
                footer,
                text="Close",
                height=40,
                corner_radius=8,
                fg_color="#5C4A35",
                hover_color="#43382F",
                text_color="#F0E6D3",
                font=("Segoe UI", 13, "bold"),
                command=popup.destroy
            ).grid(row=0, column=0, padx=16, pady=15, sticky="ew")

        # PENDING or PREPARING → show toggle button
        else:

            footer.grid_columnconfigure((0,1), weight=1)

            # Pending → Prepare
            if status == "Pending":

                ctk.CTkButton(
                    footer,
                    text="Prepare",
                    height=40,
                    corner_radius=8,
                    fg_color="#E67E22",
                    hover_color="#D68910",
                    text_color="white",
                    font=("Segoe UI", 13, "bold"),
                    command=lambda: [
                        start_preparing(oid),
                        refresh_orders(),
                        popup.destroy()
                    ]
                ).grid(row=0, column=0, padx=(16,6), pady=15, sticky="ew")

            # Preparing → Unprepare
            elif status == "Preparing":

                ctk.CTkButton(
                    footer,
                    text="Cancel Preparation",
                    height=40,
                    corner_radius=8,
                    fg_color="#C62828",
                    hover_color="#B71C1C",
                    text_color="white",
                    font=("Segoe UI", 13, "bold"),
                    command=lambda: [
                        unprepare_order(oid),
                        refresh_orders(),
                        popup.destroy()
                    ]
                ).grid(row=0, column=0, padx=(16,6), pady=15, sticky="ew")

            ctk.CTkButton(
                footer,
                text="Close",
                height=40,
                corner_radius=8,
                fg_color="#5C4A35",
                hover_color="#43382F",
                text_color="#F0E6D3",
                font=("Segoe UI", 13, "bold"),
                command=popup.destroy
            ).grid(row=0, column=1, padx=(6,16), pady=15, sticky="ew")


    # ================= DB ACTIONS =================
    def start_preparing(order_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customer_orders SET status = 'Preparing' WHERE order_id = ?",
            (order_id,)
        )
        conn.commit()
        conn.close()

    def complete_order(order_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customer_orders SET status = 'Completed' WHERE order_id = ?",
            (order_id,)
        )
        conn.commit()
        conn.close()

    def unprepare_order(order_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE customer_orders SET status = 'Pending' WHERE order_id = ?",
            (order_id,)
        )
        conn.commit()
        conn.close()

    # ================= REFRESH =================
    def refresh_orders():
        for widget in content_area.winfo_children():
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
            ctk.CTkLabel(content_area,
                         text=f"No {current_tab.get().title()} orders at the moment ☕",
                         font=("Segoe UI", 20),
                         text_color="#A09080").pack(expand=True, pady=120)
            return

        for order in orders:
            oid, customer, date, total, status = order

            card = ctk.CTkFrame(content_area, fg_color="#4A3C2F", corner_radius=10)
            card.pack(fill="x", pady=5, padx=10)
            card.grid_columnconfigure(0, weight=1)

            # Top row
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=15, pady=(6, 2))

            ctk.CTkLabel(top_row, text=f"Order #{oid}  •  {customer}",
                         font=("Segoe UI", 16, "bold"),
                         text_color="white").pack(side="left")

            ctk.CTkLabel(top_row, text=f"₱{total:,.2f}",
                         font=("Segoe UI", 16, "bold"),
                         text_color="#F5D8A8").pack(side="right")

            # Meta row
            meta_row = ctk.CTkFrame(card, fg_color="transparent")
            meta_row.pack(fill="x", padx=15, pady=(0, 2))

            ctk.CTkLabel(meta_row, text=date,
                         font=("Segoe UI", 15, "bold"),
                         text_color="#A09080").pack(side="left")

            status_color = ("#2E7D32" if status == "Completed"
                            else "#0288D1" if status == "Preparing"
                            else "#C62828")
            ctk.CTkLabel(meta_row, text=f"  {status}  ",
                         fg_color=status_color,
                         font=("Segoe UI", 11, "bold"),
                         text_color="white",
                         corner_radius=5).pack(side="left", padx=(10, 0))

            # Buttons
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(fill="x", padx=15, pady=(0, 8))

            ctk.CTkButton(btns, text="View Details",
                          width=120, height=34,
                          fg_color="#5C4A35", hover_color="#43382F",
                          font=("Segoe UI", 12, "bold"),
                          command=lambda o=order: open_details_popup(o)
                          ).pack(side="left", padx=(0, 6))

            if status in ("Pending", "Preparing"):
                ctk.CTkButton(btns, text="Mark Completed",
                              width=140, height=34,
                              fg_color="#2E7D32", hover_color="#1B5E20",
                              font=("Segoe UI", 12, "bold"),
                              command=lambda o=oid: [complete_order(o), refresh_orders()]
                              ).pack(side="left")

    # ================= BOTTOM BAR =================
    bottom_bar = ctk.CTkFrame(orders_win, fg_color="#2C241C", corner_radius=0, height=70)
    bottom_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    bottom_bar.grid_propagate(False)

    ctk.CTkButton(bottom_bar, text="← Return to Menu",
                  width=180, height=44,
                  fg_color="#43382F", hover_color="#5C4A35",
                  text_color="#F0E6D3",
                  font=("Segoe UI", 14, "bold"),
                  corner_radius=8,
                  command=lambda: show_window("profile")).pack(side="left", padx=20, pady=13)

    orders_win.after(100, refresh_orders)
    return orders_win
    
# Beverage management window
def create_management_window(master):
    beverage_window = ctk.CTkToplevel(master)
    center_window(beverage_window, 1380, 920)
    beverage_window.after(100, beverage_window.lift)      # brings window to front
    beverage_window.after(100, beverage_window.focus)     # focuses the window
    beverage_window.title("Management")
    beverage_window.configure(fg_color="#43382F")
    beverage_window.resizable(False, False)

    # ── Single column layout ──
    beverage_window.grid_columnconfigure(0, weight=1)
    beverage_window.grid_rowconfigure(1, weight=1)

    # ── Header with title + buttons ──
    header_container = ctk.CTkFrame(beverage_window, fg_color="transparent")
    header_container.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))

    ctk.CTkLabel(header_container, text="Manage Beverages",
                 font=("Segoe UI", 36, "bold"),
                 text_color="white").pack(side="left", pady=8)

    # LEFT PANEL ── full width
    left_container = ctk.CTkFrame(beverage_window, fg_color="#2C241C", corner_radius=6)
    left_container.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    left_container.grid_columnconfigure(0, weight=1)
    left_container.grid_rowconfigure(1, weight=1)

    # ── Filter bar ──
    filter_bar = ctk.CTkFrame(left_container, fg_color="#2C241C")
    filter_bar.grid(row=0, column=0, sticky="w", padx=0, pady=(15, 0))

    category_label = ctk.CTkLabel(filter_bar, text="Category:",
                                  font=("Segoe UI", 18, "bold"),
                                  text_color="white")
    category_label.grid(row=0, column=0, padx=(10, 8))

    category_var = ctk.StringVar(value="All")
    category_combobox = ctk.CTkComboBox(filter_bar,
                                        font=("Segoe UI", 16),
                                        values=CATEGORIES,
                                        variable=category_var,
                                        width=200,
                                        height=32,
                                        command=lambda _: refresh_products())
    category_combobox.grid(row=0, column=1, sticky="w", pady=(2, 0))

    reset_btn = ctk.CTkButton(filter_bar, text="↺ Reset",
                              width=90, height=32,
                              fg_color="#5C4A35",
                              hover_color="#43382F",
                              font=("Segoe UI", 13, "bold"),
                              command=lambda: [category_var.set("All"), refresh_products()])
    reset_btn.grid(row=0, column=2, padx=(10, 0), pady=(2, 0), sticky="w")

    # Scrollable product area ── 4 columns
    left = ctk.CTkScrollableFrame(left_container, fg_color="#2C241C", corner_radius=6)
    left.grid(row=1, column=0, sticky="nsew", padx=2, pady=(8, 0))

    # Configure 4 equal-width columns
    for i in range(4):
        left.grid_columnconfigure(i, weight=1, uniform="col")

    # ================= REFRESH =================
    def refresh_products():
        for widget in left.winfo_children():
            widget.destroy()

        selected_category = category_var.get()
        data = fetch_menu_items(category_filter=selected_category)

        if not data:
            empty_msg = (
                f"No beverages found in '{selected_category}' category."
                if selected_category != "All"
                else "No beverages added yet."
            )
            ctk.CTkLabel(left,
                         text=empty_msg,
                         font=("Segoe UI", 18, "bold"),
                         text_color="#A09080").grid(row=0, column=0, columnspan=4,
                                                     pady=80, padx=20)
            return

        row = 0
        col = 0

        for item_id, name, status, category, price in data:
            status = int(status)  # make sure it's int

            card = ctk.CTkFrame(left, fg_color="#4A3C2F", corner_radius=6, width=300, height=360)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=1)

            size = "Large 22oz" if category == "Favorites" else "Regular 16oz"
            # IMAGE
            img = load_image(name, size=(220, 200))
            if img:
                img_label = ctk.CTkLabel(card, image=img, text="")
                img_label.image = img  # keep reference
                img_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="n")
            else:
                placeholder = ctk.CTkLabel(card, text="", width=220, height=200)
                placeholder.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="n")

            # NAME
            ctk.CTkLabel(card, text=name,
                         font=("Segoe UI", 16, "bold"),
                         text_color="white").grid(row=1, column=0, sticky="w", padx=(10, 10), pady=(5, 2))

            # SIZE + PRICE
            ctk.CTkLabel(card,
                         text=f"{size} - ₱{price}",
                         font=("Segoe UI", 14),
                         text_color="#D0C9B8").grid(row=1, column=1, sticky="e", padx=(0, 10))

            # EDIT
            edit_button = ctk.CTkButton(card, text="Edit",
                                        font=("Segoe UI", 14, "bold"),
                                        width=80, height=40,
                                        command=lambda i=item_id, n=name, cat=category, p=price:
                                            open_edit_form(i, n, cat, p))
            edit_button.grid(row=2, column=0, padx=(10, 0), pady=(0, 0), sticky="w")

            # ─── DELETE with confirmation ───
            def confirm_delete(i=item_id, beverage_name=name):
                if messagebox.askyesno("Confirm Delete",
                                       f"Are you sure you want to delete\n'{beverage_name}'?"):
                    delete_menu_item(i)
                    refresh_products()

            delete_button = ctk.CTkButton(card, text="Delete",
                                          font=("Segoe UI", 14, "bold"),
                                          width=80, height=40,
                                          fg_color="#C62828",
                                          hover_color="#B71C1C",
                                          command=confirm_delete)
            delete_button.grid(row=3, column=0, padx=(10, 0), pady=(10, 10), sticky="w")

            # ─── TOGGLE BUTTON ───
            toggle_on_img  = load_icon("toggle_on")
            toggle_off_img = load_icon("toggle_off")

            status_label = ctk.CTkLabel(card,
                                        text="Available" if status == 1 else "Unavailable",
                                        fg_color="#2E7D32" if status == 1 else "#C62828",
                                        font=("Segoe UI", 14, "bold"),
                                        text_color="white",
                                        width=120, height=40, corner_radius=6)
            status_label.grid(row=2, column=1, padx=(12, 10), pady=(0, 0), sticky="e")

            toggle_btn = ctk.CTkButton(
                card,
                text="Toggle" if (status == 1 and not toggle_on_img) or (status == 0 and not toggle_off_img) else "",
                image=toggle_on_img if status == 1 else toggle_off_img,
                fg_color="#4A3C2F",
                hover_color="#4A3C2F",
                text_color="white",
                font=("Segoe UI", 12, "bold"),
                width=20,
                height=30,
                corner_radius=20
            )
            toggle_btn.grid(row=3, column=1, padx=(12, 10), pady=(10, 10), sticky="e")

            # ───────────────────────────────────────────────────────────────
            #  FIXED TOGGLE LOGIC – each button remembers its own product
            # ───────────────────────────────────────────────────────────────
            def make_toggle_handler(pid, btn, lbl, initial_status):
                def toggle():
                    nonlocal initial_status
                    new_status = toggle_menu_item(pid, initial_status)

                    if new_status == 1:
                        btn.configure(
                            image=toggle_on_img if toggle_on_img else None
                        )
                        lbl.configure(text="Available", fg_color="#2E7D32")
                    else:
                        btn.configure(
                            image=toggle_off_img if toggle_off_img else None
                        )
                        lbl.configure(text="Unavailable", fg_color="#C62828")

                    # Update the status for next click
                    initial_status = new_status

                    # Re-bind with the updated status
                    btn.configure(command=toggle)  # same function, status updated via nonlocal

                return toggle

            # Create and bind the handler for THIS specific product
            toggle_handler = make_toggle_handler(item_id, toggle_btn, status_label, status)
            toggle_btn.configure(command=toggle_handler)

            # Move to next column
            col += 1
            if col == 4:           # ← changed to 4 products per row
                col = 0
                row += 1

    # ================= ADD FORM =================
    def open_add_form():
        form = ctk.CTkToplevel()
        center_window(form, 500, 740)
        form.transient(beverage_window)
        form.grab_set()
        form.after(150, lambda: [form.lift(), form.focus_force()])
        form.title("Add Beverage")
        form.configure(fg_color="#2C241C")
        form.resizable(False, False)

        selected_image = {"path": None}

        ctk.CTkFrame(form, fg_color="#43382F", height=6, corner_radius=0).pack(fill="x")
        header_frame = ctk.CTkFrame(form, fg_color="#43382F", corner_radius=0)
        header_frame.pack(fill="x")
        ctk.CTkLabel(header_frame, text="Add Beverage",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#F5E6D0").pack(anchor="w", padx=24, pady=18)

        body = ctk.CTkScrollableFrame(form, fg_color="#2C241C", corner_radius=0)
        body.pack(fill="both", expand=True)

        def field_label(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=("Segoe UI", 13, "bold"),
                         text_color="#D0C0A0").pack(anchor="w", padx=24, pady=(18, 5))

        def styled_entry(parent):
            return ctk.CTkEntry(parent, height=44,
                                fg_color="#43382F",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                font=("Segoe UI", 14))

        def styled_combo(parent, values, variable):
            return ctk.CTkComboBox(parent, values=values,
                                   variable=variable,
                                   state="readonly", height=44,
                                   fg_color="#43382F",
                                   border_color="#6B5540", border_width=2,
                                   text_color="#F0E6D3", corner_radius=8,
                                   button_color="#6B5540",
                                   button_hover_color="#8B7050",
                                   dropdown_fg_color="#43382F",
                                   dropdown_text_color="#F0E6D3",
                                   dropdown_hover_color="#5C4A35",
                                   font=("Segoe UI", 14))

        field_label(body, "BEVERAGE NAME")
        name_entry = styled_entry(body)
        name_entry.pack(fill="x", padx=24)

        field_label(body, "CATEGORY")
        add_category_var = ctk.StringVar(value=CATEGORIES[1])
        styled_combo(body, CATEGORIES[1:], add_category_var).pack(fill="x", padx=24)

        field_label(body, "SIZE")
        size_var = ctk.StringVar(value="Regular 16oz")
        styled_combo(body, ["Regular 16oz", "Large 22oz"], size_var).pack(fill="x", padx=24)

        field_label(body, "PRICE  (₱)")
        price_entry = styled_entry(body)
        price_entry.pack(fill="x", padx=24)

        # ── Image picker + live preview ──
        field_label(body, "PRODUCT IMAGE")

        img_row = ctk.CTkFrame(body, fg_color="#43382F", corner_radius=8)
        img_row.pack(fill="x", padx=24)
        img_row.grid_columnconfigure(0, weight=1)

        img_name_label = ctk.CTkLabel(img_row, text="No image selected",
                                      text_color="#A09080",
                                      font=("Segoe UI", 13), anchor="w")
        img_name_label.grid(row=0, column=0, padx=14, pady=12, sticky="ew")

        # Preview box — shown only after an image is picked
        preview_label = ctk.CTkLabel(body, text="", fg_color="#43382F",
                                     corner_radius=8, width=220, height=180)

        def choose_image():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if not path:
                return
            selected_image["path"] = path
            img_name_label.configure(text=os.path.basename(path), text_color="#F5D8A8")

            # Build and show the preview
            try:
                pil_img = Image.open(path).resize((220, 180), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 180))
                preview_label.configure(image=ctk_img, text="")
                preview_label.image = ctk_img  # keep reference
            except Exception:
                preview_label.configure(text="Preview unavailable", text_color="#A09080")

            preview_label.pack(padx=24, pady=(8, 4))

        ctk.CTkButton(img_row, text="Browse",
                      width=90, height=32,
                      fg_color="#6B5540", hover_color="#8B7050",
                      text_color="#F0E6D3", font=("Segoe UI", 13, "bold"),
                      corner_radius=6,
                      command=choose_image).grid(row=0, column=1, padx=(0, 10), pady=10)

        footer = ctk.CTkFrame(form, fg_color="#43382F", corner_radius=0, height=82)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        def save():
            name     = name_entry.get().strip()
            category = add_category_var.get()

            if not name:
                messagebox.showerror("Error", "Beverage name is required.")
                return
            try:
                price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid price.")
                return

            # To prevent duplicate beverage products
            if beverage_exists(name):
                messagebox.showerror(
                    "Duplicated Beverage",
                    f"The beverage '{name}' already exists in the menu."
                )
                return

            add_menu_item(name, category, price)

            if selected_image["path"]:
                save_image(selected_image["path"], name)

            messagebox.showinfo("Success",f"'{name}' was successfully added to the menu.")
  
            form.destroy()
            # Force refresh on next frame so the DB write has time to commit
            beverage_window.after(50, refresh_products)

        ctk.CTkButton(footer, text="Save Beverage",
                      height=46, corner_radius=8,
                      fg_color="#6B5540", hover_color="#8B7050",
                      text_color="#F0E6D3",
                      font=("Segoe UI", 15, "bold"),
                      command=save).pack(fill="x", padx=24, pady=18)
    # ================= EDIT FORM =================
    def open_edit_form(item_id, name, category, price):
        form = ctk.CTkToplevel()
        center_window(form, 500, 740)
        form.transient(beverage_window)
        form.grab_set()
        form.after(150, lambda: [form.lift(), form.focus_force()])
        form.title(f"Edit  ·  {name}")
        form.configure(fg_color="#2C241C")
        form.resizable(False, False)

        selected_image = {"path": None}

        ctk.CTkFrame(form, fg_color="#43382F", height=6, corner_radius=0).pack(fill="x")
        header_frame = ctk.CTkFrame(form, fg_color="#43382F", corner_radius=0)
        header_frame.pack(fill="x")
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(header_inner, text="Edit Beverage",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#F5E6D0").pack(side="left")
        ctk.CTkLabel(header_inner, text=f"·  {name}",
                     font=("Segoe UI", 14),
                     text_color="#A09080").pack(side="left", padx=(10, 0), pady=(4, 0))

        body = ctk.CTkScrollableFrame(form, fg_color="#2C241C", corner_radius=0)
        body.pack(fill="both", expand=True)

        def field_label(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=("Segoe UI", 13, "bold"),
                         text_color="#D0C0A0").pack(anchor="w", padx=24, pady=(18, 5))

        def styled_entry(parent):
            return ctk.CTkEntry(parent, height=44,
                                fg_color="#43382F",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                font=("Segoe UI", 14))

        def styled_combo(parent, values, variable):
            return ctk.CTkComboBox(parent, values=values,
                                   variable=variable,
                                   state="readonly", height=44,
                                   fg_color="#43382F",
                                   border_color="#6B5540", border_width=2,
                                   text_color="#F0E6D3", corner_radius=8,
                                   button_color="#6B5540",
                                   button_hover_color="#8B7050",
                                   dropdown_fg_color="#43382F",
                                   dropdown_text_color="#F0E6D3",
                                   dropdown_hover_color="#5C4A35",
                                   font=("Segoe UI", 14))

        field_label(body, "BEVERAGE NAME")
        name_entry = styled_entry(body)
        name_entry.insert(0, name)
        name_entry.pack(fill="x", padx=24)

        field_label(body, "CATEGORY")
        edit_category_var = ctk.StringVar(value=category)
        styled_combo(body, CATEGORIES[1:], edit_category_var).pack(fill="x", padx=24)

        field_label(body, "PRICE  (₱)")
        price_entry = styled_entry(body)
        price_entry.insert(0, str(price))
        price_entry.pack(fill="x", padx=24)

        # ── Image picker + live preview ──
        field_label(body, "PRODUCT IMAGE")

        img_row = ctk.CTkFrame(body, fg_color="#43382F", corner_radius=8)
        img_row.pack(fill="x", padx=24)
        img_row.grid_columnconfigure(0, weight=1)

        img_name_label = ctk.CTkLabel(img_row, text="No new image selected",
                                      text_color="#A09080",
                                      font=("Segoe UI", 13), anchor="w")
        img_name_label.grid(row=0, column=0, padx=14, pady=12, sticky="ew")

        # Show existing image as initial preview if it exists
        preview_label = ctk.CTkLabel(body, text="", fg_color="#43382F",
                                     corner_radius=8, width=220, height=180)
        existing_path = os.path.join(IMAGE_FOLDER, f"{name}.png")
        if os.path.exists(existing_path):
            try:
                pil_img = Image.open(existing_path).resize((220, 180), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 180))
                preview_label.configure(image=ctk_img, text="")
                preview_label.image = ctk_img
                img_name_label.configure(text=f"{name}.png (current)", text_color="#A09080")
            except Exception:
                pass
            preview_label.pack(padx=24, pady=(8, 4))

        def choose_image():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
            if not path:
                return
            selected_image["path"] = path
            img_name_label.configure(text=os.path.basename(path), text_color="#F5D8A8")

            try:
                pil_img = Image.open(path).resize((220, 180), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(220, 180))
                preview_label.configure(image=ctk_img, text="")
                preview_label.image = ctk_img
            except Exception:
                preview_label.configure(text="Preview unavailable", text_color="#A09080")

            preview_label.pack(padx=24, pady=(8, 4))

        ctk.CTkButton(img_row, text="Browse",
                      width=90, height=32,
                      fg_color="#6B5540", hover_color="#8B7050",
                      text_color="#F0E6D3", font=("Segoe UI", 13, "bold"),
                      corner_radius=6,
                      command=choose_image).grid(row=0, column=1, padx=(0, 10), pady=10)

        footer = ctk.CTkFrame(form, fg_color="#43382F", corner_radius=0, height=82)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        def save_changes():
            new_name     = name_entry.get().strip()
            new_category = edit_category_var.get()

            if not new_name:
                messagebox.showerror("Error", "Beverage name is required.")
                return
            try:
                new_price = float(price_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid price.")
                return

            update_menu_item(item_id, new_name, new_category, new_price)

            # Rename image file if the beverage name changed
            old_image = os.path.join(IMAGE_FOLDER, f"{name}.png")
            new_image = os.path.join(IMAGE_FOLDER, f"{new_name}.png")
            if name != new_name and os.path.exists(old_image):
                os.rename(old_image, new_image)

            if selected_image["path"]:
                save_image(selected_image["path"], new_name)

            form.destroy()
            # Force refresh on next frame so the DB write has time to commit
            beverage_window.after(50, refresh_products)

        ctk.CTkButton(footer, text="Save Changes",
                      height=46, corner_radius=8,
                      fg_color="#6B5540", hover_color="#8B7050",
                      text_color="#F0E6D3",
                      font=("Segoe UI", 15, "bold"),
                      command=save_changes).pack(fill="x", padx=24, pady=18)
    # ── Buttons created AFTER function definitions ──
    ctk.CTkButton(header_container, text="Add Beverage",
                  width=160, height=42,
                  fg_color="#6B5540", hover_color="#8B7050",
                  text_color="white",
                  font=("Segoe UI", 14, "bold"),
                  command=open_add_form).pack(side="right", padx=(0, 12), pady=10)

    return_button = ctk.CTkButton(header_container, text="Return to Menu", 
                                  width=160, height=42,
                                  fg_color="#5C4A35", hover_color="#43382F",
                                  text_color="white",
                                  font=("Segoe UI", 14, "bold"),
                                  command=lambda: show_window("profile"))
    return_button.pack(side="right", padx=(0, 12), pady=10)

    beverage_window.after(100, refresh_products)
    return beverage_window

def create_profile_window(master, username, role):
    COLOR_BG_WINDOW = "#43382F"
    COLOR_BG_FRAME  = "#2C241C"
    COLOR_BTN_MAIN  = "#4A3C2F"
    COLOR_BTN_HOVER = "#754930"
    COLOR_BTN_LOGOUT = "#614637"
    COLOR_TEXT_MAIN = "#F2E5D5"
    COLOR_BADGE_BG  = "#CEAF93"
    COLOR_DIVIDER   = "#A07353"

    profile_window = ctk.CTkToplevel(master)
    center_window(profile_window, 1280, 720)
    profile_window.after(100, profile_window.lift)
    profile_window.after(100, profile_window.focus)
    profile_window.title(f"Kape'Bahay - {role.capitalize()}")
    profile_window.resizable(False, False)
    profile_window.configure(fg_color=COLOR_BG_WINDOW)

    profile_window.grid_columnconfigure(0, weight=1)
    profile_window.grid_rowconfigure(2, weight=1)

    # HEADER
    top_container = ctk.CTkFrame(profile_window, fg_color="transparent")
    top_container.grid(row=0, column=0, sticky="ew", padx=60, pady=(40, 0))
    top_container.grid_columnconfigure(1, weight=1)

    header = ctk.CTkFrame(top_container, fg_color=COLOR_BG_FRAME, corner_radius=20)
    header.grid(row=0, column=0, sticky="nw")

    profile_window.name_label = ctk.CTkLabel(
        header, text=username.upper(),
        font=("Arial", 44, "bold"), text_color=COLOR_TEXT_MAIN)
    profile_window.name_label.grid(row=0, column=0, padx=(20, 10), pady=(16, 10), sticky="w")

    profile_window.role_badge = ctk.CTkLabel(
        header, text=role.upper(),
        fg_color="#c8b591", text_color="#43382F",
        corner_radius=10, font=("Arial", 20, "bold"), width=110, height=35)
    profile_window.role_badge.grid(row=0, column=1, padx=(30, 20), pady=(10, 10), sticky="e")

    logout_btn = ctk.CTkButton(
        top_container, text="LOG OUT",
        font=("Arial", 16, "bold"),
        fg_color=COLOR_BTN_LOGOUT, hover_color=COLOR_BTN_HOVER,
        corner_radius=15, width=120, height=50,
        command=lambda: [set_employee_shift_off(username), show_window("login")])
    logout_btn.grid(row=0, column=1, sticky="ne", padx=(0, 50), pady=(25, 0))

    # MAIN BOX
    main_box = ctk.CTkFrame(profile_window, fg_color=COLOR_BG_FRAME,
                            corner_radius=30, width=1160, height=520)
    main_box.grid(row=1, column=0, pady=(40, 0))
    main_box.grid_propagate(False)
    main_box.grid_columnconfigure(1, minsize=40)

    # Left Side - Stats
    left_side = ctk.CTkFrame(main_box, fg_color="transparent")
    left_side.grid(row=0, column=0, sticky="nsew", padx=(40, 0), pady=20)

    ctk.CTkLabel(left_side, text="MY SHIFT",
                 font=("Arial", 28, "bold"),
                 text_color=COLOR_TEXT_MAIN).grid(
        row=0, column=0, columnspan=2, sticky="nw", pady=(0, 30))

    stats_font = ("Arial", 18)
    stat_style = {
        "fg_color": "transparent",
        "border_color": COLOR_DIVIDER,
        "border_width": 2,
        "text_color": COLOR_TEXT_MAIN,
        "corner_radius": 20
    }

    # Fetch live performance data
    perf = fetch_employee_performance(username)
    total_sales = perf[0] if perf else 0.0
    orders_made = perf[1] if perf else 0
    on_shift    = perf[2] if perf else 0

    # Status
    ctk.CTkLabel(left_side, text="Status:",
                 font=stats_font,
                 text_color=COLOR_TEXT_MAIN).grid(
        row=1, column=0, sticky="nw", pady=15)

    shift_btn = ctk.CTkButton(
        left_side,
        text="On Shift  ✔" if on_shift == 1 else "Off Shift  ✘",
        width=180, height=40,
        fg_color="#2E7D32" if on_shift == 1 else "#C62828",
        hover_color="#1B5E20" if on_shift == 1 else "#922B21",
        text_color=COLOR_TEXT_MAIN,
        border_color=COLOR_DIVIDER,
        border_width=2,
        corner_radius=20)
    shift_btn.grid(row=1, column=1, sticky="nw", padx=(20, 0), pady=15)

    # Check Shift before accessing functions of this window
    def require_on_shift(action):
        perf = fetch_employee_performance(username)
        on_shift = perf[2] if perf else 0

        if on_shift != 1:
            messagebox.showwarning(
                "Shift Required",
                "You must start your shift today before accessing this feature."
            )
            return

        action()

    def toggle_shift():
        # Always read current shift state fresh from DB before toggling
        current_perf = fetch_employee_performance(username)
        current_shift = current_perf[2] if current_perf else 0

        # Manually toggle based on actual DB value
        conn = create_connection()
        cursor = conn.cursor()
        new_shift = 0 if current_shift == 1 else 1
        cursor.execute(
            "UPDATE employee_performance SET on_shift = ? WHERE username = ?",
            (new_shift, username)
        )
        conn.commit()
        conn.close()

        if new_shift == 1:
            shift_btn.configure(
                text="On Shift  ✔",
                fg_color="#2E7D32",
                hover_color="#1B5E20"
            )
        else:
            shift_btn.configure(
                text="Off Shift  ✘",
                fg_color="#C62828",
                hover_color="#922B21"
            )

    shift_btn.configure(command=toggle_shift)

    # Total Sales
    ctk.CTkLabel(left_side, text="Total Sales:",
                 font=stats_font,
                 text_color=COLOR_TEXT_MAIN).grid(
        row=2, column=0, sticky="nw", pady=15)

    sales_label = ctk.CTkButton(
        left_side, text=f"PHP   {total_sales:,.2f}",
        state="disabled", width=180, height=40, **stat_style)
    sales_label.grid(row=2, column=1, sticky="nw", padx=(20, 0), pady=15)

    # Total Orders
    ctk.CTkLabel(left_side, text="Total Orders Made:",
                 font=stats_font,
                 text_color=COLOR_TEXT_MAIN).grid(
        row=3, column=0, sticky="nw", pady=15)

    orders_label = ctk.CTkButton(
        left_side, text=str(orders_made),
        state="disabled", width=130, height=40, **stat_style)
    orders_label.grid(row=3, column=1, sticky="nw", padx=(20, 0), pady=15)

    
    # Refresh stats
    def _refresh_for_user(username):
        perf = fetch_employee_performance(username)
        t_sales  = perf[0] if perf else 0.0
        t_orders = perf[1] if perf else 0
        t_shift  = perf[2] if perf else 0

        shift_btn.configure(
            text="On Shift  ✔" if t_shift == 1 else "Off Shift  ✘",
            fg_color="#2E7D32" if t_shift == 1 else "#C62828",
            hover_color="#1B5E20" if t_shift == 1 else "#922B21")
        sales_label.configure(text=f"PHP   {t_sales:,.2f}")
        orders_label.configure(text=str(t_orders))

    # Divider
    ctk.CTkFrame(left_side, width=500, height=2,
                 fg_color=COLOR_DIVIDER).grid(
        row=4, column=0, columnspan=2, pady=(30, 40))

    # Bottom buttons — layout depends on role
    if role.lower() == "admin" or role.lower() == "superadmin":

        # Admin: Update User + Manage Employee
        ctk.CTkButton(left_side, text="UPDATE USER",
                      font=("Arial", 18, "bold"),
                      fg_color=COLOR_BTN_MAIN, hover_color=COLOR_BTN_HOVER,
                      text_color=COLOR_TEXT_MAIN,
                      corner_radius=20, width=215, height=90,
                      command=lambda: open_update_user_window(profile_window)
                      ).grid(row=5, column=0, sticky="nw")

        ctk.CTkButton(left_side, text="MANAGE\nEMPLOYEES",
                      font=("Arial", 18, "bold"),
                      fg_color=COLOR_BTN_MAIN, hover_color=COLOR_BTN_HOVER,
                      text_color=COLOR_TEXT_MAIN,
                      corner_radius=20, width=215, height=90,
                      command=lambda: require_on_shift(lambda: show_window("manage_employees"))
                      ).grid(row=5, column=1, sticky="nw", padx=(20, 0))
    else:
        ctk.CTkButton(left_side, text="UPDATE USER",
                      font=("Arial", 18, "bold"),
                      fg_color=COLOR_BTN_MAIN, hover_color=COLOR_BTN_HOVER,
                      text_color=COLOR_TEXT_MAIN,
                      corner_radius=20, width=450, height=90,
                      command=lambda: open_update_user_window(profile_window)
                      ).grid(row=5, column=0, columnspan=2, sticky="nw")
    

    

    # VERTICAL DIVIDER
    ctk.CTkFrame(main_box, width=2, height=480,
                 fg_color="#3B3129").grid(
        row=0, column=1, pady=20, sticky="ns")

    # RIGHT SIDE
    right_side = ctk.CTkFrame(main_box, fg_color="transparent")
    right_side.grid(row=0, column=2, sticky="nsew", padx=(20, 40), pady=20)

    btn_style = {
        "font": ("Arial", 18, "bold"),
        "fg_color": COLOR_BTN_MAIN,
        "hover_color": COLOR_BTN_HOVER,
        "text_color": COLOR_TEXT_MAIN,
        "width": 520,
        "height": 90,
        "corner_radius": 20
    }

    if role.lower() == "admin" or role.lower() == "superadmin":
        buttons = ["CREATE ORDER", "VIEW PENDING ORDERS", "VIEW SALES REPORT", "BEVERAGE MANAGEMENT"]
        v_pady = 12
    else:
        buttons = ["CREATE ORDER", "VIEW PENDING ORDERS", "VIEW SALES REPORT"]
        v_pady = 22

    for i, btn_text in enumerate(buttons):
        if btn_text == "CREATE ORDER":
            cmd = lambda: require_on_shift(lambda: show_window("cart"))
        elif btn_text == "VIEW PENDING ORDERS":
            cmd = lambda: require_on_shift(lambda: show_window("orders"))
        elif btn_text == "VIEW SALES REPORT":
            cmd = lambda: require_on_shift(lambda: show_window("sales"))

        elif btn_text == "BEVERAGE MANAGEMENT":
            cmd = lambda: require_on_shift(lambda: show_window("management"))
        else:
            cmd = None

        ctk.CTkButton(right_side, text=btn_text, command=cmd,
                      **btn_style).grid(row=i, column=0, pady=v_pady)
    latest_username = current_user["username"]
    # Refresh stats on window focus
    profile_window.bind("<Map>", lambda e: _refresh_for_user(latest_username))

    profile_window.protocol("WM_DELETE_WINDOW", lambda: [set_employee_shift_off(username), master.destroy()])
    return profile_window


def open_update_user_window(master):
    BG_DARK = "#43382F"      
    BOX_BROWN = "#2C241C"    
    BTN_CLAY = "#4A3C2F"     
    TEXT_WHITE = "#F2E5D5"
    HOVER_COLOR = "#754930"
    LOGOUT_ORANGE = "#b84a00" 

    update_win = ctk.CTkToplevel(master)
    center_window(update_win, 450, 740)
    update_win.after(100, update_win.lift)
    update_win.after(100, update_win.focus)
    update_win.title("Update User Information")
    update_win.resizable(False, False)
    update_win.configure(fg_color=BG_DARK)
    update_win.transient(master)
    update_win.grab_set()

    # Container uses .pack
    container = ctk.CTkFrame(update_win, fg_color=BOX_BROWN, corner_radius=20)
    container.pack(expand=True, fill="both", padx=30, pady=30)
    container.grid_columnconfigure(0, weight=1)

    label_font = ("Arial", 14)
    entry_style = {
        "height": 40, "corner_radius": 10,
        "fg_color": "#e0e0e0", "text_color": "black"
    }

    # Title
    ctk.CTkLabel(container, text="Edit Profile",
                 font=("Arial", 26, "bold"),
                 text_color=TEXT_WHITE).grid(
        row=0, column=0, pady=(28, 16))

    # Username
    ctk.CTkLabel(container, text="New Username:",
                 font=label_font, text_color=TEXT_WHITE,
                 anchor="w").grid(row=1, column=0, sticky="w", padx=40)
    username_entry = ctk.CTkEntry(container,
                                  placeholder_text="Enter new username",
                                  **entry_style)
    username_entry.grid(row=2, column=0, sticky="ew", padx=40, pady=(4, 10))

    # Email
    ctk.CTkLabel(container, text="New Email Address:",
                 font=label_font, text_color=TEXT_WHITE,
                 anchor="w").grid(row=3, column=0, sticky="w", padx=40)
    email_entry = ctk.CTkEntry(container,
                               placeholder_text="Enter new email",
                               **entry_style)
    email_entry.grid(row=4, column=0, sticky="ew", padx=40, pady=(4, 10))

    # Divider + hint
    ctk.CTkFrame(container, height=1, fg_color="#4A3C2F").grid(
        row=5, column=0, sticky="ew", padx=40, pady=(10, 4))
    ctk.CTkLabel(container,
                 text="Change Password  (leave blank to keep current)",
                 font=("Arial", 12), text_color="#8B7B6B").grid(
        row=6, column=0, sticky="w", padx=40, pady=(0, 6))

    # Current Password
    ctk.CTkLabel(container, text="Current Password:",
                 font=label_font, text_color=TEXT_WHITE,
                 anchor="w").grid(row=7, column=0, sticky="w", padx=40)
    old_pw_entry = ctk.CTkEntry(container,
                                placeholder_text="Enter current password",
                                show="*", **entry_style)
    old_pw_entry.grid(row=8, column=0, sticky="ew", padx=40, pady=(4, 10))

    # New Password
    ctk.CTkLabel(container, text="New Password:",
                 font=label_font, text_color=TEXT_WHITE,
                 anchor="w").grid(row=9, column=0, sticky="w", padx=40)
    new_pw_entry = ctk.CTkEntry(container,
                                placeholder_text="Enter new password",
                                show="*", **entry_style)
    new_pw_entry.grid(row=10, column=0, sticky="ew", padx=40, pady=(4, 10))

    # Confirm Password
    ctk.CTkLabel(container, text="Confirm New Password:",
                 font=label_font, text_color=TEXT_WHITE,
                 anchor="w").grid(row=11, column=0, sticky="w", padx=40)
    confirm_pw_entry = ctk.CTkEntry(container,
                                    placeholder_text="Confirm new password",
                                    show="*", **entry_style)
    confirm_pw_entry.grid(row=12, column=0, sticky="ew", padx=40, pady=(4, 10))

    # Error label
    error_label = ctk.CTkLabel(container, text="",
                               font=("Arial", 12),
                               text_color="#EF5350",
                               wraplength=310,
                               anchor="w")
    error_label.grid(row=13, column=0, sticky="w", padx=40, pady=(4, 0))

    # Pre-fill username and email
    current_usr = current_user.get("username")
    if current_usr:
        try:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username=?", (current_usr,))
            row = cursor.fetchone()
            conn.close()
            username_entry.insert(0, current_usr)
            if row:
                email_entry.insert(0, row[0])
        except sqlite3.Error:
            pass

    # Save logic
    def save_changes():
        new_username = username_entry.get().strip()
        new_email    = email_entry.get().strip()
        old_pw       = old_pw_entry.get()
        new_pw       = new_pw_entry.get()
        confirm_pw   = confirm_pw_entry.get()

        error_label.configure(text="", text_color="#EF5350")

        if not new_username or not new_email:
            error_label.configure(text="Username and email are required.")
            return

        hashed_new_pw = None
        if old_pw or new_pw or confirm_pw:
            if not old_pw:
                error_label.configure(text="Enter your current password to set a new one.")
                return

            try:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT password FROM users WHERE username=?",
                               (current_user["username"],))
                row = cursor.fetchone()
                conn.close()
            except sqlite3.Error as e:
                error_label.configure(text=f"Database error: {e}")
                return

            if not row or row[0] != hash_password(old_pw):
                error_label.configure(text="Current password is incorrect.")
                return
            if not new_pw:
                error_label.configure(text="New password cannot be empty.")
                return
            if len(new_pw) < 6:
                error_label.configure(text="New password must be at least 6 characters.")
                return
            if new_pw != confirm_pw:
                error_label.configure(text="New passwords do not match.")
                return

            hashed_new_pw = hash_password(new_pw)

        old_username = current_user["username"]

        try:
            conn = create_connection()
            cursor = conn.cursor()

            if hashed_new_pw:
                cursor.execute("""
                    UPDATE users SET username=?, email=?, password=?
                    WHERE username=?
                """, (new_username, new_email, hashed_new_pw, old_username))
            else:
                cursor.execute("""
                    UPDATE users SET username=?, email=?
                    WHERE username=?
                """, (new_username, new_email, old_username))

            cursor.execute("""
                UPDATE employee_performance SET username=?
                WHERE username=?
            """, (new_username, old_username))

            conn.commit()
            conn.close()

            current_user["username"] = new_username
            messagebox.showinfo("Success", "Account updated successfully!")
            update_win.destroy()
            show_window("profile")

        except sqlite3.IntegrityError:
            error_label.configure(text="This username is already taken.")
        except sqlite3.Error as e:
            error_label.configure(text=f"Database error: {e}")

    # Buttons
    ctk.CTkButton(container, text="SAVE CHANGES",
                  font=("Arial", 15, "bold"),
                  fg_color=BTN_CLAY, hover_color=HOVER_COLOR,
                  corner_radius=10, height=42,
                  command=save_changes).grid(
        row=14, column=0, sticky="ew", padx=40, pady=(0, 6))

    ctk.CTkButton(container, text="CANCEL",
                  font=("Arial", 15, "bold"),
                  fg_color=LOGOUT_ORANGE, hover_color="#8e3900",
                  corner_radius=10, height=42,
                  command=update_win.destroy).grid(
        row=15, column=0, sticky="ew", padx=40, pady=(0, 24))
    

# Saving Recovery Questions
def save_recovery_questions(user_id, q1, a1, q2, a2):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO recovery_questions (user_id, question_number, recovery_question, answer)
            VALUES (?, 1, ?, ?)
        """, (user_id, q1, hash_password(a1.strip().lower())))
        cursor.execute("""
            INSERT INTO recovery_questions (user_id, question_number, recovery_question, answer)
            VALUES (?, 2, ?, ?)
        """, (user_id, q2, hash_password(a2.strip().lower())))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def fetch_user_id_by_username(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def update_recovery_questions(user_id, q1, a1, q2, a2):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recovery_questions
        SET recovery_question=?, answer=?
        WHERE user_id=? AND question_number=1
    """, (q1, hash_password(a1.strip().lower()), user_id))
    cursor.execute("""
        UPDATE recovery_questions
        SET recovery_question=?, answer=?
        WHERE user_id=? AND question_number=2
    """, (q2, hash_password(a2.strip().lower()), user_id))
    conn.commit()
    conn.close()


def open_recovery_setup_popup(master, user_id, username, edit_mode=False):
    popup = ctk.CTkToplevel(master)
    center_window(popup, 500, 520)
    popup.transient(master)
    popup.grab_set()
    popup.after(150, lambda: [popup.lift(), popup.focus_force()])
    popup.title(f"Recovery Questions — {username}")
    popup.configure(fg_color="#2C241C")
    popup.resizable(False, False)

    ctk.CTkFrame(popup, fg_color="#43382F", height=6, corner_radius=0).pack(fill="x")
    header = ctk.CTkFrame(popup, fg_color="#43382F", corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(header,
                 text="Edit Recovery Questions" if edit_mode else "Set Recovery Questions",
                 font=("Segoe UI", 20, "bold"),
                 text_color="#F5E6D0").pack(anchor="w", padx=24, pady=14)

    body = ctk.CTkScrollableFrame(popup, fg_color="#2C241C", corner_radius=0)
    body.pack(fill="both", expand=True)
    body.grid_columnconfigure(0, weight=1)

    def lbl(text, row):
        ctk.CTkLabel(body, text=text,
                     font=("Segoe UI", 13, "bold"),
                     text_color="#D0C0A0").grid(row=row, column=0,
                                                sticky="w", padx=24, pady=(14, 4))

    def entry(row, prefill=""):
        e = ctk.CTkEntry(body, height=44,
                         fg_color="#43382F",
                         border_color="#6B5540", border_width=2,
                         text_color="#F0E6D3",
                         corner_radius=8,
                         font=("Segoe UI", 14))
        e.grid(row=row, column=0, sticky="ew", padx=24)
        if prefill:
            e.insert(0, prefill)
        return e


    # Pre-fill recovery questions
    existing_q1, existing_q2 = "", ""
    if edit_mode:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT recovery_question FROM recovery_questions
            WHERE user_id=? ORDER BY question_number ASC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        if len(rows) >= 2:
            existing_q1 = rows[0][0]
            existing_q2 = rows[1][0]

    lbl("Recovery Question 1:", 0)
    q1_entry = entry(1, existing_q1)

    lbl("Answer 1:", 2)
    a1_entry = entry(3)

    lbl("Recovery Question 2:", 4)
    q2_entry = entry(5, existing_q2)

    lbl("Answer 2:", 6)
    a2_entry = entry(7)

    if edit_mode:
        ctk.CTkLabel(body,
                     text="Leave answers blank to keep existing answers.",
                     font=("Segoe UI", 12),
                     text_color="#6B5540").grid(row=8, column=0,
                                                padx=24, pady=(8, 0), sticky="w")

    error_label = ctk.CTkLabel(body, text="",
                               font=("Segoe UI", 13),
                               text_color="#EF5350")
    error_label.grid(row=9, column=0, padx=24, pady=(10, 0), sticky="w")

    def save():
        q1 = q1_entry.get().strip()
        a1 = a1_entry.get().strip()
        q2 = q2_entry.get().strip()
        a2 = a2_entry.get().strip()

        if not q1 or not q2:
            error_label.configure(text="Both questions are required.")
            return

        if edit_mode:
            conn = create_connection()
            cursor = conn.cursor()
            if a1:
                cursor.execute("""
                    UPDATE recovery_questions
                    SET recovery_question=?, answer=?
                    WHERE user_id=? AND question_number=1
                """, (q1, hash_password(a1.strip().lower()), user_id))
            else:
                cursor.execute("""
                    UPDATE recovery_questions
                    SET recovery_question=?
                    WHERE user_id=? AND question_number=1
                """, (q1, user_id))

            if a2:
                cursor.execute("""
                    UPDATE recovery_questions
                    SET recovery_question=?, answer=?
                    WHERE user_id=? AND question_number=2
                """, (q2, hash_password(a2.strip().lower()), user_id))
            else:
                cursor.execute("""
                    UPDATE recovery_questions
                    SET recovery_question=?
                    WHERE user_id=? AND question_number=2
                """, (q2, user_id))

            conn.commit()
            conn.close()
            messagebox.showinfo("Saved", "Recovery questions updated.")
            popup.destroy()
        else:
            if not a1 or not a2:
                error_label.configure(text="Both answers are required.")
                return
            save_recovery_questions(user_id, q1, a1, q2, a2)
            messagebox.showinfo("Saved", "Recovery questions set successfully.")
            popup.destroy()

    footer = ctk.CTkFrame(popup, fg_color="#43382F", corner_radius=0, height=72)
    footer.pack(fill="x", side="bottom")
    footer.pack_propagate(False)

    ctk.CTkButton(footer, text="Save Questions",
                  height=46, corner_radius=8,
                  fg_color="#2E7D32", hover_color="#1B5E20",
                  text_color="white",
                  font=("Segoe UI", 15, "bold"),
                  command=save).pack(fill="x", padx=24, pady=12)


def create_employees_window(master):
    employees_win = ctk.CTkToplevel(master)
    center_window(employees_win, 1280, 720)
    employees_win.after(100, employees_win.lift)
    employees_win.after(100, employees_win.focus)
    employees_win.title("Kape'Bahay - Manage Employees")
    employees_win.resizable(False, False)
    employees_win.configure(fg_color="#43382F")


    employees_win.grid_columnconfigure(0, weight=1)
    employees_win.grid_rowconfigure(0, weight=0)
    employees_win.grid_rowconfigure(2, weight=1)

    # HEADER
    header = ctk.CTkFrame(employees_win, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    

    ctk.CTkLabel(header, text="Manage Employees",
                 font=("Segoe UI", 32, "bold"),
                 text_color="white").grid(row=0, column=0, sticky="w", padx=10)

    # TABS
    tab_frame = ctk.CTkFrame(employees_win, fg_color="transparent")
    tab_frame.grid(row=1, column=0, sticky="w", pady=(15, 5), padx=30)

    current_tab = ctk.StringVar(value="view")

    def update_tab_colors():
        view_tab.configure(fg_color="#2E7D32" if current_tab.get() == "view" else "#5C4A35")
        add_tab.configure(fg_color="#2E7D32" if current_tab.get() == "add" else "#5C4A35")
        edit_tab.configure(fg_color="#2E7D32" if current_tab.get() == "edit" else "#5C4A35")

    def switch_tab(tab):
        current_tab.set(tab)
        update_tab_colors()
        render_tab()

    view_tab = ctk.CTkButton(tab_frame, text="View & Delete",
                             width=160, height=36,
                             fg_color="#2E7D32", hover_color="#1B5E20",
                             font=("Segoe UI", 13, "bold"),
                             command=lambda: switch_tab("view"))
    view_tab.grid(row=0, column=0, padx=(0, 6))

    add_tab = ctk.CTkButton(tab_frame, text="Add Employee",
                            width=150, height=36,
                            fg_color="#5C4A35", hover_color="#43382F",
                            font=("Segoe UI", 13, "bold"),
                            command=lambda: switch_tab("add"))
    add_tab.grid(row=0, column=1, padx=(0, 6))

    edit_tab = ctk.CTkButton(tab_frame, text="Edit Employee",
                             width=150, height=36,
                             fg_color="#5C4A35", hover_color="#43382F",
                             font=("Segoe UI", 13, "bold"),
                             command=lambda: switch_tab("edit"))
    edit_tab.grid(row=0, column=2, padx=(0, 6))

    # CONTENT AREA
    content_area = ctk.CTkFrame(employees_win, fg_color="#2C241C", corner_radius=6)
    content_area.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 0))
    content_area.grid_columnconfigure(0, weight=1)
    content_area.grid_rowconfigure(0, weight=1)

    # DB FUNCTIONS 
    def fetch_all_users():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.role, u.email,
                   COALESCE(ep.total_sales, 0),
                   COALESCE(ep.orders_made, 0),
                   COALESCE(ep.on_shift, 0)
            FROM users u
            LEFT JOIN employee_performance ep ON u.id = ep.employee_id
            ORDER BY u.username ASC
        """)
        data = cursor.fetchall()
        conn.close()
        return data

    def delete_user(user_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if row and row[0].lower() == "superadmin" and current_user["role"].lower() != "superadmin":
            conn.close()
            messagebox.showerror("Access Denied",
                                 "SuperAdmin accounts cannot be deleted.")
            return

        cursor.execute("DELETE FROM employee_performance WHERE employee_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def update_user(user_id, new_username, new_role, new_email, new_password=None):
        conn = create_connection()
        cursor = conn.cursor()
        try:
            if new_password:
                hashed = hash_password(new_password)
                cursor.execute("""
                    UPDATE users SET username=?, role=?, email=?, password=?
                    WHERE id=?
                """, (new_username, new_role, new_email, hashed, user_id))
                cursor.execute("""
                    UPDATE employee_performance SET username=? WHERE employee_id=?
                """, (new_username, user_id))
            else:
                cursor.execute("""
                    UPDATE users SET username=?, role=?, email=?
                    WHERE id=?
                """, (new_username, new_role, new_email, user_id))
                cursor.execute("""
                    UPDATE employee_performance SET username=? WHERE employee_id=?
                """, (new_username, user_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    # TAB RENDERERS
    def clear_content():
        for widget in content_area.winfo_children():
            widget.destroy()
        content_area.grid_columnconfigure(0, weight=1)
        content_area.grid_columnconfigure(1, weight=0, minsize=0)

    # VIEW & DELETE TAB
    def render_view_tab():
        clear_content()

        scroll = ctk.CTkScrollableFrame(content_area, fg_color="#2C241C", corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        users = fetch_all_users()

        if not users:
            ctk.CTkLabel(scroll, text="No employees found.",
                         font=("Segoe UI", 18, "bold"),
                         text_color="#A09080").pack(pady=80)
            return

        for user_id, uname, role, email, total_sales, orders_made, on_shift in users:
            card = ctk.CTkFrame(scroll, fg_color="#4A3C2F", corner_radius=10)
            card.pack(fill="x", pady=8, padx=10, ipady=4)
            card.grid_columnconfigure(1, weight=1)

            # Left: avatar circle
            avatar = ctk.CTkFrame(card, fg_color="#6B5540", width=56, height=56,
                                  corner_radius=28)
            avatar.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=16, sticky="ns")
            avatar.grid_propagate(False)
            ctk.CTkLabel(avatar, text=uname[0].upper(),
                         font=("Segoe UI", 22, "bold"),
                         text_color="#F5E6D0").place(relx=0.5, rely=0.5, anchor="center")

            # Center: info
            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="w", pady=(14, 2))

            ctk.CTkLabel(info, text=uname,
                         font=("Segoe UI", 22, "bold"),
                         text_color="white").pack(side="left")

            if role.lower() =="superadmin":
                fg_color = "#c5953b"
            elif role.lower() == "admin":
                fg_color = "#0277BD"
            else:
                fg_color = "#5C4A35"

            # Role badge
            ctk.CTkLabel(info,
                         text=f"  {role.capitalize()}  ",
                         fg_color=fg_color,
                         text_color="white",
                         font=("Segoe UI", 14, "bold"),
                         corner_radius=5).pack(side="left", padx=(8, 0))

            # Shift badge
            ctk.CTkLabel(info,
                         text="  On Shift  " if on_shift == 1 else "  Off Shift  ",
                         fg_color="#2E7D32" if on_shift == 1 else "#C62828",
                         text_color="white",
                         font=("Segoe UI", 14, "bold"),
                         corner_radius=5).pack(side="left", padx=(8, 0))

            # Stats row
            stats = ctk.CTkFrame(card, fg_color="transparent")
            stats.grid(row=1, column=1, sticky="w", pady=(0, 14))

            ctk.CTkLabel(stats, text=f"{email}",
                         font=("Segoe UI", 16),
                         text_color="#A09080").pack(side="left", padx=(0, 16))
            ctk.CTkLabel(stats, text=f"₱{total_sales:,.2f} sales",
                         font=("Segoe UI", 16),
                         text_color="#F5D8A8").pack(side="left", padx=(0, 16))
            ctk.CTkLabel(stats, text=f"{orders_made} orders",
                         font=("Segoe UI", 16),
                         text_color="#D0C9B8").pack(side="left")


            ctk.CTkButton(card, text="Recovery",
              width=110, height=45,
              fg_color="#0277BD", hover_color="#01579B",
              text_color="white",
              font=("Segoe UI", 18, "bold"),
              corner_radius=6,
              command=lambda uid=user_id, un=uname: open_recovery_setup_popup(
                  employees_win, uid, un, edit_mode=True)
              ).grid(row=0, column=2, rowspan=2, padx=(0, 16), pady=(20, 16))

            # Right: delete button
            ctk.CTkButton(card, text="Delete",
                          width=110, height=45,
                          fg_color="#C62828", hover_color="#922B21",
                          text_color="white",
                          font=("Segoe UI", 18, "bold"),
                          corner_radius=6,
                          command=lambda uid=user_id, un=uname, ur=role: (
                              messagebox.showerror(
                                  "Access Denied",
                                  "SuperAdmin accounts cannot be deleted by Admins."
                              ) if ur.lower() == "superadmin" and current_user["role"].lower() != "superadmin"
                              else confirm_delete(uid, un, ur)
                          )).grid(row=0, column=3, rowspan=2, padx=(0, 16), pady=(20, 16))
            
            

    def confirm_delete(user_id, username, role):
        # Hard guard
        if role.lower() == "superadmin" and current_user["role"].lower() != "superadmin":
            messagebox.showerror("Access Denied",
                                 "SuperAdmin accounts cannot be deleted by Admins.")
            return

        popup = ctk.CTkToplevel(employees_win)
        center_window(popup, 360, 200)
        popup.transient(employees_win)
        popup.grab_set()
        popup.after(150, lambda: [popup.lift(), popup.focus_force()])
        popup.title("Confirm Delete")
        popup.configure(fg_color="#2C241C")
        popup.resizable(False, False)

        ctk.CTkLabel(popup, text="Delete Employee",
                     font=("Segoe UI", 22, "bold"),
                     text_color="white").pack(pady=(24, 6))
        ctk.CTkLabel(popup,
                     text=f"Are you sure you want to delete '{username}'?\nThis cannot be undone.",
                     font=("Segoe UI", 13),
                     text_color="#A09080",
                     justify="center").pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(popup, fg_color="transparent")
        btn_row.pack()

        ctk.CTkButton(btn_row, text="Cancel",
                      width=120, height=38,
                      fg_color="#5C4A35", hover_color="#43382F",
                      font=("Segoe UI", 13, "bold"),
                      command=popup.destroy).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btn_row, text="Delete",
                      width=120, height=38,
                      fg_color="#C62828", hover_color="#922B21",
                      font=("Segoe UI", 13, "bold"),
                      command=lambda: [delete_user(user_id),
                                       popup.destroy(),
                                       render_view_tab()]
                      ).pack(side="left")

    # ADD EMPLOYEE TAB
    def render_add_tab():
        clear_content()

        scroll = ctk.CTkScrollableFrame(content_area, fg_color="#2C241C", corner_radius=0)
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)

        def field_label(parent, text, row, col):
            ctk.CTkLabel(parent, text=text,
                         font=("Segoe UI", 13, "bold"),
                         text_color="#D0C0A0").grid(
                row=row, column=col, sticky="w", padx=24, pady=(18, 5))

        def styled_entry(parent, row, col, show=None):
            e = ctk.CTkEntry(parent, height=44,
                             fg_color="#43382F",
                             border_color="#6B5540", border_width=2,
                             text_color="#F0E6D3",
                             corner_radius=8,
                             font=("Segoe UI", 14),
                             show=show)
            e.grid(row=row, column=col, sticky="ew", padx=24, pady=(0, 4))
            return e

        def styled_combo(parent, values, variable, row, col):
            c = ctk.CTkComboBox(parent, values=values,
                                variable=variable,
                                state="readonly",
                                height=44,
                                fg_color="#43382F",
                                border_color="#6B5540", border_width=2,
                                text_color="#F0E6D3",
                                corner_radius=8,
                                button_color="#6B5540",
                                button_hover_color="#8B7050",
                                dropdown_fg_color="#43382F",
                                dropdown_text_color="#F0E6D3",
                                dropdown_hover_color="#5C4A35",
                                font=("Segoe UI", 14))
            c.grid(row=row, column=col, sticky="ew", padx=24)
            return c

        # Fields — two column layout
        field_label(scroll, "USERNAME", 0, 0)
        username_entry = styled_entry(scroll, 1, 0)

        field_label(scroll, "EMAIL", 0, 1)
        email_entry = styled_entry(scroll, 1, 1)

        field_label(scroll, "PASSWORD", 2, 0)
        password_entry = styled_entry(scroll, 3, 0, show="•")

        field_label(scroll, "CONFIRM PASSWORD", 2, 1)
        confirm_entry = styled_entry(scroll, 3, 1, show="•")

        field_label(scroll, "ROLE", 4, 0)
        role_var = ctk.StringVar(value="cashier")

        if current_user["role"] == "superAdmin":
            role_var.set("superAdmin")
            styled_combo(scroll, ["superAdmin","admin", "cashier"], role_var, 5, 0)
        elif current_user["role"] == "admin":
            role_var.set("admin")
            styled_combo(scroll, ["admin", "cashier"], role_var, 5, 0)
        

        # Error label
        error_label = ctk.CTkLabel(scroll, text="",
                                   font=("Segoe UI", 13),
                                   text_color="#EF5350")
        error_label.grid(row=6, column=0, columnspan=2, pady=(16, 0))

        def save_employee():
            uname    = username_entry.get().strip()
            email    = email_entry.get().strip()
            password = password_entry.get()
            confirm  = confirm_entry.get()
            role     = role_var.get()

            if not uname or not email or not password:
                error_label.configure(text="All fields are required.")
                return
            if password != confirm:
                error_label.configure(text="Passwords do not match.")
                return

            success = add_user(uname, password, role, email)
            if success:
                new_user_id = fetch_user_id_by_username(uname)
                open_recovery_setup_popup(employees_win, new_user_id, uname)

                # Clear form after popup closes
                username_entry.delete(0, "end")

                error_label.configure(text="✔  Employee added successfully.",
                                      text_color="#66BB6A")
                username_entry.delete(0, "end")
                email_entry.delete(0, "end")
                password_entry.delete(0, "end")
                confirm_entry.delete(0, "end")
                role_var.set("cashier")
            else:
                error_label.configure(text="Username already exists.",
                                      text_color="#EF5350")

        ctk.CTkButton(scroll, text="Add Employee",
                      height=46, corner_radius=8,
                      fg_color="#2E7D32", hover_color="#1B5E20",
                      text_color="white",
                      font=("Segoe UI", 15, "bold"),
                      command=save_employee
                      ).grid(row=7, column=0, columnspan=2,
                             sticky="ew", padx=24, pady=24)

    # EDIT EMPLOYEE TAB
    def render_edit_tab():
        clear_content()

        users = fetch_all_users()

        # Set up two-column layout for edit tab only
        content_area.grid_columnconfigure(0, weight=0, minsize=280)
        content_area.grid_columnconfigure(1, weight=1)

        # Left: user list selector
        selector_frame = ctk.CTkFrame(content_area, fg_color="#2C241C", corner_radius=0)
        selector_frame.grid(row=0, column=0, sticky="nsew")
        selector_frame.grid_columnconfigure(0, weight=1)  
        selector_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(selector_frame, text="Select Employee",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#D0C0A0").grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        user_scroll = ctk.CTkScrollableFrame(selector_frame, fg_color="#2C241C", corner_radius=0)
        user_scroll.grid(row=1, column=0, sticky="nsew", padx=0)
        user_scroll.grid_columnconfigure(0, weight=1)

        # Divider
        ctk.CTkFrame(content_area, width=2, fg_color="#5C4A35"
                     ).grid(row=0, column=0, sticky="nse")

        # Right: edit form
        form_frame = ctk.CTkScrollableFrame(content_area, fg_color="#3A2F24", corner_radius=0)
        form_frame.grid(row=0, column=1, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)

        selected_user = {"data": None}

        def load_edit_form(user):
            selected_user["data"] = user
            user_id, uname, role, email, *_ = user

            for widget in form_frame.winfo_children():
                widget.destroy()

            ctk.CTkLabel(form_frame, text=f"Editing: {uname}",
                         font=("Segoe UI", 20, "bold"),
                         text_color="white").grid(row=0, column=0,
                                                  sticky="w", padx=24, pady=(24, 16))

            def field_label(text, row):
                ctk.CTkLabel(form_frame, text=text,
                             font=("Segoe UI", 13, "bold"),
                             text_color="#D0C0A0").grid(
                    row=row, column=0, sticky="w", padx=24, pady=(12, 4))

            def styled_entry(row, prefill="", show=None):
                e = ctk.CTkEntry(form_frame, height=44,
                                 fg_color="#43382F",
                                 border_color="#6B5540", border_width=2,
                                 text_color="#F0E6D3",
                                 corner_radius=8,
                                 font=("Segoe UI", 14),
                                 show=show)
                e.grid(row=row, column=0, sticky="ew", padx=24)
                if prefill:
                    e.insert(0, prefill)
                return e

            field_label("USERNAME", 1)
            name_entry = styled_entry(2, uname)

            field_label("EMAIL", 3)
            email_entry = styled_entry(4, email)

            field_label("ROLE", 5)
            role_var = ctk.StringVar(value=role)

            # Role options depend on who is editing and who is being edited
            viewer_role = current_user["role"].lower()
            target_role = role.lower()

            # Prevent admin from editing a superadmin's role
            if target_role == "superadmin" and viewer_role != "superadmin":
                role_combo = ctk.CTkComboBox(form_frame, values=[role],
                                             variable=role_var,
                                             state="disabled", height=44,
                                             fg_color="#43382F",
                                             border_color="#6B5540", border_width=2,
                                             text_color="#A09080", corner_radius=8,
                                             button_color="#6B5540",
                                             button_hover_color="#6B5540",
                                             dropdown_fg_color="#43382F",
                                             dropdown_text_color="#F0E6D3",
                                             dropdown_hover_color="#5C4A35",
                                             font=("Segoe UI", 14))
                
                # Warning label shown below combo
                ctk.CTkLabel(form_frame, text="SuperAdmin role cannot be changed by Admin.",
                             font=("Segoe UI", 12),
                             text_color="#EF9A50").grid(row=6, column=0,
                                                        sticky="w", padx=24, pady=(2, 0))
            elif viewer_role == "superadmin":
                role_combo = ctk.CTkComboBox(form_frame, values=["superadmin", "admin", "cashier"],
                                             variable=role_var,
                                             state="readonly", height=44,
                                             fg_color="#43382F",
                                             border_color="#6B5540", border_width=2,
                                             text_color="#F0E6D3", corner_radius=8,
                                             button_color="#6B5540",
                                             button_hover_color="#8B7050",
                                             dropdown_fg_color="#43382F",
                                             dropdown_text_color="#F0E6D3",
                                             dropdown_hover_color="#5C4A35",
                                             font=("Segoe UI", 14))
            else:
                role_combo = ctk.CTkComboBox(form_frame, values=["admin", "cashier"],
                                             variable=role_var,
                                             state="readonly", height=44,
                                             fg_color="#43382F",
                                             border_color="#6B5540", border_width=2,
                                             text_color="#F0E6D3", corner_radius=8,
                                             button_color="#6B5540",
                                             button_hover_color="#8B7050",
                                             dropdown_fg_color="#43382F",
                                             dropdown_text_color="#F0E6D3",
                                             dropdown_hover_color="#5C4A35",
                                             font=("Segoe UI", 14))
            role_combo.grid(row=6, column=0, sticky="ew", padx=24)

            field_label("NEW PASSWORD  (leave blank to keep current)", 7)
            pw_entry = styled_entry(8, show="•")

            field_label("CONFIRM NEW PASSWORD", 9)
            cpw_entry = styled_entry(10, show="•")

            error_label = ctk.CTkLabel(form_frame, text="",
                                       font=("Segoe UI", 13),
                                       text_color="#EF5350")
            error_label.grid(row=11, column=0, pady=(12, 0), padx=24, sticky="w")

            def save_edits():
                new_name  = name_entry.get().strip()
                new_email = email_entry.get().strip()
                new_role  = role_var.get()
                new_pw    = pw_entry.get()
                new_cpw   = cpw_entry.get()

                if role.lower() == "superadmin" and current_user["role"].lower() != "superadmin":
                    error_label.configure(text="⚠  Access denied. Cannot edit a SuperAdmin account.",
                                          text_color="#EF9A50")
                    return

                if not new_name or not new_email:
                    error_label.configure(text="Username and email are required.",
                                          text_color="#EF5350")
                    return
                if new_pw and new_pw != new_cpw:
                    error_label.configure(text="Passwords do not match.",
                                          text_color="#EF5350")
                    return

                success = update_user(user_id, new_name, new_role,
                                      new_email, new_pw if new_pw else None)
                if success:
                    error_label.configure(text="✔  Changes saved successfully.",
                                          text_color="#66BB6A")
                    render_edit_tab()
                else:
                    error_label.configure(text="Username already taken.",
                                          text_color="#EF5350")

            ctk.CTkButton(form_frame, text="Save Changes",
                          height=46, corner_radius=8,
                          fg_color="#2E7D32", hover_color="#1B5E20",
                          text_color="white",
                          font=("Segoe UI", 15, "bold"),
                          command=save_edits
                          ).grid(row=12, column=0, sticky="ew", padx=24, pady=24)

        # Placeholder before selection
        if not users:
            ctk.CTkLabel(form_frame, text="No employees to edit.",
                         font=("Segoe UI", 20, "bold"),
                         text_color="#A09080").grid(row=0, column=0, pady=80)
        else:
            ctk.CTkLabel(form_frame,
                         text="Select an employee\nfrom the list to edit",
                         font=("Segoe UI", 20),
                         text_color="#6B5540",
                         justify="center").grid(row=0, column=0, pady=100)

        # Populate user list
        for user in users:
            user_id, uname, role, email, *_ = user
            btn = ctk.CTkButton(user_scroll,
                                text=f"  {uname}\n  {role.capitalize()}",
                                height=56, corner_radius=8,
                                fg_color="#4A3C2F", hover_color="#5C4A35",
                                text_color="#F0E6D3",
                                font=("Segoe UI", 13),
                                anchor="w",
                                command=lambda u=user: load_edit_form(u))
            btn.pack(fill="x", padx=8, pady=4)
    
    # TAB ROUTER
    def render_tab():
        tab = current_tab.get()
        if tab == "view":
            render_view_tab()
        elif tab == "add":
            render_add_tab()
        elif tab == "edit":
            render_edit_tab()

    # BOTTOM BAR
    bottom_bar = ctk.CTkFrame(employees_win, fg_color="#2C241C",
                              corner_radius=0, height=70)
    bottom_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))
    bottom_bar.grid_propagate(False)

    ctk.CTkButton(bottom_bar, text="← Return to Menu",
                  width=180, height=44,
                  fg_color="#43382F", hover_color="#5C4A35",
                  text_color="#F0E6D3",
                  font=("Segoe UI", 14, "bold"),
                  corner_radius=8,
                  command=lambda: show_window("profile")
                  ).pack(side="left", padx=20, pady=13)

    employees_win.after(100, render_tab)
    return employees_win


def create_sales_report_window(master):
    sales_win = ctk.CTkToplevel(master)
    center_window(sales_win, 1200, 780)
    sales_win.after(100, sales_win.lift)
    sales_win.after(100, sales_win.focus)
    sales_win.title("Kape't Bahay - Sales Report")
    sales_win.resizable(False, False)
    sales_win.configure(fg_color="#2C241C")

    outer = ctk.CTkFrame(sales_win, fg_color="#2C241C", corner_radius=0)
    outer.pack(fill="both", expand=True, padx=12, pady=12)
    outer.grid_columnconfigure(0, weight=0, minsize=370)
    outer.grid_columnconfigure(1, weight=1)
    outer.grid_rowconfigure(0, weight=1)

 
    # Database Functions
    def fetch_available_years():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT strftime('%Y', order_date) as yr
            FROM customer_orders WHERE status = 'Completed' ORDER BY yr ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        current_year = str(datetime.now().year)
        years = [r[0] for r in rows if r[0] is not None]
        if current_year not in years:
            years.append(current_year)
        years.sort()
        return years

    def fetch_monthly_revenue(year):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT strftime('%m', order_date) as month,
                   COUNT(*) as orders, SUM(total_amount) as sales
            FROM customer_orders
            WHERE status = 'Completed' AND strftime('%Y', order_date) = ?
            GROUP BY month
        """, (str(year),))
        rows = cursor.fetchall()
        conn.close()
        data = {str(i).zfill(2): (0, 0.0) for i in range(1, 13)}
        for month, orders, sales in rows:
            data[month] = (orders, float(sales) if sales else 0.0)
        return data

    def fetch_employee_activity():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, orders_made, total_sales, on_shift
            FROM employee_performance ORDER BY total_sales DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def fetch_popular_beverages(period="All Time"):
        conn = create_connection()
        cursor = conn.cursor()
        period_filter = ""
        if period == "Daily":
            period_filter = "AND DATE(co.order_date) = DATE('now')"
        elif period == "Weekly":
            period_filter = "AND co.order_date >= DATE('now', '-7 days')"
        elif period == "Monthly":
            period_filter = "AND strftime('%Y-%m', co.order_date) = strftime('%Y-%m', 'now')"
        cursor.execute(f"""
            SELECT mi.item_name, SUM(oi.quantity) as times_bought, SUM(oi.subtotal) as total_sales
            FROM order_item oi
            JOIN menu_item mi ON oi.item_id = mi.item_id
            JOIN customer_orders co ON oi.order_id = co.order_id
            WHERE co.status = 'Completed' {period_filter}
            GROUP BY mi.item_id, mi.item_name
            ORDER BY times_bought DESC LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def build_table(parent, columns, col_widths, header_bg="#3A2F24",
                    even_bg="#4A3C2F", odd_bg="#3A2F24", col_anchors=None):
        """
        Returns (table_frame, refresh_fn).
        refresh_fn(rows, formatters=None, status_col=None)
          - rows: list of tuples
          - formatters: dict {col_index: fn} for custom cell text
          - status_col: index of a status column to colorize
        """
        table_frame = ctk.CTkFrame(parent, fg_color=header_bg, corner_radius=0)

        # Configure columns ONCE on the master frame
        for i, cw in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, minsize=cw, weight=1)

        # Header row — row 0
        for i, (col_name, _) in enumerate(columns):
            anchor = col_anchors[i] if col_anchors else "w"
            ctk.CTkLabel(table_frame, text=col_name,
                         font=("Segoe UI", 14, "bold"),
                         text_color="#F5D8A8",
                         anchor=anchor).grid(row=0, column=i, sticky="ew",
                                             padx=(16, 4), pady=10)

        # Separator
        ctk.CTkFrame(table_frame, height=2, fg_color="#5C4A35"
                     ).grid(row=1, column=0, columnspan=len(columns),
                             sticky="ew", padx=0, pady=0)

        # Scrollable body — shares column count with header above
        body_scroll = ctk.CTkScrollableFrame(table_frame, fg_color=odd_bg,
                                             corner_radius=0)
        body_scroll.grid(row=2, column=0, columnspan=len(columns),
                         sticky="nsew", padx=0, pady=0)
        table_frame.grid_rowconfigure(2, weight=1)

        # Body also uses same minsize columns
        for i, cw in enumerate(col_widths):
            body_scroll.grid_columnconfigure(i, minsize=cw, weight=1)

        def refresh(rows, formatters=None, status_col=None, status_colors=None):
            for w in body_scroll.winfo_children():
                w.destroy()

            if not rows:
                ctk.CTkLabel(body_scroll, text="No data available.",
                             font=("Segoe UI", 13), text_color="#A09080"
                             ).grid(row=0, column=0,
                                    columnspan=len(columns), pady=24)
                return

            for r_idx, row_data in enumerate(rows):
                bg = even_bg if r_idx % 2 == 0 else odd_bg
                # Each data row is a frame spanning all columns
                row_f = ctk.CTkFrame(body_scroll, fg_color=bg, corner_radius=0)
                row_f.grid(row=r_idx, column=0, columnspan=len(columns),
                           sticky="ew", pady=0)
                # Row frame ALSO uses same minsize columns
                for i, cw in enumerate(col_widths):
                    row_f.grid_columnconfigure(i, minsize=cw, weight=1)

                for c_idx, cell_val in enumerate(row_data):
                    text = formatters[c_idx](cell_val) if (formatters and c_idx in formatters) else str(cell_val)

                    # Status column gets color treatment
                    if status_col is not None and c_idx == status_col and status_colors:
                        color = status_colors.get(str(cell_val), "#F2E5D5")
                        anchor = col_anchors[c_idx] if col_anchors else "w"
                        ctk.CTkLabel(row_f, text=text,
                                     font=("Segoe UI", 13, "bold"),
                                     text_color=color,
                                     anchor=anchor).grid(row=0, column=c_idx,
                                                         sticky="ew", padx=(16, 4), pady=8)
                    else:
                        anchor = col_anchors[c_idx] if col_anchors else "w"
                        ctk.CTkLabel(row_f, text=text,
                                     font=("Segoe UI", 13),
                                     text_color="#F2E5D5",
                                     anchor=anchor).grid(row=0, column=c_idx,
                                                         sticky="ew", padx=(16, 4), pady=8)

        return table_frame, refresh

    # ══════════════════════════════════════════
    #  LEFT PANEL
    # ══════════════════════════════════════════
    left_panel = ctk.CTkFrame(outer, fg_color="#43382F", corner_radius=10)
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    left_panel.grid_columnconfigure(0, weight=1)
    left_panel.grid_rowconfigure(1, weight=1)
    left_panel.grid_rowconfigure(2, weight=0)

    # Info block
    info_block = ctk.CTkFrame(left_panel, fg_color="#5C4A35", corner_radius=8)
    info_block.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
    info_block.grid_columnconfigure(0, weight=1)

    title_row = ctk.CTkFrame(info_block, fg_color="transparent")
    title_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 6))
    title_row.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(title_row, text="CAFE REPORTS",
                 font=("Arial", 30, "bold"),
                 text_color="white").grid(row=0, column=0, sticky="w")
    logo_img = load_image_file("kape't_bahay_logo.png", size=(64, 64))
    if logo_img:
        ctk.CTkLabel(title_row, image=logo_img, text="").grid(row=0, column=1, sticky="e")

    ctk.CTkLabel(info_block,
                 text="Here you can view the reports\nconcerning the performance,\nactivity and the steady\nprogress of the business.",
                 font=("Segoe UI", 15), text_color="#F2E5D5",
                 justify="center").grid(row=1, column=0, padx=14, pady=(0, 16))

    # Monthly Revenue block
    revenue_block = ctk.CTkFrame(left_panel, fg_color="#5C4A35", corner_radius=8)
    revenue_block.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
    revenue_block.grid_columnconfigure(0, weight=1)
    revenue_block.grid_rowconfigure(1, weight=1)

    rev_hdr = ctk.CTkFrame(revenue_block, fg_color="transparent")
    rev_hdr.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 8))
    rev_hdr.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(rev_hdr, text="Monthly Revenue",
                 font=("Arial", 22, "bold"),
                 text_color="white").grid(row=0, column=0, sticky="w")

    year_var = ctk.StringVar()
    available_years = fetch_available_years()
    year_var.set(available_years[-1] if available_years else str(datetime.now().year))

    ctk.CTkComboBox(rev_hdr, values=available_years, variable=year_var,
                    width=90, height=30, state="readonly",
                    fg_color="#43382F", border_color="#A07353", border_width=1,
                    text_color="white", button_color="#43382F",
                    dropdown_fg_color="#43382F", dropdown_text_color="white",
                    font=("Segoe UI", 13),
                    command=lambda _: refresh_monthly()
                    ).grid(row=0, column=1, padx=(8, 0))

    # Revenue table — first col left, Orders and Sales centered
    rev_table, rev_refresh = build_table(
        revenue_block,
        columns=[("Month", 0), ("Orders", 1), ("Sales", 2)],
        col_widths=[130, 80, 90],
        col_anchors=["w", "center", "center"]
    )
    rev_table.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    MONTH_NAMES = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

    def refresh_monthly():
        data = fetch_monthly_revenue(year_var.get())
        rows = []
        for i, name in enumerate(MONTH_NAMES):
            orders, sales = data[str(i + 1).zfill(2)]
            rows.append((name, orders, f"{sales:,.2f}"))
        rev_refresh(rows)

    # Bottom bar
    bottom_bar = ctk.CTkFrame(left_panel, fg_color="#43382F", corner_radius=8, height=64)
    bottom_bar.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
    bottom_bar.grid_propagate(False)
    bottom_bar.grid_columnconfigure(0, weight=1)
    bottom_bar.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(bottom_bar, text="← Return",
                  font=("Arial", 15, "bold"),
                  fg_color="#5C4A35", hover_color="#4A3C2F",
                  text_color="#F2E5D5", corner_radius=8, height=44,
                  command=lambda: show_window("profile")
                  ).grid(row=0, column=0, sticky="ew", padx=(8, 4), pady=10)

    ctk.CTkButton(bottom_bar, text="Log Out",
                  font=("Arial", 15, "bold"),
                  fg_color="#8B1A1A", hover_color="#6B0000",
                  text_color="white", corner_radius=8, height=44,
                  command=lambda: [set_employee_shift_off(current_user["username"]),
                                   show_window("login")]
                  ).grid(row=0, column=1, sticky="ew", padx=(4, 8), pady=10)

    # ══════════════════════════════════════════
    #  RIGHT PANEL
    # ══════════════════════════════════════════
    right_panel = ctk.CTkFrame(outer, fg_color="transparent", corner_radius=0)
    right_panel.grid(row=0, column=1, sticky="nsew")
    right_panel.grid_columnconfigure(0, weight=1)
    right_panel.grid_rowconfigure(0, weight=1)
    right_panel.grid_rowconfigure(1, weight=1)

    # Employee Activity
    emp_block = ctk.CTkFrame(right_panel, fg_color="#43382F", corner_radius=10)
    emp_block.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
    emp_block.grid_columnconfigure(0, weight=1)
    emp_block.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(emp_block, text="Employee Activity",
                 font=("Arial", 24, "bold"),
                 text_color="white").grid(row=0, column=0,
                                          sticky="w", padx=18, pady=(14, 8))

    # Employee table — Name left, rest centered
    emp_table, emp_refresh = build_table(
        emp_block,
        columns=[("Name", 0), ("Orders Made", 1), ("Sales", 2), ("Status", 3)],
        col_widths=[160, 130, 140, 120],
        col_anchors=["w", "center", "center", "center"]
    )
    emp_table.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def refresh_employees():
        rows = fetch_employee_activity()
        formatted = []
        for uname, orders, sales, on_shift in rows:
            shift_text = "On Shift" if on_shift == 1 else "Off Shift"
            formatted.append((uname, orders, f"₱{float(sales):,.2f}", shift_text))
        emp_refresh(
            formatted,
            status_col=3,
            status_colors={"On Shift": "#66BB6A", "Off Shift": "#EF5350"}
        )

    # Popular Beverages
    bev_block = ctk.CTkFrame(right_panel, fg_color="#43382F", corner_radius=10)
    bev_block.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
    bev_block.grid_columnconfigure(0, weight=1)
    bev_block.grid_rowconfigure(1, weight=1)

    bev_hdr_row = ctk.CTkFrame(bev_block, fg_color="transparent")
    bev_hdr_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
    bev_hdr_row.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(bev_hdr_row, text="Popular Beverages",
                 font=("Arial", 24, "bold"),
                 text_color="white").grid(row=0, column=0, sticky="w")

    bev_period_var = ctk.StringVar(value="All Time")
    ctk.CTkComboBox(bev_hdr_row,
                    values=["All Time", "Daily", "Weekly", "Monthly"],
                    variable=bev_period_var,
                    width=120, height=30, state="readonly",
                    fg_color="#5C4A35", border_color="#A07353", border_width=1,
                    text_color="white", button_color="#5C4A35",
                    dropdown_fg_color="#43382F", dropdown_text_color="white",
                    font=("Segoe UI", 13),
                    command=lambda _: refresh_beverages()
                    ).grid(row=0, column=1, padx=(8, 0))

    # Beverages table — Beverage left, rest centered
    bev_table, bev_refresh = build_table(
        bev_block,
        columns=[("Beverage", 0), ("Time Bought (#)", 1), ("Sales", 2)],
        col_widths=[240, 180, 140],
        col_anchors=["w", "center", "center"]
    )
    bev_table.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def refresh_beverages():
        rows = fetch_popular_beverages(bev_period_var.get())
        formatted = [(name, str(times), f"₱{float(sales):,.2f}")
                     for name, times, sales in rows]
        bev_refresh(formatted)

    def refresh_monthly():
        def fetch():
            data = fetch_monthly_revenue(year_var.get())
            rows = []
            for i, name in enumerate(MONTH_NAMES):
                orders, sales = data[str(i + 1).zfill(2)]
                rows.append((name, orders, f"{sales:,.2f}"))
            sales_win.after(0, lambda: rev_refresh(rows))
        threading.Thread(target=fetch, daemon=True).start()

    def refresh_employees():
        def fetch():
            rows = fetch_employee_activity()
            formatted = []
            for uname, orders, sales, on_shift in rows:
                shift_text = "On Shift" if on_shift == 1 else "Off Shift"
                formatted.append((uname, orders, f"₱{float(sales):,.2f}", shift_text))
            sales_win.after(0, lambda: emp_refresh(
                formatted,
                status_col=3,
                status_colors={"On Shift": "#66BB6A", "Off Shift": "#EF5350"}
            ))
        threading.Thread(target=fetch, daemon=True).start()

    def refresh_beverages():
        def fetch():
            rows = fetch_popular_beverages(bev_period_var.get())
            formatted = [(name, str(times), f"₱{float(sales):,.2f}")
                         for name, times, sales in rows]
            sales_win.after(0, lambda: bev_refresh(formatted))
        threading.Thread(target=fetch, daemon=True).start()

    sales_win.after(300, refresh_monthly)
    sales_win.after(400, refresh_employees)
    sales_win.after(500, refresh_beverages)

    return sales_win

loginWindowCreation = lazy_create_window("login")
loginWindowCreation.deiconify()
loginWindowCreation.lift()

def show_window(name):
    # Always recreate profile window to avoid stale user data
    if name == "profile":
        if "profile" in windows and windows["profile"] is not None and windows["profile"].winfo_exists():
            windows["profile"].destroy()
        windows["profile"] = create_profile_window(
            root,
            current_user["username"],
            current_user["role"]
        )

        # Hide all other windows
        for key, win in windows.items():
            if key != "profile" and win is not None and win.winfo_exists():
                win.withdraw()
        windows["profile"].deiconify()
        windows["profile"].lift()
        windows["profile"].focus_force()
        return

    # All other windows use lazy create as normal
    target = lazy_create_window(name)

    for key, win in windows.items():
        if key != name and win is not None and win.winfo_exists():
            win.withdraw()

    target.deiconify()
    target.lift()
    target.focus_force()

root.mainloop()


# USER ACCOUNTS AND RECOVERY QUESTIONS

# username: mico
# password: admin0001
# role:     cashier  
# email:    mic0@gmail.com
#
# Recovery Question 1
# Question: 
# Asnwer:
#
# Recovery Question 2
# Question:
# Answer:


# username: paul
# password: admin0002
# role:     cashier
# email:    pa6308191@gmail.com
#
# Recovery Question 1
# Question: 
# Asnwer:
#
# Recovery Question 2
# Question:
# Answer:


# username: amiel
# password: admin0003
# role:     admin
# email:    amiel@gmail.com
#
# Recovery Question 1
# Question: 
# Asnwer:   
#
# Recovery Question 2
# Question: 
# Answer:   


# username: ivan    
# password: admin0004
# role:     superAdmin
# email:    ivan@gmail.com
#
# Recovery Question 1
# Question: What is your favorite color?
# Asnwer:   blue
#
# Recovery Question 2
# Question: What is the name of your favorite pet?
# Answer:   badongs


# username: kyle
# password: 
# role:     admin
# email:    kyle@gmail.com
#
# Recovery Question 1
# Question: 
# Asnwer:
#
# Recovery Question 2
# Question:
# Answer:


# username: jessie
# password: admin0006
# role:     cashier
# email:    JESSIE12345@gmail.com
#
# Recovery Question 1
# Question: 
# Asnwer:
#
# Recovery Question 2
# Question:
# Answer: