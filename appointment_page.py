import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import random
import requests
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk
from booking_queue_database import BookingDatabase

class TransportBookingSystem(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_user_id = controller.current_user_id
        self.current_user_name = controller.current_user_name 
        
        # Store the parent window reference
        self.parent_window = parent.winfo_toplevel()
        
        self.db = BookingDatabase()
        # Initialize all widget references first
        self.pickup_time_btn = None
        self.dropoff_time_btn = None
        self.pickup_time_display = None
        self.dropoff_time_display = None
        self.instant_btn = None
        self.schedule_btn = None
        print(f"Booking system initialized for user: {self.controller.current_user_name} (ID: {self.controller.current_user_id})")
        
        # API Key for OpenRouteService
        self.ORS_API_KEY = "5b3ce3597851110001cf624821c48bd478e94f3692170e872d0eeca3"
        
        # Initialize other variables
        self.booking_mode = True
        self.pickup = ""
        self.dropoff = ""
        self.pickup_coords = None
        self.dropoff_coords = None
        self.pickup_time = None
        self.dropoff_time = None
        self.bookings = []
        self.drivers = [
            {"id": 1, "name": "John Doe", "rating": 4.5, "vehicle": "Sedan", "available": True, "location": (14.5995, 120.9842)},
            {"id": 2, "name": "Jane Smith", "rating": 4.8, "vehicle": "SUV", "available": True, "location": (14.6000, 120.9850)},
            {"id": 3, "name": "Mike Johnson", "rating": 4.2, "vehicle": "Van", "available": True, "location": (14.5980, 120.9830)},
            {"id": 4, "name": "Sarah Williams", "rating": 4.7, "vehicle": "Luxury Sedan", "available": True, "location": (14.6010, 120.9860)},
            {"id": 5, "name": "David Brown", "rating": 4.3, "vehicle": "Minivan", "available": True, "location": (14.5975, 120.9825)}
        ]
        
        # Map variables
        self.map_widget = None
        self.pickup_marker = None
        self.dropoff_marker = None
        self.route_line = None
        self.moving_marker = None
        self.route_distance = 0
        self.route_duration = 0
        self.pickup_coords_list = []
        self.dropoff_coords_list = []
        self.pickup_timer = None
        self.destination_timer = None
        
        # Vehicle fares
        self.vehicle_fares = {
            "Car": (45, 3.75),
            "Motorcycle": (30, 2.75),
            "E-bike": (25, 2.50),
            "Tricycle": (20, 2),
            "Van": (55, 5),
            "Jeep": (35, 3)
        }
        self.selected_vehicle = tk.StringVar(value="Car")
        
        # Setup UI with new color palette
        self.setup_colors()
        self.setup_window()
        self.create_styles()
        self.setup_main_layout()
        self.setup_map()
        self.setup_controls_panel()
        self.setup_location_inputs()
        self.setup_booking_options()
        self.setup_route_info_panel()
        self.setup_action_buttons()
        self.setup_info_display()
        self.setup_back_button()
        
        # Initialize map
        self.initialize_map()
        
        # Set initial mode after all widgets exist
        self.update_booking_mode()

    def setup_colors(self):
        """Define the new color palette"""
        self.colors = {
            'primary': '#CC5500',    # Burnt Orange
            'bg': '#FFF8E8',         # Cream background
            'text': '#3A2D1F',       # Dark Chocolate
            'secondary': '#8B5A2B',  # Earth Brown
            'accent': '#5A8C5E',     # Leaf Green
            'card_bg': '#FFFFFF',    # White cards
            'border': '#E2D5C0',     # Light brown border
            'highlight': '#F0E6CC',  # Light cream highlight
            'success': '#5A8C5E',    # Leaf Green for success
            'warning': '#CC5500',     # Burnt Orange for warnings
            'danger': '#D32F2F',     # Red for errors
            'button_text': '#3A2D1F'  # Dark Chocolate text
        }
        self.configure(bg=self.colors['bg'])
    
    def create_styles(self):
        """Create custom widget styles with new colors"""
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Gives us more control over colors
        
        # Configure base styles
        self.style.configure('.', 
                           background=self.colors['bg'],
                           foreground=self.colors['text'],
                           font=('Segoe UI', 10))
        
        # Button styles
        self.style.configure('Action.TButton',
                        foreground=self.colors['button_text'],
                        background=self.colors['primary'],
                        font=('Segoe UI', 10, 'bold'),
                        padding=8,
                        borderwidth=1,
                        relief='raised')
        
        self.style.configure('Secondary.TButton',
                        foreground=self.colors['button_text'],
                        background=self.colors['primary'],
                        font=('Segoe UI', 10, 'bold'),
                        padding=8,
                        borderwidth=1,
                        relief='raised')
        
        self.style.configure('ActiveMode.TButton',
                        foreground=self.colors['button_text'],
                        background=self.colors['primary'],
                        font=('Segoe UI', 10, 'bold'),
                        padding=8,
                        borderwidth=1,
                        relief='raised')
        
        # Hover effects for all buttons
        self.style.map('Action.TButton',
                    background=[('active', self.colors['secondary'])])
        self.style.map('Secondary.TButton',
                    background=[('active', self.colors['secondary'])])
        self.style.map('ActiveMode.TButton',
                    background=[('active', self.colors['secondary'])])
        
        # Label styles
        self.style.configure('Title.TLabel',
                           foreground=self.colors['primary'],
                           background=self.colors['bg'],
                           font=('Segoe UI', 16, 'bold'))
        
        self.style.configure('Subtitle.TLabel',
                           foreground=self.colors['text'],
                           background=self.colors['bg'],
                           font=('Segoe UI', 12))
        
        self.style.configure('Regular.TLabel',
                           foreground=self.colors['text'],
                           background=self.colors['bg'],
                           font=('Segoe UI', 10))
        
        # Frame styles
        self.style.configure('Card.TFrame',
                           background=self.colors['card_bg'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'])
        
        # Entry styles
        self.style.configure('TEntry',
                           fieldbackground=self.colors['card_bg'],
                           foreground=self.colors['text'],
                           bordercolor=self.colors['border'],
                           lightcolor=self.colors['border'],
                           darkcolor=self.colors['border'])
        
        # Combobox styles
        self.style.configure('TCombobox',
                           fieldbackground=self.colors['card_bg'],
                           foreground=self.colors['text'],
                           background=self.colors['card_bg'],
                           selectbackground=self.colors['highlight'])
    
    def setup_window(self):
        """Configure window settings"""
        self.parent_window.state('zoomed')
        self.parent_window.minsize(1024, 768)
        self.parent_window.title("SwiftRide - Transport Booking System")
        self.pack(expand=True, fill="both")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # def setup_window(self):
    #     """Configure window settings"""
    #     # Remove these lines:
    #     # self.parent_window.state('zoomed')
    #     # self.parent_window.minsize(1024, 768)
        
    #     self.parent_window.title("SwiftRide - Transport Booking System")
    #     self.pack(expand=True, fill="both")
    #     self.columnconfigure(0, weight=1)
    #     self.rowconfigure(0, weight=1)
    
    def setup_main_layout(self):
        """Create main layout panes"""
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left pane (map) - 70% width
        self.map_frame = ttk.Frame(self.main_paned, style='Card.TFrame')
        self.main_paned.add(self.map_frame, weight=70)
        
        # Right pane (controls) - 30% width
        self.controls_frame = ttk.Frame(self.main_paned, style='Card.TFrame')
        self.main_paned.add(self.controls_frame, weight=30)
        
        # Configure expansion
        self.map_frame.columnconfigure(0, weight=1)
        self.map_frame.rowconfigure(0, weight=1)
        self.controls_frame.columnconfigure(0, weight=1)
        self.controls_frame.rowconfigure(1, weight=1)
    
    def setup_map(self):
        """Setup the map widget"""
        self.map_container = ttk.Frame(self.map_frame, style='Card.TFrame')
        self.map_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_back_button(self):
        """Add a back button to return to account portal"""
        back_btn = ttk.Button(self, 
                            text="← Go Back", 
                            style='Secondary.TButton',
                            command=self.go_back_to_portal)
        back_btn.place(relx=0.98, rely=0.02, anchor=tk.NE)

    def go_back_to_portal(self):
        """Return to the account portal"""
        self.pack_forget()
        self.controller.show_account_portal()
    
    def setup_controls_panel(self):
        """Setup the controls panel with logo and title"""
        # Header frame
        header_frame = ttk.Frame(self.controls_frame)
        header_frame.pack(fill=tk.X, pady=(10, 15), padx=5)

        try:
            # Load and display the logo image
            logo_img = Image.open("swift.png")
            logo_img = logo_img.resize((110, 110), Image.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            
            logo_label = ttk.Label(header_frame, image=self.logo_photo)
            logo_label.image = self.logo_photo
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            logo_canvas = tk.Canvas(header_frame, width=40, height=40,
                                bg=self.colors['primary'], highlightthickness=0)
            logo_canvas.pack(side=tk.LEFT, padx=(0, 10))
            logo_canvas.create_oval(8, 8, 32, 32, fill='white', outline='white')

        # Text labels
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(title_frame, 
                text="SWIFT", 
                style='Title.TLabel').pack(anchor=tk.W)

        ttk.Label(title_frame,
                text="Transport Booking System",
                style='Subtitle.TLabel').pack(anchor=tk.W)

        # Create scrollable area
        scroll_container = ttk.Frame(self.controls_frame)
        scroll_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(scroll_container, 
                            highlightthickness=0, 
                            bd=0,
                            bg=self.colors['bg'])
        self.scrollbar = ttk.Scrollbar(scroll_container, 
                                    orient="vertical", 
                                    command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        scroll_container.columnconfigure(0, weight=1)
        scroll_container.rowconfigure(0, weight=1)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="scroll_frame")

        def configure_scrollregion(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            if self.scrollable_frame.winfo_reqheight() > self.canvas.winfo_height():
                self.scrollbar.grid()
            else:
                self.scrollbar.grid_remove()

        self.scrollable_frame.bind("<Configure>", configure_scrollregion)
        self.scrollable_frame.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", 
                                    lambda ev: self.canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        self.scrollable_frame.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.bind("<Configure>", 
                        lambda e: self.canvas.itemconfig("scroll_frame", width=e.width))

        self.controls_container = self.scrollable_frame

    def initialize_map(self):
        """Initialize the map widget with new color scheme"""
        try:
            self.map_widget = TkinterMapView(self.map_container, 
                                                width=800, 
                                                height=600,
                                                corner_radius=10)
            self.map_widget.pack(fill=tk.BOTH, expand=True)
            self.map_widget.set_position(14.5995, 120.9842)
            self.map_widget.set_zoom(13)
            self.map_widget.add_left_click_map_command(self.map_click)
                
            # Customize map colors
            self.map_widget.canvas.configure(bg=self.colors['bg'])
                
        except Exception as e:
            messagebox.showerror("Map Error", f"Could not initialize map: {str(e)}")
            ttk.Label(self.map_container, text="Map functionality unavailable").pack()
            
    def setup_route_info_panel(self):
        """Create route information panel"""
        self.route_info_frame = ttk.Frame(self.controls_container, style='Card.TFrame', padding=10)
        self.route_info_frame.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        self.distance_label = ttk.Label(self.route_info_frame, 
                                      text="Distance: -- km",
                                      style='Regular.TLabel')
        self.distance_label.pack(anchor=tk.W)
        
        self.duration_label = ttk.Label(self.route_info_frame,
                                      text="Duration: -- min", 
                                      style='Regular.TLabel')
        self.duration_label.pack(anchor=tk.W)
        
        self.fare_label = ttk.Label(self.route_info_frame,
                                  text="Estimated Fare: ₱--",
                                  style='Regular.TLabel')
        self.fare_label.pack(anchor=tk.W)
    
    def update_route_info(self):
        """Update the route information panel"""
        if hasattr(self, 'route_distance') and hasattr(self, 'route_duration'):
            self.distance_label.config(text=f"Distance: {self.route_distance:.2f} km")
            self.duration_label.config(text=f"Duration: {self.route_duration:.1f} min")
            fare = self.calculate_fare(self.route_distance)
            self.fare_label.config(text=f"Estimated Fare: ₱{fare:.2f}")

    def setup_booking_options(self):
        """Create booking mode selection with visual feedback"""
        mode_card = ttk.Frame(self.controls_container, style='Card.TFrame', padding=(15, 10))
        mode_card.pack(fill=tk.X, pady=(0, 10), padx=5)
        mode_card.columnconfigure(0, weight=1)
        
        ttk.Label(mode_card, 
                text="Booking Mode:",
                style='Regular.TLabel').grid(row=0, column=0, sticky="w")
        
        mode_frame = ttk.Frame(mode_card)
        mode_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        self.mode_var = tk.BooleanVar(value=True)
        
        # Instant button
        self.instant_btn = ttk.Radiobutton(mode_frame, 
                                        text="Instant", 
                                        variable=self.mode_var,
                                        value=True,
                                        style='Secondary.TButton',
                                        command=self.update_booking_mode)
        self.instant_btn.grid(row=0, column=0, sticky="ew", padx=5)
        
        # Schedule button - only create this once
        self.schedule_btn = ttk.Radiobutton(mode_frame, 
                                        text="Schedule", 
                                        variable=self.mode_var,
                                        value=False,
                                        style='Secondary.TButton',
                                        command=self.update_booking_mode)
        self.schedule_btn.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Set initial active mode
        self.update_booking_mode()
    
    def update_booking_mode(self):
        """Handle booking mode changes with visual feedback"""
        if self.mode_var.get():  # Instant Booking
            self.instant_btn.config(style='ActiveMode.TButton')  # Highlighted
            self.schedule_btn.config(style='Secondary.TButton')  # Normal
            self.pickup_time_btn.config(state=tk.DISABLED)
            self.dropoff_time_btn.config(state=tk.DISABLED)
        else:  # Schedule Later
            self.instant_btn.config(style='Secondary.TButton')  # Normal
            self.schedule_btn.config(style='ActiveMode.TButton')  # Highlighted
            self.pickup_time_btn.config(state=tk.NORMAL)
            self.dropoff_time_btn.config(state=tk.NORMAL)

    def select_pickup_time(self):
        """Create a popup time picker dialog for selecting pickup time (12-hour format)"""
        top = tk.Toplevel(self.parent_window)
        top.title("Select Pickup Time")
        top.geometry("300x250")
        top.resizable(False, False)
        
        # Make the popup modal
        top.grab_set()
        top.transient(self.parent_window)
        
        # Time selection widgets
        time_frame = ttk.Frame(top, padding=20)
        time_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(time_frame, text="Select Pickup Time:").pack(pady=5)
        
        # Create a Combobox for hours (12-hour format)
        hour_var = tk.StringVar(value="12")
        ttk.Label(time_frame, text="Hour:").pack()
        hour_cb = ttk.Combobox(time_frame, textvariable=hour_var, 
                              values=[f"{i}" for i in range(1, 13)], 
                              width=5, state="readonly")
        hour_cb.pack()
        
        # Create a Combobox for minutes
        minute_var = tk.StringVar(value="00")
        ttk.Label(time_frame, text="Minute:").pack()
        minute_cb = ttk.Combobox(time_frame, textvariable=minute_var, 
                                values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                width=5, state="readonly")
        minute_cb.pack(pady=5)
        
        # AM/PM selection
        ampm_var = tk.StringVar(value="AM")
        ttk.Label(time_frame, text="AM/PM:").pack()
        ampm_cb = ttk.Combobox(time_frame, textvariable=ampm_var, 
                              values=["AM", "PM"], 
                              width=5, state="readonly")
        ampm_cb.pack(pady=5)
        
        def set_time():
            """Set the selected time"""
            time_str = f"{hour_var.get()}:{minute_var.get()} {ampm_var.get()}"
            self.pickup_time_display.config(text=time_str)
            self.pickup_time = time_str
            top.destroy()
        
        ttk.Button(time_frame, text="Set Time", command=set_time).pack(pady=10)
    
    def select_dropoff_time(self):
        """Create a popup time picker dialog for selecting dropoff time (12-hour format)"""
        top = tk.Toplevel(self.parent_window)
        top.title("Select Dropoff Time")
        top.geometry("300x250")
        top.resizable(False, False)
        
        # Make the popup modal
        top.grab_set()
        top.transient(self.parent_window)
        
        # Time selection widgets
        time_frame = ttk.Frame(top, padding=20)
        time_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(time_frame, text="Select Dropoff Time:").pack(pady=5)
        
        # Create a Combobox for hours (12-hour format)
        hour_var = tk.StringVar(value="12")
        ttk.Label(time_frame, text="Hour:").pack()
        hour_cb = ttk.Combobox(time_frame, textvariable=hour_var, 
                              values=[f"{i}" for i in range(1, 13)], 
                              width=5, state="readonly")
        hour_cb.pack()
        
        # Create a Combobox for minutes
        minute_var = tk.StringVar(value="00")
        ttk.Label(time_frame, text="Minute:").pack()
        minute_cb = ttk.Combobox(time_frame, textvariable=minute_var, 
                                values=[f"{i:02d}" for i in range(0, 60, 5)], 
                                width=5, state="readonly")
        minute_cb.pack(pady=5)
        
        # AM/PM selection
        ampm_var = tk.StringVar(value="AM")
        ttk.Label(time_frame, text="AM/PM:").pack()
        ampm_cb = ttk.Combobox(time_frame, textvariable=ampm_var, 
                              values=["AM", "PM"], 
                              width=5, state="readonly")
        ampm_cb.pack(pady=5)
        
        def set_time():
            """Set the selected time"""
            time_str = f"{hour_var.get()}:{minute_var.get()} {ampm_var.get()}"
            self.dropoff_time_display.config(text=time_str)
            self.dropoff_time = time_str
            top.destroy()
        
        ttk.Button(time_frame, text="Set Time", command=set_time).pack(pady=10)
    
    def setup_location_inputs(self):
        """Create location input fields"""
        input_card = ttk.Frame(self.controls_container, style='Card.TFrame', padding=15)
        input_card.pack(fill=tk.X, pady=(0, 15), padx=5)
        input_card.columnconfigure(0, weight=1)
        
        # Pickup Location
        ttk.Label(input_card, 
                 text="Pickup Location:",
                 style='Regular.TLabel').grid(row=0, column=0, sticky="w")
        
        self.pickup_entry = ttk.Entry(input_card, font=('Segoe UI', 10))
        self.pickup_entry.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        self.pickup_entry.bind("<KeyRelease>", self.debounce_pickup)
        
        self.pickup_listbox = tk.Listbox(input_card, height=4, font=('Segoe UI', 9))
        self.pickup_listbox.grid(row=2, column=0, sticky="ew")
        self.pickup_listbox.bind("<<ListboxSelect>>", 
                                lambda e: self.select_suggestion(e, self.pickup_entry, 
                                                               self.pickup_listbox, 
                                                               self.pickup_coords_list, True))
        
        # Pickup Time
        time_frame = ttk.Frame(input_card)
        time_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(time_frame, 
                 text="Pickup Time:",
                 style='Regular.TLabel').pack(side=tk.LEFT)
        
        self.pickup_time_btn = ttk.Button(time_frame, 
                                        text="Select Time", 
                                        style='Secondary.TButton',
                                        command=self.select_pickup_time)
        self.pickup_time_btn.pack(side=tk.LEFT, padx=5)
        
        self.pickup_time_display = ttk.Label(time_frame, 
                                           text="Not selected",
                                           style='Regular.TLabel')
        self.pickup_time_display.pack(side=tk.LEFT)
        
        # Destination Location
        ttk.Label(input_card, 
                 text="Destination:",
                 style='Regular.TLabel').grid(row=4, column=0, sticky="w", pady=(10, 0))
        
        self.destination_entry = ttk.Entry(input_card, font=('Segoe UI', 10))
        self.destination_entry.grid(row=5, column=0, sticky="ew", pady=(0, 5))
        self.destination_entry.bind("<KeyRelease>", self.debounce_destination)
        
        self.destination_listbox = tk.Listbox(input_card, height=4, font=('Segoe UI', 9))
        self.destination_listbox.grid(row=6, column=0, sticky="ew")
        self.destination_listbox.bind("<<ListboxSelect>>", 
                                    lambda e: self.select_suggestion(e, self.destination_entry, 
                                                                   self.destination_listbox, 
                                                                   self.dropoff_coords_list, False))
        
        # Dropoff Time
        dropoff_frame = ttk.Frame(input_card)
        dropoff_frame.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(dropoff_frame, 
                 text="Dropoff Time:",
                 style='Regular.TLabel').pack(side=tk.LEFT)
        
        self.dropoff_time_btn = ttk.Button(dropoff_frame, 
                                         text="Select Time", 
                                         style='Secondary.TButton',
                                         command=self.select_dropoff_time)
        self.dropoff_time_btn.pack(side=tk.LEFT, padx=5)
        
        self.dropoff_time_display = ttk.Label(dropoff_frame, 
                                            text="Not selected",
                                            style='Regular.TLabel')
        self.dropoff_time_display.pack(side=tk.LEFT)
        
        # Vehicle selection
        vehicle_frame = ttk.Frame(input_card)
        vehicle_frame.grid(row=8, column=0, sticky="ew", pady=(15, 0))
        
        ttk.Label(vehicle_frame, 
                 text="Vehicle Type:",
                 style='Regular.TLabel').pack(side=tk.LEFT)
        
        vehicle_menu = ttk.OptionMenu(vehicle_frame, 
                                    self.selected_vehicle,
                                    "Car",
                                    *self.vehicle_fares.keys(),
                                    command=lambda _: self.update_info_display())
        vehicle_menu.pack(side=tk.LEFT, padx=5)
    
    def setup_action_buttons(self):
        """Create action buttons"""
        btn_card = ttk.Frame(self.controls_container, style='Card.TFrame', padding=10)
        btn_card.pack(fill=tk.X, pady=(0, 15), padx=5)
        
        btn_container = ttk.Frame(btn_card)
        btn_container.pack(fill=tk.BOTH, expand=True)
        btn_container.columnconfigure(0, weight=1)
        
        ttk.Button(btn_container, 
                  text="Calculate Route", 
                  style='Action.TButton',
                  command=self.calculate_route).grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Button(btn_container, 
                  text="Confirm Booking", 
                  style='Action.TButton',
                  command=self.confirm_booking).grid(row=1, column=0, sticky="ew", pady=5)
        
        ttk.Button(btn_container, 
                  text="View History", 
                  style='Secondary.TButton',
                  command=self.show_booking_history_panel).grid(row=2, column=0, sticky="ew", pady=5)
    
    def setup_info_display(self):
        """Setup the information display area with properly sized scrollbar"""
        info_card = ttk.Frame(self.controls_container, style='Card.TFrame', padding=10)
        info_card.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Create container frame for proper scrollbar alignment
        container = ttk.Frame(info_card)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid for proper layout
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)  # No expansion for scrollbar
        
        self.info_display = tk.Text(container,
                                  height=10,
                                  wrap=tk.WORD,
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'],
                                  font=('Segoe UI', 10),
                                  padx=10,
                                  pady=10,
                                  relief='flat')
        self.info_display.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(container,
                                 orient="vertical",
                                 command=self.info_display.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.info_display.config(yscrollcommand=scrollbar.set)
        
        initial_text = "Welcome to SwiftRide!\n\nEnter pickup and destination locations to begin."
        self.update_info_display(initial_text)
        self.info_display.config(state=tk.DISABLED)
    
    def update_info_display(self, text):
        """Update the information display"""
        self.info_display.config(state=tk.NORMAL)
        self.info_display.insert(tk.END, "\n\n" + text)
        self.info_display.see(tk.END)
        self.info_display.config(state=tk.DISABLED)
    
    def autocomplete(self, query):
        """Get autocomplete suggestions from OpenRouteService"""
        url = "https://api.openrouteservice.org/geocode/autocomplete"
        params = {"api_key": self.ORS_API_KEY, "text": query, "size": 5}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            results = response.json().get("features", [])
            return [(res["properties"]["label"], res["geometry"]["coordinates"]) for res in results]
        except Exception as e:
            print(f"Autocomplete error: {e}")
            return []
    
    def delayed_autocomplete(self, entry, listbox, coords_list, is_pickup):
        """Delayed autocomplete to reduce API calls"""
        query = entry.get()
        listbox.delete(0, tk.END)
        coords_list.clear()

        # Add current location option
        listbox.insert(tk.END, "📍 Use My Current Location")
        coords_list.append("current_location")

        if len(query) >= 3:
            for name, coords in self.autocomplete(query):
                listbox.insert(tk.END, name)
                coords_list.append(coords)
    
    def get_current_location(self):
        """Get approximate current location using IP"""
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            loc = response.json().get("loc")
            if loc:
                return tuple(map(float, loc.split(",")))
        except Exception as e:
            print(f"Error getting current location: {e}")
            return None
    
    def select_suggestion(self, event, entry, listbox, coords_list, is_pickup):
        """Handle selection from autocomplete list"""
        if not listbox.curselection():
            return
            
        index = listbox.curselection()[0]
        name = listbox.get(index)
        coords = coords_list[index]

        if coords == "current_location":
            location = self.get_current_location()
            if not location:
                messagebox.showwarning("Warning", "Could not determine current location")
                return
            lat, lon = location
        else:
            lon, lat = coords  # OpenRouteService returns (lon, lat)

        entry.delete(0, tk.END)
        entry.insert(0, name)
        listbox.delete(0, tk.END)

        if is_pickup:
            if self.pickup_marker:
                self.pickup_marker.delete()
            self.pickup_marker = self.map_widget.set_marker(lat, lon, 
                                                          marker_color_circle="green", 
                                                          marker_color_outside="green")
            self.pickup_coords = (lat, lon)
        else:
            if self.dropoff_marker:
                self.dropoff_marker.delete()
            self.dropoff_marker = self.map_widget.set_marker(lat, lon, 
                                                           marker_color_circle="red", 
                                                           marker_color_outside="red")
            self.dropoff_coords = (lat, lon)

        if self.pickup_coords and self.dropoff_coords:
            self.calculate_route()
    
    def debounce_pickup(self, event):
        """Debounce pickup autocomplete"""
        if self.pickup_timer:
            self.parent_window.after_cancel(self.pickup_timer)
        self.pickup_timer = self.parent_window.after(400, lambda: self.delayed_autocomplete(
            self.pickup_entry, self.pickup_listbox, self.pickup_coords_list, True))
    
    def debounce_destination(self, event):
        """Debounce destination autocomplete"""
        if self.destination_timer:
            self.parent_window.after_cancel(self.destination_timer)
        self.destination_timer = self.parent_window.after(400, lambda: self.delayed_autocomplete(
            self.destination_entry, self.destination_listbox, self.dropoff_coords_list, False))
    
    def map_click(self, coords):
        """Handle map click events"""
        lat, lon = coords
        if not self.pickup_coords:
            if self.pickup_marker:
                self.pickup_marker.delete()
            self.pickup_marker = self.map_widget.set_marker(lat, lon, 
                                                          marker_color_circle="green", 
                                                          marker_color_outside="green")
            self.pickup_coords = (lat, lon)
            self.pickup_entry.delete(0, tk.END)
            self.pickup_entry.insert(0, f"{lat:.4f}, {lon:.4f}")
        elif not self.dropoff_coords:
            if self.dropoff_marker:
                self.dropoff_marker.delete()
            self.dropoff_marker = self.map_widget.set_marker(lat, lon, 
                                                           marker_color_circle="red", 
                                                           marker_color_outside="red")
            self.dropoff_coords = (lat, lon)
            self.destination_entry.delete(0, tk.END)
            self.destination_entry.insert(0, f"{lat:.4f}, {lon:.4f}")
            self.calculate_route()
        else:
            # Reset and start new selection
            if self.pickup_marker:
                self.pickup_marker.delete()
            if self.dropoff_marker:
                self.dropoff_marker.delete()
            if self.route_line:
                self.route_line.delete()
            self.pickup_coords = (lat, lon)
            self.dropoff_coords = None
            self.pickup_marker = self.map_widget.set_marker(lat, lon, 
                                                          marker_color_circle="green", 
                                                          marker_color_outside="green")
            self.pickup_entry.delete(0, tk.END)
            self.pickup_entry.insert(0, f"{lat:.4f}, {lon:.4f}")
            self.destination_entry.delete(0, tk.END)
    
    def get_route_coords(self, start, end):
        """Get route coordinates from OpenRouteService"""
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": self.ORS_API_KEY}
        params = {
            "start": f"{start[1]},{start[0]}", 
            "end": f"{end[1]},{end[0]}",
            "api_key": self.ORS_API_KEY
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("features"):
                messagebox.showerror("Routing Error", "No route found between these locations")
                return [], 0, 0
                
            feature = data["features"][0]
            coords = [(coord[1], coord[0]) for coord in feature["geometry"]["coordinates"]]
            distance_km = feature["properties"]["segments"][0]["distance"] / 1000
            duration_min = feature["properties"]["segments"][0]["duration"] / 60
            
            return coords, distance_km, duration_min
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Failed to connect to routing service: {str(e)}")
            return [], 0, 0
        except Exception as e:
            messagebox.showerror("Routing Error", f"Could not calculate route: {str(e)}")
            return [], 0, 0
    
    def calculate_route(self):
        """Calculate and display the route"""
        if not self.pickup_coords or not self.dropoff_coords:
            messagebox.showwarning("Missing Locations", "Please select both pickup and dropoff points")
            return
            
        if self.pickup_coords == self.dropoff_coords:
            messagebox.showwarning("Invalid Locations", "Pickup and dropoff locations cannot be the same")
            return
            
        try:
            if self.route_line:
                self.route_line.delete()
                
            coords, distance_km, duration_min = self.get_route_coords(self.pickup_coords, self.dropoff_coords)
            
            if coords:
                self.route_line = self.map_widget.set_path(coords, width=3, color="blue")
                self.route_distance = distance_km
                self.route_duration = duration_min
                self.update_route_info()
                self.animate_route(coords)
                
                self.update_info_display(
                    f"Route calculated!\n"
                    f"Distance: {distance_km:.2f} km\n"
                    f"Duration: {duration_min:.1f} minutes"
                )
        except Exception as e:
            messagebox.showerror("Routing Error", f"Failed to calculate route: {str(e)}")

    def animate_route(self, route_coords):
        """Animate a marker along the route"""
        try:
            # Load and resize the image once
            icon_image = Image.open("logo_swift_right.png").resize((50, 50))
            self.animated_icon = ImageTk.PhotoImage(icon_image)

            # Delete previous marker if exists
            if self.moving_marker:
                self.moving_marker.delete()

            # Place the marker at the start of the route
            self.moving_marker = self.map_widget.set_marker(
                route_coords[0][0], route_coords[0][1], text="", icon=self.animated_icon
            )

            steps = len(route_coords)
            total_duration_ms = 5000  # total animation duration (5 seconds)
            delay = total_duration_ms / steps

            def move(step):
                if step >= steps:
                    return
                lat, lon = route_coords[step]
                self.moving_marker.set_position(lat, lon)
                self.parent_window.after(int(delay), lambda: move(step + 1))

            move(0)

        except Exception as e:
            messagebox.showerror("Animation Error", f"Failed to animate route: {str(e)}")

    def calculate_fare(self, distance_km):
        """Calculate fare based on vehicle type"""
        vehicle = self.selected_vehicle.get()
        base, increment = self.vehicle_fares.get(vehicle, (0, 0))
        distance_m = distance_km * 1000
        increments_count = distance_m // 250
        return base + (increments_count * increment)
    
    def check_availability(self):
        """Check driver availability"""
        self.pickup = self.pickup_entry.get().strip()
        self.dropoff = self.destination_entry.get().strip()
        
        if not self.pickup or not self.dropoff:
            messagebox.showerror("Error", "Please enter both pickup and destination locations")
            return
            
        if not self.mode_var.get() and self.pickup_time_display.cget("text") == "Not selected":
            messagebox.showerror("Error", "Please select pickup time for scheduled booking")
            return
        
        # Calculate route if not already done
        if not hasattr(self, 'route_distance'):
            self.calculate_route()
        
        available_drivers = [d for d in self.drivers if d['available']]
        if not available_drivers:
            messagebox.showwarning("Warning", "No drivers available at this time")
            return
        
        fare = self.calculate_fare(self.route_distance)
        
        summary = (
            f"Booking Summary:\n"
            f"Pickup: {self.pickup}\n"
            f"Destination: {self.dropoff}\n"
            f"Distance: {self.route_distance:.2f} km\n"
            f"Duration: {self.route_duration:.1f} mins\n"
            f"Vehicle: {self.selected_vehicle.get()}\n"
            f"Fare: ₱{fare:.2f}\n"
            f"Type: {'Instant' if self.mode_var.get() else 'Scheduled'}\n"
            f"Available Drivers: {len(available_drivers)}"
        )
        
        self.update_info_display(summary)

    def confirm_booking(self):
        """Confirm booking with fare calculation"""
        client_id = self.controller.current_user_id
        client_name = self.controller.current_user_name

        # Validation checks
        if not hasattr(self, 'route_distance') or self.route_distance == 0:
            messagebox.showerror("Error", "Please calculate a route first")
            return
            
        if not self.mode_var.get() and self.pickup_time_display.cget("text") == "Not selected":
            messagebox.showerror("Error", "Please select pickup time for scheduled booking")
            return
            
        available_drivers = [d for d in self.drivers if d['available']]
        if not available_drivers:
            messagebox.showwarning("Warning", "No drivers available at this time")
            return
            
        # Prepare booking data
        driver = random.choice(available_drivers)
        driver['available'] = False
        
        fare = self.calculate_fare(self.route_distance)
        
        # Handle timestamps
        if self.mode_var.get():  # Instant booking
            pickup_datetime = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            dropoff_datetime = (datetime.now() + timedelta(minutes=self.route_duration)).strftime("%Y-%m-%d %I:%M %p")
        else: 
            pickup_datetime = self.pickup_time_display.cget("text")
            try:
                pickup_time = datetime.strptime(pickup_datetime, "%I:%M %p")
                dropoff_datetime = (pickup_time + timedelta(minutes=self.route_duration)).strftime("%I:%M %p")
            except:
                dropoff_datetime = "Unknown"
        
        first_num = random.randint(1, 9)
        second_num = random.randint(1, 9)
        third_num = random.randint(1, 9)
        fourth_num = random.randint(1, 9)
        unique_book_id = str(first_num) + str(second_num) + str(third_num) + str(fourth_num)

        booking = {
            "id": unique_book_id,
            "client_id": client_id,
            "client_name": client_name,
            "pickup": self.pickup_entry.get().strip(),
            "dropoff": self.destination_entry.get().strip(),
            "type": "Instant" if self.mode_var.get() else "Scheduled",
            "pickup_time": pickup_datetime,
            "dropoff_time": dropoff_datetime if not self.mode_var.get() else None,
            "fare": fare,
            "status": "Confirmed",
            "driver": driver,
            "vehicle": self.selected_vehicle.get(),
            "distance": self.route_distance
        }
        
        # Create receipt window
        receipt_window = tk.Toplevel(self.parent_window)
        receipt_window.title("Booking Receipt")
        receipt_window.geometry("500x600")
        
        # Styled receipt frame
        receipt_frame = ttk.Frame(receipt_window, style='Card.TFrame', padding=15)
        receipt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        ttk.Label(receipt_frame, 
                text="⚡ SwiftRide Receipt", 
                style='Title.TLabel').pack(pady=(0, 10))
        
        # Receipt content
        receipt_text = tk.Text(receipt_frame,
                            wrap=tk.WORD,
                            bg='white',
                            fg='black',
                            font=('Courier New', 10),
                            padx=10,
                            pady=10,
                            relief='flat')
        receipt_text.pack(fill=tk.BOTH, expand=True)
        
        # Generate receipt content
        receipt_content = [
            "═"*40,
            f" {'Booking ID:':<15} {booking['id']}",
            f" {'Status:':<15} {booking['status']}",
            f" {'Type:':<15} {booking['type']}",
            "═"*40,
            f" {'Pickup:':<15} {booking['pickup']}",
            f" {'Destination:':<15} {booking['dropoff']}",
            f" {'Distance:':<15} {booking['distance']:.2f} km",
            "─"*40,
            f" {'Vehicle:':<15} {booking['vehicle']}",
            f" {'Driver:':<15} {booking['driver']['name']}",
            f" {'Rating:':<15} {booking['driver']['rating']}",
            "─"*40,
            f" {'Pickup Time:':<15} {booking['pickup_time']}",
            f" {'Dropoff Time:':<15} {booking.get('dropoff_time', 'ASAP')}",
            "═"*40,
            f" {'FARE:':<15} ₱{booking['fare']:.2f}",
            "═"*40,
            "\nThank you for choosing SwiftRide!"
        ]
        
        # Insert formatted content
        for line in receipt_content:
            receipt_text.insert(tk.END, line + "\n")
        receipt_text.config(state=tk.DISABLED)
        
        # Action buttons
        btn_frame = ttk.Frame(receipt_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add Cancel Booking button (available for 2 minutes)
        self.cancel_btn = ttk.Button(btn_frame, 
                    text="Cancel Booking", 
                    style='Danger.TButton',
                    command=lambda: self.cancel_booking(booking['id'], receipt_window))
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        self.parent_window.after(120000, lambda: self.cancel_btn.config(state=tk.DISABLED))
        
        ttk.Button(btn_frame, 
                text="Close", 
                style='Secondary.TButton',
                command=receipt_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Upload to Sheets in background
        def upload_to_sheets():
            try:
                if not self.db.add_booking(booking):
                    messagebox.showerror("Database Error", 
                                    "Failed to save booking to database", 
                                    parent=receipt_window)
                else:
                    self.bookings.append(booking)
                    # Update receipt with success message
                    receipt_text.config(state=tk.NORMAL)
                    receipt_text.insert(tk.END, "\n\n✓ Saved to database successfully!")
                    receipt_text.config(state=tk.DISABLED)
            except Exception as e:
                receipt_text.config(state=tk.NORMAL)
                receipt_text.insert(tk.END, f"\n\n⚠️ Database Error: {str(e)}")
                receipt_text.config(state=tk.DISABLED)
        
        self.parent_window.after(300, upload_to_sheets)

    def cancel_booking(self, booking_id, receipt_window):
        """Simple cancellation method"""
        # Confirm cancellation
        if not messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
            return False
        
        try:
            # Update status in database
            if not self.db.update_booking_status(str(booking_id), "Cancelled"):
                messagebox.showerror("Error", "Could not update booking status")
                return False
            
            # Update local booking list
            for booking in self.bookings:
                if str(booking['id']) == str(booking_id):
                    booking['status'] = "Cancelled"
                    break
            
            # Update receipt display
            for widget in receipt_window.winfo_children():
                if isinstance(widget, tk.Text):
                    widget.config(state=tk.NORMAL)
                    widget.insert(tk.END, "\n\n❌ Booking Cancelled")
                    widget.config(state=tk.DISABLED)
                    break
            
            # Disable cancel button
            if hasattr(self, 'cancel_btn'):
                self.cancel_btn.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", "Booking cancelled successfully!")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong: {str(e)}")
            return False

    def show_booking_history_panel(self):
        """Create a separate window for booking history"""
        history_window = tk.Toplevel(self.parent_window)
        history_window.title("Booking History")
        history_window.geometry("600x400")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(history_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        history_text = tk.Text(text_frame, wrap=tk.WORD)
        history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history_text.config(yscrollcommand=scrollbar.set)
        
        # Populate history
        if not self.bookings:
            history_text.insert(tk.END, "No booking history available")
        else:
            for booking in self.bookings:
                history_text.insert(tk.END,
                    f"Booking ID: {booking['id']}\n"
                    f"Type: {booking['type']}\n"
                    f"From: {booking['pickup']}\n"
                    f"To: {booking['dropoff']}\n"
                    f"Vehicle: {booking['vehicle']}\n"
                    f"Driver: {booking['driver']['name']}\n"
                    f"Rating: {booking['driver']['rating']}\n"
                    f"Fare: ₱{booking['fare']:.2f}\n"
                    f"Pickup Time: {booking['pickup_time']}\n"
                    f"Status: {booking['status']}\n"
                    f"{'-'*40}\n\n"
                )
        history_text.config(state=tk.DISABLED)