import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class InfoFrame(ttk.Frame):
    def __init__(self, master, pg_styles: ttk.Style, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.style = pg_styles
        self.email = 'jakeadams@duck.com'  # TODO Updated email address
        self.nav_buttons = {}
        self.selected = None  # To track the currently selected navigation item

        # Configure grid layout for the main frame
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Navigation frame
        self.columnconfigure(1, weight=3)  # Content frame

        # Left Navigation Frame
        self.navigation_frame = ttk.Frame(self)
        self.navigation_frame.grid(row=0, column=0, sticky='nsew')
        self.navigation_frame.columnconfigure(0, weight=1)

        # Content Frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Navigation items mapping
        self.nav_items = {
            "Info": self.show_info_page,
            "Roadmap": self.show_roadmap_page
        }

        # Initialize navigation and content
        self.create_widgets()

        # Preload content frames
        self.frames = {}
        self.frames['Info'] = self.create_info_frame()
        self.frames['Roadmap'] = self.create_roadmap_frame()

        # Initially select the first navigation item
        self.select_navigation_item(list(self.nav_items.keys())[0])

    def create_widgets(self):
        # Left Navigation Title
        self.navigation_label = ttk.Label(
            self.navigation_frame,
            text="Information",
            font=('Helvetica', 16, 'bold')
        )
        self.navigation_label.grid(row=0, column=0, padx=(10,0), pady=(10, 5), sticky='nw')

        # Divider
        self.divider = ttk.Separator(self.navigation_frame, orient='horizontal')
        self.divider.grid(row=1, column=0, sticky='ew', padx=(10,0))

        # Navigation Buttons with custom styles
        for index, item in enumerate(self.nav_items.keys()):
            button = ttk.Button(
                self.navigation_frame,
                text=item,
                command=lambda value=item: self.select_navigation_item(value),
                style="LEFTNAV.PassGuardLeftNav.TButton"
            )
            button.grid(row=index + 2, column=0, sticky='ew', padx=(10,0))
            self.nav_buttons[item] = button

        # Add weight to rows to push content to the top
        self.navigation_frame.rowconfigure(len(self.nav_items) + 2, weight=1)

    def select_navigation_item(self, value):
        if self.selected != value:
            # Update styles of navigation buttons
            previous_btn = self.nav_buttons.get(self.selected)
            new_btn = self.nav_buttons.get(value)
            if previous_btn:
                previous_btn.configure(style='LEFTNAV.PassGuardLeftNav.TButton')
            if new_btn:
                new_btn.configure(style='LEFTNAV.Selected.TButton')
            self.selected = value

            # Execute the associated function
            self.nav_items.get(value)()

    def show_info_page(self):
        """Show the Info page."""
        self.show_frame('Info')

    def show_roadmap_page(self):
        """Show the Roadmap page."""
        self.show_frame('Roadmap')

    def create_info_frame(self):
        frame = ttk.Frame(self.content_frame)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.columnconfigure(0, weight=1)

        row = 0

        # Title Label
        ttk.Label(
            frame,
            text="PassGuard 9000™",
            font=('Helvetica', 18, 'bold'),
        ).grid(row=row, column=0, pady=5, padx=10, sticky='n')
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, sticky='ew', padx=20)
        row += 1

        # Info Text
        info_text = (
            "A secure solution for managing passwords. "
            "With advanced encryption and local data storage, your credentials "
            "stay safe on your device—no data ever leaves your hands."
        )
        ttk.Label(
            frame,
            text=info_text,
            wraplength=600,
            font=('Helvetica', 12),
            justify='left',
        ).grid(row=row, column=0, pady=20, padx=20, sticky='w')
        row += 1

        # Key Features
        ttk.Label(
            frame,
            text="Key Features:",
            font=('Helvetica', 14, 'bold'),
        ).grid(row=row, column=0, padx=20, sticky='w')
        row += 1

        features = [
            "No internet connection required or used.",
            "Securely stores and manages your passwords.",
            "Layered Security and robust encryption ensures data protection.",
            "Easily update and retrieve stored credentials.",
            "We respect your privacy: No tracking, only encryption.",
        ]
        for feature in features:
            ttk.Label(
                frame,
                text=f"{chr(0x25CF)} {feature}",
                font=('Helvetica', 12),
            ).grid(row=row, column=0, padx=40, pady=2, sticky='w')
            row += 1

        # Add weight to the last row to push content to the top
        frame.rowconfigure(row, weight=1)

        return frame

    def create_roadmap_frame(self):
        frame = ttk.Frame(self.content_frame)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.columnconfigure(0, weight=1)

        row = 0

        # Title Label
        ttk.Label(
            frame,
            text="Product Roadmap",
            font=('Helvetica', 18, 'bold'),
        ).grid(row=row, column=0, pady=5, padx=10, sticky='n')
        row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, sticky='ew', padx=20)
        row += 1

        # Roadmap Items
        ttk.Label(
            frame,
            text="Upcoming Features:",
            font=('Helvetica', 14, 'bold'),
        ).grid(row=row, column=0, pady=(20, 5), padx=20, sticky='w')
        row += 1

        roadmap_items = [
            "Change master password",
            "Customizable database location (e.g., USB, external drives)",
            "Web Browser extension",
            "Mobile app integration for Android and iOS",
            "Theme Builder",
        ]
        for item in roadmap_items:
            ttk.Label(
                frame,
                text=f"• {item}",
                font=('Helvetica', 12)
            ).grid(row=row, column=0, padx=40, pady=2, sticky='w')
            row += 1

        # Add weight to the last row to push content to the top
        frame.rowconfigure(row, weight=1)

        return frame

    def show_frame(self, name):
        """Show the specified frame."""
        frame = self.frames[name]
        frame.tkraise()
