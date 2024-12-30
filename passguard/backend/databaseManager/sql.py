import os
import logging
import sqlite3
from io import BytesIO
from collections import namedtuple
from contextlib import contextmanager
from passguard.backend.abstracts.abstract_methods import DatabaseInterface

class SQLite(DatabaseInterface):
    """
    Simple but efficient database class. Utilize to query SQLite database or execute commands.
    Note: does not validate inputs; relies on sqlite3 validations.
    
    Params:
            db_file (str): Path to the SQLite database file or ':memory:' for in-memory DB.
            db_bytes (bytes): Optional; decrypted database content to load into memory.
            uri (bool): Use URI mode for SQLite connections.

    Example usage:
    ```
        query = 'SELECT * FROM my_table'
        sql = SQLiteDB(db_file='my_database.db')
        query_response = sql.query(query=query)
    ```
    Functions available:
    ```
        sql.connection_manager()
        sql.query(query: Union[str, tuple])
        sql.execute_commands(sql: any)
    """
    # TODO this is about 99% identical to SQLServer... lets join 'em together..
    def __init__(self, db_file: str, db_bytes:bytes=None, uri:bool=False):
        if uri:
            self.db_file=db_file
        else:
            if db_file == ':memory:':
                self.db_file = ':memory:'
            elif os.path.exists(db_file) or os.path.isabs(db_file):
                # Use the provided db_file as is if it exists or is an absolute path
                self.db_file = db_file
            elif not db_file.endswith('.db'):
                # Append .db if the file doesn't exist and doesn't have .db extension
                self.db_file = f"{db_file}.db"
            else:
                self.db_file = db_file
            # self.db_file = ':memory:' if ':memory:' in db_file else f"{db_file}.db" if not db_file.endswith('.db') else db_file
        self.uri=uri
        self.conn = None
        self.db_bytes = db_bytes
    
    def _connect(self):
        if self.conn is None:
            try:
                if self.db_bytes:
                    # Load database from byte stream
                    self.conn = sqlite3.connect(':memory:')
                    byte_stream = BytesIO(self.db_bytes)
                    disk_conn = sqlite3.connect(f"file:{self.db_file}?mode=memory&cache=shared", uri=True)
                    with disk_conn:
                        disk_conn.backup(self.conn)
                    disk_conn.close()
                else:
                    # Regular connection
                    self.conn = sqlite3.connect(self.db_file, uri=self.uri)
            except sqlite3.Error as ex:
                logging.error(f"Connection failed.")
                raise ex
            
    # def _connect(self):
    #     if self.conn is None:
    #         try:
    #             self.conn = sqlite3.connect(self.db_file, uri=self.uri)
    #         except sqlite3.Error as ex:
    #             logging.error(f"Connection failed.")
    #             raise ex

    def _close_up(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def warm_up(self, retry:int=0):
        """
        Useful for other databases, but not SQLite..
        """
        logging.info('SQLite does not need warmed up...')
    
    def dict_factory(self, cursor, row):
        """
        SQLite factory method to convert response to dict
        https://docs.python.org/3/library/sqlite3.html#sqlite3-adapter-converter-recipes
        """
        fields = [column[0] for column in cursor.description]
        return {k:v for k,v in zip(fields, row)}

    def namedtuple_factory(self, cursor, row):
        """
            With some adjustments, the above recipe can be adapted to use a dataclass, or any other custom class, instead of a namedtuple.
            https://docs.python.org/3/library/sqlite3.html#sqlite3-adapter-converter-recipes
        """
        fields = [column[0] for column in cursor.description]
        cls = namedtuple("Row", fields)
        return cls._make(row)

    @contextmanager
    def connection_manager(self, as_dict:bool = True, close_up:bool = False):
        """
        Developers sandbox.
        Use built-in functions or create your own.
        This context manager opens a connection, yields a cursor, commits, and closes up afterwards.
        ```
           with sql.connection_manager() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                # do more stuff...
        ```
        """
        self._connect()
        try:
            if as_dict:
                self.conn.row_factory = self.dict_factory
            cursor = self.conn.cursor()
            yield cursor
            self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            logging.error(f"An error occurred: {ex}")
            raise ex
        finally:
            if close_up: # TODO THIS WILL NEED LIGHT REFACTORING OF ALL CONSUMERS TO ACCOMODATE - THEY ORIGINALLY EXPECTED AUTO CLOSE UP
                # ENCOUNTERED CASE WHERE WE NEED CONNECTION TO STAY OPEN DURING OPERATION -- FOR IN MEMORY DATABASES. 
                # TODO NEEDS REFACTORED FOR!!!!
                cursor.close()
                self._close_up()

    def query(self, query) -> list:
        """
        Execute queries.
        Params:
            query - str|tuple: the query to execute on the db.
                Note: *query can be a string or tuple for parameterized query.
                e.g.,
                ```
                resp = query(('SELECT * FROM table WHERE ?=?', where_col, value)) # tuple
                resp = query('SELECT * FROM table') # string
                ```
        """
        with self.connection_manager() as cursor:
            try:
                cursor.execute(*query) if isinstance(query, tuple) else cursor.execute(query)
                results = cursor.fetchall()
                return results
            except Exception as ex:
                logging.error(f"failed executing query.")
                raise ex

    def execute_commands(self, sql: any):
        """
        Params:
            sql - `str|tuple / list[str|tuple]`: a single command, or a list of commands
            Allows parameterized commands

        ```
        # Examples
        execute_commands(sql=["cmd1", "cmd2", ('INSERT INTO table (col) VALUES (?)', ('value',)), "cmd4"])
        execute_commands(sql=('INSERT INTO table (col) VALUES (?)', ('value',)))
        execute_commands(sql='PRAGMA foreign_keys=ON')
        ```
        """
        with self.connection_manager() as cursor:
            sql_cmds = sql if isinstance(sql, list) else [sql]
            for cmd in sql_cmds:
                try:
                    cursor.execute(*cmd) if isinstance(cmd, tuple) else cursor.execute(cmd)
                except Exception as ex:
                    logging.error(f"Failed to execute command.")
                    raise ex