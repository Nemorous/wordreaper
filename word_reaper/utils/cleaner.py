import re
import unicodedata
from tqdm import tqdm
import os

# ANSI bright red
RED = '\033[91m'
RESET = '\033[0m'

def clean_words(word_list, silent=False, chunk_size=100000, preserve=False):
    """
    Normalize and clean a list of words:
    - Convert to lowercase (unless preserve=True)
    - Remove special characters (unless preserve=True)
    - Remove diacritics (unless preserve=True)
    - Strip whitespace
    - Remove duplicates

    Args:
        word_list: List of words to clean
        silent: Suppress progress output
        chunk_size: Not used in this function
        preserve: If True, preserve original formatting (case, symbols, diacritics, spaces)
    """
    # Check for empty input
    if not word_list:
        return []

    def normalize(word):
        if preserve:
            # Only strip leading/trailing whitespace, preserve everything else
            return word.strip()
        else:
            # Original cleaning behavior
            word = unicodedata.normalize('NFKD', word)
            word = ''.join([c for c in word if not unicodedata.combining(c)])
            word = word.lower()
            return re.sub(r'[^a-z0-9]', '', word)

    # Process in memory with progress bar
    desc = "Preserving words" if preserve else "Cleaning words"
    cleaned = set()
    for word in tqdm(
        word_list,
        desc=desc,
        unit="word",
        ncols=80,
        ascii=(" ", "#"),
        bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]",
        disable=silent
    ):
        if not word:  # Skip empty words
            continue

        cleaned_word = normalize(word)
        if cleaned_word:
            cleaned.add(cleaned_word)

    return sorted(cleaned)

def clean_words_stream(word_list, silent=False, chunk_size=100000):
    """
    Stream-process words for better memory efficiency:
    - Convert to lowercase
    - Remove special characters
    - Remove diacritics
    - Strip whitespace
    - Yield deduplicated words
    """
    # Check for empty input
    if not word_list:
        # Return empty generator
        return (word for word in [])
    
    def normalize(word):
        word = unicodedata.normalize('NFKD', word)
        word = ''.join([c for c in word if not unicodedata.combining(c)])
        word = word.lower()
        return re.sub(r'[^a-z0-9]', '', word)

    if not silent:
        print(f"{RED}Streaming and cleaning words...{RESET}")
    
    # Process the stream directly using a simple generator function
    def process_words():
        seen = set()
        
        for word in word_list:
            if not word:  # Skip empty words
                continue
            
            cleaned = normalize(word)
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                yield cleaned
            
            # Reset seen set periodically to prevent unbounded growth
            if len(seen) >= chunk_size:
                seen.clear()
    
    return process_words()

def clean_file_streaming(input_file, output_file, silent=False, chunk_size=100000):
    """
    Process an entire file with streaming to avoid loading it all into memory.
    Useful for very large files.
    """
    if not silent:
        print(f"{RED}Streaming and cleaning words from file...{RESET}")
    
    seen_words = set()
    total_processed = 0
    total_unique = 0
    
    # Create a temporary file for initial cleaning
    tmp_file = output_file + ".tmp"
    
    # First pass: Clean and deduplicate in chunks
    with open(tmp_file, 'w', encoding='utf-8') as out:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in tqdm(
                f,
                desc="Cleaning file",
                unit="line", 
                ncols=80,
                ascii=(" ", "#"),
                bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]",
                disable=silent
            ):
                words = line.strip().split()
                total_processed += len(words)
                
                for word in words:
                    # Normalize and clean the word
                    cleaned = unicodedata.normalize('NFKD', word)
                    cleaned = ''.join([c for c in cleaned if not unicodedata.combining(c)])
                    cleaned = cleaned.lower()
                    cleaned = re.sub(r'[^a-z0-9]', '', cleaned)
                    
                    if cleaned and cleaned not in seen_words:
                        seen_words.add(cleaned)
                        out.write(f"{cleaned}\n")
                        total_unique += 1
                
                # Reset seen_words periodically to prevent memory buildup
                if len(seen_words) >= chunk_size:
                    seen_words.clear()
    
    # Second pass: Sort the file (if needed)
    # This uses external sort if the file is very large
    if os.path.getsize(tmp_file) > 1024 * 1024 * 200:  # 200 MB threshold
        external_sort(tmp_file, output_file)
    else:
        # For smaller files, we can sort in memory
        with open(tmp_file, 'r', encoding='utf-8') as f:
            words = sorted(set(line.strip() for line in f))
        
        with open(output_file, 'w', encoding='utf-8') as out:
            for word in words:
                out.write(f"{word}\n")
    
    # Cleanup
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    
    return total_unique

def external_sort(input_file, output_file, chunk_size=100000, temp_dir=None):
    """
    Sort a large file using external merge sort algorithm.
    This avoids loading the entire file into memory.
    """
    import tempfile
    import shutil
    
    # Create a temporary directory for the sort chunks
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp()
    
    try:
        # Split the file into sorted chunks
        chunk_files = []
        with open(input_file, 'r', encoding='utf-8') as f:
            chunk = []
            chunk_num = 0
            
            for line in f:
                chunk.append(line.strip())
                if len(chunk) >= chunk_size:
                    chunk.sort()
                    chunk_path = os.path.join(temp_dir, f"chunk_{chunk_num}.txt")
                    with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                        for item in chunk:
                            chunk_file.write(f"{item}\n")
                    chunk_files.append(chunk_path)
                    chunk = []
                    chunk_num += 1
            
            # Write the last chunk if it exists
            if chunk:
                chunk.sort()
                chunk_path = os.path.join(temp_dir, f"chunk_{chunk_num}.txt")
                with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                    for item in chunk:
                        chunk_file.write(f"{item}\n")
                chunk_files.append(chunk_path)
        
        # Merge the sorted chunks
        _merge_sorted_chunks(chunk_files, output_file)
    
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

def _merge_sorted_chunks(chunk_files, output_file):
    """Merge multiple sorted files into a single sorted file"""
    import heapq
    
    # Open all chunk files
    file_handles = [open(f, 'r', encoding='utf-8') for f in chunk_files]
    
    # Create a priority queue with (value, file_index) tuples
    heap = []
    for i, file_handle in enumerate(file_handles):
        line = file_handle.readline().strip()
        if line:  # Skip empty files
            heap.append((line, i))
    
    heapq.heapify(heap)
    
    # Merge the chunks
    with open(output_file, 'w', encoding='utf-8') as out:
        prev_value = None
        
        while heap:
            value, file_index = heapq.heappop(heap)
            
            # Skip duplicates
            if value != prev_value:
                out.write(f"{value}\n")
                prev_value = value
            
            # Get the next value from the same file
            next_line = file_handles[file_index].readline().strip()
            if next_line:
                heapq.heappush(heap, (next_line, file_index))
    
    # Close all file handles
    for handle in file_handles:
        handle.close()