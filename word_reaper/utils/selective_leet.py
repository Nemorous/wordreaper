#!/usr/bin/env python3
"""
Generate ALL possible selective leetspeak combinations
For when rules can't handle partial substitutions

Example: "password" generates:
- password (no changes)
- p@ssword (only first a)
- pa$$word (only first s)
- p@$$word (first a, first s)
- passw0rd (only o)
- p@ssw0rd (first a, o)
- etc... ALL combinations

Usage:
    python selective_leet_generator.py wordlist.txt > selective_leet_output.txt
"""

import sys
import itertools

# Leet substitution map
LEET_MAP = {
    'a': ['a', '@', '4'],
    'e': ['e', '3'],
    'i': ['i', '1', '!'],
    'o': ['o', '0'],
    's': ['s', '5', '$'],
    'l': ['l', '1'],
    't': ['t', '7'],
    'g': ['g', '9'],
    'b': ['b', '8'],
    'z': ['z', '2'],
}

# Case toggle options
CASE_OPTIONS = ['lower', 'upper', 'capitalize', 'title', 'toggle']


def generate_selective_leet(word, max_subs=None):
    """
    Generate all possible selective leetspeak variations
    
    Args:
        word: Base word to transform
        max_subs: Maximum number of substitutions (None = all)
    
    Returns:
        Set of all variations
    """
    variations = set()
    word_lower = word.lower()
    
    # Find all positions that can be substituted
    sub_positions = []
    for i, char in enumerate(word_lower):
        if char in LEET_MAP:
            sub_positions.append((i, char, LEET_MAP[char]))
    
    if not sub_positions:
        return {word}
    
    # Generate all combinations of substitutions
    # For each position, we can choose any of its leet variants
    for indices in range(len(sub_positions) + 1):
        if max_subs and indices > max_subs:
            break
            
        # Choose which positions to substitute
        for combo in itertools.combinations(range(len(sub_positions)), indices):
            # For each chosen position, try all its variants
            chars_list = list(word_lower)
            
            # Get all possible character choices for selected positions
            choices = []
            for idx in combo:
                pos, original_char, variants = sub_positions[idx]
                choices.append([(pos, v) for v in variants if v != original_char])
            
            if not choices:
                variations.add(word_lower)
                continue
            
            # Generate all combinations of variant choices
            for choice_combo in itertools.product(*choices):
                chars = list(word_lower)
                for pos, variant in choice_combo:
                    chars[pos] = variant
                variations.add(''.join(chars))
    
    return variations


def apply_case_transformations(word):
    """
    Apply various case transformations
    
    Returns:
        Set of case variations
    """
    variations = set()
    
    # Original
    variations.add(word)
    
    # All lowercase
    variations.add(word.lower())
    
    # All uppercase
    variations.add(word.upper())
    
    # Capitalize first
    variations.add(word.capitalize())
    
    # Title case
    variations.add(word.title())
    
    # Toggle cases (first few variations)
    for i in range(min(len(word), 4)):
        chars = list(word.lower())
        chars[i] = chars[i].upper()
        variations.add(''.join(chars))
    
    # Every other uppercase
    chars = list(word.lower())
    for i in range(0, len(chars), 2):
        chars[i] = chars[i].upper()
    variations.add(''.join(chars))
    
    # Every other uppercase (offset)
    chars = list(word.lower())
    for i in range(1, len(chars), 2):
        chars[i] = chars[i].upper()
    variations.add(''.join(chars))
    
    return variations


def generate_all_variations(word, max_leet_subs=None, include_case=True):
    """
    Generate all leetspeak + case variations
    
    Args:
        word: Base word
        max_leet_subs: Max number of leet substitutions (None = unlimited)
        include_case: Apply case transformations
    
    Returns:
        Set of all variations
    """
    all_variations = set()
    
    # Generate leetspeak variations
    leet_variations = generate_selective_leet(word, max_subs=max_leet_subs)
    
    # Apply case transformations to each leet variation
    if include_case:
        for leet_var in leet_variations:
            case_variations = apply_case_transformations(leet_var)
            all_variations.update(case_variations)
    else:
        all_variations = leet_variations
    
    return all_variations


def main():
    if len(sys.argv) < 2:
        print("Usage: python selective_leet_generator.py <wordlist.txt> [max_leet_subs]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  max_leet_subs: Maximum number of leet substitutions per word (default: 3)", file=sys.stderr)
        print("                 Lower = faster, higher = more comprehensive", file=sys.stderr)
        sys.exit(1)
    
    wordlist_path = sys.argv[1]
    max_leet_subs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    print(f"[*] Generating selective leetspeak with max {max_leet_subs} substitutions per word", file=sys.stderr)
    print(f"[*] Reading wordlist: {wordlist_path}", file=sys.stderr)
    
    try:
        with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[!] Error reading wordlist: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(f"[*] Processing {len(words)} base words...", file=sys.stderr)
    
    total_generated = 0
    all_variations = set()
    
    for i, word in enumerate(words, 1):
        if i % 100 == 0:
            print(f"[*] Processed {i}/{len(words)} words, {len(all_variations)} variations so far...", file=sys.stderr)
        
        variations = generate_all_variations(word, max_leet_subs=max_leet_subs, include_case=True)
        all_variations.update(variations)
    
    print(f"[*] Generated {len(all_variations)} total variations", file=sys.stderr)
    print(f"[*] Writing to stdout...", file=sys.stderr)
    
    # Output all variations
    for variation in sorted(all_variations):
        print(variation)
    
    print(f"[+] Complete! {len(all_variations)} variations generated", file=sys.stderr)


if __name__ == '__main__':
    main()
