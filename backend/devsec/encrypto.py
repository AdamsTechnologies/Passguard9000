import os
import base64
import logging
from typing import Union, Any
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from backend.abstracts.abstract_methods import EncryptionInterface


class Encrypto(EncryptionInterface):
    """
        Basic Encryption
        Lightweight Encryptor useful for most encryption needs. handles bytes primarily so you can encrypt/decrypt most things.
        
        This class does not handle Encryption Keys, it expects caller to give it the key.
        
        To generate a key:
            your_key = os.urandom(32)
            Note: its recommended to urlsafe encode your encryption key so it can be stored securely without error. base64.urlsafe_b64encode(obj).decode('utf-8')
        
        Description:
            Encryptor uses AES standard with CFB mode, 256bit key, is one of the more secure encryption options available.  
            init class by passing it your encryption key, then call decrypt or encrypt and pass in the payload you are working on.  
            
        usage:
            ```
                my_key = os.urandom(32)
                encrypt = Encryptor(key=my_key)
                my_value = "Hey I'm going to be encrypted!"
                encrypted_value = encrypt.encrypto(obj=my_value)
                decrypted_value = encrypt.decrypto(obj=encrypted_value)
            ```
    """
    def __init__(self, key: Union[str, bytes]):
        self.key = self._parse_key(key)
        
        
    def _decode(self, obj):
        """decodes object"""
        try:
            return base64.urlsafe_b64decode(obj.encode('utf-8'))
        except Exception as ex:
            logging.warning(f"_decode Error: {str(ex)}")
            raise ex
    
    
    def _encode(self, obj):
        """encodes object"""
        try:
            return base64.urlsafe_b64encode(obj).decode('utf-8')
        except Exception as ex:
            logging.warning(f"_encode Error: {str(ex)}")
            raise ex
    
    
    def _parse_key(self, key:Union[str, bytes]):
        """
        Description:
            helper function supports key management. 
            Allows user to store their key as str encoding, 
            pass it into Encryptor and it'll handle encoding back to bytes.
        """
        if isinstance(key, str):
            return self._decode(key)
        elif isinstance(key, bytes):
            return key
        else:
            raise AttributeError(f"Encryption key expected type Bytes or String, received: {type(key)}") 


    def encrypt(self, obj: bytes) -> bytes:
        """
        Params:
            obj: bytes - the str or bytes you wish to encrypt
        Returns:
            encrypted bytes.
        """
        try:
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(obj) + encryptor.finalize()
            return iv + ciphertext
        except Exception as ex:
            print(f"Encrypt Error! encountered an error while attempting encryption... error message: {str(ex)}")
            raise ex


    def decrypt(self, obj: bytes) -> bytes: #, return_str:bool=False
        """
        Params:
            obj (bytes): the encrypted payload

        Returns:
            Decrypted bytes
        """
        try:
            iv = obj[:16]
            actual_ciphertext = obj[16:]
            cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_text = decryptor.update(actual_ciphertext) + decryptor.finalize()
            return decrypted_text # decrypted_text.decode() if return_str else 
        except Exception as ex:
            print(f"Decrypt Error! encountered an error while attempting decryption... error message: {str(ex)}")
            raise ex
        
    def encrypto(self, obj: Any, encode_errors_method:str='strict') -> str:
        """
        Params:
            obj (Any): the object to encrypt
            encode_errors_method (str): The error handling scheme to use for encoding errors...  e.g., `str.encode(obj, errors='strict')`
                - 'strict'	- Default, raises an error on failure  
                - 'backslashreplace'	- uses a backslash instead of the character that could not be encoded  
                - 'ignore'	- ignores the characters that cannot be encoded  
                - 'namereplace'	- replaces the character with a text explaining the character  
                - 'replace'	- replaces the character with a questionmark  
                - 'xmlcharrefreplace'	- replaces the character with an xml character  

        Returns:
            str: encrypted bytes as url friendly string.
            
        Descrition:
            checks datatype, tries to set to string and encodes in 'utf-8'.
            if catches exception, will try again based on the errors method passed in. 
            Default of strict, will just raise the exception without retry.
            
            calls _encode() on the encrypted response. which encodes it further to a urlsafe format. 
        """
        if not isinstance(obj, bytes):
            try:
                obj = str(obj).encode(encoding='utf-8')
            except (UnicodeEncodeError, TypeError):
                if encode_errors_method != 'strict': # no sense in retrying if using strict mode. 
                    logging.warning(f"Encoding error encountered. Retrying with errors='{encode_errors_method}' mode")
                    obj = str(obj).encode(encoding='utf-8', errors=encode_errors_method)
                else:
                    raise 
        return self._encode(self.encrypt(obj))
    
    def decrypto(self, obj: Any) -> Union[str, bytes]:
        """
        Params:
            obj (Union[str, bytes]):  can be a bytes object or a str representation of encrypted data.

        Returns:
            Union[str, bytes]:  either a string or bytes object.
        
        Descrption:  
            tries to return the decrypted (bytes) decoded() back into a string object, if exception occurs  
            (usually indicating the encrypted object was bytes or some non string encodable format)
            
            The function will retry to decrypt returning response as bytes.
        """
        decoded_obj = self._decode(obj)
        try:
            return self.decrypt(decoded_obj).decode()
        except (UnicodeDecodeError, TypeError):
            logging.warning(f"Decoding error encountered. Retrying without .decode()")
            return self.decrypt(decoded_obj)