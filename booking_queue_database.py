import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

class BookingDatabase:
    def __init__(self):
        # Spreadsheet details (made private)
        self.__sheet_id = "1i3lWKS-o8VjeGykXbRP27MZS0xniY490DAibQgNMwoE"
        # Google Sheets API setup (made private)
        self.__scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.__creds = Credentials.from_service_account_file('credentials.json', scopes=self.__scopes)
        self.__client = gspread.authorize(self.__creds)
        self.__sheet = self.__client.open_by_key(self.__sheet_id).sheet1
        
        # Initialize headers if sheet is empty
        if not self.__get_sheet().get_all_records():
            self._initialize_headers()

    # Made sheet id private in accordance with OOP
    def __get_sheet(self):
        """Private method to access the sheet with proper encapsulation"""
        return self.__sheet

    # Create column headers in the sheet
    def _initialize_headers(self):
        headers = [
            "Booking ID", "Client ID", "Client Name", "Pickup Location", "Destination", "Vehicle Type",
            "Driver Name", "Distance (km)", "Fare (₱)", "Booking Type",
            "Pickup Time", "Dropoff Time", "Status", "Last Updated"
        ]
        self.__get_sheet().insert_row(headers, 1)

    def add_booking(self, booking_data):
        """Add a new booking to the sheet"""
        try:
            # Prepare data row
            row_data = [
                booking_data["id"],
                booking_data["client_id"],
                booking_data["client_name"],
                booking_data["pickup"],
                booking_data["dropoff"],
                booking_data["vehicle"],
                booking_data["driver"]["name"],
                booking_data["distance"],
                booking_data["fare"],
                booking_data["type"],
                booking_data["pickup_time"],
                booking_data.get("dropoff_time", "ASAP"),
                booking_data["status"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
            
            # Append to sheet
            self.__get_sheet().append_row(row_data)
            return True
        except Exception as e:
            print(f"Error adding booking: {e}")
            return False
        
    # Updates booking status whenever client cancelled
    def update_booking_status(self, booking_id, new_status):
        """Update the status of a booking in the spreadsheet"""
        try:
            # Get all the column headers
            header_row = self.__get_sheet().row_values(1)
            
            # Find which column numbers we need
            status_column_number = header_row.index("Status") + 1 
            last_updated_column_number = header_row.index("Last Updated") + 1
            booking_id_column_number = header_row.index("Booking ID") + 1
            
            # Get all the booking records
            all_bookings = self.__get_sheet().get_all_records()
            
            # Look through each booking to find the right one
            for row_number, booking in enumerate(all_bookings, start=2):  # Start at row 2
                # Check if this is the booking we want to update
                if str(booking["Booking ID"]) == str(booking_id):
                    # Update the status
                    self.__get_sheet().update_cell(row_number, status_column_number, new_status)
                    
                    # Update the last updated time
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.__get_sheet().update_cell(row_number, last_updated_column_number, current_time)
                    
                    # Let the user know it worked
                    return True
                    
            # If we get here, we didn't find the booking
            print(f"Couldn't find booking with ID: {booking_id}")
            return False
            
        except Exception as error:
            print(f"Something went wrong: {error}")
            return False

    # Retrieve all bookings from the sheet
    def get_all_bookings(self):
        
        try:
            return self.__get_sheet().get_all_records()
        except Exception as e:
            print(f"Error retrieving bookings: {e}")
            return []

    # Check if booking exists in sheet
    def get_booking_by_id(self, booking_id):
        try:
            records = self.__get_sheet().get_all_records()
            for record in records:
                if str(record["Booking ID"]) == str(booking_id):
                    return record
            return None
        except Exception as e:
            print(f"Error finding booking: {e}")
            return None

    # Updates the sheet for new input bookings
    def update_booking(self, booking_data):
        """Full booking update"""
        try:
            records = self.__get_sheet().get_all_records()
            for idx, record in enumerate(records, start=2):
                if str(record["Booking ID"]) == str(booking_data["id"]):
                    row_data = [
                        booking_data["id"],
                        booking_data["client_id"], 
                        booking_data["client_name"], 
                        booking_data["pickup"],
                        booking_data["dropoff"],
                        booking_data["vehicle"],
                        booking_data["driver"]["name"],
                        booking_data["distance"],
                        booking_data["fare"],
                        booking_data["type"],
                        booking_data["pickup_time"],
                        booking_data.get("dropoff_time", "ASAP"),
                        booking_data["status"],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    self.__get_sheet().delete_rows(idx)
                    self.__get_sheet().insert_row(row_data, idx)
                    return True
            return False
        except Exception as e:
            print(f"Error updating booking: {e}")
            return False