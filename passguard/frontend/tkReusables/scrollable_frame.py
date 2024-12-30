import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bootstyle='round')
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", self.update_scrollregion)

        # Store the window ID
        self.scrollable_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind the canvas's <Configure> event
        self.canvas.bind('<Configure>', self.frame_width)

        # Bind mousewheel to scroll
        self.scrollable_frame.bind_all("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-4>", self._on_mousewheel)
        self.scrollable_frame.bind_all("<Button-5>", self._on_mousewheel)

    def frame_width(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.scrollable_frame_id, width=canvas_width)

    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta == -120:
            self.scrollable_frame.master.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            self.scrollable_frame.master.yview_scroll(-1, "units")

    def update_scrollregion(self, event=None):
        bbox = self.canvas.bbox("all")  # Get the bounding box of the content
        if bbox:
            # Get the height of the canvas and the content
            content_height = bbox[3]
            canvas_height = self.canvas.winfo_height()
            
            # Ensure scrollregion doesn't allow scrolling above or below the content
            self.canvas.configure(
                scrollregion=(0, 0, bbox[2], max(canvas_height, content_height))
            )