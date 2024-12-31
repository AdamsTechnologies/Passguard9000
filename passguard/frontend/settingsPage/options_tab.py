import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip

class OptionsPage(ttk.Frame):
    def __init__(self, master, style, appearance_func, settings_manager, snackbar_messenger, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.style = style
        self.appearance_func = appearance_func
        self.settings_manager = settings_manager
        self.available_themes = self.style.theme_names()
        self.snackbar_messenger = snackbar_messenger
        # Example settings items
        self.settings_items = [
            # theme
            {
                "label": "Theme:",
                "widget_type": "optionmenu",
                "values": self.available_themes,
                "default": self.style.theme_use(),
                "callback": self.on_theme_change,
                # "tooltip": {'text':"change app theme", 'bootstyle':'info'},
            },
            # idle timeout
            {
                "label": "Auto Timeout:",
                "widget_type": "optionmenu",
                "values": [1, 5, 10, 15, 30, 60],
                "default": 5,
                "callback": self.on_idle_timeout_change,
                "tooltip": {'text':"time idle before logging out. (minutes)", 'bootstyle':'info'},
            },
        ]

        self.create_widgets()

    def create_widgets(self):
        """
        Build the UI for the Options page.
        """
        title_label = ttk.Label(self, text="Options", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky='n')

        divider = ttk.Separator(self, orient='horizontal')
        divider.grid(row=1, column=0, columnspan=3, sticky='ew', padx=10)

        # A container frame for the dynamic form
        form_frame = ttk.Frame(self)
        form_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

        # Build each setting
        for row_index, item in enumerate(self.settings_items):
            label_text = item.get("label", "")
            widget_type = item.get("widget_type", "entry").lower()
            values = item.get("values", [])
            default_val = item.get("default")
            callback = item.get("callback")
            tool_tip = item.get("tooltip")

            # Label
            label = ttk.Label(form_frame, text=label_text, font=("Helvetica", 12))
            label.grid(row=row_index, column=0, sticky='w', padx=5, pady=5)

            if widget_type == "optionmenu":
                var = ttk.StringVar(value=str(default_val))
                option = ttk.OptionMenu(form_frame, var, var.get(), *values, command=callback)
                option.grid(row=row_index, column=1, sticky='w', padx=5, pady=5)
                item["variable"] = var
                if tool_tip:
                    ToolTip(widget=option, **tool_tip)
            else:
                # fallback to Entry or Combobox etc.
                pass

    def on_theme_change(self, new_theme):
        """
        Callback for theme changes.
        """
        self.snackbar_messenger(f"Theme changed to: {new_theme}")
        self.appearance_func(new_theme) # force update the theme immediately.
        self.settings_manager.set("theme", new_theme)

    def on_idle_timeout_change(self, new_idle):
        """
        Callback for idle timeout changes.
        """
        self.snackbar_messenger(f"auto logout after: {new_idle} minutes")
        self.settings_manager.set("idle_timeout", (new_idle*60)) # multiply by 60 to convert minutes to seconds...
