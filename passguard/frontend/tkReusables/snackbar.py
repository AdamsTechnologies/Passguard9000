import tkinter as tk
from ttkbootstrap import Style

class SnackBar(tk.Frame):
    def __init__(self, parent, pg_styles: Style, default_msg: str = None, **kwargs):
        super().__init__(parent, **kwargs)

        # Get the background color from the style or parent
        self.style = pg_styles
        self.colors = self.style.colors
        bg_color = self.colors.bg
        if not bg_color:
            bg_color = parent.cget('bg')

        self.default_msg = default_msg
        self.configure(bg=bg_color)

        # Create a StringVar to hold the message
        self.message_var = tk.StringVar(value=self.default_msg or "")

        # Create a Label widget to display the messages
        self.label = tk.Label(
            self,
            textvariable=self.message_var,
            bg=bg_color,
            fg=self.colors.fg,
            font=("Helvetica", 8),
            anchor="e",  # Align text to the right
            padx=10,
            pady=5,
            bd=0,  # Remove border
            highlightthickness=0,
        )
        self.label.grid(row=0, column=0, sticky="nsew")

        # Configure grid behavior for the Snackbox
        self.columnconfigure(0, weight=1)  # Allow the label to expand horizontally
        self.rowconfigure(0, weight=1)
        self.current_timer = None

    def add_message(self, message: str, duration: int = 3000):
        """Display a message in the Snackbox for a specified duration.
            neatly cleans up the old message for a seamless transition.
        """
        if self.current_timer:
            self.after_cancel(self.current_timer)

        self.message_var.set(message)
        # self.label.update_idletasks()

        self.current_timer = self.after(duration, self.clear_message)

    def clear_message(self):
        """Clear the displayed message but keep the Snackbox visible."""
        self.message_var.set(self.default_msg or "")