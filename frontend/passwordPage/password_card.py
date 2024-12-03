import tkinter as tk
import ttkbootstrap as ttk
from typing import Callable
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

from backend.controllers.password_manager import PasswordController

class PasswordCard(ttk.Frame):
    def __init__(self, master, parent, pg_styles:ttk.Style, password_controller: PasswordController, on_select: Callable, log_func:Callable, id: str, username: str, password: str, service: str, servicetype: str, url: str, **params):
        super().__init__(master)
        self.parent = parent
        self.password_controller = password_controller
        self.on_select = on_select
        self.default_val = str(chr(0x25CF) * 15)
        self.style = pg_styles
        self.log_func=log_func
        
        self.id = id
        self.username = username
        self.password = password
        self.service = service
        self.servicetype = servicetype
        self.url = url

        self.params = params
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Title Label
        self.title = ttk.Label(self, text=str(service).title(), font=("Helvetica", 16, "bold"))
        self.title.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='n')

        # Divider Line
        self.divider = ttk.Separator(self, orient='horizontal')
        self.divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10)

        # Username Frame
        self.username_frame = ttk.Frame(self)
        self.username_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.username_frame.columnconfigure(1, weight=1)

        # Username Label
        self.username_label = ttk.Label(self.username_frame, text="Username:", font=("Helvetica", 12))
        self.username_label.grid(row=0, column=0, sticky='w')
        self.username_label.bind("<Button-1>", self.copy_username)

        # Username Entry
        self.username_entry = ttk.Entry(self.username_frame) # TODO copy pw on click
        self.username_entry.insert(0, username)
        self.username_entry.config(state='readonly')
        self.username_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        self.username_entry.bind("<Button-1>", self.copy_username)
        
        # Copy Username Button
        self.copy_username_button = ttk.Button(
            self.username_frame,
            text="Copy",
            command=self.copy_username,
            bootstyle="toolbutton"
        )
        self.copy_username_button.grid(row=0, column=2, padx=(5, 0))

        # Password Frame
        self.password_frame = ttk.Frame(self)
        self.password_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky='ew')
        self.password_frame.columnconfigure(1, weight=1)

        # Password Label
        self.password_label = ttk.Label(self.password_frame, text="Password:", font=("Helvetica", 12))
        self.password_label.grid(row=0, column=0, sticky='w')
        self.password_label.bind("<Button-1>", self.copy_password)

        # Password Entry
        self.password_entry = ttk.Entry(self.password_frame, show='') # TODO copy pw on click
        self.password_entry.insert(0, self.default_val)
        self.password_entry.config(state='readonly')
        self.password_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        self.password_entry.bind("<Button-1>", self.copy_password)

        # Show Password Checkbutton
        self.show_password_var = ttk.BooleanVar(value=False)
        self.show_password_switch = ttk.Checkbutton(
            self.password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password,
            bootstyle="toolbutton"
        )
        self.show_password_switch.grid(row=0, column=2, padx=(5, 0))

        # Buttons Frame
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=(15, 10), sticky='ew')

        # Configure columns in buttons_frame
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)

        # Update Button
        self.update_button = ttk.Button(
            self.buttons_frame,
            text="Edit",
            command=self.update_password,
            bootstyle=PRIMARY
        )
        self.update_button.grid(row=0, column=0, sticky='ew', padx=(0, 5), pady=5)
        
        # Copy Password Button
        self.copy_button = ttk.Button(
            self.buttons_frame,
            text="Copy", # TODO
            command=self.copy_password,
            bootstyle=SUCCESS
        )
        self.copy_button.grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=5)
        ToolTip(widget=self.copy_button, text="copies the password", bootstyle='info')

    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show='')
            self.password_entry.config(state='normal')
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, self.password_controller._decrypt_item(self.password))
            self.password_entry.config(state='readonly')
            self.password_frame.after(2500, self.hide_passwords) # re-hide passwords 2.5 seconds after showing.
        else:
            self.password_entry.config(show='')
            self.password_entry.config(state='normal')
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, self.default_val)
            self.password_entry.config(state='readonly')

    def hide_passwords(self):
        if self.show_password_var.get():
            self.show_password_var.set(False) # Update the variable
            self.password_entry.config(show='')
            self.password_entry.config(state='normal')
            self.password_entry.delete(0, 'end')
            self.password_entry.insert(0, self.default_val)
            self.password_entry.config(state='readonly')


    def copy_username(self, event=None):
        self.clipboard_clear()
        self.clipboard_append(self.username)
        self.update()
        self.log_func("copied") # LOG MSG

    def copy_password(self, event=None):
        # TODO We'll implement some logging in a log box.
        self.clipboard_clear()
        self.clipboard_append(self.password_controller._decrypt_item(self.password))
        self.update()
        self.log_func("copied") # LOG MSG

    def update_password(self):
        if self.on_select:
            # self.log_func("opening account-update page") # LOG MSG
            self.on_select(
                title="Update Password",
                id=self.id,
                username=self.username,
                password=self.password,
                service=self.service,
                servicetype=self.servicetype,
                url=self.url,
                **self.params
            )

    def reload_password_card(self):
        """Redisplays the password card after edit or cancel."""
        self.parent.show_password_card(self.id)

    def close_update_window(self):
        """Closes the update window and reloads the password card."""
        self.parent.after(100, self.reload_password_card)