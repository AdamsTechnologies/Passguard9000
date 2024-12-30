import os
import base64
import logging
from typing import Union
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from passguard.backend.abstracts.abstract_methods import EncryptionInterface

class Encrypto(EncryptionInterface):
    """
    Secure encryption class using AES-GCM for authenticated encryption.
    """

    def __init__(self, key: Union[str, bytes]):
        """
        Initializes the Encrypto class with a 256-bit (32-byte) key.

        :param key: The encryption key as bytes or a base64-encoded string.
        :raises ValueError: If the key is not 32 bytes long.
        """
        self.key = self._parse_key(key)
        if len(self.key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits) for AES-256.")
    
    def _decode(self, obj):
        """decodes object"""
        try:
            return base64.urlsafe_b64decode(obj.encode('utf-8'))
        except Exception as ex:
            logging.warning(f"decode Error")
            raise ex
    
    def _encode(self, obj):
        """encodes object"""
        try:
            return base64.urlsafe_b64encode(obj).decode('utf-8')
        except Exception as ex:
            logging.warning(f"encode Error")
            raise ex

    def _parse_key(self, key: Union[str, bytes]) -> bytes:
        if isinstance(key, str):
            try:
                return base64.urlsafe_b64decode(key.encode('utf-8'))
            except Exception:
                raise ValueError("Invalid key format. Key must be a base64-encoded string.")
        elif isinstance(key, bytes):
            return key
        else:
            raise TypeError(f"Encryption key must be bytes or a base64-encoded string, not {type(key)}.")

    def encrypt(self, obj: bytes) -> bytes:
        """
        Encrypts the given data using AES-GCM.

        :param data: Data to encrypt (bytes).
        :return: Encrypted data with nonce prepended (bytes).
        """
        nonce = os.urandom(12)  # AESGCM nonce size is 12 bytes
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, obj, None)
        return nonce + ciphertext

    def decrypt(self, obj: bytes) -> bytes:
        """
        Decrypts the given data using AES-GCM.

        :param data: Encrypted data with nonce prepended (bytes).
        :return: Decrypted plaintext data (bytes).
        :raises ValueError: If decryption fails (e.g., due to authentication failure).
        """
        if len(obj) < 13:  # 12 bytes nonce + at least 1 byte ciphertext
            raise ValueError("Invalid data. Not enough data to extract nonce and ciphertext.")
        nonce = obj[:12]
        ciphertext = obj[12:]
        aesgcm = AESGCM(self.key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext

    def encrypto(self, obj: bytes) -> str:
        """
        Encrypts data and encodes the result as a base64 string.

        :param data: Data to encrypt (bytes).
        :return: Base64-encoded encrypted data (str).
        """
        if not isinstance(obj, bytes):
            try:
                obj = str(obj).encode(encoding='utf-8')
            except Exception as ex: #(UnicodeEncodeError, TypeError)
                raise 
        return self._encode(self.encrypt(obj))

    def decrypto(self, obj: str) -> bytes:
        """
        Decrypts data from a base64-encoded string.

        :param data: Base64-encoded encrypted data (str).
        :return: Decrypted plaintext data (bytes).
        """
        decoded_obj = self._decode(obj)
        try:
            return self.decrypt(decoded_obj).decode()
        except (UnicodeDecodeError, TypeError):
            logging.warning(f"Decoding error encountered. Retrying without .decode()")
            return self.decrypt(decoded_obj)