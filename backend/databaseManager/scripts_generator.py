from typing import List, Dict, Any, Tuple

class scripts: 
    # TODO Tech Debt Schemas are not used in sqlite.
    # this whole thing needs refactoring.. 
    @staticmethod
    def check_table_exists_script(table_name: str, schema_name:str=None) -> Tuple[str, Tuple]:
        return f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)

    @staticmethod
    def create_table_script(table_name: str, columns: dict, schema_name:str=None) -> str:
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"

    @staticmethod
    def create_insert_statement(table_name: str, data: List[Dict[str, Any]], schema_name:str=None) -> Tuple[str, List[Tuple]]:
        if not data:
            return "", []

        columns = data[0].keys()
        columns_str = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(columns))

        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        values = [tuple(row[col] for col in columns) for row in data]
        return insert_query, values
    
    @staticmethod
    def create_update_statement(table_name: str, data:Dict[str, Any], unique_keys: List[str], schema_name:str=None) -> Tuple[str, List[Tuple]]:
        columns = data.keys()
        unique_condition = ' AND '.join([f"{key} = ?" for key in unique_keys])
        updates = ', '.join([f"{col} = ?" for col in columns]) # if col not in unique_keys
        
        update_query = f"UPDATE {table_name} SET {updates} WHERE {unique_condition}"
        values = tuple(data[col] for col in columns) + tuple(data[key] for key in unique_keys)
        return update_query, values

    @staticmethod
    def create_merge_statement(table_name: str, data: List[Dict[str, Any]], unique_keys: List[str], schema_name:str=None) -> Tuple[str, List[Tuple]]:
        if isinstance(unique_keys, str):
            unique_keys = [unique_keys]
        # SQLite does not support MERGE statements directly, so you might need to use UPSERT.
        columns = data[0].keys()
        columns_list = ', '.join(columns)
        updates = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col not in unique_keys])

        merge_query = f"""
        INSERT INTO {table_name} ({columns_list})
        VALUES ({', '.join(['?'] * len(columns))})
        ON CONFLICT({', '.join(unique_keys)})
        DO UPDATE SET {updates};
        """
        values = [tuple(row.values()) for row in data]
        return merge_query, values

    @staticmethod
    def get_max_incrementor_script(table_name: str, field_name: str, schema_name:str=None) -> str:
        return f"SELECT COALESCE(MAX({field_name}), 0) + 1 AS max_{field_name} FROM {table_name}"

    @staticmethod
    def get_query(table_name: str, select_cols: List[str], conditions: Dict[str, Any], schema_name:str=None) -> Tuple[str, Tuple]:
        # TODO get_query should allow for dynamic where clauses.
        select_cols_str = ", ".join(select_cols)
        if conditions:
            placeholders = " AND ".join([f"{field} = ?" for field in conditions.keys()])
            return (f"SELECT {select_cols_str} FROM {table_name} WHERE {placeholders}", tuple(conditions.values()))
        else:
            return f"SELECT {select_cols_str} FROM {table_name}", ()

    @staticmethod
    def get_delete_record_script(table_name: str, conditions: Dict[str, Any], schema_name:str=None) -> Tuple[str, Tuple]:
        placeholders = " AND ".join([f"{field} = ?" for field in conditions.keys()])
        return (f"DELETE FROM {table_name} WHERE {placeholders}", tuple(conditions.values()))
