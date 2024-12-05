#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SpreadsheetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spreadsheet Manager")

        # Initialize Google Sheets connection
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        self.client = gspread.authorize(creds)

        # Open spreadsheet
        self.sheet = self.client.open('test').sheet1

        # Create buttons
        tk.Button(root, text="Add Row", command=self.add_row).pack(pady=5)
        tk.Button(root, text="Clear Sheet", command=self.clear_sheet).pack(pady=5)
        tk.Button(root, text="Read Data", command=self.read_data).pack(pady=5)

        # Create entry field
        self.entry = tk.Entry(root)
        self.entry.pack(pady=5)

    def add_row(self):
        data = self.entry.get()
        try:
            self.sheet.append_row([data])
            messagebox.showinfo("Success", "Data added successfully!")
            self.entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add data: {str(e)}")

    def clear_sheet(self):
        try:
            self.sheet.clear()
            messagebox.showinfo("Success", "Sheet cleared successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear sheet: {str(e)}")

    def read_data(self):
        try:
            data = self.sheet.get_all_values()
            display_window = tk.Toplevel(self.root)
            display_window.title("Sheet Data")

            for row in data:
                tk.Label(display_window, text=' | '.join(row)).pack()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpreadsheetGUI(root)
    root.mainloop()
