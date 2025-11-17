"""
Temporary files management for WordReaper.

This module provides utilities for managing temporary files during processing,
ensuring proper cleanup and preventing resource leaks.
"""

import os
import tempfile
import shutil
import atexit
import uuid
import time
import logging
from contextlib import contextmanager

# Create a logger for this module
logger = logging.getLogger("temp_files")
logger.setLevel(logging.WARNING)

# Add a console handler if none exists
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s [TempFiles]: %(message)s'))
    logger.addHandler(console_handler)

# ANSI colors for output
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

# Global registry of temporary files and directories
_TEMP_FILES = set()
_TEMP_DIRS = set()

def _cleanup_all():
    """Clean up all registered temporary files and directories."""
    # First clean up files
    for filepath in list(_TEMP_FILES):
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                logger.debug(f"Cleaned up temporary file: {filepath}")
            _TEMP_FILES.remove(filepath)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {filepath}: {e}")
    
    # Then clean up directories
    for dirpath in list(_TEMP_DIRS):
        try:
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
                logger.debug(f"Cleaned up temporary directory: {dirpath}")
            _TEMP_DIRS.remove(dirpath)
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory {dirpath}: {e}")

# Register cleanup function to run at program exit
atexit.register(_cleanup_all)

def create_temp_file(prefix="wordreaper_", suffix=".tmp", directory=None, register=True):
    """
    Create a temporary file with a unique name.
    
    Args:
        prefix: Prefix for the filename
        suffix: Suffix for the filename
        directory: Directory to create the file in (None for system temp dir)
        register: Whether to register for automatic cleanup
        
    Returns:
        Path to the temporary file
    """
    # Generate a unique filename
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    
    if directory is None:
        directory = tempfile.gettempdir()
    
    filename = f"{prefix}{timestamp}_{unique_id}{suffix}"
    filepath = os.path.join(directory, filename)
    
    # Create an empty file
    with open(filepath, 'w') as f:
        pass
    
    if register:
        _TEMP_FILES.add(filepath)
        logger.debug(f"Registered temporary file: {filepath}")
    
    return filepath

def create_temp_directory(prefix="wordreaper_", suffix="", base_dir=None, register=True):
    """
    Create a temporary directory with a unique name.
    
    Args:
        prefix: Prefix for the directory name
        suffix: Suffix for the directory name
        base_dir: Parent directory to create the directory in
        register: Whether to register for automatic cleanup
        
    Returns:
        Path to the temporary directory
    """
    dirpath = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=base_dir)
    
    if register:
        _TEMP_DIRS.add(dirpath)
        logger.debug(f"Registered temporary directory: {dirpath}")
    
    return dirpath

def register_temp_file(filepath):
    """
    Register an existing file for cleanup when the program exits.
    
    Args:
        filepath: Path to the file to register
    """
    if os.path.exists(filepath):
        _TEMP_FILES.add(filepath)
        logger.debug(f"Registered existing file for cleanup: {filepath}")
    else:
        logger.warning(f"Attempted to register non-existent file: {filepath}")

def register_temp_directory(dirpath):
    """
    Register an existing directory for cleanup when the program exits.
    
    Args:
        dirpath: Path to the directory to register
    """
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        _TEMP_DIRS.add(dirpath)
        logger.debug(f"Registered existing directory for cleanup: {dirpath}")
    else:
        logger.warning(f"Attempted to register non-existent directory: {dirpath}")

def unregister_temp_file(filepath):
    """
    Unregister a file from automatic cleanup.
    
    Args:
        filepath: Path to the file to unregister
    """
    if filepath in _TEMP_FILES:
        _TEMP_FILES.remove(filepath)
        logger.debug(f"Unregistered file from cleanup: {filepath}")

def unregister_temp_directory(dirpath):
    """
    Unregister a directory from automatic cleanup.
    
    Args:
        dirpath: Path to the directory to unregister
    """
    if dirpath in _TEMP_DIRS:
        _TEMP_DIRS.remove(dirpath)
        logger.debug(f"Unregistered directory from cleanup: {dirpath}")

