import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Dialog, Messagebox

from passguard.backend.helpers.password_generator import PasswordFactory

class PassGeneratorDialog(Dialog):
    def __init__(self, parent, title: str = "Password Generator", text: str = "Generate a customized password"):
        """
        Initializes the PassGeneratorDialog.

        Args:
            parent (tk.Widget): The parent window.
            title (str): The title of the dialog.
            text (str): Instructional text within the dialog.
        """
        self.instruction_text = text
        super().__init__(parent, title=title)

    def create_body(self, master):
        """
        Creates the body of the dialog.

        Args:
            master (tk.Widget): The master widget.
        """
        # Instructional Label
        self.label = ttk.Label(master, text=self.instruction_text, wraplength=350)
        self.label.pack(pady=(20, 10), padx=20)

        # Length Selection Frame
        length_frame = ttk.Frame(master)
        length_frame.pack(pady=10, padx=20, fill='x')

        # Minimum Length
        min_frame = ttk.Frame(length_frame)
        min_frame.pack(side='left', padx=5)

        self.min_length_var = ttk.IntVar(value=8)
        self.min_length_var.trace_add("write", self._sync_min_max_length)  # Add trace to ensure logic
        min_label = ttk.Label(min_frame, text="Min Length:")
        min_label.pack(side='left', padx=5)
        min_spinbox = ttk.Spinbox(
            min_frame,
            from_=4,
            to=128,
            textvariable=self.min_length_var,
            width=5
        )
        min_spinbox.pack(side='left', padx=5)

        # Maximum Length
        max_frame = ttk.Frame(length_frame)
        max_frame.pack(side='left', padx=5)

        self.max_length_var = ttk.IntVar(value=12)
        self.max_length_var.trace_add("write", self._sync_min_max_length)  # Add trace to ensure logic
        max_label = ttk.Label(max_frame, text="Max Length:")
        max_label.pack(side='left', padx=5)
        max_spinbox = ttk.Spinbox(
            max_frame,
            from_=4,
            to=128,
            textvariable=self.max_length_var,
            width=5
        )
        max_spinbox.pack(side='left', padx=5)

        # Exclude Characters Entry
        exclude_label = ttk.Label(master, text="Characters to Exclude:")
        exclude_label.pack(pady=(10, 5), padx=20, anchor='w')
        self.exclude_chars_entry = ttk.Entry(master)
        self.exclude_chars_entry.pack(pady=5, padx=20, fill='x')

        return self.label  # Set initial focus

    def create_buttonbox(self, master):
        """
        Creates the button box of the dialog.

        Args:
            master (tk.Widget): The master widget.
        """
        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(pady=10)

        # OK Button
        self.ok_button = ttk.Button(
            self.button_frame,
            text='OK',
            command=self.ok,  # Bind to the 'ok' method
            bootstyle='primary'
        )
        self.ok_button.pack(side='left', padx=5)

        # Cancel Button
        self.cancel_button = ttk.Button(
            self.button_frame,
            text='Cancel',
            command=self.cancel,  # Bind to the 'cancel' method
            bootstyle='secondary'
        )
        self.cancel_button.pack(side='left', padx=5)
    
    def _sync_min_max_length(self, *args):
        """
        Ensures that max_length_var is always at least 1 more than min_length_var.
        """
        min_length = self.min_length_var.get()
        max_length = self.max_length_var.get()

        if max_length < min_length + 1:
            self.max_length_var.set(min_length + 1)

    def apply(self):
        """
        Called when the user confirms the dialog (e.g., clicks "OK").
        """
        min_length = self.min_length_var.get()
        max_length = self.max_length_var.get()
        exclude_chars = self.exclude_chars_entry.get()

        try:
            generated_password = PasswordFactory.generate_password(
                min_length=min_length,
                max_length=max_length,
                exclude_chars=exclude_chars
            )
            self._result = generated_password  # Set the dialog's result
        except Exception as e:
            Messagebox.show_error(
                title="Error",
                message=f"Failed to generate password: {str(e)}",
                parent=self._toplevel
            )
            self._result = None

    def get_input(self):
        """
        Displays the dialog and returns the generated password.

        Returns:
            Optional[str]: The generated password or None if canceled.
        """
        self.show()  # Display the dialog
        return self._result

    def ok(self):
        """
        Handles the OK button click.
        """
        self.apply()
        self._toplevel.destroy()

    def cancel(self):
        """
        Handles the Cancel button click.
        """
        self._toplevel.destroy()
