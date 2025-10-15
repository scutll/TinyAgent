# file operation for agent editing or reading file
import os
def read_file(path:str):
    """Read a text file and return its content.

    On error returns a string starting with "error in reading <path>: <error>".
    """
    try:
        with open(path, "r", encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        content = f"error in reading {path}: {e}"
    return content

def search_replace(path:str, match: str, replace: str):
    """Search and replace in a text file.

    If `match` is None, the whole file content will be
    replaced with `replace`.

    Returns the new content on success, or an error string starting with
    "error in" on failure.
    """
    try:
        # Read existing content
        with open(path, "r", encoding='utf-8') as f:
            content = f.read()

        if match is None:
            new_content = replace
        else:
            # Replace all occurrences of the match substring
            new_content = content.replace(match, replace)

        # Write back new content
        with open(path, "w", encoding='utf-8') as f:
            f.write(new_content)

        return new_content
    except Exception as e:
        return f"error in search_replace {path}: {e}"


def create_file(path:str, file_name:str, content: str):
    '''
    Create a new file with specified content in the given directory.
    
    Args:
        path (str): The directory path where the file will be created. 
                   If the directory does not exist, it will be created automatically.
        file_name (str): The name of the file to be created (including extension if needed).
        content (str): The initial content to write into the file.
    
    Returns:
        str: Success message with full file path on success,
             or error message starting with "error in creating file" on failure.
    
    Note:
        - If the file already exists, an error will be returned to prevent overwriting.
        - The directory path will be created recursively if it doesn't exist.
    '''
    try:
        # Ensure the directory exists
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        # Construct full file path
        full_path = os.path.join(path, file_name)
        
        # Check if file already exists
        if os.path.exists(full_path):
            return f"error in creating file: {full_path} already exists"
        
        # Create and write to the file
        with open(full_path, "w", encoding='utf-8') as f:
            f.write(content)
        
        return f"File created successfully: {full_path}"

    except Exception as e:
        return f"error in creating file {os.path.join(path, file_name)}: {e}"