import logging
from typing import Literal
from tkinter import PhotoImage
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

from passguard_appsettings import AppInit
from passguard_styles import PassGuardStyles

from frontend.loginDialog.login_module import LoginDialog
from frontend.passwordPage.password_frame import PasswordFrame
from frontend.settingsPage.settings_page import SettingsFrame
from frontend.infoPage.info_page import InfoFrame
from frontend.tkReusables.snackbar import SnackBar

from backend.devsec.encrypto import Encrypto
from backend.devsec.key_generator import generate_key
from backend.controllers.database_controller import SQLiteController
from backend.databaseManager.sqlite_encrypto import encrypted_database_context
from backend.abstracts.abstract_methods import KeyStorageInterface, PasswordStorageInterface


from sqlite3 import DatabaseError

# EXECUTE: python -m adamsutils.PassGuard.passguard
class App(ttk.Window):  # TODO review login page, seems slow after refectors.
    def __init__(self):
        super().__init__(themename='superhero', iconphoto=None)
        self.iconphoto(True, PhotoImage(file='frontend/icons/PassGuardLogoII.png'))
        self.title("PassGuard")
        self.geometry("800x500")
        self.styles = PassGuardStyles()

        # Application configurations
        self.keystore = None
        self.passtore = None
        self.db_obj = None  # Will hold decrypted database connection
        self.config_settings = {}
        self.config = AppInit()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Initialize configurations, login, and pages
        self._init_configs()
        self.login()


    def log_message(self, message: str, duration:int=3000):
        """Log a message to the Snackbar."""
        self.snackbar.add_message(message, duration)

    def _init_configs(self):
        try:
            if (settings := self.config.retrieve_settings()):
                self.config_settings = settings
            appearance_theme = self.config_settings.get('appearance_theme', 'superhero')
            self._set_appearance_mode(theme_name=appearance_theme, update_tbl=False)
        except Exception as ex:
            logging.error(f"Failed to initialize configurations: {ex}")
            Messagebox.show_error("Configuration Error", "Failed to load application settings.")
            self.destroy()

    def _user_login(self):
        r = self.config_settings.get('r')
        s = self.config_settings.get('s')
        dialog_text = "Register Account" if not r else "Login"
        dialog_title = 'PassGuard: Registration' if not r else 'PassGuard: Login'

        # Ensure that LoginDialog is refactored to use standard Tkinter
        dialog = LoginDialog(self, text=dialog_text, title=dialog_title)
        login_resp = dialog.get_input()
        if not login_resp:
            return None

        username = login_resp.get('username')
        password = login_resp.get('password')

        if not username or not password:
            return None
        return {'u': username, 'p': password, 's': s}

    def _initialize_database(self, user_details):
        try:
            self.db_context = encrypted_database_context(
                db_path="datastore.db",
                encrypto_cls=Encrypto,
                keys=[user_details['u'], user_details['p']],
                salt=user_details.get('s', None)
            )
            self.db_obj = self.db_context.__enter__()

            # Validate the database was decrypted by performing a simple query
            qry = self.db_obj['sql'].query("SELECT 1 FROM sqlite_master LIMIT 1;")

            self.keystore = KeyStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="km"))
            self.passtore = PasswordStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="pm"))
            self._on_database_initialized()
        except DatabaseError:
            raise DatabaseError("Decryption failed: file is not a valid database. Likely due to incorrect credentials.")
        except Exception as ex:
            raise Exception(f"An error occurred during database initialization: {ex}")

    # def _initialize_database(self, user_details):
    #     try:
    #         self.db_context = encrypted_database_context(
    #             db_path="datastore.db",
    #             encrypto_cls=Encrypto,
    #             keys=[user_details['u'], user_details['p']],
    #             salt=user_details.get('s', None)
    #         )
    #         self.db_obj = self.db_context.__enter__()
    #         self.keystore = KeyStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="km"))
    #         self.passtore = PasswordStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="pm"))
    #         self.after(0, self._on_database_initialized)
    #     except Exception as ex:
    #         self.after(0, lambda: self._on_database_error(ex))

    def _on_database_initialized(self):
        if not self.winfo_exists():
            return
        self._create_pages()
        self.create_snackbar()

    def _on_database_error(self, error):
        Messagebox.show_error("Database Error", str(error))
        self.destroy()

    def login(self):
        while True:  # Keep retrying until a successful login or the user cancels
            user_details = self._user_login()
            if not user_details:
                print(f"DESTROYING")
                self.destroy()
                return
            try:
                self._initialize_database(user_details=user_details)
                self.config_settings['r'] = 1
                self.config_settings['s'] = self.db_obj['salt']
                self.config.set_setting(**self.config_settings)
                self.user_details = user_details
                break  # Successful login
            except DatabaseError as ex:
                logging.error(f"Login failed: {ex}")
                Messagebox.show_error(title="Login Failed", message="Incorrect username or password. Please try again.")
            except Exception as ex:
                logging.error(f"Unexpected error during login: {ex}")
                Messagebox.show_error(title="Login Failed", message="An unexpected error occurred. Please try again.")




    # def login(self):
    #     user_details = self._user_login()
    #     if user_details:
    #         self._initialize_database(user_details=user_details)
    #         self.config_settings['r'] = 1
    #         self.config_settings['s'] = self.db_obj['salt']
    #         self.config.set_setting(**self.config_settings)
    #         self.user_details = user_details
    #     else:
    #         self.destroy()
        
    def create_snackbar(self,):
        # Add Snackbar
        self.snackbar = SnackBar(self, pg_styles=self.styles.style) #, bootstyle="info" # {chr(0x00A9)} copyright. # chr(8482) is the trademark symbol. 
        self.snackbar.grid(row=1, column=0, sticky="ew")
        self.log_message(message="Database initialized successfully",duration=1500)
        # self.snackbar.add_message(f"...initializing PassGuard 9000{chr(8482)}", duration=1000)
        self.log_message(f"PassGuard 9000{chr(8482)}")

    def _create_pages(self):
        # Configure grid for the main window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create a Notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # Create frames for each tab
        self.passwords_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.info_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.passwords_tab, text='Passwords')
        self.notebook.add(self.settings_tab, text='Settings')
        self.notebook.add(self.info_tab, text='Info')

        # Configure grid for each tab frame
        self.passwords_tab.columnconfigure(0, weight=1)
        self.passwords_tab.rowconfigure(0, weight=1)
        self.settings_tab.columnconfigure(0, weight=1)
        self.settings_tab.rowconfigure(0, weight=1)
        self.info_tab.columnconfigure(0, weight=1)
        self.info_tab.rowconfigure(0, weight=1)

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)
        self.notebook.select(self.passwords_tab)
    
    def _on_tab_selected(self, event):
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 0 and not hasattr(self, 'password_page'):
            self.init_passwords_page()
        elif selected_tab == 1 and not hasattr(self, 'settings_page'):
            self.init_settings_page()
        elif selected_tab == 2 and not hasattr(self, 'info_page'):
            self.init_info_page()

    def init_info_page(self):
        self.info_page = InfoFrame(
            master=self.info_tab,
            pg_styles=self.styles.style,
            # Any additional parameters if needed
        )
        self.info_page.grid(row=0, column=0, sticky='nsew')

    def init_passwords_page(self):
        self.password_page = PasswordFrame(
            master=self.passwords_tab,
            passtore=self.passtore,
            keystore=self.keystore,
            pg_styles=self.styles.style,
            log_func=self.log_message  # Pass log_message method
        )
        self.password_page.grid(row=0, column=0, sticky='nsew')

    def init_settings_page(self):
        self.settings_page = SettingsFrame(
            master=self.settings_tab,
            parent=self,
            appearance_func=self._set_appearance_mode,
            change_password_func=self.change_master_password,
            pg_styles=self.styles.style,
            log_func=self.log_message  # Pass log_message method
        )
        self.settings_page.grid(row=0, column=0, sticky='nsew')

    def _set_appearance_mode(self, theme_name: str = 'superhero', update_tbl:bool=True):
        # Change the theme
        self.style.theme_use(theme_name)
        self.styles.reapply_styles()
        self.update_idletasks()
        if update_tbl:
            self.config_settings['appearance_theme'] = theme_name
            self.config.set_setting(**self.config_settings)


    # ------------------------------------------------------------------------------------------------------------------------------
    # TODO EXPERIMENTAL CODE BEGIN
    # ------------------------------------------------------------------------------------------------------------------------------
    def change_master_password(self, current_password, new_password):
        # Implement the password change logic here
        try:
            username = self.user_details['u']
            salt = self.config_settings.get('s')

            # Step 1: Verify the current password
            decrypted_data = self.verify_old_credentials(username, current_password, salt)
            if decrypted_data is None:
                logging.error("Current password is incorrect.")
                Messagebox.show_error("Password Error", "Current password is incorrect.")
                return False

            # Step 2: Derive new key
            new_encryptor, new_salt = self.derive_new_key(username, new_password, salt)

            # Step 3: Re-encrypt the database
            success = self.reencrypt_database(decrypted_data, new_encryptor)
            if not success:
                logging.error("Failed to re-encrypt the database with the new password.")
                Messagebox.show_error("Encryption Error", "Failed to re-encrypt the database with the new password.")
                return False

            # Step 4: Update settings
            self.update_settings(username, new_salt)

            # Update the in-memory encryption key and database connection
            self.db_context.__exit__(None, None, None)
            self.db_context = encrypted_database_context(
                db_path="datastore.db",
                encrypto_cls=Encrypto,
                keys=[username, new_password],
                salt=new_salt
            )
            self.db_obj = self.db_context.__enter__()
            # Reinitialize controllers with the new database connection
            self.keystore = KeyStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="km"))
            self.passtore = PasswordStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name='pm'))

            logging.info("Master password changed successfully.")
            return True
        except Exception as ex:
            logging.error(f"An error occurred while changing the password: {ex}")
            Messagebox.show_error("Error", f"An error occurred while changing the password: {ex}")
            return False

    def verify_old_credentials(self, username, password, salt):
        try:
            # Generate the old encryption key
            encryption_key, _ = generate_key(keys=[username, password], salt=salt)
            encryptor = Encrypto(encryption_key)

            # Read the encrypted database
            with open('datastore.db', 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = encryptor.decrypt(encrypted_data)
            return decrypted_data
        except Exception as ex:
            logging.error(f"Failed to verify old credentials: {ex}")
            return None

    def derive_new_key(self, username, new_password, salt):
        encryption_key, new_salt = generate_key(keys=[username, new_password], salt=salt)
        encryptor = Encrypto(encryption_key)
        return encryptor, new_salt

    def reencrypt_database(self, decrypted_data, new_encryptor):
        try:
            # Encrypt the data with the new key
            encrypted_data = new_encryptor.encrypt(decrypted_data)
            # Write the encrypted data back to the database file
            with open('datastore.db', 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as ex:
            logging.error(f"Failed to re-encrypt the database: {ex}")
            return False

    def update_settings(self, username, new_salt):
        self.config_settings['s'] = new_salt
        self.config.set_setting(**self.config_settings)
    # ------------------------------------------------------------------------------------------------------------------------------
    # TODO EXPERIMENTAL CODE END
    # ------------------------------------------------------------------------------------------------------------------------------

    def on_closing(self):
        try:
            if hasattr(self, 'db_obj') and self.db_context:
                # Manually exit the context manager
                self.db_context.__exit__(None, None, None)
                logging.info("Database encrypted and saved successfully.")
        except Exception as ex:
            logging.error(f"Failed to encrypt and save the database: {ex}")
            Messagebox.show_error("Shutdown Error", "Failed to save the encrypted database.")
        finally:
            self.destroy()

if __name__ == '__main__':
    app = App()
    app.mainloop()
