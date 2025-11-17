"""
Optimized formatter for WordReaper.

This module provides efficient file saving functionality.
"""

import os
from tqdm import tqdm

# ANSI Bright Red
RED = '\033[91m'
RESET = '\033[0m'

def save_to_file_fast(words, output_path, silent=False):
    """
    Save wordlist to file using the most efficient method based on type.
    
    This function detects if words is a list or generator and uses
    the appropriate optimized method.
    
    Args:
        words: Words to save (list or generator)
        output_path: Path to output file
        silent: Whether to suppress output
    """
    if words is None:
        if not silent:
            print(f"{RED}No words to save.{RESET}")
        return
    
    try:
        # Determine if words is a generator/iterator or a list
        is_generator = hasattr(words, '__iter__') and not hasattr(words, '__len__')
        
        if is_generator:
            # For generators, write in chunks to avoid memory issues
            _save_generator_to_file_fast(words, output_path, silent)
        else:
            # For lists, write all at once for maximum speed
            _save_list_to_file_fast(words, output_path, silent)
    except Exception as e:
        print(f"{RED}Error saving file: {e}{RESET}")

def _save_list_to_file_fast(words, output_path, silent=False):
    """Save a list of words to a file in bulk for maximum speed"""
    if not silent:
        print(f"\nSaving {RED}{len(words)}{RESET} words to output...")
    
    # Filter empty words
    words = [word.strip() for word in words if word and word.strip()]
    
    # Write all words at once
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(words))
        # Add final newline if there are words
        if words:
            f.write('\n')

def _save_generator_to_file_fast(generator, output_path, silent=False, chunk_size=100000):
    """Save a generator to file efficiently using chunk writing"""
    if not silent:
        print(f"Streaming words to {output_path}...")
    
    total_words = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        chunk = []
        
        for word in generator:
            if word and word.strip():
                chunk.append(word.strip())
                total_words += 1
                
                if len(chunk) >= chunk_size:
                    # Write chunk to file
                    f.write('\n'.join(chunk) + '\n')
                    chunk = []
        
        # Write any remaining words
        if chunk:
            f.write('\n'.join(chunk) + '\n')
    
    if not silent:
        print(f"Saved {total_words} words to {output_path}")

# Keep original functions for backward compatibility
def save_to_file(words, output_path, chunk_size=10000):
    """Legacy function for backward compatibility"""
    save_to_file_fast(words, output_path)

def print_stats(words, massive=False, silent=False):
    """
    Statistics functionality removed - just returns the words without any processing.
    """
    # Simply return the words without any statistics calculation
    return words

def print_file_stats(file_path):
    """
    Statistics functionality removed.
    """
    # Do nothing
    pass

def print_list(words, limit=20):
    """Print a sample of words from the wordlist"""
    # Handle generators differently
    if hasattr(words, '__iter__') and not isinstance(words, (list, set, tuple)):
        sample = []
        try:
            for i, word in enumerate(words):
                if i < limit:
                    sample.append(word)
                else:
                    break
            words = sample
        except Exception as e:
            print(f"Error sampling generator: {e}")
    
    print("\nSample words:")
    for word in words[:limit]:
        print(f"- {word}")
    if hasattr(words, '__len__') and len(words) > limit:
        print(f"... and {len(words) - limit} more")
