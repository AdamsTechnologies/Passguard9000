import re
import ttkbootstrap as ttk
from ttkbootstrap import Colors
from ttkbootstrap.constants import *

class PassGuardStyles:
    def __init__(self):
        self.style = ttk.Style()
        self.colors = self.style.colors
        self.disabled_fg = Colors.make_transparent(0.30, self.style.colors.fg, self.style.colors.bg)
        # Configure all styles
        self.configure_global_styles()
        self.configure_outline_button_styles()
        self.configure_left_nav_styles()

    def is_dark_theme(self):
        """Determine if the current theme is dark or light."""
        bg_color = self.style.colors.bg
        # Check if the color is in hex format (e.g., #RRGGBB)
        if isinstance(bg_color, str) and re.match(r"^#[0-9A-Fa-f]{6}$", bg_color):
            # Extract RGB values from hex color
            r, g, b = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
            # Calculate brightness
            brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return brightness < 0.5
        return False

    def configure_global_styles(self):
        """Globally removes focus lines for all ttkbootstrap buttons."""
        
        for colorname in self.style.colors:
            self.style.configure(f"{colorname}.TButton", focusthickness=0, focuscolor="")
            self.style.configure(f"{colorname}.Outline.TButton", focusthickness=0, focuscolor="")
            self.style.configure(f"{colorname}.Selected.TButton", focusthickness=0, focuscolor="")

        # Default button styles
        self.style.configure("TButton", focusthickness=0, focuscolor="")
        self.style.configure("Outline.TButton", focusthickness=0, focuscolor="")

    # --------------------------------------------------
    # LEFT-NAV BUTTONS
    # --------------------------------------------------
    def configure_left_nav_styles(self):
        """Creates styles for left navigation buttons, adapting to current theme."""
        colors = self.style.colors
        default_fg = colors.fg
        background_color = colors.bg
        primary_color = colors.primary
        dark_color = colors.dark
        active_color = colors.active

        is_dark = self.is_dark_theme()
        selected_bg_color = dark_color if is_dark else colors.light
        selected_fg_color = primary_color if is_dark else colors.dark

        # Left Navigation Button Style
        self.style.configure(
            "LEFTNAV.PassGuardLeftNav.TButton",
            foreground=default_fg,
            background=background_color,
            bordercolor=background_color,
            darkcolor=background_color,
            lightcolor=background_color,
            relief=FLAT,
            focusthickness=0,
            focuscolor=background_color,
            anchor=W,
            padding=(10, 5),
        )
        self.style.map(
            "LEFTNAV.PassGuardLeftNav.TButton",
            shiftrelief=[("pressed !disabled", -1)],
            foreground=[
                ("disabled", self.disabled_fg),
                ("pressed !disabled", primary_color),
                ("hover !disabled", primary_color),
            ],
            background=[
                ("pressed !disabled", dark_color),
                ("hover !disabled", active_color),
            ],
            bordercolor=[
                ("disabled", primary_color),
                ("pressed !disabled", primary_color),
                ("hover !disabled", primary_color),
            ],
            focuscolor=[
                ("pressed !disabled", dark_color),
                ("hover !disabled", active_color)
            ]
        )

        # Selected Left Navigation Button Style
        self.style.configure(
            "LEFTNAV.Selected.TButton",
            foreground=selected_fg_color,
            background=selected_bg_color,
            bordercolor=selected_bg_color,
            darkcolor=background_color,
            lightcolor=background_color,
            relief=FLAT,
            focusthickness=0,
            focuscolor=selected_bg_color,
            anchor=W,
            padding=(10, 5),
        )
        self.style.map(
            "LEFTNAV.Selected.TButton",
            shiftrelief=[("pressed !disabled", -1)],
            foreground=[
                ("disabled", self.disabled_fg),
                ("pressed !disabled", selected_fg_color),
                ("hover !disabled", selected_fg_color),
            ],
            background=[
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", active_color),
            ],
            bordercolor=[
                ("disabled", primary_color),
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", active_color),
            ],
            focuscolor=[
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", active_color)
            ]
        )
    # --------------------------------------------------
    # OUTLINE BUTTONS
    # --------------------------------------------------
    def configure_outline_button_styles(self):
        """Style for all outline buttons, adapting to current theme."""
        colors = self.style.colors
        default_fg = colors.fg
        background_color = colors.bg
        primary_color = colors.primary
        dark_color = colors.dark
        active_color = colors.active

        is_dark = self.is_dark_theme()
        selected_bg_color = dark_color if is_dark else colors.light
        selected_fg_color = primary_color if is_dark else colors.dark

        self.style.configure(
            "Outline.TButton",
            foreground=default_fg,
            background=background_color,
            bordercolor=primary_color,
            focusthickness=0,
            focuscolor=background_color,  # Match focus color with background
            borderwidth=1,  # Keep border but ensure it blends well with the background
            padding=(8, 4),
            relief=RAISED,  # Keep a subtle raised effect for visual clarity
        )
        self.style.map(
            "Outline.TButton",
            foreground=[
                ("disabled", self.disabled_fg),
                ("pressed !disabled", primary_color),
                ("hover !disabled", primary_color),
                ("!pressed !disabled", default_fg)  # Reset to default foreground color if not pressed
            ],
            background=[
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", active_color),
                ("!pressed !disabled", background_color)  # Reset to default background color if not pressed
            ],
            bordercolor=[
                ("disabled", self.disabled_fg),
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", primary_color),
                ("!pressed !disabled", primary_color)  # Reset to default border color if not pressed
            ],
            focuscolor=[
                ("disabled", background_color),
                ("pressed !disabled", selected_bg_color),
                ("hover !disabled", active_color),
                ("!pressed !disabled", background_color)  # Ensure focus color matches background at all times
            ],
            relief=[
                ("pressed !disabled", FLAT),
                ("hover !disabled", RAISED),
                ("!pressed !disabled", RAISED)  # Reset to default relief if not pressed
            ]
        )

    def reapply_styles(self):
        """Reapply styles after theme change."""
        self.configure_global_styles()
        self.configure_outline_button_styles()
        self.configure_left_nav_styles()