@contextmanager
def temp_file_context(prefix="wordreaper_", suffix=".tmp", directory=None):
    """
    Context manager for temporary files.
    
    Creates a temporary file that is automatically cleaned up
    when the context exits.
    
    Args:
        prefix: Prefix for the filename
        suffix: Suffix for the filename
        directory: Directory to create the file in
        
    Yields:
        Path to the temporary file
    """
    filepath = create_temp_file(prefix, suffix, directory)
    try:
        yield filepath
    finally:
        if filepath in _TEMP_FILES:
            _TEMP_FILES.remove(filepath)
        
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                logger.debug(f"Removed temporary file: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {filepath}: {e}")

@contextmanager
def temp_directory_context(prefix="wordreaper_", suffix="", base_dir=None):
    """
    Context manager for temporary directories.
    
    Creates a temporary directory that is automatically cleaned up
    when the context exits.
    
    Args:
        prefix: Prefix for the directory name
        suffix: Suffix for the directory name
        base_dir: Parent directory to create the directory in
        
    Yields:
        Path to the temporary directory
    """
    dirpath = create_temp_directory(prefix, suffix, base_dir)
    try:
        yield dirpath
    finally:
        if dirpath in _TEMP_DIRS:
            _TEMP_DIRS.remove(dirpath)
        
        try:
            if os.path.exists(dirpath) and os.path.isdir(dirpath):
                shutil.rmtree(dirpath)
                logger.debug(f"Removed temporary directory: {dirpath}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary directory {dirpath}: {e}")

def make_temp_path(filename, prefix="wordreaper_", directory=None):
    """
    Create a path in a temporary directory for a specific filename.
    
    Useful for giving a specific name to a temporary file.
    
    Args:
        filename: Desired filename
        prefix: Prefix for the directory name
        directory: Base directory (None for system temp dir)
        
    Returns:
        Full path including the temporary directory and filename
    """
    if directory is None:
        directory = tempfile.gettempdir()
    
    # Create a uniquely named subdirectory
    unique_id = str(uuid.uuid4())[:8]
    timestamp = int(time.time())
    subdir_name = f"{prefix}{timestamp}_{unique_id}"
    subdir_path = os.path.join(directory, subdir_name)
    
    # Create the subdirectory
    os.makedirs(subdir_path, exist_ok=True)
    
    # Register the subdirectory for cleanup
    _TEMP_DIRS.add(subdir_path)
    
    # Return the full path
    return os.path.join(subdir_path, filename)

def list_temp_files():
    """
    List all registered temporary files.
    
    Returns:
        List of registered temporary file paths
    """
    return list(_TEMP_FILES)

def list_temp_directories():
    """
    List all registered temporary directories.
    
    Returns:
        List of registered temporary directory paths
    """
    return list(_TEMP_DIRS)

def cleanup_orphaned_temps(max_age_hours=24, dry_run=False):
    """
    Clean up orphaned temporary files and directories.
    
    This function looks for files and directories with the wordreaper
    prefix in the system temp directory and removes those older than
    the specified age.
    
    Args:
        max_age_hours: Maximum age in hours for temp files to keep
        dry_run: If True, only report but don't delete
        
    Returns:
        Number of files and directories cleaned up
    """
    temp_dir = tempfile.gettempdir()
    prefix = "wordreaper_"
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    
    files_removed = 0
    dirs_removed = 0
    
    # List all items in the temp directory
    try:
        items = os.listdir(temp_dir)
    except Exception as e:
        logger.error(f"Failed to list temporary directory: {e}")
        return 0, 0
    
    # Check each item
    for item in items:
        if not item.startswith(prefix):
            continue
        
        full_path = os.path.join(temp_dir, item)
        
        try:
            # Get item stats
            stats = os.stat(full_path)
            age = current_time - stats.st_mtime
            
            # Skip if not old enough
            if age < max_age_seconds:
                continue
            
            # Handle based on type
            if os.path.isfile(full_path):
                if not dry_run:
                    os.unlink(full_path)
                    logger.info(f"Removed orphaned temp file: {full_path}")
                files_removed += 1
            elif os.path.isdir(full_path):
                if not dry_run:
                    shutil.rmtree(full_path)
                    logger.info(f"Removed orphaned temp directory: {full_path}")
                dirs_removed += 1
        except Exception as e:
            logger.warning(f"Failed to process {full_path}: {e}")
    
    if dry_run:
        logger.info(f"Dry run: Would remove {files_removed} files and {dirs_removed} directories")
    else:
        logger.info(f"Removed {files_removed} orphaned temp files and {dirs_removed} orphaned temp directories")
    
    return files_removed, dirs_removed

