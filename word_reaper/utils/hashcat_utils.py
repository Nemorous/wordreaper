"""
Enhanced Hashcat utilities integration for WordReaper.

This module provides direct functions to interact with Hashcat binaries
for high-performance word list manipulation with support for complex mask patterns.
"""

import os
import subprocess
import tempfile
import platform
from pathlib import Path
import time
import shutil
import uuid
import re
import pkg_resources
from tqdm import tqdm

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def get_binary_path(binary_name):
    """
    Get the path to a Hashcat binary.

    Args:
        binary_name: Base name of the binary to find

    Returns:
        Path to the binary or None if not found
    """
    system = platform.system().lower()

    if system == 'windows':
        binary_name = f"{binary_name}.exe"
    elif system in ['linux', 'darwin']:
        binary_name = f"{binary_name}.bin" if system == 'linux' else f"{binary_name}_macos"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    try:
        bin_path = pkg_resources.resource_filename("word_reaper", f"bin/{binary_name}")
    except Exception:
        bin_path = None

    if bin_path and os.path.exists(bin_path):
        if system != "Windows":
            try:
                os.chmod(bin_path, 0o755)
            except Exception as e:
                print(f"{RED}Warning: Could not set executable permissions: {e}{RESET}")
        return bin_path

    print(f"{RED}Warning: Could not find {binary_name} in word_reaper/bin directory{RESET}")
    return None


def create_hidden_temp_file(prefix="", suffix=""):
    unique_id = uuid.uuid4().hex[:8]
    timestamp = int(time.time())
    temp_dir = tempfile.gettempdir()
    filename = f".{prefix}{timestamp}_{unique_id}{suffix}"
    filepath = os.path.join(temp_dir, filename)

    with open(filepath, 'w') as f:
        pass

    return filepath


def create_rule_file(rules):
    path = create_hidden_temp_file(prefix="wordreaper_rule_", suffix=".rule")

    with open(path, 'w') as f:
        for rule in rules:
            f.write(f"{rule}\n")

    return path


def is_complex_mask(mask):
    return not bool(re.match(r'^(?:\?[asdluhHbB])+$', mask))


def apply_mask(input_file, mask, output_file, append=True, silent=False, increment=False):
    mp_bin = get_binary_path("mp64") or get_binary_path("mp32")
    combinator_bin = get_binary_path("combinator")

    if not mp_bin:
        print(f"{RED}Error: Could not find maskprocessor binary (mp64.bin or mp32.bin){RESET}")
        return False

    if not combinator_bin:
        print(f"{RED}Error: Could not find combinator binary (combinator.bin){RESET}")
        return False

    temp_mask_file = create_hidden_temp_file(prefix="wordreaper_mask_", suffix=".tmp")

    try:
        # Build maskprocessor command with optional increment flag
        if increment:
            # Calculate mask length for increment range
            # Each mask placeholder (?d, ?l, etc.) represents 1 character
            mask_length = mask.count('?')
            increment_flag = f"-i 1:{mask_length}" if mask_length > 0 else ""
        else:
            increment_flag = ""

        if is_complex_mask(mask):
            mp_cmd = f"{mp_bin} {increment_flag} '{mask}' > {temp_mask_file}"
        else:
            mp_cmd = f"{mp_bin} {increment_flag} {mask} > {temp_mask_file}"

        if not silent:
            increment_msg = " (incremental)" if increment else ""
            action = "Appending" if append else "Prepending"
            print(f"\n{action} {RED}{mask}{RESET} mask combinations{increment_msg} with {RED}{os.path.basename(mp_bin)}{RESET}...\n")

        start_time = time.time()
        result = subprocess.run(mp_cmd, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"{RED}Error running maskprocessor: {result.stderr}{RESET}")
            return False

        if not silent:
            elapsed = time.time() - start_time
            print(f"Mask generation completed in {RED}{elapsed:.2f}{RESET} seconds")

        if append:
            combine_cmd = f"{combinator_bin} {input_file} {temp_mask_file} > {output_file}"
        else:
            combine_cmd = f"{combinator_bin} {temp_mask_file} {input_file} > {output_file}"

        if not silent:
            print(f"Combining wordlist with mask using {RED}{os.path.basename(combinator_bin)}{RESET}...")

        start_time = time.time()
        result = subprocess.run(combine_cmd, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"{RED}Error running combinator: {result.stderr}{RESET}")
            return False

        if not silent:
            elapsed = time.time() - start_time
            print(f"Combination completed in {RED}{elapsed:.2f}{RESET} seconds")

        return True

    finally:
        if os.path.exists(temp_mask_file):
            os.remove(temp_mask_file)


def apply_rules(input_file, rules, output_file, silent=False, rules_file=None, user_flags_count=0):
    if rules_file:
        return apply_custom_rules_file(input_file, rules_file, output_file, silent)

    try:
        from word_reaper.utils.wordreaper_mutator import mutate_wordlist_file

        if not rules or user_flags_count <= 2:
            level = 0
        elif user_flags_count <= 4:
            level = 1
        else:
            level = 2

        if not silent:
            level_names = {0: "Basic", 1: "Intermediate", 2: "Advanced"}
            print(f"{GREEN}Applying {level_names[level]} mutations to wordlist...{RESET}")

        success = mutate_wordlist_file(
            input_file=input_file,
            output_file=output_file,
            level=level,
            silent=silent
        )

        if not success:
            print(f"{RED}Error: Mutation failed{RESET}")
            return False

        if not silent:
            print(f"{GREEN}Mutation completed successfully!{RESET}")

        return True

    except ImportError:
        print(f"{RED}Error: Could not import wordreaper_mutator{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Error applying mutations: {str(e)}{RESET}")
        return False


