#!/usr/bin/env python3

import tkinter as tk
from tkinter import messagebox, ttk
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class WireTrackingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wire Tracking System")

        # Initialize Google Sheets connection
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open('test').sheet1

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create entry fields
        ttk.Label(main_frame, text="Module ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.module_id = ttk.Entry(main_frame)
        self.module_id.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(main_frame, text="Wire ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.wire_id = ttk.Entry(main_frame)
        self.wire_id.grid(row=1, column=1, padx=5, pady=5)

        # Create buttons
        ttk.Button(main_frame, text="Submit Entry", command=self.add_entry).grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(main_frame, text="View Data", command=self.view_data).grid(row=3, column=0, columnspan=2, pady=5)

        # Create status display
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)

    def add_entry(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            module_id = self.module_id.get()
            wire_id = self.wire_id.get()

            # Validate inputs
            if not module_id or not wire_id:
                messagebox.showerror("Error", "Please fill in all fields")
                return

            # Add row to spreadsheet
            row_data = [timestamp, module_id, wire_id]
            self.sheet.append_row(row_data)

            # Clear entries and show success message
            self.module_id.delete(0, tk.END)
            self.wire_id.delete(0, tk.END)
            self.status_label.config(text=f"Entry added successfully at {timestamp}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to add entry: {str(e)}")

    def view_data(self):
        try:
            # Create new window for data display
            data_window = tk.Toplevel(self.root)
            data_window.title("Wire Tracking Data")

            # Create treeview
            tree = ttk.Treeview(data_window, columns=('Timestamp', 'Module ID', 'Wire ID'), show='headings')

            # Set column headings
            tree.heading('Timestamp', text='Timestamp')
            tree.heading('Module ID', text='Module ID')
            tree.heading('Wire ID', text='Wire ID')

            # Set column widths
            tree.column('Timestamp', width=150)
            tree.column('Module ID', width=100)
            tree.column('Wire ID', width=100)

            # Get and insert data
            data = self.sheet.get_all_values()
            for row in data[1:]:  # Skip header row
                tree.insert('', tk.END, values=row)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(data_window, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            # Pack elements
            tree.grid(row=0, column=0, sticky='nsew')
            scrollbar.grid(row=0, column=1, sticky='ns')

            # Configure grid weights
            data_window.grid_columnconfigure(0, weight=1)
            data_window.grid_rowconfigure(0, weight=1)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WireTrackingGUI(root)
    root.mainloop()
