"""
WordReaper Password Mutator

Consolidated password mutation functionality extracted and adapted from passmutate
for integration with WordReaper. Provides powerful password transformations without
external dependencies.

Based on passmutate by Kaimo (https://github.com/kaimosec/passmutate)
Adapted for WordReaper by d4rkfl4m3z
"""

import re
import itertools
from typing import List, Set, Iterator

RED = '\033[91m'
RESET = '\033[0m'

class PasswordMutator:
    """
    Advanced password mutation engine with multiple complexity levels.
    """
    
    def __init__(self):
        # Common number sequences for appending
        self.numbers = ['1', '2', '3', '123', '12', '23', '01', '02', '03']
        self.years = ['2024', '2023', '2022', '2021', '2020', '1990', '1991', '1992']
        
        # Common special characters
        self.specials = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=']
        
        # Leetspeak mappings
        self.leet_map = {
            'a': '@', 'A': '@',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'l': '1', 'L': '1',
            'o': '0', 'O': '0',
            's': '$', 'S': '$',
            't': '7', 'T': '7',
            'g': '9', 'G': '9',
            'b': '6', 'B': '6'
        }
    
    def apply_leet(self, word: str) -> List[str]:
        """Apply leetspeak transformations"""
        results = set()
        
        # Full leet
        leet_word = ''.join(self.leet_map.get(char, char) for char in word)
        if leet_word != word:
            results.add(leet_word)
        
        # Partial leet (only some characters)
        for char, replacement in self.leet_map.items():
            if char in word:
                results.add(word.replace(char, replacement))
        
        # Advanced leet combinations
        chars_in_word = [char for char in self.leet_map.keys() if char.lower() in word.lower()]
        if len(chars_in_word) > 1:
            # Try combinations of 2 leet substitutions
            for combo in itertools.combinations(chars_in_word[:4], 2):  # Limit to prevent explosion
                temp_word = word
                for char in combo:
                    temp_word = temp_word.replace(char, self.leet_map[char])
                    temp_word = temp_word.replace(char.swapcase(), self.leet_map[char])
                if temp_word != word:
                    results.add(temp_word)
        
        return list(results)
    
    def apply_case_variations(self, word: str) -> List[str]:
        """Apply various case transformations"""
        results = set()
        
        if len(word) > 0:
            results.add(word.upper())
            results.add(word.lower())
            results.add(word.capitalize())
            
            # Title case
            results.add(word.title())
            
            # Alternating case
            if len(word) > 1:
                alt1 = ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(word))
                alt2 = ''.join(c.lower() if i % 2 == 0 else c.upper() for i, c in enumerate(word))
                results.add(alt1)
                results.add(alt2)
            
            # First and last upper
            if len(word) > 2:
                first_last_upper = word[0].upper() + word[1:-1].lower() + word[-1].upper()
                results.add(first_last_upper)
        
        return list(results)
    
    def apply_number_appending(self, word: str) -> List[str]:
        """Append common numbers and years"""
        results = []
        
        for num in self.numbers + self.years:
            results.append(word + num)
        
        # Prepend numbers too
        for num in self.numbers[:5]:  # Limit prepending to avoid too many results
            results.append(num + word)
        
        return results
    
    def apply_special_chars(self, word: str) -> List[str]:
        """Add special characters at the end and beginning"""
        results = []
        
        # Append specials
        for spec in self.specials:
            results.append(word + spec)
            
        # Common double specials
        for spec in ['!!', '@@', '##', '$$']:
            results.append(word + spec)
        
        # Prepend some specials
        for spec in ['!', '@', '#', '$']:
            results.append(spec + word)
        
        return results
    
    def apply_character_insertion(self, word: str) -> List[str]:
        """Insert characters between letters"""
        results = []
        
        if len(word) > 1:
            # Insert underscores
            results.append('_'.join(word))
            
            # Insert hyphens
            results.append('-'.join(word))
            
            # Insert dots
            results.append('.'.join(word))
            
            # Insert spaces
            results.append(' '.join(word))
            
            # Insert at specific positions (not between every character)
            for i in range(1, min(len(word), 4)):  # Insert at positions 1-3
                for char in ['_', '-', '.']:
                    new_word = word[:i] + char + word[i:]
                    results.append(new_word)
        
        return results
    
    def apply_common_suffixes(self, word: str) -> List[str]:
        """Add common password suffixes"""
        suffixes = ['123', '321', '1234', '12345', '!', '!!', '123!', '!123', 
                   '1!', '2!', '3!', '@1', '@2', '@3', '2024', '2023']
        
        return [word + suffix for suffix in suffixes]
    
    def apply_common_prefixes(self, word: str) -> List[str]:
        """Add common password prefixes"""
        prefixes = ['1', '2', '3', '12', '123', '!', '@', '#']
        
        return [prefix + word for prefix in prefixes]
    
    def reverse_mutations(self, word: str) -> List[str]:
        """Reverse and reverse+modify mutations"""
        results = []
        
        reversed_word = word[::-1]
        results.append(reversed_word)
        
        # Reverse + numbers
        for num in self.numbers[:5]:
            results.append(reversed_word + num)
        
        # Reverse + specials
        for spec in ['!', '@', '#']:
            results.append(reversed_word + spec)
        
        return results
    
    def duplications(self, word: str) -> List[str]:
        """Word duplication patterns"""
        results = []
        
        if len(word) <= 10:  # Avoid creating very long words
            results.append(word + word)  # double
            results.append(word + word.capitalize())
            results.append(word + word.upper())
            
            # With separators
            for sep in ['', '_', '-', '.']:
                if sep:
                    results.append(word + sep + word)
        
        return results
    
    def mutate_level_1(self, word: str) -> Set[str]:
        """
        Basic mutations - generates ~60 variations per word
        """
        mutations = set()
        mutations.add(word)  # Original word
        
        # Case variations
        mutations.update(self.apply_case_variations(word))
        
        # Simple number appending
        for num in ['1', '2', '3', '123']:
            mutations.add(word + num)
        
        # Simple special chars
        for spec in ['!', '@', '#', '$']:
            mutations.add(word + spec)
        
        # Basic leet
        simple_leet = word.replace('a', '@').replace('e', '3').replace('i', '1').replace('o', '0')
        if simple_leet != word:
            mutations.add(simple_leet)
        
        return mutations
    
    def mutate_level_2(self, word: str) -> Set[str]:
        """
        Intermediate mutations - generates ~350 variations per word
        """
        mutations = self.mutate_level_1(word)
        
        # Extended leet
        mutations.update(self.apply_leet(word))
        
        # More numbers and years
        mutations.update(self.apply_number_appending(word))
        
        # More special characters
        mutations.update(self.apply_special_chars(word))
        
        # Common suffixes
        mutations.update(self.apply_common_suffixes(word))
        
        # Character insertion (limited)
        for i in range(1, min(len(word), 3)):
            for char in ['_', '-']:
                mutations.add(word[:i] + char + word[i:])
        
        # Apply mutations to case variations
        case_vars = self.apply_case_variations(word)
        for var in case_vars[:3]:  # Limit to prevent explosion
            mutations.update(self.mutate_level_1(var))
        
        return mutations
    
    def mutate_level_3(self, word: str) -> Set[str]:
        """
        Advanced mutations - generates ~24,200 variations per word
        WARNING: Use only for small wordlists due to size explosion
        """
        mutations = self.mutate_level_2(word)
        
        # Full character insertion
        mutations.update(self.apply_character_insertion(word))
        
        # Prefixes
        mutations.update(self.apply_common_prefixes(word))
        
        # Reversals
        mutations.update(self.reverse_mutations(word))
        
        # Duplications
        mutations.update(self.duplications(word))
        
        # Apply level 1 mutations to case variations
        case_vars = self.apply_case_variations(word)
        for var in case_vars:
            # Add some level 1 mutations for each case variation
            var_mutations = self.mutate_level_1(var)
            for mut in list(var_mutations)[:20]:  # Limit to prevent extreme explosion
                # Add numbers and specials to variations
                mutations.add(mut + '1')
                mutations.add(mut + '!')
                mutations.add(mut + '123')
        
        # Cross-mutations: apply leet to case variations
        for var in case_vars:
            mutations.update(self.apply_leet(var)[:10])  # Limit
        
        return mutations
    
    def mutate_word(self, word: str, level: int = 1) -> List[str]:
        """
        Mutate a single word at the specified level

        Args:
            word: Input word to mutate
            level: Mutation level (1=basic, 2=intermediate, 3=advanced)

        Returns:
            List of mutated words
        """
        if level == 1:
            mutations = self.mutate_level_1(word)
        elif level == 2:
            mutations = self.mutate_level_2(word)
        elif level == 3:
            mutations = self.mutate_level_3(word)
        else:
            raise ValueError("Mutation level must be 1, 2, or 3")
        
        # Remove the original word if you only want mutations
        mutations.discard(word)
        
        return sorted(list(mutations))
    
    def mutate_wordlist(self, words: List[str], level: int = 1,
                       max_length: int = None, min_length: int = 1) -> Iterator[str]:
        """
        Mutate a list of words

        Args:
            words: List of input words
            level: Mutation level (1, 2, or 3)
            max_length: Maximum word length to include
            min_length: Minimum word length to include

        Yields:
            Mutated words (original words are not included)
        """
        seen = set()

        for word in words:
            word = word.strip()
            if not word:
                continue

            # Add mutations (original word is NOT added)
            try:
                mutations = self.mutate_word(word, level)
                for mutation in mutations:
                    if min_length <= len(mutation) <= (max_length or float('inf')):
                        if mutation not in seen:
                            seen.add(mutation)
                            yield mutation
            except Exception as e:
                print(f"Warning: Could not mutate word '{word}': {e}")
                continue


