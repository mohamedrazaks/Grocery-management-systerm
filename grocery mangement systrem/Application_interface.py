import os
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import schedule
import time
import threading
import logging


# Global dictionary to track last notification times
last_notification_times = {}

# Configure logging
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Email configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")  # Set these environment variables
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_USER or not EMAIL_PASSWORD:
    logging.error("Email credentials are missing! Set EMAIL_USER and EMAIL_PASSWORD as environment variables.")

def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="customer",
            user="postgres",
            password="12345",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True  # Auto-commit transactions
        logging.info("Connected to the database successfully!")
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Function to send email
def send_email_notification(subject, message, recipient_email):
    try:
        if not EMAIL_USER or not EMAIL_PASSWORD:
            logging.error("Cannot send email: Missing email credentials.")
            return

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, recipient_email, msg.as_string())

        logging.info(f"Email sent to {recipient_email} successfully!")
    except Exception as e:
        logging.error(f"Error sending email to {recipient_email}: {e}")



"""
from twilio.rest import Client

# Twilio configuration
# Twilio credentials
TWILIO_ACCOUNT_SID = "AC07768ab0385c623d5062ebe9fb47036c"  # Replace with your Account SID
TWILIO_AUTH_TOKEN = "9d3911ab1e5e2cdbdb8e1cf2a69fc35d"  # Replace with your Auth Token
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio WhatsApp Sandbox number
#RECIPIENT_NUMBER = "whatsapp:+918072858091" # Twilio WhatsApp Sandbox number

#def send_whatsapp_notification(message, recipient_number):
   
 #   Send a WhatsApp notification using the Twilio API.
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            logging.error("Cannot send WhatsApp notification: Missing Twilio credentials.")
            return

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

         Log the recipient number and message
         logging.info(f"Sending WhatsApp message to {recipient_number}: {message}")

         Send the message
         message = client.messages.create(
              body=message,
             from_=TWILIO_WHATSAPP_NUMBER,
             to=recipient_number
        )

         Log the message SID for tracking
        logging.info(f"WhatsApp message sent successfully! Message SID: {message.sid}")
    except Exception as e:
        logging.error(f"Error sending WhatsApp message: {e}") 
        """
        
