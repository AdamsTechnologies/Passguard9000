import os
import base64

# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes

# def generate_key(keys:list[str],salt:bytes=None, iterations:int=100000):
#     """
#     The function generates a 256-bit key using the concatenation of the keys str list, and a random salt.  
#     Storing the salt: The salt should be stored securely, either in your database or an external file, so it can be reused to regenerate the same key.
    
#     Returns: 
#         key - the encryption key
#         salt - the randomly generated salt; needs to be stored securely as it will be used to generate the key.

#     ```
#         key, salt = generate_key(keys=[username, password], salt=salt)
#     ```
#     """
#     if salt is None:
#         salt = os.urandom(16)

#     # Combine username and password to make a stronger key input
#     key_material = ":".join(keys).encode('utf-8')
    
#     kdf = PBKDF2HMAC(
#         algorithm=hashes.SHA256(),
#         length=32,  # 256-bit key
#         salt=salt,
#         iterations=iterations,
#         backend=default_backend()
#     )
#     key = base64.urlsafe_b64encode(kdf.derive(key_material))
#     key_str = key.decode('utf-8')
#     return key_str, salt

from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
import base64
import os


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

    # kdf = Argon2id(
    #     memory_cost=2**16, # 64MB # TODO SET TO 48MB IF ON IOS or Android? one of the phones.. do research before shipping.
    #     time_cost=2, # iterations
    #     parallelism=1,
    #     length=32, # key length in bytes
    #     salt=salt
    # )
    kdf = Argon2id(
        salt=salt,
        length=32,         # Desired key length in bytes (256 bits)
        iterations=3,      # Number of iterations (time_cost)
        lanes=1,           # Number of parallel threads (parallelism)
        memory_cost=65536  # Memory cost in KiB (64 MiB)
        # ad and secret are optional and default to None
    )
    # key = kdf.derive(password.encode('utf-8'))
    # key_b64 = base64.urlsafe_b64decode(key).decode('utf-8')
    # return key_b64, salt
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    key_str = key.decode('utf-8')
    return key_str, salt