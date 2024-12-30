from abc import ABC, abstractmethod
from typing import Any, Union

class EncryptionInterface(ABC):
    @abstractmethod
    def _decode(self, obj):
        pass
    def _encode(self, obj):
        pass
    @abstractmethod
    def encrypt(self, obj:str) -> str:
        pass
    @abstractmethod
    def decrypt(self, obj:str) -> str:
        pass
    @abstractmethod
    def decrypto(self, obj:Any) -> Union[str, bytes]:
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
        pass
    @abstractmethod
    def encrypto(self, obj:Any, encode_errors_method:str='strict')->str:
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
        pass

class DatabaseInterface(ABC):
    @abstractmethod
    def connection_manager(self, *args, **kwargs):
        pass
    @abstractmethod
    def query(self, *args, **kwargs):
        pass
    @abstractmethod
    def execute_commands(self, *args, **kwargs):
        pass
    @abstractmethod
    def warm_up(self, *args, **kwargs):
        pass

class BaseInterface(ABC):
    def __init__(self, controller, schema, upsert_keys):
        self.controller = controller
        self.schema = schema
        self.upsert_keys = upsert_keys
    @abstractmethod
    def set_item(self, *args, **kwargs):
        pass
    @abstractmethod
    def get_item(self, *args, **kwargs):
        pass
    @abstractmethod
    def get_record(self, *args, **params):
        pass
    @abstractmethod
    def get_all_items(self, *args, **params):
        pass
    @abstractmethod
    def create_if_not_exists(self, *args, **params) -> dict:
        pass
    @abstractmethod
    def execute_operation(self, *args, **params):
        pass
    
class KeyStorageInterface(BaseInterface):
    def __init__(self, controller, key_section:str='section', key_field:str='field'):
        super().__init__(controller, 
                        schema=dict(section='nvarchar(1000)',field='nvarchar(MAX)'),
                        upsert_keys = ['section'])
        self.key_section = 'section' # TODO review this hard-coding.
        self.key_field = 'field'
        
    def set_item(self, *args, **params):
        return self.controller.set_item(*args, **params)
    def get_item(self, *args, **params):
        """
        pass in kwargs - will be used as key:value pairs
        """
        return self.controller.get_item(*args, **params)
    def get_record(self, *args, **params):
        return self.controller.get_record(*args, **params)
    def get_all_items(self, *args, **params):
        return self.controller.get_all_items(*args, **params)
    def remove(self, *args, **params):
        return self.controller.remove(*args, **params)
    def create_if_not_exists(self, *args, **params) -> dict:
        return self.controller.create_if_not_exists(*args, **params)
    def execute_operation(self, *args, **params):
        return self.controller.execute_operation(*args, **params)

class PasswordStorageInterface(BaseInterface):
    def __init__(self, controller):
        super().__init__(controller, schema = dict(
                id='nvarchar(50) PRIMARY KEY',
                username='nvarchar(256)', 
                password='nvarchar(256)', 
                service='nvarchar(1000)', 
                servicetype='nvarchar(1000)', 
                isactive='bit', 
                url='nvarchar(MAX) NULL',
                dt='datetime',
                ), 
                upsert_keys = ['id']) # TODO review this hard-coding.
    def set_item(self, *args, **params):
        return self.controller.set_item(*args, **params)
    def get_item(self, *args, **params):
        return self.controller.get_item(*args, **params)
    def get_all_items(self, *args, **params):
        return self.controller.get_all_items(*args, **params)
    def get_record(self, *args, **params):
        return self.controller.get_record(*args, **params)
    def remove(self, *args, **params):
        return self.controller.remove(*args, **params)
    def create_if_not_exists(self, *args, **params) -> dict:
        return self.controller.create_if_not_exists(*args, **params)
    def execute_operation(self, *args, **params):
        return self.controller.execute_operation(*args, **params)