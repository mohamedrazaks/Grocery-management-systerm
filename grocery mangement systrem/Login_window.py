from tkinter import *
from PIL import ImageTk
import tkinter as tk
from tkinter import messagebox
import psycopg2
import importlib
from Application_interface import GroceryManager 



# Functionality
def user_enter(event):
    if username.get() == "Username":
        username.delete(0, END)

def password_enter(event):
    if password.get() == "Password":
        password.delete(0, END)

def hide():
    openeye.config(file="C:\\Users\\aleem\\Downloads\\WhatsApp Image 2025-03-03 at 7.44.59 PM (1).jpeg")
    password.config(show="*")
    eyebutton.config(command=show)

def show():
    openeye.config(file="C:\\Users\\aleem\\Downloads\\WhatsApp Image 2025-03-03 at 7.45.00 PM.jpeg")
    password.config(show='')
    eyebutton.config(command=hide)

def sign_page():
    login_window.destroy()
    import razak  # Ensure this module exists and is correct

def login_user():
    print("Login button clicked!")  
    global username, password
    if not username.get() or not password.get():
        messagebox.showerror('Error', 'All Fields are Required')
        return

    try:
        # Connect to the database
        con = psycopg2.connect(
            database="customer",
            host="localhost",
            user="postgres",
            password="12345",
            port="5432"
        )
        mycursor = con.cursor()

        # Query to check username and password
        query = 'SELECT customer_id, username FROM details WHERE username = %s AND password = %s'
        print(f"Query: {query}")  # Debugging
        print(f"Username: {username.get()}")  # Debugging
        print(f"Password: {password.get()}")  # Debugging

        mycursor.execute(query, (username.get(), password.get()))
        row = mycursor.fetchone()

        if row is None:
            messagebox.showerror("Error", "Invalid username or password")
        else:
            # Fetch user_id and db_username from the database
            user_id, db_username = row  # Use a different variable name to avoid shadowing
            messagebox.showinfo("Welcome", "Your Login is Successful")
            login_window.destroy()  # Close the login window

            # Launch the GroceryManager GUI for the logged-in user
            root = tk.Tk()
            app = GroceryManager(root, user_id, db_username)
            root.mainloop()

    except Exception as e:
        messagebox.showerror("Error", f"Error during login: {e}")

        # Query to check username and password

# Create the login window
login_window = tk.Tk()
login_window.title("Login UI")
login_window.geometry("900x600")
login_window.resizable(0, 0)

# Background Image
background = ImageTk.PhotoImage(file="C:\\Users\\aleem\\Downloads\\WhatsApp Image 2025-03-03 at 7.44.59 PM.jpeg")
bglabel = Label(login_window, image=background)
bglabel.place(x=410)

# Frame for login form
frame = Frame(login_window, bg='white')
frame.place(x=950, y=200)

# Heading
heading = Label(login_window, text="USER LOGIN", font=('Montserrat', 23, 'bold'), fg='Royalblue4')
heading.place(x=115, y=50)

# Username Entry
username = Entry(login_window, width=28, font=('Montserrat', 14, 'bold'), bd=0, fg='Royalblue4')
username.place(x=50, y=120)
username.insert(0, "Username")
username.bind('<FocusIn>', user_enter)

# Underline for Username Entry
Frame1 = Frame(login_window, width=309, height=2, bg="Royalblue4")
Frame1.place(x=50, y=150)

# Password Entry
password = Entry(login_window, width=28, font=('Montserrat', 14, 'bold'), bd=0, fg='Royalblue4')
password.place(x=50, y=180)
password.insert(0, "Password")
password.bind('<FocusIn>', password_enter)

# Underline for Password Entry
Frame2 = Frame(login_window, width=309, height=2, bg="Royalblue4")
Frame2.place(x=50, y=210)

# Eye Button for Password Visibility
openeye = PhotoImage(file="C:\\Users\\Abinandh_Lakshman\\Downloads\\openeye.png")
eyebutton = Button(login_window, image=openeye, bg="white", bd=0, activebackground='white', cursor="hand2", command=hide, width=19)
eyebutton.place(x=335, y=179.2)

# Login Button
loginButton = Button(login_window, text="Login", font=("Open Sans", 10, 'bold'), fg='white', bg='RoyalBlue4', activeforeground='white', activebackground='RoyalBlue4', cursor='hand2', width=12, command=login_user)
loginButton.place(x=155, y=280)

# Signup Label and Button
Signuplabel = Label(login_window, text="Don't have an account?", font=('Montserrat', 12, 'bold'), fg='Royalblue4')
Signuplabel.place(x=50, y=340)

createnewbutton = Button(login_window, text="Create new one", font=('Open Sans', 12, 'bold underline'), fg="blue", activebackground='white', cursor="hand2", activeforeground='blue', bd=0, command=sign_page)
createnewbutton.place(x=240, y=337)

# Run the Tkinter main loop
login_window.mainloop()