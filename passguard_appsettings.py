from backend.devsec.encrypto import Encrypto
from backend.controllers.database_controller import SQLiteController

class AppInit:
    def __init__(self):
        self.settings_schema = dict(
            r='INTEGER',
            s='TEXT',
            color_theme='TEXT',
            appearance_theme='TEXT',
            # TODO can expand settings here.
        )
        self.upsert_keys = ['r','s'] # obfuscation!
        
        self.settings = SQLiteController(db_file='app_settings.db', table_name='setting', schema=self.settings_schema, upsert_keys=self.upsert_keys)
        self.encrypto = Encrypto
        self.key = None
        self._initialize_settings()
    
    """
    ------------- Init -------------
    """

    def _check_if_exists(self, store):
        # if store.controller has attribute, elif store has attribute, else None... 
        if hasattr(store, 'controller'):
            schema_name = getattr(store.controller, 'schema_name', None)
            table_name = getattr(store.controller, 'table_name', None) #UwU
        else:
            schema_name = getattr(store, 'schema_name', None)
            table_name = getattr(store, 'table_name', None)
        schema = getattr(store, 'schema', None) 

        return store.create_if_not_exists(schema_name=schema_name, table_name=table_name, schema=schema)
    
    def _setup_store(self, store):
        self._check_if_exists(store)
        if hasattr(store, 'controller'):
            if hasattr(store.controller, 'upsert_keys'):
                # had inheritance issue.. this forces controller to get upsert_keys if it should have it.
                store.controller.upsert_keys = store.upsert_keys

    def _initialize_settings(self):
        self._setup_store(store=self.settings)

    """
    ------------- Retrieve Data -------------
    """

    def retrieve_settings(self):
        return self.settings.get_all_items(return_single=True) # settings are just 1 record. I don't see value in appending changes.. maybe bonus feature.

    def retrieve_setting(self, **params):
        """
        Params Expecting:
            Upsert Keys:
                ```
                r,
                s
                ```
        """
        return self.settings.get_record(**params) # getting pretty nested..
    
    """
    ------------- Set Data -------------
    """
    def set_setting(self, **params):
        """
        Params Expecting:
            ```
            r,
            s,
            color_theme,
            appearance_theme,
            ```
        """
        return self.settings.set_item(**params)
