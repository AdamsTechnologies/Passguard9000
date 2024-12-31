import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from typing import Dict, Callable
from passguard.frontend.infoPage.roadmap_tab import RoadmapTab
from passguard.frontend.infoPage.info_tab import InfoTab

class InfoFrame(ttk.Frame):
    def __init__(self, master, pg_styles: ttk.Style, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.style = pg_styles
        self.nav_buttons = {}
        self.selected = None  # track the selected nav item

        # dictionary of pages
        self.pages = {}
        self.setup_layout()
        self.create_pages()
        self.create_widgets()

        # Default to first nav item
        first_item = next(iter(self.pages.keys()))
        self.select_navigation_item(first_item)

    def setup_layout(self):
        # 2 columns: left nav, right content
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1, uniform='col')
        self.columnconfigure(1, weight=3, uniform='col')

        self.navigation_frame = ttk.Frame(self)
        self.navigation_frame.grid(row=0, column=0, sticky='nsew')
        self.navigation_frame.columnconfigure(0, weight=1)

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

    def create_pages(self):
        # instantiate your separate page classes
        self.info_tab = InfoTab(self.content_frame, style=self.style)
        self.roadmap_tab = RoadmapTab(self.content_frame, style=self.style)

        # dictionary that maps nav labels -> page instance
        self.pages = {
            "Info": self.info_tab,
            "Roadmap": self.roadmap_tab,
        }

        # place each page in content_frame
        for page_key, page in self.pages.items():
            page.grid(row=0, column=0, sticky='nsew')

    def create_widgets(self):
        # Navigation Label
        nav_label = ttk.Label(
            self.navigation_frame,
            text="Information",
            font=('Helvetica', 16, 'bold')
        )
        nav_label.grid(row=0, column=0, padx=10, pady=(10,5), sticky='nw')

        divider = ttk.Separator(self.navigation_frame, orient='horizontal')
        divider.grid(row=1, column=0, sticky='ew', padx=10)

        # Create nav buttons
        for index, (page_key, page_frame) in enumerate(self.pages.items()):
            btn = ttk.Button(
                self.navigation_frame,
                text=page_key,
                command=lambda k=page_key: self.select_navigation_item(k),
                style="LEFTNAV.PassGuardLeftNav.TButton"
            )
            btn.grid(row=index+2, column=0, sticky='ew', padx=10)
            self.nav_buttons[page_key] = btn

        # Add weight so nav items push upward
        self.navigation_frame.rowconfigure(len(self.pages)+2, weight=1)

    def select_navigation_item(self, page_key):
        if self.selected != page_key:
            # re-style old button
            old_btn = self.nav_buttons.get(self.selected)
            if old_btn:
                old_btn.configure(style="LEFTNAV.PassGuardLeftNav.TButton")

            # style new button
            new_btn = self.nav_buttons.get(page_key)
            if new_btn:
                new_btn.configure(style="LEFTNAV.Selected.TButton")

            # raise the appropriate page
            page = self.pages.get(page_key)
            if page:
                page.tkraise()

            self.selected = page_key