def apply_custom_rules_file(input_file, rules_file, output_file, silent=False):
    try:
        if not silent:
            print(f"{GREEN}Applying custom rules from {rules_file}...{RESET}")

        with open(rules_file, 'r', encoding='utf-8') as f:
            rules = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if not rules:
            print(f"{RED}Error: No valid rules found in {rules_file}{RESET}")
            return False

        if not silent:
            print(f"Loaded {len(rules)} rules from file")

        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            words = [line.strip() for line in f if line.strip()]

        results = set()

        for word in words:
            for rule in rules:
                try:
                    mutated = apply_hashcat_rule(word, rule)
                    if mutated:
                        results.add(mutated)
                except Exception as e:
                    if not silent:
                        print(f"{RED}Warning: Could not apply rule '{rule}' to '{word}': {e}{RESET}")

        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(results):
                f.write(word + '\n')

        if not silent:
            print(f"{GREEN}Applied rules to {len(words)} words, generated {len(results)} total words{RESET}")

        return True

    except FileNotFoundError:
        print(f"{RED}Error: Rules file not found: {rules_file}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Error applying custom rules: {str(e)}{RESET}")
        return False


def apply_hashcat_rule(word, rule):
    if not rule:
        return word

    result = word
    i = 0
    while i < len(rule):
        cmd = rule[i]

        if cmd == ':':
            pass
        elif cmd == 'l':
            result = result.lower()
        elif cmd == 'u':
            result = result.upper()
        elif cmd == 'c':
            result = result.capitalize()
        elif cmd == 'C':
            if result:
                result = result[0].lower() + result[1:].upper()
        elif cmd == 't':
            result = result.swapcase()
        elif cmd == 'r':
            result = result[::-1]
        elif cmd == 'd':
            result = result + result
        elif cmd == 'f':
            result = result + result[::-1]
        elif cmd == 'T' and i + 1 < len(rule):
            pos = int(rule[i + 1], 16)
            if 0 <= pos < len(result):
                result = result[:pos] + result[pos].swapcase() + result[pos + 1:]
            i += 1
        elif cmd == '$' and i + 1 < len(rule):
            char = rule[i + 1]
            result = result + char
            i += 1
        elif cmd == '^' and i + 1 < len(rule):
            char = rule[i + 1]
            result = char + result
            i += 1
        elif cmd == 's' and i + 2 < len(rule):
            old_char = rule[i + 1]
            new_char = rule[i + 2]
            result = result.replace(old_char, new_char)
            i += 2
        elif cmd == '@' and i + 1 < len(rule):
            char = rule[i + 1]
            result = result.replace(char, '')
            i += 1
        elif cmd == '.' and i + 1 < len(rule):
            pos = int(rule[i + 1], 16)
            if i + 2 < len(rule) and 0 <= pos < len(result):
                new_char = rule[i + 2]
                result = result[:pos] + new_char + result[pos + 1:]
                i += 2
            else:
                i += 1
        elif cmd == 'i' and i + 2 < len(rule):
            pos = int(rule[i + 1], 16)
            char = rule[i + 2]
            if 0 <= pos <= len(result):
                result = result[:pos] + char + result[pos:]
            i += 2

        i += 1

    return result

def combinatorize(file1_path, file2_path, output_path, silent=False):
    combinator_bin = get_binary_path("combinator")

    if not combinator_bin:
        print(f"{RED}Error: Could not find combinator binary (combinator.bin){RESET}")
        return False

    try:
        if not silent:
            print(f"\nCombining wordlists with {RED}{os.path.basename(combinator_bin)}{RESET}...\n")

        start_time = time.time()

        with open(output_path, "wb") as outfile, \
             subprocess.Popen([combinator_bin, file1_path, file2_path],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:

            for chunk in iter(lambda: proc.stdout.read(4096), b""):
                outfile.write(chunk)

            proc.wait()

        if proc.returncode != 0:
            stderr = proc.stderr.read().decode("utf-8", errors="ignore")
            print(f"{RED}Error running combinator: {stderr}{RESET}")
            return False

        if not silent:
            elapsed = time.time() - start_time
            print(f"Combination completed in {RED}{elapsed:.2f}{RESET} seconds")

        return True

    except Exception as e:
        print(f"{RED}Error combining wordlists: {str(e)}{RESET}")
        return False

def generate_mask_directly(mask, output_file, silent=False):
    mp_bin = get_binary_path("mp64") or get_binary_path("mp32")

    if not mp_bin:
        print(f"{RED}Error: Could not find maskprocessor binary (mp64.bin or mp32.bin){RESET}")
        return False

    try:

        if is_complex_mask(mask):
            cmd = f"{mp_bin} '{mask}' > {output_file}"
        else:
            cmd = f"{mp_bin} {mask} > {output_file}"

        start_time = time.time()
        result = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"{RED}Error running maskprocessor: {result.stderr}{RESET}")
            return False

        if not silent:
            elapsed = time.time() - start_time
            print(f"Custom mask pattern generation completed in {RED}{elapsed:.2f}{RESET} seconds")

        return True

    except Exception as e:
        print(f"{RED}Error generating from mask: {str(e)}{RESET}")
        return False


def check_hashcat_available():
    return {
        "permute": get_binary_path("permute") is not None,
        "combinator": get_binary_path("combinator") is not None,
        "maskprocessor": (get_binary_path("mp64") is not None) or (get_binary_path("mp32") is not None)
    }

