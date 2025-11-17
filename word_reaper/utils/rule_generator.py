"""
Hashcat rule generation for WordReaper.

This module translates WordReaper command-line arguments into Hashcat rule syntax
for efficient word list manipulation.
"""

import re
import itertools
from typing import List, Dict, Tuple, Optional, Set

# ANSI colors for output
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

# Hashcat character set definitions
HASHCAT_CHARSETS = {
    '?d': '0123456789',
    '?l': 'abcdefghijklmnopqrstuvwxyz',
    '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    '?s': '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
    '?a': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
}

def generate_rules_from_args(args) -> List[str]:
    """
    Generate Hashcat rules based on WordReaper arguments.
    
    Args:
        args: Command-line arguments from WordReaper
        
    Returns:
        List of Hashcat rules
    """
    rules = []
    
    # Start with the identity rule if no transformations are applied
    if not any([args.leet, args.toggle, args.underscores, args.spaces, args.hyphens]):
        rules.append("")  # Empty rule = identity
    
    # Apply leetspeak rules
    if args.leet:
        leet_rules = [
            "sa@", "se3", "si1", "so0", "ss$", "st7", "sl1"
        ]
        rules.extend(leet_rules)
    
    # Apply toggle case rules
    if args.toggle:
        # Generate rules for toggling different positions
        # Note: Basic toggle rules are provided; more comprehensive rules can be added
        toggle_rules = []
        
        # Toggle first letter
        toggle_rules.append("T0")
        
        # Toggle all (uppercase all)
        toggle_rules.append("u")
        
        # Toggle all (lowercase all)
        toggle_rules.append("l")
        
        # Toggle every other character
        toggle_rules.append("E")
        
        # Toggle everything except first character
        toggle_rules.append("T0E")
        
        # Add more common toggle patterns
        for i in range(1, 8):  # Reasonable limit for word length
            toggle_rules.append(f"T{i}")
        
        # Add toggle combinations for first few characters
        toggle_rules.append("T0T1")
        toggle_rules.append("T0T2")
        toggle_rules.append("T0T1T2")
        
        rules.extend(toggle_rules)
    
    # Apply character insertion rules
    if args.underscores:
        underscore_rules = []
        for i in range(1, 8):  # Insert at positions 1-7
            underscore_rules.append(f"i{i}_")
        rules.extend(underscore_rules)
    
    if args.spaces:
        space_rules = []
        for i in range(1, 8):  # Insert at positions 1-7
            space_rules.append(f"i{i} ")
        rules.extend(space_rules)
    
    if args.hyphens:
        hyphen_rules = []
        for i in range(1, 8):  # Insert at positions 1-7
            hyphen_rules.append(f"i{i}-")
        rules.extend(hyphen_rules)
    
    return rules

def parse_mask(mask: str) -> List[str]:
    """
    Parse a Hashcat-style mask into a list of character sets.
    
    Args:
        mask: Hashcat-style mask (e.g. ?d?d?d?s)
        
    Returns:
        List of character sets, one for each position in the mask
    """
    if not mask:
        return []
    
    charsets = []
    i = 0
    
    while i < len(mask):
        if i + 1 < len(mask) and mask[i] == '?' and mask[i+1] in 'dlusaDbLUSA':
            charset_key = mask[i:i+2]
            if charset_key.lower() in HASHCAT_CHARSETS:
                charsets.append(HASHCAT_CHARSETS[charset_key.lower()])
            i += 2
        else:
            # Handle literal characters
            charsets.append(mask[i])
            i += 1
    
    return charsets

def generate_mask_combinations(charsets: List[str], limit: int = 100000) -> List[str]:
    """
    Generate all combinations from the given charsets.
    
    Args:
        charsets: List of character sets
        limit: Maximum number of combinations to generate
        
    Returns:
        List of generated strings
    """
    if not charsets:
        return []
    
    # Calculate total combinations
    total_combinations = 1
    for charset in charsets:
        total_combinations *= len(charset)
    
    if total_combinations > limit:
        print(f"{RED}Warning: Mask would generate {total_combinations} combinations.{RESET}")
        print(f"{RED}Limiting to {limit} combinations for efficiency.{RESET}")
    
    # Generate combinations
    combinations = []
    for chars in itertools.product(*charsets):
        combinations.append(''.join(chars))
        if len(combinations) >= limit:
            break
    
    return combinations

def mask_to_character_lists(mask: str) -> Optional[List[List[str]]]:
    """
    Convert a mask to lists of characters for each position.
    
    Args:
        mask: Hashcat-style mask
        
    Returns:
        List of character lists, or None if invalid
    """
    if not mask:
        return None
    
    if not re.match(r'^(?:\?[asdlu])+$', mask):
        print(f"{RED}Invalid mask format: {mask}. Must contain only ?a, ?d, ?s, ?l, ?u sequences.{RESET}")
        return None
    
    charset_ids = [mask[i:i+2] for i in range(0, len(mask), 2)]
    
    charsets = []
    for charset_id in charset_ids:
        if charset_id in HASHCAT_CHARSETS:
            charsets.append(list(HASHCAT_CHARSETS[charset_id]))
        else:
            print(f"{RED}Unknown character set: {charset_id}{RESET}")
            return None
    
    return charsets

