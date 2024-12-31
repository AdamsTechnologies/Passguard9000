# app_settings_def.py
SETTINGS_DEFINITION = {
    "u": { # username hash
        "type": str,
        "default": None,
    },
    "r": {  # is app registered
        "type": str,
        "default": None,
    },
    "s": { # salt
        "type": str,
        "default": None,   
    },
    "theme": {
        "type": str,
        "default": "superhero",   # or "nightly", "coral", etc.
    },
    "idle_timeout": {
        "type": int,
        "default": 300 # 300 seconds = 5 minutes
    },
    # Add more as needed
}