from view_history import ManageHistory
import tkinter as tk 
from tkinter import messagebox
from appointment_page import TransportBookingSystem

class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#FFF8E8")
        self.controller = controller

        self.colors = {
            'primary': "#CC5500",
            'primary_dark':"#A34700",
            'bg': "#FFF8E8",
            'card_bg': "#FFF8E8",
            'text_dark': "#3A2D1F",
            'text_medium': "#5A4633",
            'border': "#E2E8F0",
            'highlight': "#DBEAFE",
            'button_text': "#F18E24"
        }
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg=self.colors['bg'], padx=20, pady=20)
        main_frame.pack(expand=True, fill="both")

        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill="x", pady=(0, 30))

        logo = tk.Canvas(header_frame, width=50, height=50, bg=self.colors['primary'], highlightthickness=0)
        logo.pack(side="left", padx=(0,15))

        title_frame = tk.Frame(header_frame, bg=self.colors['bg'])
        title_frame.pack(side="left", fill="y")

        tk.Label(title_frame, text="ACCOUNT PORTAL", font=('Segoe UI', 24, 'bold'), fg=self.colors['primary'], bg=self.colors['bg']).pack(anchor="w")
        tk.Label(title_frame, text="Manage your account and bookings", font=('Segoe UI', 12), fg=self.colors['text_medium'], bg=self.colors['bg']).pack(anchor="w")

        card_frame = tk.Frame(main_frame, bg=self.colors['card_bg'], padx=30, pady=30)
        card_frame.pack(fill="both", expand=True)

        tk.Button(card_frame, text="Book a Service", bg=self.colors['primary'], fg="white", font=('Segoe UI', 11, 'bold'), command=self.controller.show_booking).pack(fill="x", pady=10, ipadx=10)
        tk.Button(card_frame, text="View Booking History", bg=self.colors['primary'], fg="white", font=('Segoe UI', 11, 'bold'), command=self.show_history).pack(fill="x", pady=10, ipadx=10)
        tk.Button(card_frame, text="Logout", bg="white", fg=self.colors['primary'], font=('Segoe UI', 11, 'bold'), command=self.logout).pack(fill="x", pady=20, ipadx=10)

    def show_history(self):
        if self.controller.current_user_id:
            # Create ManageHistory instance and pass the current user_id
            history_manager = ManageHistory(self.controller.current_user_id)
            history_manager.print_rows()
        else:
            messagebox.showerror("Error", "Please log in first")
    
    # def show_booking(self):
    #     """Show the booking page"""
    #     self.pack_forget()  # Hide account portal
    #     # Create booking frame as a Frame widget
    #     self.booking_frame = tk.Frame(self.master)
    #     self.booking_frame.pack(expand=True, fill="both")
    #     # Initialize booking system inside this frame
    #     TransportBookingSystem(self.booking_frame, self.controller)

    def show_booking(self):
        """Show the booking page"""
        self.pack_forget()  # Hide account portal
        # Create booking frame with same parent
        self.booking_frame = tk.Frame(self.master)
        self.booking_frame.pack(expand=True, fill="both")
        # Initialize booking system inside this frame
        TransportBookingSystem(self.booking_frame, self.controller)
        
        # Store the current window size
        self.stored_geometry = self.master.winfo_geometry()
        
    def show_account_portal(self):
        """Show the account portal again"""
        # Restore the window to account portal size
        if hasattr(self, 'stored_geometry'):
            self.master.geometry(self.stored_geometry)
        self.pack(expand=True, fill="both")

    def logout(self):
        # Clear the user tracking variables
        self.controller.current_user_id = None
        self.controller.current_user_name = None
        # Then show welcome menu as before
        self.controller.show_welcome_menu()
