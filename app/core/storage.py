import os
from pathlib import Path

def get_storage_path(tenant_name: str, document_type: str, record_id: str, file_extension: str = ".pdf") -> str:
    """
    Determines the correct storage path for a new document, creating sequential subdirectories as needed.

    Args:
        tenant_name: The name of the tenant.
        document_type: The type of the document (e.g., 'prontuarios', 'consentimentos').
        record_id: The ID of the database record for the document.
        file_extension: The file extension (default: '.pdf').

    Returns:
        The full path to store the new document.
    """
    base_path = "storage"
    document_type_path = Path(os.path.join(base_path, tenant_name, document_type))
    print(f"DEBUG: Attempting to create directory: {document_type_path}")
    try:
        document_type_path.mkdir(parents=True, exist_ok=True)
        print(f"DEBUG: Directory created successfully: {document_type_path}")
    except Exception as e:
        print(f"ERROR: Failed to create directory {document_type_path}: {e}")
        raise

    # Find the latest sequential subfolder
    subfolders = [d for d in document_type_path.iterdir() if d.is_dir() and d.name.isdigit()]
    if not subfolders:
        latest_subfolder = Path(os.path.join(str(document_type_path), "0001"))
        print(f"DEBUG: Attempting to create subfolder: {latest_subfolder}")
        try:
            latest_subfolder.mkdir()
            print(f"DEBUG: Subfolder created successfully: {latest_subfolder}")
        except Exception as e:
            print(f"ERROR: Failed to create subfolder {latest_subfolder}: {e}")
            raise
    else:
        latest_subfolder = max(subfolders, key=lambda d: int(d.name))
        print(f"DEBUG: Found latest subfolder: {latest_subfolder}")

    # Count files in the latest subfolder
    files_in_subfolder = [f for f in latest_subfolder.iterdir() if f.is_file()]
    if len(files_in_subfolder) >= 400:
        new_subfolder_name = str(int(latest_subfolder.name) + 1).zfill(4)
        latest_subfolder = Path(os.path.join(str(document_type_path), new_subfolder_name))
        print(f"DEBUG: Attempting to create new subfolder (due to 400 limit): {latest_subfolder}")
        try:
            latest_subfolder.mkdir()
            print(f"DEBUG: New subfolder created successfully: {latest_subfolder}")
        except Exception as e:
            print(f"ERROR: Failed to create new subfolder {latest_subfolder}: {e}")
            raise
    else:
        print(f"DEBUG: Current subfolder has {len(files_in_subfolder)} files, no new subfolder needed.")

    file_name = f"{record_id}{file_extension}"
    final_path = os.path.join(str(latest_subfolder), file_name)
    print(f"DEBUG: Final file path: {final_path}")
    return os.path.abspath(final_path)