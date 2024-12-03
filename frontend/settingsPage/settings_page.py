import ttkbootstrap as ttk
from typing import Callable
from ttkbootstrap.constants import *

class SettingsFrame(ttk.Frame):
    def __init__(self, master, pg_styles:ttk.Style, parent, appearance_func: Callable, change_password_func: Callable, log_func:Callable):
        super().__init__(master)
        self.master = master
        self.parent = parent
        self.appearance_func = appearance_func
        self.change_password_func = change_password_func
        self.style = pg_styles
        self.log_func = log_func
        self.available_themes = self.style.theme_names()

        self.nav_items = { 
            # TODO if needing to add more items to the Settings page, do so here. 
            # create a new func that will load the page with your widgets. 
            # Key = left nav button name, Value = function that loads the right frame.
            "Appearance":self.show_appearance_settings, 
            "Change Password":self.show_change_password,
            } 
        self.nav_buttons = {}
        self.selected = None
        
        self.rowconfigure(0, weight=1)  # Allow vertical expansion
        self.columnconfigure(0, weight=1)  # Left navigation frame
        self.columnconfigure(1, weight=3)  # Content frame

        self.navigation_frame = ttk.Frame(self)
        self.navigation_frame.grid(row=0, column=0, sticky='nsew')
        self.navigation_frame.columnconfigure(0, weight=1)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.columnconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        self.navigation_label = ttk.Label(
            self.navigation_frame,
            text="Settings",
            font=('Helvetica', 16, 'bold')
        )
        self.navigation_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nw')

        self.divider = ttk.Separator(self.navigation_frame, orient='horizontal')
        self.divider.grid(row=1, column=0, sticky='ew', padx=10)

        for index, item in enumerate(self.nav_items.keys()):
            button = ttk.Button(
                self.navigation_frame,
                text=item,
                command=lambda value=item: self.select_navigation_item(value),
                bootstyle="LEFTNAV.PassGuardLeftNav.TButton"
            )
            button.grid(row=index + 2, column=0, padx=10, sticky='ew')
            self.nav_buttons[item] = button
            button.configure(style="LEFTNAV.PassGuardLeftNav.TButton")

        # Initially select the first navigation item
        self.select_navigation_item(list(self.nav_items.keys())[0])

    def select_navigation_item(self, value):
        if self.selected != value:
            previous_btn = self.nav_buttons.get(self.selected, None)
            if value in self.nav_buttons and (new_btn:=self.nav_buttons.get(value, False)):
                new_btn.configure(style='LEFTNAV.Selected.TButton')
            if previous_btn:
                previous_btn.configure(style='LEFTNAV.PassGuardLeftNav.TButton')
            self.selected = value

            # execute the function.
            self.nav_items.get(value)()

    def show_appearance_settings(self):
        # self.log_func("opening appearance settings page") # LOG MSG
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.content_frame, text="Appearance", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='n')

        divider = ttk.Separator(self.content_frame, orient='horizontal')
        divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10) 

        appearance_frame = ttk.Frame(self.content_frame)
        appearance_frame.grid(row=2, column=0, columnspan=3, padx=10, sticky='ew')
        appearance_frame.columnconfigure(1, weight=2)
        appearance_frame.columnconfigure(1, weight=1)
        appearance_frame.columnconfigure(1, weight=6)
        appearance_mode_label = ttk.Label(
            appearance_frame,#self.content_frame,
            text="Appearance Mode:",
            font=("Helvetica", 12)
        )
        appearance_mode_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.appearance_mode_var = ttk.StringVar(value=self.style.theme_use())
        appearance_mode_menu = ttk.OptionMenu(
            appearance_frame,#self.content_frame,
            self.appearance_mode_var,
            self.appearance_mode_var.get(),
            *self.available_themes,
            command=self.change_appearance_mode_event
        )
        appearance_mode_menu.grid(row=0, column=1, pady=5, sticky="w")

    
    def show_change_password(self):
        # self.log_func("opening master password change page") # LOG MSG
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        title_label = ttk.Label(self.content_frame, text="Change Password: coming soon.", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='n')

        divider = ttk.Separator(self.content_frame, orient='horizontal')
        divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10)

        password_frame = ttk.Frame(self.content_frame)
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

        buttons_frame = ttk.Frame(password_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(15, 10), sticky='ew')
        buttons_frame.columnconfigure(0, weight=1)

        save_button = ttk.Button(
            buttons_frame,
            text="Save Changes",
            command=self.attempt_password_change,
            bootstyle="secondary"
        )
        save_button.grid(row=0, column=0, columnspan=2, sticky='ew', padx=(0,5), pady=10)

        self.show_password_var = ttk.BooleanVar(value=False)
        show_password_switch = ttk.Checkbutton(
            buttons_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.show_change_passwords,
            bootstyle="toolbutton"
        )
        
        show_password_switch.grid(row=0, column=2, sticky='ew', pady=10)
        # TODO Add a show button to show the password, bonus points if it lasts 10 seconds then hides again.

    def show_change_passwords(self,):
        if self.show_password_var.get():
            self.current_password_entry.configure(show='')
            self.new_password_entry.configure(show='')
            self.confirm_password_entry.configure(show='')
            
            # Schedule a check after 5 seconds
            self.content_frame.after(5000, self.hide_passwords)
        else:
            self.current_password_entry.configure(show=chr(0x25CF))
            self.new_password_entry.configure(show=chr(0x25CF))
            self.confirm_password_entry.configure(show=chr(0x25CF))
    
    def hide_passwords(self):
        if self.show_password_var.get():
            self.show_password_var.set(False)  # Update the variable
            self.current_password_entry.configure(show=chr(0x25CF))
            self.new_password_entry.configure(show=chr(0x25CF))
            self.confirm_password_entry.configure(show=chr(0x25CF))

    def attempt_password_change(self):
        self.log_func("coming soon") # LOG MSG
        # self.log_func("updating master password") # LOG MSG
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        # TODO
        # confirm = Messagebox.yesno( 
        #     title="Confirm Master Password Change",
        #     message=f"Are you sure you want to change you login password?",
        #     parent=self
        # )
        # if confirm.lower() == 'yes':
        #     if new_password != confirm_password:
        #         Messagebox.show_error("Error", "New passwords do not match.")
        #         return

        #     success = self.change_password_func(current_password, new_password)
        #     if success:
        #         Messagebox.show_info("Success", "Password changed successfully.")
        #     else:
        #         Messagebox.show_error("Error", "Failed to change password.")

    def change_appearance_mode_event(self, value):
        self.log_func(f"update: theme {value}") # LOG MSG
        self.appearance_func(value)