import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

def generate_key(keys:list[str],salt:bytes=None, iterations:int=100000):
    """
    The function generates a 256-bit key using the concatenation of the keys str list, and a random salt.  
    Storing the salt: The salt should be stored securely, either in your database or an external file, so it can be reused to regenerate the same key.
    
    Returns: 
        key - the encryption key
        salt - the randomly generated salt; needs to be stored securely as it will be used to generate the key.

    ```
        key, salt = generate_key(keys=[username, password], salt=salt)
    ```
    """
    if salt is None:
        salt = os.urandom(16)

    # Combine username and password to make a stronger key input
    key_material = ":".join(keys).encode('utf-8')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 256-bit key
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(key_material))
    key_str = key.decode('utf-8')
    key = None
    return key_str, salt