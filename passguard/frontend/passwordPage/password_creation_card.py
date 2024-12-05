import ttkbootstrap as ttk
from typing import Any, Callable
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip

from passguard.backend.controllers.password_manager import PasswordController
from passguard.frontend.passwordPage.complex_pass_generator import PassGeneratorDialog

class PasswordCreationCard(ttk.Frame):
    def __init__(self, master, pg_styles:ttk.Style, title: str, password_controller: PasswordController, data_reload_func: Callable, show_password_card:Callable, log_func:Callable, field_data: dict):
        """
        Initializes the NewOrUpdatePasswordCard.

        Args:
            master (tk.Widget): The parent widget.
            password_controller (PasswordController): Controller for password operations.
            data_reload_func (Callable): Function to reload password data.
            field_data (dict): Initial field data for the form.
        """
        super().__init__(master)
        self.title_text = title
        self.field_data = field_data
        self.data_reload_func = data_reload_func
        self.password_controller = password_controller
        self.style = pg_styles
        self._temp_val = None
        self.entries = {}
        self.show_password_card = show_password_card
        self.log_func = log_func
        # self.create_form()
        self.DEFAULT_VAL = str(chr(0x25CF) * 15)
        self.FONT_TITLE = ("Helvetica", 16, "bold")
        self.FONT_LABEL = ("Helvetica", 9)
        self.FONT_PLACEHOLDER = ("Helvetica", 8, "italic")
        self.PLACEHOLDER_COLOR = "grey"

        self.form_fields = [ # UPDATE HERE IF YOU NEED TO ADD MORE ENTRIES.. may need a light refactor to include in db.
            ("Username", "username", "MyUsername", False),
            ("Password", "password", self.DEFAULT_VAL, True),
            ("Service", "service", "e.g., Chase Bank, MySpace", False),
            ("Service Type", "servicetype", "e.g., Bills, Social Media", False),
            ("URL", "url", "https://example.com/login", False),
        ]

    """
    ------------------------
        FORM GENERATION / HANDLING LOGIC
    ------------------------
    """
    def create_form(self, update_flag: bool = True):
        # Configure grid weights for the main frame
        self.columnconfigure(1, weight=1)

        # Title Label
        self.create_label(name="title", text=self.title_text.title(), row=0, column=0, columnspan=3, font=self.FONT_TITLE, sticky='n', pady=(10, 5))

        # Divider Line
        self.divider = ttk.Separator(self, orient='horizontal')
        self.divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10)

        # Start from row 2
        current_row = 2
        for label_text, key, placeholder, is_password in self.form_fields:
            self.create_label(name=f"{key}_label", text=f"{label_text}:", row=current_row, column=0, font=self.FONT_LABEL, sticky='w', pady=5)
            entry = self.create_entry(name=f"{key}_entry", placeholder=placeholder, row=current_row, column=1, is_password=is_password)
            self.entries[key] = entry

            # Show Password Switch
            if is_password:
                self.show_password_var = ttk.BooleanVar(value=False)
                self.show_password_switch = ttk.Checkbutton(
                    self,
                    text="Show",
                    variable=self.show_password_var,
                    command=lambda e=entry: self.toggle_password_visibility(e),
                    bootstyle="toolbutton"
                )
                self.show_password_switch.grid(row=current_row, column=2, padx=(5, 10), pady=5, sticky='w')
            current_row += 1

        # Generate Password Frame and Button
        self.generate_pw_frame = self.create_frame(name="generate_pw_frame", row=current_row, column=0, columnspan=3)
        self.generate_pw_frame.columnconfigure(0, weight=1)
        self.generate_pw_frame.columnconfigure(1, weight=5)
        self.generate_pw_frame.columnconfigure(2, weight=5)

        self.create_button(
            name="generate_pw_button", text="Generate Password", command=self.password_generator, parent=self.generate_pw_frame, row=0, column=0, style='Outline.TButton', tooltip_msg="tool to generate a strong password"
        )
        
        current_row += 1
    # updated -> 
        self.buttons_frame = self.create_frame(name="buttons_frame", row=current_row, column=0, columnspan=3)
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(1, weight=1)
        self.create_action_buttons(update_flag=update_flag, row=current_row)


    def create_label(self, name, text, row, column, columnspan=1, font=None, sticky='w', pady=0):
        label = ttk.Label(self, text=text, font=font)
        label.grid(row=row, column=column, columnspan=columnspan, padx=5, pady=pady, sticky=sticky)
        setattr(self, name, label)

    def create_entry(self, name, placeholder, row, column, is_password=False):
        entry = ttk.Entry(self, show='')
        if is_password:
            entry.insert(0, self.DEFAULT_VAL)
        else:
            entry.insert(0, placeholder)
        entry.grid(row=row, column=column, padx=5, pady=5, sticky='ew')
        
        setattr(self, name, entry)

        # Set placeholder style
        entry.configure(foreground=self.PLACEHOLDER_COLOR, font=self.FONT_PLACEHOLDER)
        entry.bind("<FocusIn>", lambda event, e=entry, p=placeholder, ip=is_password: self.clear_placeholder(e, p, ip))
        entry.bind("<FocusOut>", lambda event, e=entry, p=placeholder, ip=is_password: self.add_placeholder(e, p, ip))

        return entry
    """
    HANDLE CLICKING INTO ENTRY EVENTS, FOCUSIN and FOCUSOUT
    """
    def clear_placeholder(self, entry, placeholder, is_password):
        def clear_entry():
            entry.delete(0, "end")
            entry.configure(foreground=self.style.colors.fg, font=self.FONT_LABEL)

        if entry.get() == placeholder:
            if is_password:
                self.show_password_var.set(value=True)
                self.toggle_password_visibility(entry)
                if self._temp_val:
                    return # return before we execute clear_entry(). this allows us to keep set-values. 
            clear_entry()


    def add_placeholder(self, entry, placeholder, is_password):
        if not entry.get():
            if is_password: # TODO resolve this to get the passwords button working properly
                self.show_password_var.set(value=False)
            entry.insert(0, placeholder)
            entry.configure(foreground=self.PLACEHOLDER_COLOR, font=self.FONT_PLACEHOLDER)

    def create_grid_payload(self, row, column, columnspan=None, sticky=None, padx=None, pady=None, **params)->dict:
        # creates a .grid() ready payload. it removes None values so we get the true default from the source. 
        # makes code more reliable, only change defaults when needed
        kwargs = {
            "row": row,
            "column": column,
            "columnspan":columnspan,
            "sticky":sticky,
            "padx":padx,
            "pady":pady,
        }  
        kwargs.update(**params)
        return {key: value for key, value in kwargs.items() if value is not None}


    def create_frame(self, name, row, column, columnspan=None, sticky='ew', pady=(5, 10), **params):
        frame = ttk.Frame(self)
        kwargs = self.create_grid_payload(row=row, column=column, columnspan=columnspan, sticky=sticky, padx=10, pady=pady, **params)
        frame.grid(**kwargs)
        setattr(self, name, frame)
        return frame
    
    def create_button(self, name, text, command, parent, row, column, columnspan=None, style=None, tooltip_msg=None, tooltip_style='info'):
        button = ttk.Button(master=parent, text=text, command=command, style=style)
        
        payload = self.create_grid_payload(row=row, column=column, columnspan=columnspan, sticky='ew', padx=5, pady=5)
        button.grid(**payload)
        
        if tooltip_msg:
            ToolTip(widget=button, text=tooltip_msg, bootstyle=tooltip_style)
        setattr(self, name, button)

    def create_action_buttons(self, update_flag, row):
        # Save Button
        self.create_button(name="save_button", text="Save", command=self.save_password, parent=self.buttons_frame, row=0, column=0, style='Success.TButton')
        if update_flag:
            # Delete Button
            self.create_button(name="delete_button", text="Delete", command=self.delete_password, parent=self.buttons_frame, row=0, column=1, style='Danger.TButton')
            # Cancel Button (next row, spans both columns)
            self.create_button(name="cancel_button", text="Cancel", command=self.close_frame, parent=self.buttons_frame, row=1, column=0, columnspan=2, style='Secondary.TButton')
        else:
            # Cancel Button (same row as Save button)
            self.create_button(name="cancel_button", text="Cancel", command=self.close_frame, parent=self.buttons_frame, row=0, column=1, style='Secondary.TButton')

    def populate_fields(self, field_data):
        for label_text, key, placeholder, is_password in self.form_fields:
            value = field_data.get(key, "")
            entry = self.entries[key]
            entry.delete(0, 'end')

            if value != placeholder:
                entry.configure(foreground=self.style.colors.fg, font=self.FONT_LABEL) # TODO handle default values.
                
            if key == "password":
                entry.config(show='')
                entry.insert(0, self.DEFAULT_VAL)
            else:
                entry.insert(0, value)

    def password_generator(self):
        """
        Opens the PassGeneratorDialog to generate a new password.
        """
        dialog = PassGeneratorDialog(self.winfo_toplevel(), title='PassGuard: Password Generator')
        password_resp = dialog.get_input()
        if password_resp:
            self.log_func("success") # LOG MSG
            self.set_password(password_resp)
            self._temp_val = password_resp
            self.show_password_var.set(value=True)
            self.toggle_password_visibility(self.entries.get('password')) 

    """
    ------------------------
        INPUT VALIDATION
    ------------------------
    """
    """
    ------------------------
        HANDLE SHOW PASSWORD TOGGLE
    ------------------------
    """
    def validate_pw_entry_data(self, data: Any) -> Any:
        """Overwrite this method for specific new or update functionality."""
        raise NotImplementedError("You must overwrite this method for specific new or update functionality.")

    def handle_password_toggle(self, data: Any) -> Any:
        """Overwrite this method for specific new or update functionality."""
        raise NotImplementedError("You must overwrite this method for specific new or update functionality.")

    def validate_entry(self, data:Any) -> Any:
        """Overwrite this method for specific new or update functionality."""
        raise NotImplementedError("You must overwrite this method for specific new or update functionality.")

    def toggle_password_visibility(self, entry:ttk.Entry):
        validated_entry = self.validate_entry(entry.get())
        if not self._temp_val and validated_entry == self.DEFAULT_VAL:
            entry.configure(foreground=self.PLACEHOLDER_COLOR, font=self.FONT_PLACEHOLDER)
        else:
            entry.configure(foreground=self.style.colors.fg, font=self.FONT_LABEL)

        self.set_password(validated_entry)

    def set_password(self, value: Any):
        """Receive value, validates it, and displays accordingly."""
        value = self.handle_password_toggle(data=value)
        entry = self.entries["password"]
        entry.delete(0, "end")
        entry.insert(0, value)

    """
    ------------------------
        PAGE MANAGEMENT LOGIC
    ------------------------
    """
    def close_frame(self, log_flag:bool=True):
        if log_flag:
            self.log_func("cancelled") # LOG MSG
        if (id:=self.field_data.get('id')):
            self.master.after(5, self.show_password_card, id) # after 5ms, self.show_password_card(id=id)
        self.destroy()

    def reload_and_close(self, log_flag:bool=True):
        if self.data_reload_func:
            self.data_reload_func()
        self.close_frame(log_flag=log_flag)

    def get_password(self):
        entry = self.entries['password']
        if entry.get() == self.DEFAULT_VAL:
            return self._temp_val if self._temp_val is not None else self.field_data.get('password')
        else:
            return entry.get()

    def save_password(self):
        data = {key: entry.get() if key.lower() != 'password' else self.get_password() for key, entry in self.entries.items()}
        if not data.get("id"):
            data['id'] = self.field_data.get('id', None)
        response = self.password_controller.upsert_record(**data)
        self.log_func("success") # LOG MSG
        self.reload_and_close(log_flag=False)

        # data = {} # TODO to support the refactor swapping default values.
        # for label, key, default, is_password in self.form_fields:
        #     if is_password:
        #         data[key] = self.get_password() # gets the encrypted password.
        #     else:
        #         entry_value = self.entries.get(key).get() if key in self.entries else '-----'
        #         data[key] = entry_value if entry_value != default else '-----'
        # if not data.get("id"):
        #     data['id'] = self.field_data.get("id", None)

        # response = self.password_controller.upsert_record(**data)
        # self.reload_and_close()

    def delete_password(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        confirm = Messagebox.yesno(
            title="Confirm Delete",
            message=f"Are you sure you want to delete this password?\nService: {data['service']}\nUsername: {data['username']}",
            parent=self
        )
        if confirm.lower()=='yes':
            response = self.password_controller.remove_record(
                id=self.field_data.get('id'),
                username=data["username"],
                service=data["service"],
                servicetype=data["servicetype"],
                section=data["service"],
                field='password'
            )
            self.log_func("success") # LOG MSG
            self.reload_and_close(log_flag=False)
        else:
            self.log_func("cancelled") # LOG MSG


# ----------------------------------------------------------------------------------------
# New Password Card
# ----------------------------------------------------------------------------------------
class NewPasswordCard(PasswordCreationCard):
    def __init__(self, master, pg_styles:ttk.Style, title: str, password_controller: PasswordController, data_reload_func: Callable, show_password_card:Callable, log_func:Callable, field_data: dict):
        super().__init__(master=master, pg_styles=pg_styles, title=title, password_controller=password_controller, data_reload_func=data_reload_func, show_password_card=show_password_card, log_func=log_func, field_data=field_data)
        self.create_form(update_flag=False)

    def validate_pw_entry_data(self, data: Any) -> Any:
        """This is called during the NewPasswordCard flow - but adding it to just return as a safety measure."""
        return data

    def handle_password_toggle(self, data: Any) -> Any:
        """
        Validates the password in the entry box.
        
        since we don't actually mask the real data, instead use '●'x15 
        we needed a way to preserve the users input or the encrypted data.
        this logic helps us toggle the password visible and not, while also ensuring Passguard never stores a decrypted password in a variable or anything.
        """
        if self.show_password_var.get() == True:
            if data != self.DEFAULT_VAL:
                return data
            elif data == self.DEFAULT_VAL and self._temp_val is not None:
                return self._temp_val
            else:
                return ''
        else:
            if data != self.DEFAULT_VAL and data != self._temp_val:
                self._temp_val = data
            return self.DEFAULT_VAL

    def validate_entry(self, data) -> Any:
        """
        Validate Entry ensures the data returned is in right format for handle_password_toggle.
        very similar to handle_password_toggle, but does things just enough differently.

        It was getting way too messy trying to fit this logic into one function. 
        breaking them apart simplified things 10x
        """
        if self.show_password_var.get() == True:
            if data == self.DEFAULT_VAL:
                return self._temp_val if self._temp_val is not None else ''
            else:
                return data
        else:
            if data != self.DEFAULT_VAL:
                self._temp_val = data
                return self.DEFAULT_VAL
            else:
                return self.DEFAULT_VAL


# ----------------------------------------------------------------------------------------
# Update Password Card
# ----------------------------------------------------------------------------------------
class UpdatePasswordCard(PasswordCreationCard):
    """

    """
    def __init__(self, master, pg_styles:ttk.Style, title: str, password_controller: PasswordController, data_reload_func: Callable, show_password_card:Callable, log_func:Callable, field_data: dict):
        super().__init__(master=master, pg_styles=pg_styles, password_controller=password_controller, data_reload_func=data_reload_func, title=title, show_password_card=show_password_card, log_func=log_func, field_data=field_data)
        self.create_form(update_flag=True)
        self.populate_fields(self.field_data)

    def validate_pw_entry_data(self, data: Any) -> Any:
        password_received = True if self.field_data.get('password') is not None else False
        if password_received and data == self.field_data.get("password"):
            return self.password_controller._decrypt_item(data)
        else:
            return data

    def handle_password_toggle(self, data: Any) -> Any:
        if self.show_password_var.get() == True:
            if data != self.DEFAULT_VAL:
                return self.validate_pw_entry_data(data=data)
            elif data == self.DEFAULT_VAL and self._temp_val is not None:
                return self.validate_pw_entry_data(data=self._temp_val)
        else:
            if data != self.DEFAULT_VAL and data != self._temp_val:
                self._temp_val = data
            return self.DEFAULT_VAL

    def validate_entry(self, data) -> Any:
        password_received = True if self.field_data.get('password') is not None else False
        if self.show_password_var.get() == True:
            if data == self.DEFAULT_VAL:
                return self._temp_val if self._temp_val is not None else self.field_data.get('password')
            else:
                return data
        else:
            if data != self.DEFAULT_VAL:
                if password_received:
                    if data != self.password_controller._decrypt_item(self.field_data.get('password')):
                        self._temp_val = data
                    else:
                        self._temp_val = self.field_data.get('password')
                return self.DEFAULT_VAL
            elif data == self.DEFAULT_VAL:
                if password_received:
                    self._temp_val = self.field_data.get('password')
                else:
                    self._temp_val = data
                return self.DEFAULT_VAL