def create_mask_for_hashcat(mask: str) -> str:
    """
    Convert a WordReaper mask to a Hashcat-compatible mask.
    
    Args:
        mask: WordReaper mask (e.g. ?d?d?d)
        
    Returns:
        Hashcat-compatible mask
    """
    # For simple masks, they're already compatible
    if re.match(r'^(?:\?[asdlu])+$', mask, re.IGNORECASE):
        return mask
    
    # Handle more complex masks if needed
    return mask

def generate_prepend_rules(chars: List[str]) -> List[str]:
    """
    Generate rules to prepend characters.
    
    Args:
        chars: Characters to prepend
        
    Returns:
        List of Hashcat rules
    """
    rules = []
    
    for char in chars:
        # Escape special characters for Hashcat rules
        if char in '^$[]():.-\\|?*+{},&/':
            rule = f"^\\{char}"
        else:
            rule = f"^{char}"
        rules.append(rule)
    
    return rules

def generate_append_rules(chars: List[str]) -> List[str]:
    """
    Generate rules to append characters.
    
    Args:
        chars: Characters to append
        
    Returns:
        List of Hashcat rules
    """
    rules = []
    
    for char in chars:
        # Escape special characters for Hashcat rules
        if char in '^$[]():.-\\|?*+{},&/':
            rule = f"$\\{char}"
        else:
            rule = f"${char}"
        rules.append(rule)
    
    return rules

def generate_complex_mask_rules(prepend_mask, append_mask, synchronize=False, increment=False):
    """
    Generate complex mask rules that might require multiple tools.
    
    Args:
        prepend_mask: Mask to prepend
        append_mask: Mask to append
        synchronize: Whether to synchronize masks
        increment: Whether to increment mask lengths
        
    Returns:
        Dict with operation info
    """
    result = {
        'use_permute': False,          # Whether to use permute.bin
        'use_maskprocessor': False,    # Whether to use maskprocessor
        'use_combinator': False,       # Whether to use combinator.bin
        'prepend_chars': [],           # Characters to prepend
        'append_chars': [],            # Characters to append
        'rules': [],                   # Rules for permute.bin
        'prepend_mask': None,          # Mask for prepending
        'append_mask': None,           # Mask for appending
        'complex_operation': False     # Whether this is a complex operation requiring multiple tools
    }
    
    # Parse masks
    prepend_charsets = parse_mask(prepend_mask) if prepend_mask else []
    append_charsets = parse_mask(append_mask) if append_mask else []
    
    # Check if we can use simple rules
    if (not prepend_charsets or len(prepend_charsets) == 1) and \
       (not append_charsets or len(append_charsets) == 1) and \
       not synchronize and not increment:
        
        # We can use simple prepend/append rules
        result['use_permute'] = True
        
        if prepend_charsets:
            for char in prepend_charsets[0]:
                result['rules'].append(f"^{char}")
                result['prepend_chars'].append(char)
        
        if append_charsets:
            for char in append_charsets[0]:
                result['rules'].append(f"${char}")
                result['append_chars'].append(char)
    
    else:
        # Complex operation
        result['complex_operation'] = True
        
        # Determine which tools to use
        if prepend_mask:
            result['prepend_mask'] = prepend_mask
            result['use_maskprocessor'] = True
            result['use_combinator'] = True
        
        if append_mask:
            result['append_mask'] = append_mask
            result['use_maskprocessor'] = True
            result['use_combinator'] = True
    
    return result

def expand_mask_incrementally(mask, max_length=None):
    """
    Expand a mask incrementally (similar to Hashcat's --increment flag).
    
    Args:
        mask: Hashcat-style mask
        max_length: Maximum length to expand to
        
    Returns:
        List of masks with increasing lengths
    """
    if not mask:
        return []
    
    # Parse mask into individual charset sequences
    charset_seqs = []
    i = 0
    while i < len(mask):
        if i + 1 < len(mask) and mask[i] == '?' and mask[i+1] in 'dlusaDbLUSA':
            charset_seqs.append(mask[i:i+2])
            i += 2
        else:
            charset_seqs.append(mask[i])
            i += 1
    
    # Get maximum length if not specified
    if max_length is None:
        max_length = len(charset_seqs)
    else:
        max_length = min(max_length, len(charset_seqs))
    
    # Generate masks with increasing lengths
    masks = []
    for length in range(1, max_length + 1):
        masks.append(''.join(charset_seqs[:length]))
    
    return masks
