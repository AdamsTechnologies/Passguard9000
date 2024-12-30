import os
import re
import logging
import tempfile
from contextlib import contextmanager
from .sql import SQLite, sqlite3

from passguard.backend.devsec.encrypto import Encrypto
from passguard.backend.devsec.key_generator import generate_key
from passguard.backend.helpers.password_generator import PasswordFactory

def _generate_temp_name()->str:
    # did not want a single deterministic temp db name.. 
    # using password generator to generate semi-random temp db names instead..
    tmp_str = PasswordFactory.generate_password(min_length=4, max_length=10) 
    return re.sub(pattern=r'[^a-zA-Z0-9]', repl='', string=tmp_str)

@contextmanager
def encrypted_database_context(db_path: str, encrypto_cls, password: str, salt: bytes = None):
    """
    Context manager for handling an encrypted SQLite database entirely in memory,
    backed up at the end via .backup() rather than using iterdump().
    
    Steps:
      1) Decrypt existing file (if it exists) into a temp file.
      2) Copy (backup) from that temp file into an in-memory SQLite db.
      3) Yield the in-memory db connection for usage.
      4) On close, backup from in-memory to a temp file.
      5) Encrypt that temp file and overwrite the real db on disk.
      6) Clean up temp files.
    """
    temp_path = f"{_generate_temp_name()}.db"
    memory_sql = None

    try:
        # Step 1: Generate key and decrypt if existing db
        key, salt = generate_key(password=password, salt=salt)
        encryptor = encrypto_cls(key)

        if os.path.exists(db_path):
            # Read the encrypted bytes
            with open(db_path, 'rb') as f:
                encrypted_data = f.read()
            # Decrypt them
            decrypted_data = encryptor.decrypt(encrypted_data)

            # Write to a temp file so we can do a native .backup() 
            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)

            # Step 2: Load that unencrypted temp file into memory
            memory_sql = SQLite(db_file=":memory:")
            memory_sql._connect()

            # Backup from temp file -> in-memory
            disk_conn = sqlite3.connect(temp_path)
            disk_conn.backup(memory_sql.conn)
            disk_conn.close()

            # Remove the unencrypted temp file once loaded into memory
            os.remove(temp_path)
        else:
            # Brand new DB in memory
            memory_sql = SQLite(db_file=":memory:")
            memory_sql._connect()

        # Step 3: Yield the in-memory database + the salt
        yield {'sql': memory_sql, 'salt': salt}

        # Step 4: Backup from in-memory -> temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        disk_conn = sqlite3.connect(temp_path)
        memory_sql.conn.backup(disk_conn)
        disk_conn.close()

        # Step 5: Encrypt the raw bytes
        with open(temp_path, 'rb') as f:
            raw_bytes = f.read()
        encrypted_data = encryptor.encrypt(raw_bytes)

        # Write the re-encrypted bytes to the final db_path
        with open(db_path, 'wb') as f:
            f.write(encrypted_data)

    except Exception as e:
        logging.error(f"An error occurred in encrypted_database_context: {e}")
        raise
    finally:
        # Step 6: Clean up
        if memory_sql:
            memory_sql._close_up()
        if os.path.exists(temp_path):
            os.remove(temp_path)
