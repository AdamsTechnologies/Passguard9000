import json
import base64
from passguard.settings_definition import SETTINGS_DEFINITION
from passguard.backend.controllers.database_controller import SQLiteController

class SettingsManager:
    def __init__(self, db_path='app_settings.db'):
        self.table_name = 'settings'
        self.schema = {
                "key": "TEXT PRIMARY KEY",
                "value": "TEXT",
            }
        self.upsert_keys = ['key']
        
        self.db = SQLiteController(
            db_file=db_path,
            table_name=self.table_name,
            schema=self.schema,
            upsert_keys=self.upsert_keys
        )
        # Ensure table is created
        self._check_if_exists()
        self._settings_cache = {}

        # Load everything on startup
        self.load_all_settings()

    def _check_if_exists(self):
        self.db.create_if_not_exists(table_name=self.table_name, schema=self.schema)

    def _parse_values(self, raw_value, desired_type):
        if desired_type == int:
            parsed_value = int(raw_value)
        elif desired_type == float:
            parsed_value = float(raw_value)
        elif desired_type == bool:
            parsed_value = (raw_value.lower() == "true")
        elif desired_type == bytes:
            parsed_value = base64.b64decode(raw_value)
        else:
            parsed_value = raw_value
        return parsed_value

    def load_all_settings(self):
        """
            1) Pull all rows from the DB (key, value).
            2) Parse them (cast them to correct Python type).
            3) If something is missing, use the default.
        """
        rows = self.db.get_all_items(return_single=False)
        db_dict = {row["key"]: row["value"] for row in rows} if rows else {}

        for key, definition in SETTINGS_DEFINITION.items():
            desired_type = definition["type"]
            default_value = definition.get("default")

            if key in db_dict:
                raw_value = db_dict[key]
                # Attempt to cast the raw_value to desired_type
                try:
                    parsed_value = self._parse_values(raw_value=raw_value, desired_type=desired_type)
                except (ValueError, TypeError):
                    # fallback to default if cast fails
                    parsed_value = default_value
            else:
                parsed_value = default_value

            self._settings_cache[key] = parsed_value
    

    def get(self, key):
        """
            Get a setting from the in-memory cache.
        """
        return self._settings_cache.get(key, None)
    
    
    def get_all(self):
        """
            Return all settings as a dict (in-memory).
        """
        return dict(self._settings_cache)
    
    def set(self, key, value):
        """
            1) Update the in-memory cache.
            2) Convert value to string and persist in DB.
        """
        if key not in SETTINGS_DEFINITION:
            raise KeyError(f"Unknown setting '{key}'")
        
        desired_type = SETTINGS_DEFINITION[key]["type"]
        self._settings_cache[key] = value
        
        if desired_type == bytes:
            str_value = base64.b64encode(value).decode("ascii")
        else:
            str_value = str(value)
        self.db.set_item(key=key, value=str_value)
        self.load_all_settings() # reload cache.


    def set_items(self, obj:dict):
        """
            can set multiple items before the cache is re-loaded.. 
        """
        for key,value in obj.items():
            desired_type = SETTINGS_DEFINITION[key]["type"] if key in SETTINGS_DEFINITION else str
            self._settings_cache[key] = value
            
            if desired_type == bytes:
                str_value = base64.b64encode(value).decode("ascii")
            else:
                str_value = str(value)
            self.db.set_item(key=key, value=str_value)
        self.load_all_settings() # reload cache.


    