import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Callable

from passguard.backend.devsec.encrypto import Encrypto
from passguard.frontend.passwordPage.password_list import PasswordList
from passguard.frontend.passwordPage.password_card import PasswordCard
from passguard.backend.controllers.password_manager import PasswordController
from passguard.backend.abstracts.abstract_methods import KeyStorageInterface, PasswordStorageInterface
from passguard.frontend.passwordPage.password_creation_card import NewPasswordCard, UpdatePasswordCard


class PasswordFrame(ttk.Frame):
    """
    PASSWORDFRAME FEATURES:
        * double clicking a button in the passwordlist will copy the password to clipboard. *
        ** make password list case senstive, allow a setting to make it title case **
    LEGEND:
        * - low priority.
        ** - medium priority.
        *** - high priority.
    """
    def __init__(self, master, pg_styles:ttk.Style, passtore: PasswordStorageInterface, log_func:Callable, keystore: KeyStorageInterface=None, key=None):
        super().__init__(master)
        self.master = master
        self.password_controller = PasswordController(encrypto=Encrypto, keystore=keystore, passtore=passtore, key=key)
        self.items_mapping = {}
        self.style = pg_styles
        self.password_card = None
        self._default_ = '-----' # TODO handle a default instead of the default hints...
        self.log_func = log_func
        self.create_widgets()
        self.load_passwords()

    def create_widgets(self):
        self.rowconfigure(0, weight=1)

        # Adjust column weights for 33% (1) and 66% (2) split
        self.columnconfigure(0, weight=1, uniform='col')  # 33%
        self.columnconfigure(1, weight=2, uniform='col')  # 66%

        # Left Frame for Password List
        self.left_frame = ttk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='nsew')
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(1, weight=1)

        # Right Frame for Details
        self.right_frame = ttk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky='nsew')
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        # Add Password Button
        self.add_password_button = ttk.Button(
            self.left_frame,
            text="+ Add Password",
            command=self.generate_new_password_card,
            style="Outline.TButton"
        )
        self.add_password_button.grid(row=0, column=0, pady=5, sticky='ew', padx=5)

        # Password List
        self.password_list_frame = PasswordList(
            master=self.left_frame,
            pg_styles=self.style,
            log_func=self.log_func,
            values=[],
            items_mapping=self.items_mapping,
            on_select=self.show_password_card
        )
        self.password_list_frame.grid(row=1, column=0, sticky='nsew')

    def load_passwords(self):
        records = self.password_controller.get_all_records(decrypt_fields=[])
        if records:
            self.items_mapping = {record['id']: record for record in records}
            self.services_list = [f"{record.get('service').title()} ({record['username']})" for record in records]
        else:
            self.items_mapping = {}
            self.services_list = []

        self.password_list_frame.update_list(items_mapping=self.items_mapping)

    def generate_update_password_card(self, **params):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.log_func(f"editing") # LOG MSG
        field_data = dict(id=params.get('id'),
                          username=params.get('username'),
                          password=params.get('password'),
                          service=params.get('service'),
                          servicetype=params.get('servicetype'),
                          url=params.get('url', ''))

        update_password_card = UpdatePasswordCard(
            master=self.right_frame,
            pg_styles=self.style,
            title=params.get('title', "Update Password"),
            password_controller=self.password_controller,
            data_reload_func=self.load_passwords,
            show_password_card=self.show_password_card,
            log_func=self.log_func,
            field_data=field_data
        )
        update_password_card.grid(row=0, column=0, sticky='nsew')

    def generate_new_password_card(self, **params):
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.log_func("create new") # LOG MSG
        new_password_card = NewPasswordCard(
            master=self.right_frame,
            pg_styles=self.style,
            password_controller=self.password_controller,
            data_reload_func=self.load_passwords,
            title=params.get('title', "New Password"),
            show_password_card=self.show_password_card,
            log_func=self.log_func,
            field_data={}
        )
        new_password_card.grid(row=0, column=0, sticky='nsew')

    def show_password_card(self, id: str):
        if id in self.items_mapping:
            data = self.items_mapping[id]
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            self.password_card = PasswordCard(
                master=self.right_frame,
                parent=self,
                pg_styles=self.style,
                password_controller=self.password_controller,
                on_select=self.generate_update_password_card,
                log_func=self.log_func,
                id=data['id'],
                username=data['username'],
                password=data['password'],
                service=data['service'],
                servicetype=data['servicetype'],
                url=data.get('url', '')
            )
            self.password_card.grid(row=0, column=0, sticky='nsew')