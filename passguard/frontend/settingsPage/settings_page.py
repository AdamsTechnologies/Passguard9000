import ttkbootstrap as ttk
from typing import Callable, Any
from ttkbootstrap.constants import *

# Import settings tabs.
from passguard.backend.pubSub.publish_subscribe import PubSub
from passguard.frontend.settingsPage.options_tab import OptionsPage
from passguard.frontend.settingsPage.change_pass_tab import ChangePasswordPage

class SettingsFrame(ttk.Frame):
    def __init__(
        self,
        master,
        pg_styles: ttk.Style,
        change_password_func: Callable,
        snackbar_messenger: Callable,
        pubsub:PubSub,
        settings_manager: Any
    ):
        super().__init__(master)
        self.master = master
        self.style = pg_styles
        # self.appearance_func = appearance_func
        self.change_password_func = change_password_func
        self.snackbar_messenger = snackbar_messenger
        self.settings_manager = settings_manager

        # Create page instances
        self.options_page = OptionsPage(
            self,
            style=self.style,
            settings_manager=self.settings_manager,
            pubsub=pubsub,
            snackbar_messenger=self.snackbar_messenger
        )
        self.change_pass_page = ChangePasswordPage(
            self,
            style=self.style,
            settings_manager=self.settings_manager,
            change_password_func=self.change_password_func,
            pubsub=pubsub,
            snackbar_messenger=self.snackbar_messenger,
        )
        # If you add more pages, create them here...

        # Dictionary of pages
        self.pages = {
            "Options": self.options_page,
            "Change Password": self.change_pass_page,
        }
        self.nav_buttons = {}
        self.selected = None

        self.setup_layout()
        self.create_widgets()


    def setup_layout(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform='col')  # 33%
        self.columnconfigure(1, weight=3, uniform='col')  # 66%

        self.navigation_frame = ttk.Frame(self)
        self.navigation_frame.grid(row=0, column=0, sticky='nsew')
        self.navigation_frame.columnconfigure(0, weight=1)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Add all page frames to self.content_frame, but not shown initially
        # We’ll raise the selected page on navigation
        for page_key, page_frame in self.pages.items():
            page_frame.grid(row=0, column=0, sticky='nsew', in_=self.content_frame)


    def create_widgets(self):
        nav_label = ttk.Label(self.navigation_frame, text="Settings", font=('Helvetica', 16, 'bold'))
        nav_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky='nw')

        divider = ttk.Separator(self.navigation_frame, orient='horizontal')
        divider.grid(row=1, column=0, sticky='ew', padx=10)

        for index, (page_key, page_frame) in enumerate(self.pages.items()):
            button = ttk.Button(
                self.navigation_frame,
                text=page_key,
                command=lambda pk=page_key: self.select_navigation_item(pk),
                style="LEFTNAV.PassGuardLeftNav.TButton"
            )
            button.grid(row=index + 2, column=0, padx=10, sticky='ew')
            self.nav_buttons[page_key] = button

        # Default to first item
        first_item = next(iter(self.pages.keys()))
        self.select_navigation_item(first_item)


    def select_navigation_item(self, page_key):
        if self.selected != page_key:
            # Deselect the old button
            prev_btn = self.nav_buttons.get(self.selected)
            new_btn = self.nav_buttons.get(page_key)
            if prev_btn:
                prev_btn.configure(style='LEFTNAV.PassGuardLeftNav.TButton')
            if new_btn:
                new_btn.configure(style='LEFTNAV.Selected.TButton')

            # Raise the page
            page_frame = self.pages.get(page_key)
            if page_frame:
                page_frame.tkraise()

            self.selected = page_key
