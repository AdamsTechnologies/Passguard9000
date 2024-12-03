import time
import tkinter as tk
import ttkbootstrap as ttk
from typing import Optional, Dict
from ttkbootstrap.constants import *

class LoginDialog(tk.Toplevel):
    def __init__(self, parent, title: str = "Login", text: str = "Please enter your credentials"):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("350x200")
        self.style = ttk.Style()
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self._user_input: Optional[str] = None
        self._pass_input: Optional[str] = None

        self.username_error = False
        self.password_error = False

        self._create_widgets(text)
        self._center_window()

    def _create_widgets(self, text):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        self.label = ttk.Label(self, text=text, wraplength=300, font=('Helvetica', 12))
        self.label.grid(row=0, column=0, columnspan=2, pady=(20, 10), padx=20, sticky='n')

        self.username_entry = ttk.Entry(self, foreground='grey')
        self.username_placeholder = "Username"
        self.username_entry.insert(0, self.username_placeholder)
        self.username_entry.bind("<FocusIn>", self._on_username_focus)
        self.username_entry.bind("<FocusOut>", self._add_username_placeholder)
        self.username_entry.grid(row=1, column=0, columnspan=2, pady=5, padx=20, sticky='ew')

        self.password_entry = ttk.Entry(self, show='', foreground='grey')
        self.password_placeholder = "Password"
        self.password_entry.insert(0, self.password_placeholder)
        self.password_entry.bind("<FocusIn>", self._on_password_focus)
        self.password_entry.bind("<FocusOut>", self._add_password_placeholder)
        self.password_entry.grid(row=2, column=0, columnspan=2, pady=5, padx=20, sticky='ew')

        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.ok_button = ttk.Button(self.button_frame, text='OK', command=self._ok_event)
        self.ok_button.pack(side='left', padx=5)

        self.cancel_button = ttk.Button(self.button_frame, text='Cancel', command=self._cancel_event)
        self.cancel_button.pack(side='left', padx=5)

        self.password_entry.bind("<Return>", self._ok_event)

    def _center_window(self):
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        width = self.winfo_width()
        height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.geometry(f'{width}x{height}+{x}+{y}')

    def _on_username_focus(self, event):
        if self.username_entry.get() in [self.username_placeholder, "*Please enter a username"]:
            self.username_entry.delete(0, tk.END)
            self.username_entry.config(foreground=self.style.colors.fg)
        self.username_error = False

    def _add_username_placeholder(self, event):
        if not self.username_entry.get():
            self.username_entry.insert(0, self.username_placeholder)
            self.username_entry.config(foreground=self.style.colors.secondary)

    def _on_password_focus(self, event):
        if self.password_entry.get() in [self.password_placeholder, "*Please enter a password"]:
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(show=chr(0x25CF), foreground=self.style.colors.fg)
        self.password_error = False

    def _add_password_placeholder(self, event):
        if not self.password_entry.get():
            self.password_entry.config(show='', foreground=self.style.colors.secondary)
            self.password_entry.insert(0, self.password_placeholder)

    def _ok_event(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == self.username_placeholder or not username:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, "*Please enter a username")
            self.username_entry.config(foreground=self.style.colors.danger)
            self.username_error = True
            return
        if password == self.password_placeholder or not password:
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, "*Please enter a password")
            self.password_entry.config(foreground=self.style.colors.danger, show="")
            self.password_error = True
            return

        self._user_input = username
        self._pass_input = password
        self.destroy()

    def _cancel_event(self):
        self._user_input = None
        self._pass_input = None
        self.destroy()

    def get_input(self) -> Dict[str, Optional[str]]:
        self.wait_window()
        input_dict = {'username': self._user_input, 'password': self._pass_input}
        return input_dict
