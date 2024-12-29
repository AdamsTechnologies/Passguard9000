import json
import hashlib

def hash_object(obj, salt=""):
    """
    Deterministically hash an object (e.g., a username) using SHA-256.
    
    Args:
        obj (any): The object to be hashed. It must be JSON-serializable.
        salt (str): Optional salt to add to the hash for extra security.
    
    Returns:
        str: The SHA-256 hash as a hexadecimal string.
    """
    try:
        obj_string = json.dumps(obj, sort_keys=True, default=None)
        data = (salt + obj_string).encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    except (TypeError, ValueError) as e:
        raise ValueError("The object must be JSON-serializable.") from e
