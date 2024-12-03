import tkinter as tk
import ttkbootstrap as ttk
from datetime import datetime
from ttkbootstrap.constants import *
from typing import List, Dict, Any, Callable

from frontend.tkReusables.scrollable_frame import ScrollableFrame

class PasswordList(ttk.Frame):
    def __init__(self, master, pg_styles:ttk.Style, values: List[tuple], items_mapping: Dict[str, Dict[str, Any]], on_select: Callable, log_func:Callable):
        super().__init__(master)
        self.values = values
        self.items_mapping = items_mapping
        self.on_select = on_select
        self.selected_id = None
        self.style = pg_styles
        self.log_func=log_func
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Search Bar
        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(self, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        self.search_bar.bind('<KeyRelease>', self.filter_list)
        self.search_bar.bind('<FocusIn>', self.clear_placeholder)
        self.search_bar.bind('<FocusOut>', self.add_placeholder)

        # Placeholder color and default text color
        self.default_text_color = self.search_bar.cget('foreground')
        self.placeholder_color = 'grey'

        self.add_placeholder()

        # Use ScrollableFrame
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky='nsew')
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Dictionary to keep track of buttons
        self.buttons = {}

        # Populate the list
        self.populate_buttons()

    def clear_placeholder(self, event=None):
        if self.search_bar.get() == 'Search':
            self.search_bar.delete(0, 'end')
            self.search_bar.config(foreground=self.default_text_color)

    def add_placeholder(self, event=None):
        if not self.search_bar.get():
            self.search_bar.insert(0, 'Search')
            self.search_bar.config(foreground=self.placeholder_color)

    def filter_list(self, event=None):
        search_term = self.search_var.get().lower()
        if search_term == 'search':
            search_term = ''
        filtered_values = [item for item in self.values if search_term in item[0].lower()]
        self.populate_buttons(filtered_values)

    def populate_buttons(self, values=None):
        if values is None:
            values = self.values

        # Clear existing widgets
        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        self.buttons.clear()
        
        # self.scrollable_frame.scrollable_frame.columnconfigure(0, weight=1)
        # Create new buttons
        for index, (display_text, id) in enumerate(values):
            is_selected = id == self.selected_id  # Check if this button is selected
            button_style = (
                "LEFTNAV.Selected.TButton" if is_selected else "LEFTNAV.PassGuardLeftNav.TButton"
            )
            button = ttk.Button(
                self.scrollable_frame.scrollable_frame,
                text=display_text,
                command=lambda id=id: self.button_event(id=id),
                style=button_style
            )
            button.grid(row=index, column=0,  sticky='ew', padx=(5,0))
            # self.scrollable_frame.scrollable_frame.rowconfigure(index, weight=0)
            self.buttons[id] = button
        self.scrollable_frame.scrollable_frame.grid_columnconfigure(0, weight=1)

    def sort_password_list(self, items_mapping):
        # Sort items by service alphabetically, then by datetime
        sorted_items = sorted(
            items_mapping.values(),
            key=lambda x: (x['service'].lower(), x['dt'])
        )

        service_counter = {}
        updated_items_mapping = {}
        for item in sorted_items:
            service = item['service'].lower()
            count = service_counter.get(service, 0)
            service_counter[service] = count + 1

            new_item = item.copy()
            if count > 0:
                new_item['service'] = f"{item['service']} ({count:02d})"
            new_item['dt'] = datetime.fromisoformat(new_item['dt'])
            # Update the mapping
            updated_items_mapping[new_item['id']] = new_item

        return updated_items_mapping

    def update_list(self, items_mapping: Dict[str, Dict[str, Any]]):
        self.items_mapping = self.sort_password_list(items_mapping=items_mapping)
        self.values = [
            (record['service'].title(), id)  # only show the title..
            for id, record in self.items_mapping.items()
        ]
        self.populate_buttons()

    def button_event(self, id: str): 
        # most efficient now - function toggles on the selected btn and toggles off the old one. no more re-rendering all btns each call.
        previous_btn = False
        selected_btn = self.buttons.get(id, False)
        isnew_selection = self.selected_id != id
        
        if selected_btn:
            selected_btn.configure(style="LEFTNAV.Selected.TButton")
            if self.on_select and isnew_selection:
                self.on_select(id)

        if self.selected_id is not None and isnew_selection:
            previous_btn = self.buttons.get(self.selected_id, False)

        if previous_btn:
            previous_btn.configure(style="LEFTNAV.PassGuardLeftNav.TButton")

        self.selected_id=id