def check_expiring_products(*args, **kwargs):
    global last_notification_times

    # Extract user_id from args or kwargs
    if args:
        user_id = args[0]  # Positional argument
    elif "user_id" in kwargs:
        user_id = kwargs["user_id"]  # Keyword argument
    else:
        logging.error("No user_id provided to check_expiring_products!")
        return

    logging.info(f"Checking for expiring products for user ID {user_id}...")
    try:
        conn = connect_db()
        if not conn:
            return

        today = datetime.today().date()
        expiry_end = today + timedelta(days=3)

        # Query to fetch expiring products for the logged-in user
        query = """
        SELECT product_name, expiry_date
        FROM groceries
        WHERE user_id = %s AND expiry_date BETWEEN %s AND %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (user_id, today, expiry_end))
        expiring_products = cursor.fetchall()

        if not expiring_products:
            logging.info(f"No expiring products found for user ID {user_id}.")
            return

        # Fetch the user's email from the details table
        cursor.execute("SELECT email FROM details WHERE customer_id = %s", (user_id,))
        user_details = cursor.fetchone()

        if not user_details:
            logging.error(f"No details found for user ID {user_id}.")
            return

        user_email = user_details[0]

        if not user_email:
            logging.error(f"No email found for user ID {user_id}.")
            return

        # Prepare the notification message
        product_list = "\n".join([f"- {product[0]} (Expires on: {product[1]})" for product in expiring_products])
        subject = "Grocery Expiry Alert"
        message = f"Dear customer,\n\nExpiring products:\n{product_list}\n\nare expiring within a few days."

        # Check if notifications were sent in the last 5 minutes
        current_time = time.time()
        for product in expiring_products:
            product_key = f"{user_id}_{product[0]}_{product[1]}"  # Unique key for each product

            # Check if the product was notified in the last 5 minutes
            if product_key in last_notification_times:
                last_notified = last_notification_times[product_key]
                if current_time - last_notified < 300:  # 300 seconds = 5 minutes
                    logging.info(f"Skipping notification for {product[0]} (already notified recently).")
                    continue

            # Send email notification
            logging.info(f"Sending email to {user_email}...")
            send_email_notification(subject, message, user_email)

            # Update the last notification time for this product
            last_notification_times[product_key] = current_time

    except Exception as e:
        logging.error(f"Error checking expiring products for user ID {user_id}: {e}")
    finally:
        if conn:
            conn.close()

def run_scheduler(user_id):
    """
    Run the scheduler to check for expiring products every 5 minutes.
    """
    if hasattr(run_scheduler, "scheduler_started"):
        logging.info("Scheduler is already running!")
        return

    run_scheduler.scheduler_started = True  # Mark scheduler as started
    logging.info(f"Scheduler started for user ID {user_id}!")
    schedule.every(5).minutes.do(check_expiring_products, user_id)  # Check every 5 minutes
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage

# Tkinter GUI Class
class GroceryManager:
    def __init__(self, root, user_id, username):
        self.user_id = user_id  # Store the logged-in user's ID
        self.username = username  # Store the logged-in username
        logging.info(f"Initializing GroceryManager for user ID {self.user_id} ({self.username})...")
        self.root = root
        self.root.title(f"Smart Grocery Manager - {self.username}")
        self.root.geometry("1200x800")
        self.root.configure(bg="#F0F0F0")

        # Database connection
        self.conn = connect_db()
        if not self.conn:
            messagebox.showerror("Database Error", "Failed to connect to the database!")
            self.root.destroy()
            return

        # Create frames
        self.create_frames()

        # Load background image
        self.load_background_image()

        # Load groceries
        self.load_groceries()

        # Start the scheduler for the logged-in user
        scheduler_thread = threading.Thread(target=run_scheduler, args=(self.user_id,), daemon=True)
        scheduler_thread.start()

    def create_frames(self):
        # Header Frame
        self.header_frame = tk.Frame(self.root, bg="alice blue", height=80)
        self.header_frame.place(relx=0.5, rely=0.075, anchor="center")
        logo_label = tk.Label(self.header_frame, text=f"🛒 Smart Grocery Manager", font=("Helvetica", 24, "bold"), fg="green", bg="alice blue")
        logo_label.pack(side="left", padx=20)

        # Logout Button
        logout_button = tk.Button(self.header_frame, text="🚪 Logout", font=("Helvetica", 12, "bold"), bg="blue2", fg="white",activebackground="white",activeforeground="blue2",
                                  command=self.logout, bd=0, padx=10, pady=5)
        logout_button.pack(side="right", padx=20)

        # Form Frame
        self.form_frame = tk.Frame(self.root, bg="alice blue", padx=20, pady=20, relief="flat", borderwidth=0)
        self.form_frame.place(relx=0.5, rely=0.320, anchor="center")

        # Product Name
        tk.Label(self.form_frame, text="🍎 Product Name:", font=("Helvetica", 12), bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.product_name_entry = tk.Entry(self.form_frame, font=("Helvetica", 12), bd=2, relief="sunken", bg="ivory2")
        self.product_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Quantity
        tk.Label(self.form_frame, text="🔢 Quantity:", font=("Helvetica", 12), bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.quantity_entry = tk.Entry(self.form_frame, font=("Helvetica", 12), bd=2, relief="sunken", bg="ivory2")
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Category Dropdown
        tk.Label(self.form_frame, text="📦 Category:", font=("Helvetica", 12), bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.category_entry = ttk.Combobox(self.form_frame, font=("Helvetica", 12), state="readonly",
                                           values=["Vegetables", "Fruits", "Dairy", "Cereals", "Snacks", "Beverages", "Others"])
        self.category_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.category_entry.current(0)

        # Purchase Date
        tk.Label(self.form_frame, text="📅 Purchase Date:", font=("Helvetica", 12), bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.purchase_date_entry = DateEntry(self.form_frame, date_pattern="yyyy-mm-dd", font=("Helvetica", 12), bd=2, relief="sunken", bg="#F9F9F9")
        self.purchase_date_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Expiry Date
        tk.Label(self.form_frame, text="⏳ Expiry Date:", font=("Helvetica", 12), bg="white").grid(row=4, column=0, sticky="w", pady=5)
        self.expiry_date_entry = DateEntry(self.form_frame, date_pattern="yyyy-mm-dd", font=("Helvetica", 12), bd=2, relief="sunken", bg="#F9F9F9")
        self.expiry_date_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Notify Days
        tk.Label(self.form_frame, text="🔔 Notify Before (days):", font=("Helvetica", 12), bg="white").grid(row=5, column=0, sticky="w", pady=5)
        self.notify_before_entry = tk.Entry(self.form_frame, font=("Helvetica", 12), bd=2, relief="sunken", bg="ivory2")
        self.notify_before_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Buttons Frame
        button_frame = tk.Frame(self.form_frame, bg="alice blue")
        button_frame.grid(row=6, column=0, columnspan=2, pady=19, sticky="ew")

        # Add Grocery Button
        tk.Button(button_frame, text="➕ Add Grocery", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
                  command=self.add_grocery, bd=0, padx=20, pady=10).pack(side="left", padx=10)

        # Update Grocery Button
        tk.Button(button_frame, text="🔄 Update Grocery", font=("Helvetica", 12, "bold"), bg="#FFC107", fg="white",
                  command=self.update_grocery, bd=0, padx=20, pady=10).pack(side="left", padx=10)

        # Delete Grocery Button
        tk.Button(button_frame, text="🗑️ Delete Grocery", font=("Helvetica", 12, "bold"), bg="#FF5733", fg="white",
                  command=self.delete_grocery, bd=0, padx=20, pady=10).pack(side="left", padx=10)

        # Treeview (Table) to display groceries
        self.tree_frame = tk.Frame(self.root, bg="alice blue")
        self.tree_frame.place(relx=0.5, rely=0.75, anchor="center", width=900, height=300)

        # Treeview and Scrollbar
        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Product Name", "Quantity", "Category", "Purchase Date", "Expiry Date", "Notify Days"), show="headings")
        for col in ("ID", "Product Name", "Quantity", "Category", "Purchase Date", "Expiry Date", "Notify Days"):
            self.tree.heading(col, text=col)
        self.tree.pack(side="left",padx=10, fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind Treeview selection to populate form fields
        self.tree.bind("<<TreeviewSelect>>", self.populate_form_fields)

    def load_background_image(self):
        try:
            self.bg_image = Image.open("C:\\Users\\Abinandh_Lakshman\\Downloads\\938ad57aebc3a17c92fe7d707fe2ae49.jpg")  # Replace with your image path
            self.bg_image = self.bg_image.resize((1200, 800), Image.LANCZOS)
            self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

            # Create a canvas for the background image
            self.canvas = tk.Canvas(self.root, width=1200, height=800)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor="nw")

            # Place other widgets on top of the canvas
            self.header_frame.lift()
            self.form_frame.lift()
            self.tree_frame.lift()
        except Exception as e:
            logging.error(f"Error loading background image: {e}")

    def load_groceries(self):
     try:
        self.tree.delete(*self.tree.get_children())
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, product_name, quantity, category, purchase_date, expiry_date, notify_before FROM groceries WHERE user_id = %s", (self.user_id,))
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
     except Exception as e:
        logging.error(f"Error loading groceries: {e}")
    def add_grocery(self):
        print("Adding grocery...")
        if not self.product_name_entry.get().strip():
            messagebox.showerror("Error", "Product Name cannot be empty!")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO groceries (product_name, quantity, category, purchase_date, expiry_date, notify_before, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    self.product_name_entry.get(),
                    self.quantity_entry.get(),
                    self.category_entry.get(),
                    self.purchase_date_entry.get(),
                    self.expiry_date_entry.get(),
                    self.notify_before_entry.get(),
                    self.user_id,
                ),
            )
            self.conn.commit()
            messagebox.showinfo("Success", "Grocery added successfully!")
            self.load_groceries()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to add grocery: {e}")

    def update_grocery(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to update!")
            return

        item = self.tree.item(selected_item)
        grocery_id = item["values"][0]

        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE groceries SET product_name=%s, quantity=%s, category=%s, purchase_date=%s, expiry_date=%s, notify_before=%s WHERE id=%s AND user_id=%s",
                            (self.product_name_entry.get(), self.quantity_entry.get(), self.category_entry.get(),
                             self.purchase_date_entry.get(), self.expiry_date_entry.get(), self.notify_before_entry.get(), grocery_id, self.user_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Grocery updated successfully!")
            self.load_groceries()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to update grocery: {e}")

    def delete_grocery(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete!")
            return

        item = self.tree.item(selected_item)
        grocery_id = item["values"][0]

        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM groceries WHERE id=%s AND user_id=%s", (grocery_id, self.user_id))
            self.conn.commit()
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Grocery deleted successfully!")
            self.load_groceries()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to delete grocery: {e}")

    def populate_form_fields(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item)
        values = item["values"]
        self.product_name_entry.delete(0, tk.END)
        self.product_name_entry.insert(0, values[1])
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, values[2])
        self.category_entry.set(values[3])
        self.purchase_date_entry.set_date(values[4])
        self.expiry_date_entry.set_date(values[5])
        self.notify_before_entry.delete(0, tk.END)
        self.notify_before_entry.insert(0, values[6])

    def logout(self):
        response = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if response:
            logging.info("User logged out.")
            self.root.destroy()
            import Login_window


def main():
    root = tk.Tk()
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id, username FROM details LIMIT 1")
        user_details = cursor.fetchone()
        if user_details:
            user_id, db_username = user_details
            app = GroceryManager(root, user_id, db_username)
            root.mainloop()