def mutate_wordlist_file(input_file: str, output_file: str, level: int = 1,
                        max_length: int = None, min_length: int = 1, silent: bool = False):
    """
    Mutate words from an input file and save to output file

    Args:
        input_file: Path to input wordlist
        output_file: Path to output wordlist
        level: Mutation level (1, 2, or 3)
        max_length: Maximum word length
        min_length: Minimum word length
        silent: Suppress output
    """
    mutator = PasswordMutator()

    if not silent:
        level_descriptions = {
            1: "Basic (~60 mutations per word)",
            2: "Intermediate (~350 mutations per word)",
            3: "Advanced (~24,200 mutations per word)"
        }
        print(f"Mutating wordlist with level {level}: {level_descriptions.get(level, 'Unknown')}")
    
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as infile:
            words = [line.strip() for line in infile if line.strip()]
        
        if not silent:
            print(f"Loaded {len(words)} words from {input_file}\n")
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            count = 0
            for mutation in mutator.mutate_wordlist(words, level, max_length, min_length):
                outfile.write(mutation + '\n')
                count += 1
        
        if not silent:
            print(f"Generated {RED}{count}{RESET} mutated words to output...")
    
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True


# Example usage
if __name__ == "__main__":
    # Test the mutator
    mutator = PasswordMutator()
    
    test_word = "password"
    print(f"Testing mutations for '{test_word}':")

    for level in [1, 2]:  # Skip level 3 for testing
        mutations = mutator.mutate_word(test_word, level)
        print(f"\nLevel {level}: {len(mutations)} mutations")
        print(f"First 10: {mutations[:10]}")
