import os
import base64
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


def generate_key(password:str, salt:bytes=None):
    """
    Generates a 256-bit key using Argon2id KDF

    The function generates a 256-bit key using a password and a random salt.  
    Storing the salt: The salt should be stored securely, either in your database or an external file, so it can be reused to regenerate the same key.  
    
    Returns: 
        key - the encryption key
        salt - the randomly generated salt; needs to be stored securely as it will be used to generate the key.

    ```
        key, salt = generate_key(keys=[username, password], salt=salt)
    ```
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")
    
    if salt is None:
        salt = os.urandom(16)

    kdf = Argon2id(
        salt=salt,
        length=32,         # Desired key length in bytes (256 bits)
        iterations=3,      # Number of iterations (time_cost)
        lanes=1,           # Number of parallel threads (parallelism)
        memory_cost=65536  # Memory cost in KiB (64 MiB)
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    key_str = key.decode('utf-8')
    return key_str, salt