import os
from pathlib import Path

def load_azure_storage_connection_string():
    """
    Load Azure Storage connection string from a text file.
    The file should be located in the users module directory.
    """
    try:
        # Get the directory of the current file
        current_dir = Path(__file__).parent
        # Path to the connection string file
        connection_file = current_dir / 'azure_storage_connection.txt'
        
        if not connection_file.exists():
            raise FileNotFoundError("Azure Storage connection string file not found")
            
        with open(connection_file, 'r') as f:
            connection_string = f.read().strip()
            
        if not connection_string:
            raise ValueError("Azure Storage connection string is empty")
            
        return connection_string
    except Exception as e:
        raise Exception(f"Failed to load Azure Storage connection string: {str(e)}") 