class TempFileManager:
    """
    Class to manage temporary files for a specific operation.
    
    This class provides methods to create, track, and clean up
    temporary files associated with a particular operation.
    
    Example usage:
        manager = TempFileManager("word-processing")
        temp_file1 = manager.create_temp_file()
        temp_file2 = manager.create_temp_file()
        # ... use temp files ...
        manager.cleanup()  # Clean up all temp files
    """
    
    def __init__(self, operation_name, base_dir=None):
        """
        Initialize the temporary file manager.
        
        Args:
            operation_name: Name of the operation (used as prefix)
            base_dir: Base directory for temporary files
        """
        self.operation_name = operation_name
        self.base_dir = base_dir
        self.temp_files = set()
        self.temp_dirs = set()
    
    def create_temp_file(self, suffix=".tmp"):
        """
        Create a temporary file specific to this operation.
        
        Args:
            suffix: Suffix for the filename
            
        Returns:
            Path to the temporary file
        """
        prefix = f"wordreaper_{self.operation_name}_"
        filepath = create_temp_file(prefix=prefix, suffix=suffix, directory=self.base_dir, register=False)
        self.temp_files.add(filepath)
        return filepath
    
    def create_temp_directory(self, suffix=""):
        """
        Create a temporary directory specific to this operation.
        
        Args:
            suffix: Suffix for the directory name
            
        Returns:
            Path to the temporary directory
        """
        prefix = f"wordreaper_{self.operation_name}_"
        dirpath = create_temp_directory(prefix=prefix, suffix=suffix, base_dir=self.base_dir, register=False)
        self.temp_dirs.add(dirpath)
        return dirpath
    
    def register_file(self, filepath):
        """
        Register an existing file with this manager.
        
        Args:
            filepath: Path to the file to register
        """
        if os.path.exists(filepath):
            self.temp_files.add(filepath)
    
    def register_directory(self, dirpath):
        """
        Register an existing directory with this manager.
        
        Args:
            dirpath: Path to the directory to register
        """
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            self.temp_dirs.add(dirpath)
    
    def unregister_file(self, filepath):
        """
        Unregister a file from this manager.
        
        Args:
            filepath: Path to the file to unregister
        """
        if filepath in self.temp_files:
            self.temp_files.remove(filepath)
    
    def unregister_directory(self, dirpath):
        """
        Unregister a directory from this manager.
        
        Args:
            dirpath: Path to the directory to unregister
        """
        if dirpath in self.temp_dirs:
            self.temp_dirs.remove(dirpath)
    
    def keep_file(self, filepath, new_location=None):
        """
        Mark a temporary file to be kept (not deleted during cleanup).
        
        Args:
            filepath: Path to the file to keep
            new_location: Optional new location to move the file to
            
        Returns:
            Final path of the kept file
        """
        if filepath in self.temp_files:
            self.temp_files.remove(filepath)
            
            if new_location:
                # Move the file to the new location
                os.rename(filepath, new_location)
                return new_location
        
        return filepath
    
    def cleanup(self):
        """Clean up all temporary files and directories managed by this instance."""
        # Clean up files
        for filepath in list(self.temp_files):
            try:
                if os.path.exists(filepath):
                    os.unlink(filepath)
                    logger.debug(f"Removed temporary file: {filepath}")
                self.temp_files.remove(filepath)
            except Exception as e:
                logger.warning(f"Failed to remove temporary file {filepath}: {e}")
        
        # Clean up directories
        for dirpath in list(self.temp_dirs):
            try:
                if os.path.exists(dirpath) and os.path.isdir(dirpath):
                    shutil.rmtree(dirpath)
                    logger.debug(f"Removed temporary directory: {dirpath}")
                self.temp_dirs.remove(dirpath)
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {dirpath}: {e}")
    
    def __enter__(self):
        """Support with-statement context management."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up when exiting the context."""
        self.cleanup()
    
    def __del__(self):
        """Ensure cleanup when the object is deleted."""
        self.cleanup()