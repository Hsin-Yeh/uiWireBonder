#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

import os
from tkinter import PhotoImage
from PIL import Image, ImageTk

class ModuleTrackingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Module Tracking System")

        # Initialize Google Sheets connection
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open('test').sheet1

        # Get parameters from first row
        self.parameters = self.sheet.row_values(1)[2:]

        # Load or create module params with timestamps
        try:
            with open('module_params.json', 'r') as f:
                self.module_params = json.load(f)
        except FileNotFoundError:
            self.module_params = {}

        # Create main frame with three columns
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Left Column - Module Selection
        self.left_frame = ttk.LabelFrame(self.main_frame, text="Module Selection")
        self.left_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        ttk.Label(self.left_frame, text="Module ID:").pack(pady=5)
        self.module_id_var = tk.StringVar()
        self.module_id_combo = ttk.Combobox(self.left_frame, textvariable=self.module_id_var)
        self.module_id_combo['values'] = list(self.module_params.keys())
        self.module_id_combo.pack(pady=5)
        self.module_id_combo.bind('<<ComboboxSelected>>', self.on_module_select)

        # Add buttons
        ttk.Button(self.left_frame, text="Add New Module",
                  command=self.show_add_module_dialog).pack(pady=5)
        ttk.Button(self.left_frame, text="Clear Module",
                  command=self.clear_module).pack(pady=5)
        ttk.Button(self.left_frame, text="Submit All to Sheet",
                  command=self.submit_all_to_sheet).pack(pady=5)
        ttk.Button(self.left_frame, text="Read All from Sheet",
                   command=self.read_all_from_sheet).pack(pady=5)

        # Add TIDC logo at the bottom of left_frame
        try:
            logo_image = Image.open('tidc_icon.png')
            logo_image = logo_image.resize((150, 50), Image.Resampling.LANCZOS)  # Adjust size as needed
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(self.left_frame, image=self.logo_photo)
            logo_label.pack(side='bottom', pady=10)
        except Exception as e:
            print(f"Could not load logo: {e}")

        # Middle Column - Parameter Entry
        self.middle_frame = ttk.LabelFrame(self.main_frame, text="Module Parameters")
        self.middle_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Parameter Frame
        self.param_frame = ttk.Frame(self.middle_frame)
        self.param_frame.pack(fill='both', expand=True, pady=5)

        # Always visible Save Parameters button in middle frame
        self.save_button = ttk.Button(self.middle_frame, text="Save Parameters",
                                    command=self.save_parameters)
        self.save_button.pack(side='bottom', pady=10)
        self.save_button.config(state='disabled')  # Initially disabled

        # Right Column - Context Information
        self.right_frame = ttk.LabelFrame(self.main_frame, text="Module Information")
        self.right_frame.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        self.created_label = ttk.Label(self.right_frame, text="Created: ")
        self.created_label.pack(pady=5)
        self.modified_label = ttk.Label(self.right_frame, text="Modified: ")
        self.modified_label.pack(pady=5)

        # Add History Section
        ttk.Label(self.right_frame, text="Modification History:").pack(pady=(10,0))
        self.history_listbox = ttk.Treeview(self.right_frame, height=6,
                                          columns=('Timestamp',), show='headings')
        self.history_listbox.heading('Timestamp', text='Timestamp')
        self.history_listbox.pack(pady=5, fill='x')
        self.history_listbox.bind('<<TreeviewSelect>>', self.show_history_details)

        # Status Label
        self.status_label = ttk.Label(self.main_frame, text="")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=5)

        self.param_entries = {}

    def update_timestamps(self):
        module_id = self.module_id_var.get()
        if module_id in self.module_params:
            self.created_label.config(
                text=f"Created: {self.module_params[module_id]['created']}")
            self.modified_label.config(
                text=f"Modified: {self.module_params[module_id]['modified']}")
    def show_add_module_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Module")
        dialog.geometry("400x500")  # Larger window for parameters

        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog window
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()/2 - 200,
            self.root.winfo_rooty() + self.root.winfo_height()/2 - 250))

        # Create main frame with scrollbar
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Module ID entry
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(id_frame, text="Module ID:").pack(side='left')
        module_id_entry = ttk.Entry(id_frame)
        module_id_entry.pack(side='left', padx=(10, 0), expand=True, fill='x')

        # Parameters frame
        param_frame = ttk.LabelFrame(main_frame, text="Initialize Parameters")
        param_frame.pack(fill='both', expand=True)

        # Create dictionary to store parameter entries
        param_entries = {}

        # Create entry fields for each parameter
        for i, param_name in enumerate(self.parameters):
            param_row = ttk.Frame(param_frame)
            param_row.pack(fill='x', pady=2)
            ttk.Label(param_row, text=f"{param_name}:").pack(side='left', padx=5)
            entry = ttk.Entry(param_row)
            entry.pack(side='left', padx=5, expand=True, fill='x')
            param_entries[param_name] = entry

        def add_module():
            module_id = module_id_entry.get().strip()
            if not module_id:
                messagebox.showerror("Error", "Please enter a Module ID", parent=dialog)
                return

            if module_id in self.module_params:
                messagebox.showerror("Error", "Module ID already exists", parent=dialog)
                return

            # Initialize module without timestamps
            self.module_params[module_id] = {
                'parameters': [entry.get() for entry in param_entries.values()],
                'created': '',  # Will be set on first save
                'modified': '',
                'history': []
            }

            # Update UI
            self.update_module_list()
            dialog.destroy()

            # Set the new module as selected
            self.module_id_combo.set(module_id)
            self.on_module_select(None)
            self.save_button.config(state='normal')

            self.status_label.config(text=f"Module {module_id} initialized. Please save to confirm creation.")

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        ttk.Button(button_frame, text="Initialize",
                  command=add_module).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel",
                  command=dialog.destroy).pack(side='right', padx=5)

    def on_module_select(self, event):
        self.clear_param_frame()
        module_id = self.module_id_var.get()
        if module_id in self.module_params:
            # Display timestamps
            created_time = self.module_params[module_id]['created']
            modified_time = self.module_params[module_id]['modified']

            self.created_label.config(
                text=f"Created: {created_time if created_time else 'Not saved'}")
            self.modified_label.config(
                text=f"Modified: {modified_time if modified_time else 'Not saved'}")

            # Display parameters
            for i, (param_name, param_value) in enumerate(
                zip(self.parameters, self.module_params[module_id]['parameters'])):
                ttk.Label(self.param_frame, text=f"{param_name}:").grid(
                    row=i, column=0, pady=2, padx=5, sticky='e')
                entry = ttk.Entry(self.param_frame)
                entry.insert(0, param_value)
                entry.grid(row=i, column=1, pady=2, padx=5, sticky='w')
                self.param_entries[param_name] = entry

            # Enable save button
            self.save_button.config(state='normal')
        else:
            # Disable save button if no module selected
            self.save_button.config(state='disabled')

        self.update_history_display()

    def save_parameters(self):
        module_id = self.module_id_var.get()
        if module_id:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # If first save, set created timestamp
            if not self.module_params[module_id]['created']:
                self.module_params[module_id]['created'] = current_time

            # Get current parameters
            new_parameters = [entry.get() for entry in self.param_entries.values()]

            # Add to history
            self.module_params[module_id]['history'].append({
                'timestamp': current_time,
                'parameters': new_parameters
            })

            # Update current parameters and modified timestamp
            self.module_params[module_id]['parameters'] = new_parameters
            self.module_params[module_id]['modified'] = current_time

            # Save to file and update display
            with open('module_params.json', 'w') as f:
                json.dump(self.module_params, f)

            self.update_history_display()
            self.update_timestamps()
            self.status_label.config(text="Parameters saved successfully")

    def submit_all_to_sheet(self):
        try:
            # Clear the sheet except header
            self.sheet.resize(rows=1)

            # Prepare data for sheet - include all history for each module
            data = []
            for module_id, module_data in self.module_params.items():
                # Add current state
                current_row = [
                    module_data['modified'],
                    module_id
                ] + module_data['parameters']
                data.append(current_row)

                # Add historical entries
                for history_entry in module_data['history']:
                    history_row = [
                        history_entry['timestamp'],
                        module_id
                    ] + history_entry['parameters']
                    data.append(history_row)

            # Sort all data by timestamp
            data.sort(key=lambda x: x[0], reverse=True)

            # Append all data at once
            if data:
                self.sheet.append_rows(data)
                self.status_label.config(text="All data submitted to sheet successfully")
            else:
                self.status_label.config(text="No data to submit")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit to sheet: {str(e)}")

    def clear_module(self):
        module_id = self.module_id_var.get()
        if not module_id:
            messagebox.showerror("Error", "Please select a Module ID first")
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                     f"Are you sure you want to delete Module ID: {module_id}?")
        if confirm:
            try:
                del self.module_params[module_id]
                with open('module_params.json', 'w') as f:
                    json.dump(self.module_params, f)

                self.module_id_combo.set('')
                self.update_module_list()
                self.clear_param_frame()
                self.created_label.config(text="Created: ")
                self.modified_label.config(text="Modified: ")
                self.save_button.config(state='disabled')
                self.update_history_display()
                self.status_label.config(text=f"Module {module_id} deleted successfully")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete module: {str(e)}")

    def clear_param_frame(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        self.param_entries.clear()

    def update_module_list(self):
        self.module_id_combo['values'] = list(self.module_params.keys())

    def update_history_display(self):
        module_id = self.module_id_var.get()
        # Clear current history display
        for item in self.history_listbox.get_children():
            self.history_listbox.delete(item)

        if module_id and 'history' in self.module_params[module_id]:
            for entry in reversed(self.module_params[module_id]['history']):
                self.history_listbox.insert('', 'end', values=(entry['timestamp'],))

    def show_history_details(self, event):
        selection = self.history_listbox.selection()
        if not selection:
            return

        module_id = self.module_id_var.get()
        selected_item = self.history_listbox.item(selection[0])
        selected_timestamp = selected_item['values'][0]

        # Find matching history entry
        history_entry = next(
            (entry for entry in self.module_params[module_id]['history']
             if entry['timestamp'] == selected_timestamp), None)

        if history_entry:
            # Create popup window with historical parameters
            dialog = tk.Toplevel(self.root)
            dialog.title(f"History - {selected_timestamp}")
            dialog.geometry("300x400")

            # Make dialog modal
            dialog.transient(self.root)
            dialog.grab_set()

            # Display historical parameters
            frame = ttk.Frame(dialog, padding="10")
            frame.pack(fill='both', expand=True)

            ttk.Label(frame, text="Historical Parameters:").pack(pady=(0,10))

            for param_name, param_value in zip(self.parameters, history_entry['parameters']):
                param_frame = ttk.Frame(frame)
                param_frame.pack(fill='x', pady=2)
                ttk.Label(param_frame, text=f"{param_name}:").pack(side='left', padx=5)
                ttk.Label(param_frame, text=param_value).pack(side='left', padx=5)

            ttk.Button(frame, text="Close",
                      command=dialog.destroy).pack(side='bottom', pady=10)

    def read_all_from_sheet(self):
        try:
            # Get all data from sheet
            sheet_data = self.sheet.get_all_values()
            if len(sheet_data) <= 1:  # Only header row exists
                messagebox.showinfo("Info", "No data found in sheet")
                return

            # Skip header row
            for row in sheet_data[1:]:
                timestamp = row[0]
                module_id = row[1]
                parameters = row[2:]

                # Create new module if it doesn't exist
                if module_id not in self.module_params:
                    self.module_params[module_id] = {
                        'parameters': parameters,
                        'created': timestamp,
                        'modified': timestamp,
                        'history': []
                    }
                # Update existing module
                else:
                    # Add to history if parameters are different
                    if parameters != self.module_params[module_id]['parameters']:
                        self.module_params[module_id]['history'].append({
                            'timestamp': timestamp,
                            'parameters': parameters
                        })
                        self.module_params[module_id]['parameters'] = parameters
                        self.module_params[module_id]['modified'] = timestamp

            # Save updated data to JSON
            with open('module_params.json', 'w') as f:
                json.dump(self.module_params, f)

            # Update UI
            self.update_module_list()
            self.update_history_display()
            self.status_label.config(text="Data successfully loaded from sheet")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read from sheet: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModuleTrackingGUI(root)
    root.mainloop()
