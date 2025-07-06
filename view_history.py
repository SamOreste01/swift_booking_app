import tkinter as tk
from tkinter import ttk, messagebox
import gspread
from google.oauth2.service_account import Credentials

class ManageHistory:
    def __init__(self, user_id):
        self.__sheet_id = "1i3lWKS-o8VjeGykXbRP27MZS0xniY490DAibQgNMwoE"  # Made private
        self.__scopes = ['https://www.googleapis.com/auth/spreadsheets']  # Made private
        self.__creds = Credentials.from_service_account_file("credentials.json", scopes=self.__scopes)  # Made private
        self.__client = gspread.authorize(self.__creds)  # Made private
        self.__sheet = self.__client.open_by_key(self.__sheet_id).sheet1  # Made private
        self.user_id = user_id  # Kept public as it's used externally

    def __get_sheet(self):
        # Private method to safely access the sheet
        return self.__sheet

    def all_user_id(self):
        all_data = self.__get_sheet().get_all_records()
        client_ids = [row['Client ID'] for row in all_data]
        return client_ids

    def print_rows(self):
        # Get all rows matching user_id and show them in a new window
        client_ids = self.all_user_id()
        matching_rows = []
        all_cells = []

        for client_id in client_ids:
            if client_id == self.user_id:
                all_cells = self.__get_sheet().findall(str(client_id))

        for cell in all_cells:
            row_data = self.__get_sheet().row_values(cell.row)
            matching_rows.append(row_data)
            print(row_data)

        if matching_rows:
            self.show_history_window(matching_rows)
        else:
            messagebox.showinfo("No History Found", "You have no booking history.")

    def show_history_window(self, rows):
        # Display booking history in a Treeview table
        window = tk.Toplevel()
        window.title("Your Booking History")
        window.geometry("1200x500")

        # Column headers
        headers = [
            "Booking ID", "Client ID", "Client Name", "Pickup Location", "Destination",
            "Vehicle Type", "Driver Name", "Distance (km)", "Fare (₱)", "Booking Type",
            "Pickup Time", "Dropoff Time", "Status", "Last Updated"
        ]

        tree = ttk.Treeview(window, columns=headers, show='headings')
        tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Set column headings
        for header in headers:
            tree.heading(header, text=header)
            tree.column(header, anchor='center', width=120)

        # Insert data rows
        for row in rows:
            # Pad or trim row to match column count
            row_data = row[:len(headers)] + [""] * (len(headers) - len(row))
            tree.insert("", "end", values=row_data)

        # Scrollbars
        vsb = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(window, orient="horizontal", command=tree.xview)
        hsb.pack(side='bottom', fill='x')
        tree.configure(xscrollcommand=hsb.set)

        # Close button
        btn_close = tk.Button(
            window,
            text="Close",
            command=window.destroy,
            bg="#CC5500",
            fg="white",
            font=('Arial', 10, 'bold'),
            padx=10, pady=5
        )
        btn_close.pack(pady=10)