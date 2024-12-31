import os
import time
import logging
import tempfile
import ttkbootstrap as ttk
from tkinter import PhotoImage
from sqlite3 import DatabaseError
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from passguard.resource_path import resource_path
from passguard.backend.devsec.encrypto import Encrypto
from passguard.passguard_styles import PassGuardStyles
from passguard.app_settings_manager import SettingsManager
from passguard.frontend.infoPage.info_page import InfoFrame
from passguard.frontend.tkReusables.snackbar import SnackBar
from passguard.backend.pubSub.publish_subscribe import PubSub
from passguard.backend.devsec.key_generator import generate_key
from passguard.frontend.loginDialog.login_dialog import LoginDialog
from passguard.frontend.settingsPage.settings_page import SettingsFrame
from passguard.frontend.passwordPage.password_frame import PasswordFrame
from passguard.backend.controllers.database_controller import SQLiteController
from passguard.backend.databaseManager.sqlite_encrypto import encrypted_database_context
from passguard.backend.abstracts.abstract_methods import KeyStorageInterface, PasswordStorageInterface


# ------------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------

class App(ttk.Window):  
    # TODO FIX LAYOUT BUG IN INFO_PAGE. Can just mirror settings page.
    # fyi reminder: latest works were total refactoring of settings page and how app settings are managed.
    def __init__(self):
        super().__init__(themename='superhero', iconphoto=None)
        self.iconphoto(True, PhotoImage(file='passguard/frontend/icons/PassGuardLogo.png'))#self.iconphoto(True, PhotoImage(resource_path('passguard/frontend/icons/PassGuardLogo.png'))) # self.iconphoto(True, PhotoImage(file='passguard/frontend/icons/PassGuardLogo.png'))  switch when testing locally...
        self.title("PassGuard9000")
        self.geometry("800x500")

        # Styles
        self.styles = PassGuardStyles()
        self.db_location = 'datastore.db'

        # Database placeholders
        self.keystore = None
        self.passtore = None
        self.db_obj = None
        self.derived_key = None
        self.db_context = None

        # New: Use the SettingsManager to load all app settings
        self.pubsub = PubSub()
        self.settings_manager = SettingsManager(db_path='app_settings.db')

        # Tracks user details from login
        self.user_details = {}

        # Last activity for idle timeout
        self.idle_timeout = 300  # fallback if not in DB
        self.last_activity_time = time.time()

        # Protocol for window closing
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initialize
        self._init_configs()   # load theme, idle_timeout from SettingsManager
        self.login()           # show login flow
        self.check_inactivity()  # schedule idle checking

        # Global bindings for idle timeout
        self.pubsub.subscribe('theme', self._set_appearance_mode) # subscribe to changes for appearance mode.
        self.pubsub.subscribe('idle_timeout', self._set_idle_timeout)
        self.bind_all("<Button-1>", self.reset_idle_time)
        self.bind_all("<Key>", self.reset_idle_time)

    # ------------------------------------------------------------------------------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def _init_configs(self):
        """
        Load settings from SettingsManager (theme, idle_timeout, etc.)
        and apply them to the application.
        """
        try:
            appearance_theme = self.settings_manager.get('theme') or 'superhero'
            self.idle_timeout = self.settings_manager.get('idle_timeout') or 300
            self._set_appearance_mode(theme_name=appearance_theme)
        except Exception as ex:
            logging.error("Failed to initialize config settings: %s", ex)
            Messagebox.show_error("Configuration Error", "Failed to load application settings.")
            self.destroy()
    
    def _user_login(self):
        """
        Show login or registration dialog to get username/password.
        Returns a dict { 'u': <username>, 'p': <password>, 's': <salt> } or None if canceled.
        """
        r = self.settings_manager.get('r')  # 0 or None means not registered
        s = self.settings_manager.get('s')
        dialog_text = "Register Account" if not r else "Login"
        dialog_title = 'PassGuard: Registration' if not r else 'PassGuard: Login'

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
        """
        Decrypt (or create if new) the main datastore.db with the user credentials.
        """
        try:
            self.db_context = encrypted_database_context(
                db_path=self.db_location,
                encrypto_cls=Encrypto,
                password=(user_pass := user_details['p']),
                salt=user_details.get('s', None)
            )
            self.db_obj = self.db_context.__enter__()
            
            self.derived_key, _ = generate_key(password=user_pass, salt=self.db_obj.get('salt', None))
            # Simple query to ensure DB is valid
            self.db_obj['sql'].query("SELECT 1 FROM sqlite_master LIMIT 1;")

            # Set up controllers
            self.passtore = PasswordStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="pm"))
            self._on_database_initialized()
        except DatabaseError:
            raise DatabaseError("Decryption failed: file is not a valid database. Possibly incorrect credentials.")
        except Exception as ex:
            raise Exception(f"An error occurred during database initialization: {ex}")

    def _on_database_initialized(self):
        """
        Called once DB is successfully decrypted.
        """
        if not self.winfo_exists():
            return
        self._create_pages()
        self.create_snackbar()

    def login(self):
        """
        Main login loop. If user cancels or fails, destroy the app.
        """
        while True:
            user_details = self._user_login()
            if not user_details:
                # User canceled the login/registration dialog
                self.destroy()
                return

            is_registered = self.settings_manager.get('r')
            stored_username = self.settings_manager.get('u')

            if is_registered:
                # Check username matches if user is already registered
                if not stored_username:
                    Messagebox.show_error(title="Login Failed", message="Configuration error: missing username. Please re-register.")
                    continue
                if user_details['u'] != stored_username:
                    Messagebox.show_error(title="Login Failed", message="Incorrect username. Please try again.")
                    continue

            # Attempt to initialize the database with these credentials
            try:
                self._initialize_database(user_details=user_details)
                
                appdata={'r':1, 's':self.db_obj['salt']}
                if not stored_username:
                    appdata.update({'u':user_details['u']})
                self.settings_manager.set_items(obj=appdata)
                self.user_details = user_details
                break  # Successful login
            except DatabaseError as ex:
                logging.error(f"Login failed: {ex}")
                Messagebox.show_error(title="Login Failed", message="Incorrect password. Please try again.")
            except Exception as ex:
                logging.error(f"Unexpected error during login: {ex}")
                Messagebox.show_error(title="Login Failed", message="An unexpected error occurred. Please try again.")

    # ------------------------------------------------------------------------------------------------------------------------------------------
    # Main UI (Notebook / Pages)
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def _create_pages(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        self.passwords_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.info_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.passwords_tab, text='Passwords')
        self.notebook.add(self.settings_tab, text='Settings')
        self.notebook.add(self.info_tab, text='Info')

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
        if selected_tab == 0:
            if not hasattr(self, 'password_page') or self.password_page is None or not self.password_page.winfo_exists():
                self.init_passwords_page()
        elif selected_tab == 1:
            if not hasattr(self, 'settings_page') or self.settings_page is None or not self.settings_page.winfo_exists():
                self.init_settings_page()
        elif selected_tab == 2:
            if not hasattr(self, 'info_page') or self.info_page is None or not self.info_page.winfo_exists():
                self.init_info_page()

    def init_passwords_page(self):
        self.password_page = PasswordFrame(
            master=self.passwords_tab,
            passtore=self.passtore,
            keystore=self.keystore,
            key=self.derived_key,
            pg_styles=self.styles.style,
            pubsub=self.pubsub,
            log_func=self.log_message,
            settings_manager=self.settings_manager,
        )
        self.password_page.grid(row=0, column=0, sticky='nsew')

    def init_settings_page(self):
        """
        Pass the SettingsManager so the SettingsFrame can directly
        get/set 'theme', 'idle_timeout', etc.
        """
        self.settings_page = SettingsFrame(
            master=self.settings_tab,
            pg_styles=self.styles.style,
            # appearance_func=self._set_appearance_mode,  # for immediate theme change
            change_password_func=self.change_master_password,
            snackbar_messenger=self.log_message,
            pubsub=self.pubsub,
            settings_manager=self.settings_manager,     # <-- NEW
        )
        self.settings_page.grid(row=0, column=0, sticky='nsew')

    def init_info_page(self):
        self.info_page = InfoFrame(
            master=self.info_tab,
            pg_styles=self.styles.style,
        )
        self.info_page.grid(row=0, column=0, sticky='nsew')

    # ---------------------------------------------------------------------
    # Appearance (Theme)
    # ---------------------------------------------------------------------
    def _set_idle_timeout(self, val:int):
        self.idle_timeout = val

    def _set_appearance_mode(self, theme_name: str = 'superhero'):
        """
        Change the application theme.
        """
        self.style.theme_use(theme_name)
        self.styles.reapply_styles()
        self.update_idletasks()

    # ---------------------------------------------------------------------
    # Snackbar / Logging
    # ---------------------------------------------------------------------
    def create_snackbar(self):
        self.snackbar = SnackBar(self, pg_styles=self.styles.style)
        self.snackbar.grid(row=1, column=0, sticky="ew")
        self.log_message("Database initialized successfully", duration=2000)
        self.log_message(f"PassGuard 9000™")

    def log_message(self, message: str, duration: int = 3000):
        """Log a message to the Snackbar."""
        self.snackbar.add_message(message, duration)

    # ---------------------------------------------------------------------
    # Idle Timeout Handling
    # ---------------------------------------------------------------------
    def reset_idle_time(self, event=None):
        self.last_activity_time = time.time()

    def check_inactivity(self):
        current_time = time.time()
        idle_timeout = self.idle_timeout or 300
        if (current_time - self.last_activity_time) > idle_timeout:
            self.on_idle_logout()
        self.after(5000, self.check_inactivity)  # re-check every 5 seconds

    def on_idle_logout(self):
        """
        Perform steps to lock the app and return to login.
        """
        if self.db_context:
            self.db_context.__exit__(None, None, None)
            self.db_context = None
            self.db_obj = None
        self.derived_key = None
        self.keystore = None
        self.passtore = None
        self.password_page = None
        if hasattr(self, 'notebook'):
            self.notebook.destroy()


        self.login()  # Re-open the login dialog

    # ---------------------------------------------------------------------
    # Closing / Shutdown
    # ---------------------------------------------------------------------
    def on_closing(self):
        try:
            if self.db_context:
                self.db_context.__exit__(None, None, None)
                self.db_context = None
                logging.info("Database encrypted and saved successfully.")
        except Exception as ex:
            logging.error(f"Failed to encrypt and save the database: {ex}")
            Messagebox.show_error("Shutdown Error", "Failed to save the encrypted database.")
        finally:
            self.db_obj = None
            self.derived_key = None
            self.keystore = None
            self.passtore = None
            self.password_page = None
            if hasattr(self, 'notebook'):
                self.notebook.destroy()
            self.destroy()

    # ---------------------------------------------------------------------
    # Master Password Changing (unchanged from your snippet, except to 
    # ---------------------------------------------------------------------
    def change_master_password(self, current_password, new_password):
        try:
            username = self.user_details['u']
            salt = self.settings_manager.get('s')

            # 1) Verify current password
            decrypted_data = self.verify_old_credentials(username, current_password, salt)
            if decrypted_data is None:
                self.log_message(message="Password Error: password is incorrect.")
                Messagebox.show_error(title="Password Error", message="Current password is incorrect.")
                return False

            # 2) Derive new key
            new_encryptor, new_salt = self.derive_new_key(username, new_password, salt)

            # 3) Re-encrypt the database to a temp file
            temp_db_fd, temp_db_path = tempfile.mkstemp()
            os.close(temp_db_fd)
            success = self.reencrypt_database(decrypted_data, new_encryptor, temp_db_path)
            if not success:
                logging.error("Failed to re-encrypt the database with the new password.")
                Messagebox.show_error("Encryption Error", "Failed to re-encrypt the database with the new password.")
                os.remove(temp_db_path)
                return False

            # 4) Replace the old database atomically
            backup_db_path = self.db_location + '.bak'
            try:
                os.replace(self.db_location, backup_db_path)  # backup current
                os.replace(temp_db_path, self.db_location)    # replace with new
                os.remove(backup_db_path)
            except Exception as ex:
                logging.error(f"Failed to replace the database file: {ex}")
                Messagebox.show_error("File Error", "Failed to replace the database file.")
                if os.path.exists(backup_db_path):
                    os.replace(backup_db_path, self.db_location)
                if os.path.exists(temp_db_path):
                    os.remove(temp_db_path)
                return False

            # 5) Reinitialize DB with new credentials
            try:
                self.db_context.__exit__(None, None, None)
                self.db_context = encrypted_database_context(
                    db_path=self.db_location,
                    encrypto_cls=Encrypto,
                    keys=[username, new_password],
                    salt=new_salt
                )
                self.db_obj = self.db_context.__enter__()
                self.keystore = KeyStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name="km"))
                self.passtore = PasswordStorageInterface(controller=SQLiteController(db=self.db_obj['sql'], table_name='pm'))
            except Exception as ex:
                logging.error(f"Failed to reinitialize database context: {ex}")
                Messagebox.show_error("Initialization Error", "Failed to reinitialize database context.")
                # Attempt to roll back
                os.replace(self.db_location, temp_db_path)
                os.replace(backup_db_path, self.db_location)
                os.remove(temp_db_path)
                return False

            # 6) Update the salt in the settings manager
            self.settings_manager.set('s', new_salt)
            self.log_message(message="Password changed successfully.")
            return True

        except Exception as ex:
            logging.error(f"An error occurred while changing the password: {ex}")
            Messagebox.show_error("Error", f"An error occurred while changing the password: {ex}")
            return False

    def verify_old_credentials(self, username, password, salt):
        try:
            encryption_key, _ = generate_key(keys=[username, password], salt=salt)
            encryptor = Encrypto(encryption_key)
            with open(self.db_location, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = encryptor.decrypt(encrypted_data)
            return decrypted_data
        except Exception as ex:
            logging.error(f"Failed to verify old credentials: {ex}")
            return None

    def derive_new_key(self, username, new_password, salt):
        encryption_key, new_salt = generate_key(keys=[username, new_password], salt=salt)
        encryptor = Encrypto(encryption_key)
        return encryptor, new_salt

    def reencrypt_database(self, decrypted_data, new_encryptor, out_file):
        try:
            encrypted_data = new_encryptor.encrypt(decrypted_data)
            with open(out_file, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as ex:
            logging.error(f"Failed to re-encrypt the database: {ex}")
            return False
