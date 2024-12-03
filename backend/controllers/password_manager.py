from backend.abstracts.abstract_methods import PasswordStorageInterface, EncryptionInterface, KeyStorageInterface
from datetime import datetime, timezone
from typing import Any
import os
import logging
import base64
from uuid import uuid4
import binascii

# TODO Salt password.

class PasswordController:
    """
    Params:
        * encrypto: EncrypytionInterface - 
        * keystore: KeyStoreInterface - 
        * passtore: PasswordStorageInterface - 
        * **params:
            * schema_name: str -  
            * table_name: str - 
            * schema: dict -  PasswordStorageInterface has a default schema.
            * section: str - Default 'items'
            * field: str - Default 'item'
            * check_if_exists_flag: bool - Default True
    """
    def __init__(self, encrypto:EncryptionInterface, keystore:KeyStorageInterface, passtore:PasswordStorageInterface,  **params):
        self.passtore = passtore
        self.encrypto = encrypto
        self.keystore = keystore
        self.key = None
        self._initialize_key()
        self._initialize_pass()
    
    # TODO better method documentation...
    
    """
    ------------------- ENCRYPTION -------------------
    """
    def _decrypt_item(self, result)->str:
        """decrypts single field"""
        try:
            return self.encrypto.decrypto(obj=result) # You're a wizard!
        except binascii.Error:
            logging.error(f"binascii.Error: Likely a bad encryption key..")
        except UnicodeDecodeError as ex:
            logging.error(f"UnicodeDecodeError: y tho?")
            raise ex
    
    def _decrypt_items(self, obj:dict, decrypt_fields:list)->dict:
        """
        Params:
            obj:dict - the record as a dictionary. 
            decrypt_fields:list - list of field names that are encrypted.
        
        replaces obj's encrypted values with decrypted ones."""
        return {key: (self._decrypt_item(value) if key in decrypt_fields else value) 
                for key, value in obj.items()}
    """
    ------------------- Key Wrangling -------------------
    """
    def _check_if_exists(self, store):
        schema_name = getattr(store.controller, 'schema_name', None)
        table_name = getattr(store.controller, 'table_name', None)
        schema = getattr(store, 'schema', None)
        return store.create_if_not_exists(schema_name=schema_name, table_name=table_name, schema=schema)
    
    def setup_store(self, store):
        self._check_if_exists(store)
        if hasattr(store.controller, 'upsert_keys'):
            # had inheritance issue.. this forces controller to get upsert_keys if it should have it.
            store.controller.upsert_keys = store.upsert_keys
    
    def _set_key(self):
        encoded_key = self.encrypto._encode(obj=self.key)
        data = {(key_sect:=self.keystore.key_section): key_sect, 
                self.keystore.key_field: encoded_key}
        return self.keystore.set_item(key_field=key_sect, **data)
    
    def _initialize_key(self):
        self.setup_store(store=self.keystore)
        raw_key = self.keystore.get_item(section=self.keystore.key_section, field=self.keystore.key_field)
        self.key = base64.urlsafe_b64decode(raw_key.encode('utf-8')) if raw_key else None
        if self.key is None:
            self.key = os.urandom(32)
        self.encrypto = self.encrypto(key=self.key)
        self._set_key()
    """
    ------------------- Password Wrangling -------------------
    """
    def _initialize_pass(self):
        self.setup_store(store=self.passtore)

    def get_password(self, id:str, decrypt:bool=False) -> str:
        params = dict(id=id, section=id, field='password')
        result = self.passtore.get_item(**params)
        if result:
            return self._decrypt_item(result) if decrypt else result
        else:
            raise AttributeError(f"password not found in database.. {result=}")
    
    def get_record(self, id:str, decrypt_fields:list=None):
        params = dict(id=id, section=id)
        result = self.passtore.get_record(**params)
        return self._decrypt_items(obj=result, decrypt_fields=decrypt_fields) if decrypt_fields else result

    def get_all_records(self, decrypt_fields:list=None):
        result = self.passtore.get_all_items()
        if decrypt_fields:
            decrypted_records = []
            for r in result:
                decrypted_records.append(self._decrypt_items(obj=r, decrypt_fields=decrypt_fields))
            return decrypted_records
        return result

    def upsert_record(self, username: str, password: str, service:str=None, servicetype:str=None, url:str=None, id:str=None, isactive:bool=True):
        """
        UPSERTs a single record
        """
        if not id:
            id = str(uuid4())

        dt = datetime.now(timezone.utc)
        data = {
            'id':id,
            'username': username, 
            'password': self.encrypto.encrypto(password), 
            'service': service, 
            'servicetype': servicetype, 
            'isactive':isactive,
            'url':url,
            'dt':dt
            }
        return self.passtore.set_item(key_field=service, **data) # iniController friendly.
    
    def upsert_multiple_records(self, data:list):
        """
        loops over data list; tries to call upsert_record() for each item in list.
        catches errors and logs them.
        """
        error_list = []
        for record in data:
            try:
                self.upsert_record(**record)
            except Exception as ex:
                error_list.append({**record, 'error':ex})
        if error_list:
            logging.warning(f"{len(error_list)} errors occured while processing upsert_multiple_records.. {error_list}")

    def remove_record(self, **params):
        """
        Params:
            if passtore is database:
                'id'
            if passtore is config file:
                'section', 'field' 
            if you want to be extra safe or cover all use-cases..pass in all
        
        ```
        remove_record(id='uuid4', section='myBank', field='password')
        ```
        """
        return self.passtore.remove(**params)