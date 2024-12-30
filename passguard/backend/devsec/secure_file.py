import os
import stat
import logging
import platform
import subprocess

def secure_file(file_path:str, grant_user_access:bool=True):
    """
    Secure a file by setting appropriate permissions based on the OS.

    Parameters:
        file_path (str): Path to the file to secure.
        grant_user_access (bool): Whether to grant the user access along with the application.

    Raises:
        NotImplementedError: If the OS is unsupported.
    """
    current_os = platform.system()

    if current_os == "Windows":
        secure_file_windows(file_path, grant_user_access)
    elif current_os in ("Linux", "Darwin"):  # Unix-like systems
        secure_file_unix(file_path, grant_user_access)
    else:
        print(f"File permissions are not supported for OS: {current_os}.")
        logging.warning(f"File permissions are not supported for OS: {current_os}.")

def secure_file_windows(file_path:str, grant_user_access:bool):
    """
    Secure a file on Windows using ACLs.

    Parameters:
        file_path (str): Path to the file.
        grant_user_access (bool): Whether to grant the user access.
    """
    try:
        user = os.getlogin()
        if grant_user_access:
            # Grant access to the application and the current user
            command = f'icacls "{file_path}" /grant "{user}":F /inheritance:r'
        else:
            # Restrict access to the application only
            # This assumes the application is running under a service account
            command = f'icacls "{file_path}" /inheritance:r /remove:g "{user}"'

        subprocess.check_call(command, shell=True)
        
        print(f"Permissions updated successfully for {file_path} on Windows.")
        logging.info(f"Permissions updated successfully for {file_path} on Windows.")
    except Exception as e:
        print(f"Failed to set permissions on Windows: {e}")
        logging.error(f"Failed to set permissions on Windows: {e}")

def secure_file_unix(file_path:str, grant_user_access:bool):
    """
    Secure a file on Unix-like systems.

    Parameters:
        file_path (str): Path to the file.
        grant_user_access (bool): Whether to grant the user access.
    """
    try:
        if grant_user_access:
            # Set permissions to rw-r-----
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
        else:
            # Set permissions to rw-------
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

        print(f"Permissions updated successfully for {file_path} on Unix.")
        logging.info(f"Permissions updated successfully for {file_path} on Unix.")
    except Exception as e:
        print(f"Failed to set permissions on Unix: {e}")
        logging.error(f"Failed to set permissions on Unix: {e}")