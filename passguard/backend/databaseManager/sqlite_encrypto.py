import os
import io
import shutil
import logging
import tempfile
from contextlib import contextmanager
from .sql import SQLite

from passguard.backend.devsec.encrypto import Encrypto
from passguard.backend.devsec.key_generator import generate_key

@contextmanager
def encrypted_database_context(db_path:str, encrypto_cls:Encrypto, password: str, salt: bytes= None):
    """
    Context manager for handling an encrypted SQLite database using a temporary directory.

    Decrypts the database on entry and encrypts it back on exit.

    Parameters:
        db_path (str): Path to the encrypted SQLite database.
        password (str): Password used to derive the encryption key.
        salt_path (str): Path to the salt file.

    Yields:
        dict: Contains the SQLite controller.
    """
    sql = None
    encryptor = None
    try:
        key, salt = generate_key(password=password, salt=salt)
        encryptor = Encrypto(key)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db_path = os.path.join(temp_dir, 'temp_db.sqlite')
            backup_path = os.path.join(temp_dir, 'backup_db.sqlite')

            # Handle new database creation
            if not os.path.exists(db_path) or os.path.getsize(db_path) < 16:
                sql = SQLite(db_file=temp_db_path)
                sql._connect()
                yield {'sql': sql, 'salt': salt}
            else:
                logging.info("Decrypting the existing database.")
                with open(db_path, 'rb') as f:
                    encrypted_data = f.read()

                decrypted_data = encryptor.decrypt(encrypted_data)
                with open(temp_db_path, 'wb') as temp_db:
                    temp_db.write(decrypted_data)
                os.chmod(temp_db_path, 0o600)


                sql = SQLite(db_file=temp_db_path)
                sql._connect()
                yield {'sql': sql, 'salt': salt}

            # Exiting the context: Encrypt and save the database
            if sql and sql.conn:
                backup_sql = SQLite(db_file=backup_path)
                backup_sql._connect()
                sql.conn.backup(backup_sql.conn)
                backup_sql._close_up()
                sql._close_up()

                with open(backup_path, 'rb') as f:
                    backup_data = f.read()

                encrypted_data = encryptor.encrypt(backup_data)
                with open(db_path, 'wb') as f:
                    f.write(encrypted_data)
                os.chmod(db_path, 0o600)
    except Exception as e:
        logging.error("An error occurred in encrypted_database_context.")
        raise
