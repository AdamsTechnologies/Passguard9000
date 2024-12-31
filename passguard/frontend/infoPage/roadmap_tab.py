from tkinter import Event
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class RoadmapTab(ttk.Frame):
    def __init__(self, master, style, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.style = style
        self.create_widgets()

    def _dynamic_wrap(self, label: ttk.Label, pad: int = 20):
        """
        Bind a configure event so the label's wraplength
        matches its current width (minus some padding).
        """
        def on_configure(event: Event):
            label.configure(wraplength=event.width - pad)
        label.bind("<Configure>", on_configure)

    def create_widgets(self):
        self.columnconfigure(0, weight=1)
        row = 0

        # Title Label
        label_title = ttk.Label(
            self,
            text="Product Roadmap",
            font=('Helvetica', 18, 'bold'),
        )
        label_title.grid(row=row, column=0, pady=5, padx=10, sticky='n')
        row += 1

        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=row, column=0, sticky='ew', padx=20)
        row += 1

        # Roadmap Heading
        label_roadmap_header = ttk.Label(
            self,
            text="Upcoming Features:",
            font=('Helvetica', 14, 'bold'),
        )
        label_roadmap_header.grid(row=row, column=0, pady=(20, 5), padx=20, sticky='w')
        row += 1

        # One "card" for all bullet points
        roadmap_card = ttk.Frame(self, padding=10) # , bootstyle="secondary"
        roadmap_card.grid(row=row, column=0, sticky='ew', padx=20, pady=(5, 0))
        row += 1

        roadmap_card.columnconfigure(0, weight=1)

        roadmap_items = [
            "Change master password",
            "Customizable database location (e.g., USB, external drives)",
            "Web browser extension",
            "Mobile app integration (Android and iOS)",
            "Theme Builder",
        ]
        for i, item in enumerate(roadmap_items):
            lbl_item = ttk.Label(
                roadmap_card,
                text=f"{chr(0x2022)} {item}",
                font=('Helvetica', 12)
            )
            lbl_item.grid(row=i, column=0, sticky='ew', pady=2)
            self._dynamic_wrap(lbl_item, pad=40)
        self.rowconfigure(row, weight=1)