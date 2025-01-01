import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # Running from PyInstaller executable
        return os.path.join(sys._MEIPASS, 'passguard', relative_path)
    else:
        # Running in development
        return os.path.join(os.path.dirname(__file__), relative_path)
