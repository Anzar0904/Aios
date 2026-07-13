from pathlib import Path


def validate_workspace_path(path_str: str, workspace_root: str) -> Path:
    """
    Validates that the given target path is strictly within the active workspace root.
    Resolves symbolic links and normalizes the path to prevent directory traversal.

    Raises:
        PermissionError: If the resolved path escapes the workspace root.
        ValueError: If the path is invalid.
    """
    try:
        root_path = Path(workspace_root).resolve()
        target_path = Path(path_str).resolve()
    except Exception as e:
        raise ValueError(f"Invalid path format: {e}")

    # Check if target_path is relative to root_path
    # Note: is_relative_to is standard in Python 3.9+
    if not target_path.is_relative_to(root_path):
        raise PermissionError("Access denied: path escapes workspace.")

    return target_path
