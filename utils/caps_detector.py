import re
from config import CAPS_LOCK_LIMIT

def is_caps_lock(text: str) -> bool:
    letras = [c for c in text if c.isalpha()]
    if len(letras) < 5:
        return False

    maiusculas = sum(1 for c in letras if c.isupper())
    return (maiusculas / len(letras)) >= 0.7