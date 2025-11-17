#!/usr/bin/env python3
"""
Transform operations for WordReaper.

This module handles various word transformations including:
- Leetspeak using Hashcat rules
- Case toggles using Hashcat rules
- Selective leetspeak
- Word reversal
- Word segmentation with separators
"""

import os
import sys

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def apply_transform(input_file, output_file, leet=False, toggles=None,
                   selective_leet=None, reverse=False, separators=None, silent=False):
    """
    Apply transformation operations to a wordlist.

    Args:
        input_file: Input wordlist file
        output_file: Output wordlist file
        leet: Apply Hashcat leetspeak.rule
        toggles: Apply Hashcat toggles[1-5].rule (int 1-5)
        selective_leet: Apply selective_leet.py with max substitutions
        reverse: Reverse each word
        separators: Add separator character between word segments
        silent: Suppress output

    Returns:
        bool: Success status
    """
    from word_reaper.utils.hashcat_utils import apply_custom_rules_file

    current_file = input_file
    temp_files = []

    try:
        # Apply transforms in sequence
        operations = []

        # 1. Leetspeak using Hashcat rule
        if leet:
            operations.append(('leetspeak', apply_leet_transform))

        # 2. Toggles using Hashcat rule
        if toggles:
            operations.append((f'toggles{toggles}', lambda i, o, s: apply_toggles_transform(i, o, toggles, s)))

        # 3. Selective leet using selective_leet.py
        if selective_leet:
            operations.append((f'selective_leet({selective_leet})', lambda i, o, s: apply_selective_leet_transform(i, o, selective_leet, s)))

        # 4. Reverse words
        if reverse:
            operations.append(('reverse', apply_reverse_transform))

        # 5. Word segmentation with separators
        if separators:
            operations.append((f'separators({separators})', lambda i, o, s: apply_separators_transform(i, o, separators, s)))

        # Execute operations
        for idx, (op_name, op_func) in enumerate(operations):
            if not silent:
                print(f"{GREEN}Applying {op_name} transformation...{RESET}")

            # Determine output file for this operation
            if idx == len(operations) - 1:
                # Last operation writes to final output
                next_file = output_file
            else:
                # Intermediate operation writes to temp file
                from word_reaper.utils.hashcat_utils import create_hidden_temp_file
                next_file = create_hidden_temp_file(prefix=f"wordreaper_{op_name}_", suffix=".tmp")
                temp_files.append(next_file)

            # Apply transformation
            success = op_func(current_file, next_file, silent)
            if not success:
                print(f"{RED}Error: {op_name} transformation failed{RESET}")
                return False

            current_file = next_file

        if not operations:
            # No operations specified, just copy file
            import shutil
            shutil.copy2(input_file, output_file)

        return True

    except Exception as e:
        print(f"{RED}Error during transformation: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


def apply_leet_transform(input_file, output_file, silent=False):
    """Apply Hashcat leetspeak.rule to wordlist."""
    from word_reaper.utils.hashcat_utils import apply_custom_rules_file

    # Get path to leetspeak.rule
    rules_dir = os.path.join(os.path.dirname(__file__), '..', 'rules')
    leetspeak_rule = os.path.join(rules_dir, 'leetspeak.rule')

    if not os.path.exists(leetspeak_rule):
        print(f"{RED}Error: leetspeak.rule not found at {leetspeak_rule}{RESET}")
        return False

    return apply_custom_rules_file(input_file, leetspeak_rule, output_file, silent)


def apply_toggles_transform(input_file, output_file, level, silent=False):
    """Apply Hashcat toggles[1-5].rule to wordlist."""
    from word_reaper.utils.hashcat_utils import apply_custom_rules_file

    # Get path to toggles rule
    rules_dir = os.path.join(os.path.dirname(__file__), '..', 'rules')
    toggles_rule = os.path.join(rules_dir, f'toggles{level}.rule')

    if not os.path.exists(toggles_rule):
        print(f"{RED}Error: toggles{level}.rule not found at {toggles_rule}{RESET}")
        return False

    return apply_custom_rules_file(input_file, toggles_rule, output_file, silent)


def apply_selective_leet_transform(input_file, output_file, max_subs, silent=False):
    """Apply selective leet using selective_leet.py."""
    try:
        from word_reaper.utils.selective_leet import generate_selective_leet


        # Read input words
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        # Generate selective leet variations
        results = set()
        for word in words:
            variations = generate_selective_leet(word, max_subs=max_subs)
            results.update(variations)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(results):
                f.write(f"{word}\n")

        if not silent:
            print(f"Generated {RED}{len(results)}{RESET} leet variations to output...")

        return True

    except Exception as e:
        print(f"{RED}Error in selective leet: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


def apply_reverse_transform(input_file, output_file, silent=False):
    """Reverse each word in the wordlist."""
    try:

        # Read input words
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        # Reverse each word
        results = set()
        for word in words:
            reversed_word = word[::-1]
            if reversed_word != word:  # Only add if different from original
                results.add(reversed_word)
            else:
                results.add(word)  # Add palindromes

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(results):
                f.write(f"{word}\n")

        if not silent:
            print(f"Generated {RED}{len(results)}{RESET} reversed words to output...")

        return True

    except Exception as e:
        print(f"{RED}Error in reverse: {e}{RESET}")
        return False


def apply_separators_transform(input_file, output_file, separator, silent=False):
    """Add separator between word segments using wordninja, or remove spaces if separator is empty."""
    try:
        # Special case: empty separator means remove all spaces
        if separator == "":

            # Read input words
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]

            # Remove spaces from each word
            results = set()
            for word in words:
                # Remove all spaces
                no_spaces = word.replace(' ', '')
                if no_spaces:  # Only add if not empty
                    results.add(no_spaces)

            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in sorted(results):
                    f.write(f"{word}\n")

            if not silent:
                print(f"Generated {RED}{len(results)}{RESET} words with spaces removed to output...")

            return True

        # Normal case: use wordninja for segmentation
        # Try to import wordninja
        try:
            import wordninja
        except ImportError:
            print(f"{RED}Error: wordninja library not installed.{RESET}")
            print(f"{RED}Install it with: pip install wordninja{RESET}")
            return False


        # Read input words
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        # Segment and add separators
        results = set()
        for word in words:
            # Split word into segments
            segments = wordninja.split(word)

            # Add segmented version
            if len(segments) > 1:
                segmented = separator.join(segments)
                results.add(segmented)
            # If no segments found, wordninja returns the original as single segment
            # We skip adding it to exclude originals

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(results):
                f.write(f"{word}\n")

        if not silent:
            print(f"Generated {RED}{len(results)}{RESET} words with separators to output...{RESET}")

        return True

    except Exception as e:
        print(f"{RED}Error in separators: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False


def apply_case_conversion(input_file, output_file, case_options, silent=False):
    """
    Apply case conversion to a wordlist.

    Args:
        input_file: Input wordlist file
        output_file: Output wordlist file
        case_options: List of case conversion options (lower, upper, pascal, sentence, all)
        silent: Suppress output

    Returns:
        bool: Success status
    """
    try:
        # Expand 'all' option to include all case types
        if 'all' in case_options:
            case_options = ['lower', 'upper', 'pascal', 'sentence']

        if not silent:
            conversions_display = {
                'lower': 'lowercase',
                'upper': 'UPPERCASE',
                'pascal': 'PascalCase',
                'sentence': 'Sentencecase'
            }
            conversions = [conversions_display[opt] for opt in case_options if opt in conversions_display]
            print(f"\nConverting to {RED}{', '.join(conversions)}{RESET}...\n")

        # Read input words
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        results = set()

        # Check if wordninja is needed
        if 'pascal' in case_options:
            try:
                import wordninja
            except ImportError:
                print(f"{RED}Error: wordninja library not installed (required for pascal).{RESET}")
                print(f"{RED}Install it with: pip install wordninja{RESET}")
                return False

        # Apply lowercase
        if 'lower' in case_options:
            for word in words:
                results.add(word.lower())

        # Apply uppercase
        if 'upper' in case_options:
            for word in words:
                results.add(word.upper())

        # Apply PascalCase
        if 'pascal' in case_options:
            import wordninja
            for word in words:
                # Split word into segments
                segments = wordninja.split(word.lower())

                # Capitalize each segment
                pascal_word = ''.join([seg.capitalize() for seg in segments])
                results.add(pascal_word)

        # Apply Sentence case
        if 'sentence' in case_options:
            for word in words:
                if len(word) > 0:
                    # Capitalize first character, lowercase the rest
                    sentence_word = word[0].upper() + word[1:].lower()
                    results.add(sentence_word)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(results):
                f.write(f"{word}\n")

        if not silent:
            print(f"Generated {RED}{len(results)}{RESET} words to output...")

        return True

    except Exception as e:
        print(f"{RED}Error in case conversion: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return False
