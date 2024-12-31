from tkinter import Event
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class InfoTab(ttk.Frame):
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
            text="PassGuard 9000™",
            font=('Helvetica', 18, 'bold')
        )
        label_title.grid(row=row, column=0, pady=5, padx=10, sticky='n')
        row += 1

        # Separator
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(row=row, column=0, sticky='ew', padx=20)
        row += 1

        # Large Info Text (dynamic wrap)
        info_text = (
            "A secure solution for managing passwords. "
            "With advanced encryption and local data storage, your credentials "
            "stay safe on your device — no data ever leaves your hands."
        )
        label_info = ttk.Label(
            self,
            text=info_text,
            font=('Helvetica', 12),
            justify='left',
        )
        label_info.grid(row=row, column=0, pady=20, padx=20, sticky='ew')
        self._dynamic_wrap(label_info)  # enable dynamic wrapping
        row += 1

        # Features Title
        label_features_title = ttk.Label(
            self,
            text="Key Features:",
            font=('Helvetica', 14, 'bold'),
        )
        label_features_title.grid(row=row, column=0, padx=20, sticky='w')
        row += 1

        # One "card" containing all bullet points
        features_card = ttk.Frame(self, padding=10) # bootstyle='light'
        features_card.grid(row=row, column=0, sticky='ew', padx=20, pady=(5, 0))
        row += 1

        features_card.columnconfigure(0, weight=1)

        features = [
            "No internet connection required or used.",
            "Securely stores and manages your passwords.",
            "Layered security and robust encryption ensures data protection.",
            "Easily update and retrieve stored credentials.",
            "We respect your privacy: No tracking, only encryption.",
        ]
        # Display each bullet item in a separate label, inside the card
        for i, feature in enumerate(features):
            lbl_feature = ttk.Label(
                features_card,
                text=f"{chr(0x2022)} {feature}",
                font=('Helvetica', 12),
                justify='left'
            )
            lbl_feature.grid(row=i, column=0, sticky='ew', pady=2)
            self._dynamic_wrap(lbl_feature, pad=40)

        # Make the last row fill space
        self.rowconfigure(row, weight=1)