import logging
from typing import Any, List, Dict
import inspect

from backend.databaseManager.sql import SQLite
from backend.databaseManager.scripts_generator import scripts


class SQLiteController:
    """
    Params:
        * db_conn: str - sqlite filename default 'base'
        * db: SQLServer - default=None
        * verbose_logging: bool - default=True
        * logger:Any - default=None
        * **params:
            * table_name: str -
            * schema: dict - 
            * upsert_keys: list - 
    """
    def __init__(self, db_file:str='base.db', db:SQLite=None, verbose_logging:bool=True, logger:Any=None, **params):
        super().__init__()
        self.database = db or self._establish_conn(db_file)
        if not self.database:
            raise AttributeError("Could not instantiate class! no db_conn or db received..")
        self.schema = params.get('schema', None)
        self.upsert_keys = params.get('upsert_keys', None)
        self.table_name = params.get('table_name', None)
        self.batch_id = None
        self.verbose_logging = verbose_logging
        self.logger = logger
        self.type_mapping = {
            'nvarchar': 'TEXT',
            'varchar': 'TEXT',
            'char': 'TEXT',
            'bit': 'INTEGER',
            'datetime': 'TEXT',
            'int': 'INTEGER',
            'bigint': 'INTEGER',
            'float': 'REAL',
            'decimal': 'REAL',
            'money': 'REAL',
            'uniqueidentifier': 'TEXT',  # Assuming UUIDs are stored as text
            'binary': 'BLOB',  # For binary data
            'varbinary': 'BLOB'  # For variable-length binary data
            }


    def convert_schema(self, schema:dict=None):        
        """
        abstract methods store schemas in SQL92 format, since SQLite is kindof an outlier for datatypes 
        we preserve the SQL92 format in source and just convert it to sqlite schema on the fly.
        """
        active_schema = schema or self.schema
        for k, v in active_schema.items():
            addons = []
            # Identify the field's special conditions
            if 'NOT NULL' in v.upper():
                v = v.replace('NOT NULL', '').strip()
                addons.append('NOT NULL')
            if 'UNIQUE' in v.upper():
                v = v.replace('UNIQUE', '').strip()
                addons.append('UNIQUE')
            if 'PRIMARY KEY' in v.upper():
                v = v.replace('PRIMARY KEY', '').strip()
                addons.append('PRIMARY KEY')
            type_part = v.split('(')[0].strip()
            # get sqlite datatype - default 'TEXT'
            sqlite_type = self.type_mapping[type_part] if type_part in self.type_mapping else 'TEXT'
            # create Schema script by joining the sqlite datatype and the special conditions. 
            # e.g., "myField varchar(200) NOT NULL" becomes "myField TEXT NOT NULL"
            active_schema[k] = f"{sqlite_type}{' ' if len(addons) > 0 else ''}{' '.join(addons)}"
        #set schema
        self.schema = active_schema
        return self.schema
        

    def _establish_conn(self, db_file:dict):
        return SQLite(db_file=db_file)
    

    def _log_message(self, log_msg, **params):
        """writes logs to custom logger or logging.severity if no logger passed in."""
        # allows us to log errors regardless of log flag. so still pass in a logger with log flag = False to get errors logged.
        if self.verbose_logging or params.get('exception', False):
            if self.logger:
                calling_func = f"database_controller.{inspect.stack()[2].function}"
                self.logger.log(message=log_msg,function_name=calling_func, **params)
            else:
                severity = params.pop('severity', 'info')
                for k, v in params.items():
                    log_msg += f",{k}:{v}"
                log_method = getattr(logging, severity, logging.info)
                log_method(log_msg)
    

    def get_batch_no(self, table_name, incr_field, cursor=None):
        if self.batch_id is None:
            incr_script = scripts.get_max_incrementor_script(table_name, incr_field)
            if cursor:
                cursor.execute(incr_script)
                resp = cursor.fetchone()
                self._log_message(log_msg=f"{resp=}",system_generated=True)
                self.batch_id = resp[f'max_{incr_field}']
            else:
                self.batch_id = (self.database.query(incr_script))[0][0] #[f'max_{incr_field}'] #TODO figure out what the response looks like..
        self._log_message(log_msg=f"{self.batch_id=}", severity='info', system_generated=True)
        return self.batch_id
    

    # def _create_db_schema_script(self,:
    #     self.schema_name = schema_name
    #     return scripts.create_db_schema_script(schema_name)
    

    def _create_table_script(self, table_name:str, schema:dict):
        if isinstance(schema, dict):
            self.schema = schema
            self.table_name = table_name
            columns = ', '.join([f"{col} {datatype}" for col, datatype in self.schema.items()])
            return scripts.create_table_script(table_name, columns)
        else:
            raise ValueError(f"Invalid schema format. Must be a dict. received: {type(schema)}")

    """CREATE SCHEMA.TABLE IF NEEDED"""

    def create_schema_and_table_if_not_exists(self, table_name:str, schema:dict, incr_field:str=None):
        """
        checks if schema exists, if not creates, checks if tablename exists, if not creates.
        incr_field - used if you want your table to have a batch_id type field. 
        requires  table_name:str, schema:dict.`

        e.g.,

        ```
        schema = dict(primaryId="int", fName="nvarchar(25)", city="nvarchar(50)", state_abbrev="nvarchar(2)")
        table_name = 'my_table'
        incr_field = 'batch_no'

        #response
        {'status_code': 200, 'severity': 'info', 'log_msg': 'Appended 5 rows to mySchema.my_table.', 'system_generated': True}
        ```
        
        """
        if incr_field:
            schema[incr_field] = 'INTEGER'
        # self.database.execute_commands(sql=self._create_db_schema_script(schema_name)) #TODO SQLITE does not have schemas
        sql=self._create_table_script(table_name, schema)
        self.database.execute_commands(sql=sql)
        if incr_field:# why'd I do this to myself.
            self.get_batch_no(table_name, incr_field)
        success_response= dict(status_code=200, log_msg=f"Successfully created {table_name}", table_name=table_name, incr_field=incr_field, schema=schema, system_generated=True)
        self._log_message(**success_response)
        return success_response
    
    # is subclass parents log_exceptions.
    def _process_data(self, table_name: str, data: List[Dict[str, Any]], incr_field:str=None, batch_size:int=1000, unique_keys: List[str] = None):
        if not data:
            self._log_message(log_msg="No data provided for processing.", severity='warning')
            return
        with self.database.connection_manager() as cursor:
            if incr_field:
                batch_id = self.get_batch_no(table_name, incr_field, cursor)
                batch_id_update = {incr_field: int(batch_id)}

            total_rows = len(data)
            for i in range(0, total_rows, batch_size):
                batch_data = data[i:i + batch_size]
                if incr_field:
                    batch_data = [dict(item, **batch_id_update) for item in batch_data]
                else:
                    query, values = scripts.create_insert_statement(table_name, batch_data)
                cursor.executemany(query, values)
            
            resp = dict(status_code=200, severity='info', log_msg=f"Appended {total_rows} rows to {table_name}.", system_generated=True)
            self._log_message(**resp)
            return resp

    def _upsert_data(self, table_name:str, data:List[Dict[str, Any]], incr_field:str=None, unique_keys: List[str] = None):
        if not data:
            self._log_message(log_msg="No data provided for processing.", severity='warning')
            return
        with self.database.connection_manager() as cursor:
            if incr_field:
                batch_id = self.get_batch_no(table_name, incr_field, cursor)
                batch_id_update = {incr_field: int(batch_id)}
                data = [dict(item, **batch_id_update) for item in data]
            for row in data:
                update_query, values = scripts.create_update_statement(table_name=table_name, data=row, unique_keys=unique_keys)

                cursor.execute(update_query, values)
                if cursor.rowcount == 0:
                    logging.info('must insert...')
                    insert_query, values = scripts.create_insert_statement(table_name=table_name, data=[row])
                    logging.info(f"{insert_query}, {values}")
                    cursor.execute(insert_query, values[0])
                
        resp = dict(status_code=200, severity='info', log_msg=f"Upserted {len(data)} rows to {table_name}.", system_generated=True)
        return resp


    def append_data(self, table_name: str, data: List[Dict[str, Any]], incr_field:str=None, batch_size:int=1000):
        """
        Appends data to the specified table. appends in batches of 1000

        Params:
            table_name - str: The name of the table.
            data - list[dict]: A list of dictionaries where each dictionary represents a row to insert.
                               The keys should match the column names of the table.
            incr_field - str: name of incremental field if you use one. such as `batch_id` or `execution_id`. Default = None
            batch_size - int: function appends data in batches. this param allows you to determine the batch size. Default = 1000
        Example:
            ```
            table_name='my_table'
            data = [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"}
            ]
            ```
        """
        return self._process_data(table_name, data, incr_field, batch_size)
        

    def upsert_data(self, table_name:str, data:List[Dict[str, Any]], unique_keys:List[str], incr_field:str=None, batch_size:int = 1000):
        """
        Upserts data to the specified table.
        
        Params:
            table_name - str: The name of the table.
            data - list[dict]: A list of dictionaries where each dictionary represents a row to upsert.
                               The keys should match the column names of the table.
            unique_keys - list[str]: A list of column names that uniquely identify each row.
            batch_size - int: The size of batches to insert. TODO not used in sqllite
        Example:
            ```
            table_name='my_table'
            data = [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"}
            ]
            unique_keys = ["column1"]
            ```
        """
        return self._upsert_data(table_name, data, incr_field, unique_keys)
    
    def _execute_query(self, table_name:str, select_cols:list=None, conditions:dict=None, return_single:bool=False):
        """
        Executes query
        
        Params:
            table_name: str
            select_cols: list
            conditions: dict
            return_single: bool   

        Example:
            TODO            
        
        """
        query = scripts.get_query(table_name=table_name, select_cols=select_cols, conditions=conditions)
        resp = self.database.query(query)
        if resp:
            return resp[0] if return_single and isinstance(resp, list) else resp
        else:
            return None
    """
    --------------------------ABSTRACT METHODS OPERATIONS--------------------------
    """
    def compare_values(self, key, **params):
        """
        Params:
            key : str - the key you wish to compare again. e.g, 'schema'
            **kwargs: any
        Description:
            tries to find key in params, as incoming
            tries to find key in class attributes, as old

            compares if incoming is different than currently set value.
        returns
            inc if its different than whats set in self.[key]
        """
        return inc if (inc := params.get(key, None)) != (old := getattr(self, str(key), None)) else old

    def create_if_not_exists(self, *args, **params):
        self.table_name = self.compare_values('table_name', **params)
        self.schema = self.compare_values('schema', **params)
        self.convert_schema(schema=self.schema) # abstract method has a SQLSErver / SQL92 style schema.. this aligns it with sqlite... TODO
        self.create_schema_and_table_if_not_exists(table_name=self.table_name, schema=self.schema, incr_field=params.get('incr_field', None))
        return dict(status_code=202, message=f"{self.table_name} exists")

    def get_record(self, *args, **params)->dict:
        if not self.upsert_keys:
            raise ValueError("Unique Keys for upsert(get) are not defined.")
        conditions = {key:value for key,value in params.items() if key in self.upsert_keys}
        return self._execute_query(table_name=self.table_name, select_cols=['*'], conditions=conditions, return_single=True)
    
    # get_item(section=self.keystore.key_section, field=self.keystore.key_field)
    def get_item(self, *args, **params) -> str:
        """gets specific column"""
        if not self.upsert_keys:
            raise ValueError("Unique Keys are not defined. These are used to query for your specific record..")
        # search kwargs for key fields found in self.upsert_keys - we will use these to identify keys to build our query off of aka, "conditions".
        conditions = {key:value for key,value in params.items() if key in self.upsert_keys} 
        resp = self._execute_query(table_name=self.table_name, select_cols=[(field:=params.get('field'))], conditions=conditions, return_single=True)
        if not resp:
            return None
        return resp.get(field, None)

    def set_item(self,*args, **params):
        """retrieve the field from params and maps it to the schema."""
        try:
            upsert_data = {key:params.get(key) for key in self.schema.keys()}
            self.upsert_data(table_name=self.table_name, data=[upsert_data], unique_keys=self.upsert_keys)
            return dict(status_code=202, message=f"Successfully upsert record.")
        except Exception as ex:
            raise ex

    def get_all_items(self, *args, **params):
        return self._execute_query(table_name=self.table_name, select_cols=['*'], return_single=params.get('return_single', False))

    def remove(self, *args, **params):
        conditions = {key:value for key,value in params.items() if key in self.upsert_keys}
        cmd = scripts.get_delete_record_script(table_name=self.table_name, conditions=conditions)
        resp = self.database.execute_commands(cmd)
        return dict(status_code=202, message=f"Successfully deleted record.")

    def execute_operation(self, *args, **params):
        return dict(status_code=404, msg='execute_operation, nahh I dont think i will..')

    """ 
    --------------------------------------------------------
    underbelly of weird functions --------------------------
    --------------------------------------------------------
    """

    # def create_schema_if_not_exists(self, schema_name):
    #     """
    #     This probably shouldn't be used, but I'm leaving them available.
    #     Using create_schemas or create_table will allow for weird side-effects to happen.
        
    #     useful if you wish to change context and write to a different table with the class instantiation.. 
    #     but beware this opens potential for side effects.
    #     """
    #     create_db_schema_script = self._create_db_schema_script(schema_name=schema_name)
    #     result = self.database.query(create_db_schema_script)
    #     self._log_message(status_code=200,severity='info',log_msg=f"Schema '{schema_name}' {result=}",system_generated=True)


    def create_table_if_not_exists(self, table_name:str, schema:dict):
        """
        This probably shouldn't be used, but I'm leaving them available. 
        Using create_schemas or create_table will allow for weird side-effects to happen.
        itll work really well if you do it right.

        useful if you wish to change context and write to a different table with the class instantiation.. 
        but beware this opens potential for side effects.
        """
        create_table_script = self._create_table_script(table_name, schema)
        result = self.database.query(create_table_script)
        self._log_message(status_code=200,severity='info',log_msg=f"Table '{table_name}' {result=}",system_generated=True)