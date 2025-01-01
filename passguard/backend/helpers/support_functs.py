from typing import Literal

def apply_casing(text: str, casing:Literal["none", "title", "upper", "lower", 'capitalize']) -> str:
    if not text:
        return text
    if casing == "upper":
        return text.upper()
    elif casing == "lower":
        return text.lower()
    elif casing == "title":
        return text.title()
    elif casing == 'capitalize':
        return text.capitalize()
    else:
        # "none" or any unknown string; return how user input
        return text