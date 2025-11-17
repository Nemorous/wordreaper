from tqdm import tqdm
import os
import mmap

# ANSI red for progress bar
RED = '\033[91m'
RESET = '\033[0m'

def load(file_path, silent=False, chunk_size=10000, preserve=False):
    """
    Load words from file.

    Args:
        file_path: Path to the file to load
        silent: If True, suppress progress output
        chunk_size: Size of chunks to process at once
        preserve: If True, keep entire lines intact (don't split by whitespace)

    Returns:
        List of words from the file
    """
    if not silent:
        print(f"\nLoading stats from file: {file_path}\n")

    if not os.path.exists(file_path):
        print("File not found.")
        return []

    file_size = os.path.getsize(file_path)
    return _load_regular(file_path, file_size, silent, preserve)

def load_streaming(file_path, silent=False, chunk_size=10000):
    """
    Stream words from file without loading the entire file into memory.
    Uses memory-mapped files for very large files when possible.
    
    Args:
        file_path: Path to the file to load
        silent: If True, suppress progress output
        chunk_size: Size of chunks to process at once
        
    Returns:
        Generator yielding words from the file
    """
    if not os.path.exists(file_path):
        print("File not found.")
        return (word for word in [])  # Empty generator
    
    file_size = os.path.getsize(file_path)
    
    # For very large files (>1GB), try to use memory mapping
    if file_size > 1024 * 1024 * 1024:  # > 1GB
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Create memory map
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Process line by line
                    current_pos = 0
                    line_start = 0
                    
                    while current_pos < file_size:
                        # Find next newline
                        newline_pos = mm.find(b'\n', current_pos)

                        if newline_pos == -1:  # No more newlines
                            if current_pos < file_size:
                                line = mm[current_pos:].decode('utf-8', errors='ignore')
                                stripped_line = line.strip()
                                if stripped_line:
                                    yield stripped_line
                            break

                        # Get line
                        line = mm[current_pos:newline_pos].decode('utf-8', errors='ignore')

                        # Keep entire line as single entry
                        stripped_line = line.strip()
                        if stripped_line:
                            yield stripped_line

                        # Move to next line
                        current_pos = newline_pos + 1
                        
                    if not silent:
                        print(f"{RED}Streamed words from {file_path}{RESET}")
                    return
        except Exception as e:
            print(f"Memory mapping failed: {e}. Falling back to standard file reading.")
    
    # Standard file reading for smaller files or if memory mapping fails
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Process in chunks for better performance
            lines_processed = 0
            
            for line in f:
                lines_processed += 1
                stripped_line = line.strip()

                # Keep entire line as single entry
                if stripped_line:
                    yield stripped_line
                
                # Update progress periodically
                if not silent and lines_processed % 100000 == 0:
                    print(f"\r{RED}Lines processed: {lines_processed:,}{RESET}", end='')
            
            if not silent:
                print(f"\n{RED}Completed streaming from file{RESET}")
    
    except Exception as e:
        print(f"Error reading file: {e}")

def _load_regular(file_path, file_size, silent=False, preserve=False):
    """
    Load words from file into memory with progress bar.

    Args:
        file_path: Path to the file to load
        file_size: Size of the file in bytes
        silent: If True, suppress progress output
        preserve: If True, keep entire lines intact (don't split by whitespace)
    """
    words = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # For large files, show a warning
            if file_size > 100 * 1024 * 1024:  # 100MB
                print(f"{RED}Warning: Loading a large file ({file_size/(1024*1024):.1f} MB) into memory.{RESET}")

            lines = f.readlines()
            for line in tqdm(
                lines,
                desc="Reading lines",
                unit="line",
                ncols=80,
                ascii=(" ", "#"),
                bar_format="{l_bar}" + RED + "{bar}" + RESET + "| {n_fmt}/{total_fmt} [{elapsed}]",
                disable=silent
            ):
                # Keep entire line as a single entry (like HTML scraper does)
                stripped_line = line.strip()
                if stripped_line:
                    words.append(stripped_line)

    except Exception as e:
        print(f"Error reading file: {e}")

    return words
