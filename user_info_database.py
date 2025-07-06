import tkinter as tk
from tkinter import messagebox
import gspread
from google.oauth2.service_account import Credentials
import random

class UserInfoDatabase:
    def __init__(self):
        self.__sheet_id = "13GKmBOKz_XvvAFdGGqSoDRS7UTlvf_YqUNSCdD6hceI"
        self.__scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.__creds = Credentials.from_service_account_file("credentials.json", scopes=self.__scopes)
        self.__client = gspread.authorize(self.__creds)
        self.__sheet = self.__client.open_by_key(self.__sheet_id).sheet1
        
        # Add headers if not present
        expected_headers = ["ID", "Name", "Contact", "Email", "Passcode", "Address"]
        current_headers = self.__sheet.row_values(1)
        if current_headers != expected_headers:
            self.__sheet.update('A1:F1', [expected_headers])

    # As part of OOP, we made the sheet address private
    def __get_sheet(self):
        """Private accessor for the sheet object"""
        return self.__sheet

    # Generate a 4 numbered unique combination to be used for user account id
    def __identification_assignment(self):
        first_num = random.randint(1, 9)
        second_num = random.randint(1, 9)
        third_num = random.randint(1, 9)
        fourth_num = random.randint(1, 9)
        id = str(first_num) + str(second_num) + str(third_num) + str(fourth_num)
        return id

    # Uploads user credentials during sign up
    def upload_user(self, name, contact, email, passcode, address):
        """Public method (unchanged interface)"""
        user_id = self.__identification_assignment()
        row = [user_id, name, contact, email, passcode, address]
        self.__get_sheet().append_row(row, value_input_option='RAW')
        return user_id

    # Examines the whole sheet database and checks if the inputted email matches an account
    def find_user_by_credentials(self, user_id, email, passcode):
        try:
            email = email.strip().lower()
            user_id = str(user_id).strip() 
            records = self.__get_sheet().get_all_records()
            
            for row in records:
                # Check all three credentials match
                if (str(row.get("ID", ""))) == user_id and (row.get("Email", "")).strip().lower() == email and str(row.get("Passcode", "")) == str(passcode):
                    return row
            return None
        except Exception as e:
            print(f"Error finding user: {e}")
            return None