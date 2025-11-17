"""
Optimized permutator for WordReaper with support for complex mask patterns.

This module provides direct and efficient word list manipulation using Hashcat 
utilities with support for complex mask patterns like NCL-?uS?u?u-1234.
"""

import os
import string
import re
from word_reaper.utils.hashcat_utils import (
    apply_mask, apply_rules, combinatorize, check_hashcat_available,
    create_hidden_temp_file, generate_mask_directly, is_complex_mask
)

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Map of charset identifiers to Hashcat character sets
CHARSET_MAP = {
    'a': '?a',  # All characters
    'd': '?d',  # Digits
    'l': '?l',  # Lowercase
    'u': '?u',  # Uppercase
    's': '?s',  # Special characters
    'h': '?h',  # Hex lowercase
    'H': '?H',  # Hex uppercase
    'b': '?b',  # Binary
}

def generate_rules(leet=False, toggle=False, underscores=False, spaces=False, hyphens=False):
    """
    Generate Hashcat rules based on transformation options.
    
    Args:
        leet: Whether to apply leetspeak
        toggle: Whether to apply case toggling
        underscores: Whether to insert underscores
        spaces: Whether to insert spaces
        hyphens: Whether to insert hyphens
        
    Returns:
        List of Hashcat rules
    """
    rules = []
    
    # Start with identity rule if no transformations are applied
    if not any([leet, toggle, underscores, spaces, hyphens]):
        rules.append("")  # Empty rule = identity
    
    # Apply leetspeak rules
    if leet:
        leet_rules = [
            "sa@", "se3", "si1", "so0", "ss$", "st7", "sl1"
        ]
        rules.extend(leet_rules)
    
    # Apply toggle case rules
    if toggle:
        toggle_rules = [
            "T0",       # Toggle first letter
            "u",        # Uppercase all
            "l",        # Lowercase all
            "E",        # Toggle every other character
            "T0E"       # Toggle everything except first character
        ]
        
        # Add more toggle patterns for different positions
        for i in range(1, 8):
            toggle_rules.append(f"T{i}")
        
        # Add toggle combinations for first few characters
        toggle_rules.append("T0T1")
        toggle_rules.append("T0T2")
        toggle_rules.append("T0T1T2")
        
        rules.extend(toggle_rules)
    
    # Apply character insertion rules
    if underscores:
        for i in range(1, 8):
            rules.append(f"i{i}_")
    
    if spaces:
        for i in range(1, 8):
            rules.append(f"i{i} ")
    
    if hyphens:
        for i in range(1, 8):
            rules.append(f"i{i}-")
    
    return rules

def mentalize(input_file, output_file, leet=False, toggle=False, underscores=False, 
              spaces=False, hyphens=False, append_mask=None, prepend_mask=None, 
              synchronize=False, increment=False, rules_file=None, silent=False):
    """
    Apply transformations to a wordlist using Hashcat utilities.
    Optimized to write directly to output file when possible.
    """
    import shutil
    import os

    # Initialize current_file immediately
    current_file = input_file

    # Calculate user flags count
    user_flags_count = sum([
        leet, toggle, underscores, spaces, hyphens
    ])
    
    # Generate rules (this is still needed for the custom rules file approach)
    rules = generate_rules(leet, toggle, underscores, spaces, hyphens)

    # Check for Hashcat utilities
    hashcat_utils = check_hashcat_available()
    
    if not any(hashcat_utils.values()):
        print(f"{RED}Error: No Hashcat utilities found. Please make sure they exist in the ./bin directory.{RESET}")
        return False
    
    # Check for required utilities based on operations
    missing_utils = []
    if any([leet, toggle, underscores, spaces, hyphens]) and not hashcat_utils["permute"]:
        missing_utils.append("permute.bin")
    if (append_mask or prepend_mask) and not hashcat_utils["maskprocessor"]:
        missing_utils.append("mp64.bin/mp32.bin")
    if (append_mask or prepend_mask) and not hashcat_utils["combinator"]:
        missing_utils.append("combinator.bin")
    if missing_utils:
        print(f"{RED}Error: The following Hashcat utilities are required but not found:{RESET}")
        for util in missing_utils:
            print(f"{RED}  - {util}{RESET}")
        return False

    # OPTIMIZATION CASES

    # Case 1 — Basic transformations, no masks
    if any([leet, toggle, underscores, spaces, hyphens]) and not (append_mask or prepend_mask):
        if rules:
            return apply_rules(input_file, rules, output_file, silent, rules_file=rules_file, user_flags_count=user_flags_count)
        else:
            shutil.copy2(input_file, output_file)
            return True

    # Case 2 — Only append mask, no transformations
    if append_mask and not prepend_mask and not any([leet, toggle, underscores, spaces, hyphens]):
        return apply_mask(input_file, append_mask, output_file, append=True, silent=silent)

    # Case 3 — Only prepend mask, no transformations
    if prepend_mask and not append_mask and not any([leet, toggle, underscores, spaces, hyphens]):
        return apply_mask(input_file, prepend_mask, output_file, append=False, silent=silent)

    # COMPLEX CASES — Multiple operations
    temp_files = []
    try:
        # Apply basic transformations if needed
        if any([leet, toggle, underscores, spaces, hyphens]):
            if rules:
                transform_file = create_hidden_temp_file(prefix="wordreaper_transform_", suffix=".tmp")
                temp_files.append(transform_file)
                if not apply_rules(current_file, rules, transform_file, silent):
                    return False
                current_file = transform_file

        # Handle synchronized masks
        if synchronize and append_mask and prepend_mask:
            if not silent:
                print(f"{RED}Note: Synchronized masks require multiple passes.{RESET}")
            prepend_file = create_hidden_temp_file(prefix="wordreaper_prepend_", suffix=".tmp")
            temp_files.append(prepend_file)
            if not apply_mask(current_file, prepend_mask, prepend_file, append=False, silent=silent):
                return False
            if not apply_mask(prepend_file, append_mask, output_file, append=True, silent=silent):
                return False
            return True

        # Handle prepend mask only
        if prepend_mask:
            if current_file == input_file and not append_mask:
                return apply_mask(current_file, prepend_mask, output_file, append=False, silent=silent)
            prepend_file = create_hidden_temp_file(prefix="wordreaper_prepend_", suffix=".tmp")
            temp_files.append(prepend_file)
            if not apply_mask(current_file, prepend_mask, prepend_file, append=False, silent=silent):
                return False
            current_file = prepend_file

        # Handle append mask
        if append_mask:
            return apply_mask(current_file, append_mask, output_file, append=True, silent=silent)

        # If no masks but transformations applied
        if current_file != output_file:
            shutil.copy2(current_file, output_file)

        if not silent:
            print(f"{GREEN}Wordlist processing completed successfully!{RESET}")

        return True

    finally:
        # Clean up temp files
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)


def generate_from_mask(mask, output_file, silent=False):
    """
    Generate words directly from a mask pattern without an input wordlist.
    Support complex patterns like NCL-?uS?u?u-1234.
    
    Args:
        mask: Mask pattern to use
        output_file: Path to output file
        silent: Whether to suppress output
        
    Returns:
        True if successful
    """
    # Check for Hashcat utility
    hashcat_utils = check_hashcat_available()
    
    if not hashcat_utils["maskprocessor"]:
        print(f"{RED}Error: mp64.bin/mp32.bin not found but required for mask operations.{RESET}")
        return False
    
    return generate_mask_directly(mask, output_file, silent)

# Alias for backward compatibility
mentalize_stream = mentalize
