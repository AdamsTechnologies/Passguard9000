import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class ChangePasswordPage(ttk.Frame):
    def __init__(self, master, style, change_password_func, settings_manager, snackbar_messenger, pubsub, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.style = style
        self.settings_manager = settings_manager
        self.change_password_func = change_password_func
        self.show_password_var = ttk.BooleanVar(value=False)
        self.pubsub=pubsub
        self.snackbar_messenger = snackbar_messenger
        self.create_widgets()

    def create_widgets(self):
        title_label = ttk.Label(self, text="Change Password", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='n')

        divider = ttk.Separator(self, orient='horizontal')
        divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10)

        password_frame = ttk.Frame(self)
        password_frame.grid(row=2, column=0, columnspan=3, padx=10, sticky='ew')
        password_frame.columnconfigure(1, weight=1)

        current_password_label = ttk.Label(password_frame, text="Current Password:", font=("Helvetica", 12))
        current_password_label.grid(row=0, column=0, sticky='w', pady=5)

        self.current_password_entry = ttk.Entry(password_frame, show=chr(0x25CF))
        self.current_password_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0), pady=5)

        new_password_label = ttk.Label(password_frame, text="New Password:", font=("Helvetica", 12))
        new_password_label.grid(row=1, column=0, sticky='w', pady=5)

        self.new_password_entry = ttk.Entry(password_frame, show=chr(0x25CF))
        self.new_password_entry.grid(row=1, column=1, sticky='ew', padx=(5, 0), pady=5)

        confirm_password_label = ttk.Label(password_frame, text="Confirm New Password:", font=("Helvetica", 12))
        confirm_password_label.grid(row=2, column=0, sticky='w', pady=5)

        self.confirm_password_entry = ttk.Entry(password_frame, show=chr(0x25CF))
        self.confirm_password_entry.grid(row=2, column=1, sticky='ew', padx=(5, 0), pady=5)

        # Buttons and Show Password
        buttons_frame = ttk.Frame(password_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(15, 10), sticky='ew')
        buttons_frame.columnconfigure(0, weight=1)

        save_button = ttk.Button(buttons_frame, text="Save Changes", command=self.attempt_password_change, bootstyle="secondary")
        save_button.grid(row=0, column=0, columnspan=2, sticky='ew', padx=(0,5), pady=10)

        show_password_switch = ttk.Checkbutton(
            buttons_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.show_change_passwords,
            bootstyle="toolbutton"
        )
        show_password_switch.grid(row=0, column=2, sticky='ew', pady=10)

    def show_change_passwords(self):
        if self.show_password_var.get():
            self.current_password_entry.configure(show='')
            self.new_password_entry.configure(show='')
            self.confirm_password_entry.configure(show='')
            # Hide again after 5 seconds
            self.after(5000, self.hide_passwords)
        else:
            self.hide_passwords()

    def hide_passwords(self):
        if self.show_password_var.get():
            self.show_password_var.set(False)
        self.current_password_entry.configure(show=chr(0x25CF))
        self.new_password_entry.configure(show=chr(0x25CF))
        self.confirm_password_entry.configure(show=chr(0x25CF))

    def attempt_password_change(self):
        self.snackbar_messenger("Password change - coming soon!")
        current = self.current_password_entry.get()
        new = self.new_password_entry.get()
        confirm = self.confirm_password_entry.get()
        # ... call self.change_password_func if they match, etc.
