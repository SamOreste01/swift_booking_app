import tkinter as tk 
from tkinter import messagebox
from PIL import Image, ImageTk
from user_info_database import UserInfoDatabase
from account_portal import AccountPage
from appointment_page import TransportBookingSystem

# Contains the main log-in and sign-up page
# It will serve as the main welcome page to teh program
class LandingPage:
    def __init__(self, root):
        self.root = root
        self.current_user_id = None
        self.current_user_name = None
        self.root.title("Swift Booking App")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # Themed colors being implemented
        self.colors = {
            'bg': "#FFF8E8",
            'card_bg': "#F5EDE3",
            'text': "#3A2D1F",
            'button_bg': "#CC5500",
            'button_fg': "#FFFFFF",
            'entry_bg': "#FDF8F3",
            'entry_border': "#C5B9AE"
        }
        self.root.configure(bg="#FFF8E8")
        self.database = UserInfoDatabase()
        self.current_frame = None
        self.show_welcome_menu()

    def clear_window(self):
        """Clear all frames from window"""
        if hasattr(self, 'current_frame') and self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
        
        if hasattr(self, 'booking_frame') and self.booking_frame:
            self.booking_frame.pack_forget()
            self.booking_frame.destroy()

    def show_account_portal(self):
        """Show account portal frame"""
        self.clear_window()
        self.current_frame = AccountPage(self.root, self)
        self.current_frame.pack(expand=True, fill="both")
        # Set the preferred size for account portal
        self.root.geometry("800x500")  # Match your initial size

    def show_booking(self):
        """Show booking system frame"""
        self.clear_window()  # Clear any existing frames first
        self.booking_frame = TransportBookingSystem(self.root, self)
        self.booking_frame.pack(expand=True, fill="both")

    # Sets up the main welcome menu
    def show_welcome_menu(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(expand=True, fill="both")
        self.current_frame = frame

        left = tk.Frame(frame, bg=self.colors['bg'], width=400)
        left.pack(side="left", fill="both", expand=True)

        try:
            image = Image.open("Final_Favicon.png")
            image = image.resize((200, 200))
            self.logo_image = ImageTk.PhotoImage(image)
            tk.Label(left, image=self.logo_image, bg=self.colors['bg']).pack(pady=(30, 10))
        except:
            tk.Label(left, text="SWIFT", font=("Arial", 32, "bold"), bg=self.colors['bg'], fg=self.colors['button_bg']).pack(pady=(30, 10))

        tk.Label(left, text="SWIFT", font=("Arial", 20, "bold"), bg=self.colors['bg'], fg=self.colors['button_bg']).pack()
        tk.Label(left, text="WELCOME", font=("Arial", 16, "bold"), bg=self.colors['button_bg'], fg=self.colors['button_bg']).pack()
        tk.Label(left, text="Drive Secure. Arrive Confident. Let's Ride!", font=("Arial", 10), bg=self.colors['bg'], fg=self.colors['text']).pack(pady=(10, 0))

        right = tk.Frame(frame, bg=self.colors['card_bg'], padx=20, pady=20)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="Get Started Here!", font=("Arial", 16, "bold"), bg=self.colors['card_bg'], fg=self.colors['text']).pack(pady=(20, 30))
        tk.Button(right, text="SIGN UP", width=35, height=4, bg=self.colors['button_bg'], fg=self.colors['button_fg'], command=self.show_signup_form).pack(pady=10)
        tk.Button(right, text="LOG IN", width=35, height=4, bg=self.colors['button_bg'], fg=self.colors['button_fg'], command=self.show_login_form).pack(pady=10)

    # sets-up the entry fields for sign-up instances
    def show_signup_form(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg=self.colors['card_bg'], padx=20, pady=20)
        frame.pack(expand=True, fill="both")
        self.current_frame = frame

        tk.Label(frame, text="Sign Up", font=("Arial", 14), bg=self.colors['card_bg'], fg=self.colors['text']).pack(pady=10)

        self.signup_name = self.create_entry(frame, "Full Name")
        self.signup_contact = self.create_entry(frame, "Contact Number")
        self.signup_email = self.create_entry(frame, "Email")
        self.signup_password = self.create_entry(frame, "Password", show="*")
        self.signup_address = self.create_entry(frame, "Home Address")

        tk.Button(frame, text="Submit", width=15, bg=self.colors['button_bg'], fg=self.colors['button_fg'], command=self.process_signup).pack(pady=10)
        tk.Button(frame, text="Back", width=15, bg="white", command=self.show_welcome_menu).pack()

    # sets-up the entry fields for log-in instances
    def show_login_form(self):
        self.clear_window()

        frame = tk.Frame(self.root, bg=self.colors['card_bg'], padx=20, pady=20)
        frame.pack(expand=True, fill="both")
        self.current_frame = frame

        tk.Label(frame, text="Log In", font=("Arial", 14), bg=self.colors['card_bg'], fg=self.colors['text']).pack(pady=10)

        # Added user ID field
        self.login_userid = self.create_entry(frame, "User ID")
        self.login_email = self.create_entry(frame, "Email")
        self.login_password = self.create_entry(frame, "Password", show="*")

        tk.Button(frame, text="Log In", width=15, bg=self.colors['button_bg'], fg=self.colors['button_fg'], command=self.process_login).pack(pady=10)
        tk.Button(frame, text="Back", width=15, bg="white", command=self.show_welcome_menu).pack()

    def create_entry(self, parent, label_text, show=None):
        tk.Label(parent, text=label_text, bg=self.colors['card_bg'], fg=self.colors['text'], anchor="w").pack(fill='x', pady=(5, 0))
        entry = tk.Entry(parent, bg=self.colors['entry_bg'], fg=self.colors['text'], relief="flat", show=show)
        entry.pack(fill='x', pady=(0, 10), ipady=3)
        return entry
    
    # Filters if user input satisfies the required
    def process_signup(self):
        name = self.signup_name.get()
        contact = self.signup_contact.get()
        email = self.signup_email.get()
        password = self.signup_password.get()
        address = self.signup_address.get()

        if len(name) < 2:
            messagebox.showerror("Error", "Name must be at least 2 characters.")
            return
        if not contact.isdigit() or not (10 <= len(contact) <= 13):
            messagebox.showerror("Error", "Contact number must be 10–13 digits.")
            return
        if "@" not in email or "." not in email:
            messagebox.showerror("Error", "Please enter a valid email address.")
            return
        if len(password) < 4 or not password.isalnum():
            messagebox.showerror("Error", "Password must be at least 4 alphanumeric characters.")
            return
        if not all([name, contact, email, password, address]):
            messagebox.showerror("Error", "Please fill in all fields.")
        else:
            try:
                # Uploads the user infromation logged in to the spreedsheet as a database
                self.database.upload_user(str(name), str(contact), str(email), str(password), str(address))
                messagebox.showinfo("Success", "Account created!")

                # User is now verified
                self.client_enrolled = True
                self.show_welcome_menu()

            except Exception as Failed_Upload:
                messagebox.showerror("Error", f"Failed to upload data.\n{Failed_Upload}")

    def process_login(self):
        # Get user ID from input
        user_id = self.login_userid.get()  
        email = self.login_email.get()
        password = self.login_password.get()

        # Checks if all fields are filled
        if not all([user_id, email, password]):  
            messagebox.showerror("Error", "Please enter all login details.")
            return

        # Utilizes the database to verify whether the account is present and already created
        user = self.database.find_user_by_credentials(user_id, email, password)  

        if user:
            # Store user info directly
            self.current_user_id = user['ID']
            self.current_user_name = user['Name']
            
            print(f"Logged in - ID: {self.current_user_id}, Name: {self.current_user_name}")
            
            self.clear_window()
            self.current_frame = AccountPage(self.root, self)
            self.current_frame.pack(expand=True, fill="both")
            messagebox.showinfo("Success", f"Welcome back, {user['Name']}!")
        else:
            messagebox.showerror("Error", "Invalid login details.")


if __name__ == "__main__":
    root = tk.Tk()
    app = LandingPage(root)
    root.mainloop()


    