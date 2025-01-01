from typing import Callable, Any
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from passguard.backend.pubSub.publish_subscribe import PubSub
from passguard.backend.helpers.support_functs import apply_casing

class OptionsPage(ttk.Frame):
    def __init__(
            self, 
            master, 
            style, 
            settings_manager, 
            pubsub:PubSub, 
            snackbar_messenger, 
            *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.style = style
        self.settings_manager = settings_manager
        self.available_themes = self.style.theme_names()
        self.snackbar_messenger = snackbar_messenger
        self.pubsub = pubsub
        
        # Setting Options:
        self.settings_items = [
            { # theme
                "key":"theme",
                "label": "Theme:",
                "widget_type": "optionmenu",
                "values": self.available_themes,
                "default": self.style.theme_use(),
                "value_format":None,
                "snackbar": lambda val: f"Theme changed to: {val}",
                # "tooltip": {'text':"change app theme", 'bootstyle':'info'},
            },
            { # idle timeout
                "key":"idle_timeout",
                "label": "Auto Timeout:",
                "widget_type": "optionmenu",
                "values": [1, 5, 10, 15, 30, 60],
                "default": int(self.settings_manager.get('idle_timeout')/60) or 5, # divide by 60 to convert from seconds to minutes.
                "value_format": lambda val: (int(val)*60), # converts minutes to seconds
                "snackbar": lambda val: f"auto logout after: {val} minutes",
                "tooltip": {'text':"idle time before logging out. (minutes)", 'bootstyle':'info'},
            },
            { # passlist_casing
                "key":"passlist_case",
                "label": "List Format:",
                "widget_type": "optionmenu",
                "values": ["none", "title", "upper", "lower"],
                "default": self.settings_manager.get('passlist_case') or 'title',
                "value_format":None,
                "snackbar": lambda val: f"Password list format: {apply_casing(text=val, casing=val)}",
                "tooltip": {'text':"formats the password list buttons", 'bootstyle':'info'},
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
            tool_tip = item.get("tooltip")

            # Label
            label = ttk.Label(form_frame, text=label_text, font=("Helvetica", 12))
            label.grid(row=row_index, column=0, sticky='w', padx=5, pady=5)

            if widget_type == "optionmenu":
                var = ttk.StringVar(value=str(default_val))
                option = ttk.OptionMenu(form_frame, var, var.get(), *values, command=lambda val, k=item["key"]: self.on_setting_changed(k, val)) # command=callback
                option.grid(row=row_index, column=1, sticky='w', padx=5, pady=5)
                item["variable"] = var
                if tool_tip:
                    ToolTip(widget=option, **tool_tip)
            else:
                # fallback to Entry or Combobox etc.
                pass
    
    def _find_item_by_key(self, key: str):
        for item in self.settings_items:
            if item.get("key") == key:
                return item
        return None

    def on_setting_changed(self, key:str, val:Any):
        """
        One single callback to handle all dynamic settings changes.
        """
        metadata = self._find_item_by_key(key)
        if (value_format_func:=metadata.get("value_format")) is not None and callable(value_format_func):
            value = value_format_func(val)
        else:
            value = val
        
        self.settings_manager.set(key, value) # update app settings
        self.pubsub.publish(key, value)  # publish message for subscribers.
        
        if (snackbar_func:=metadata.get("snackbar")) and callable(snackbar_func):
            self.snackbar_messenger(snackbar_func(val)) # write to snackbar