#!/usr/bin/env python3
"""
Word Reaper - Reap & Forge Wordlists for Password Cracking

This tool allows you to scrape, manipulate, and combine wordlists for password cracking
with high-performance using Hashcat utilities.

Author: d4rkfl4m3z
Version: 2.0.0
"""
import argparse
import sys
import os
import logging
from word_reaper.scraper import html_scraper, github_scraper, file_loader, text_scraper
from word_reaper.utils import cleaner, formatter, permutator, merge, wordreaper_mutator
import word_reaper.utils.ascii_art as ascii_art
from word_reaper.utils import ascii as banner

# Check if Hashcat utilities are available
try:
    from word_reaper.utils.hashcat_utils import check_hashcat_available, combinatorize
    HASHCAT_UTILS = check_hashcat_available()
    HASHCAT_AVAILABLE = any(HASHCAT_UTILS.values())
except ImportError:
    HASHCAT_AVAILABLE = False
    HASHCAT_UTILS = {"permute": False, "combinator": False, "maskprocessor": False}

# Configure logging to reduce verbosity
logging.basicConfig(level=logging.WARNING)

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Custom help formatter classes
class LeadingBlankLineMixin:
    """Insert a blank line before the generated 'usage:' line."""
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "usage: "
        return super().add_usage(usage, actions, groups, prefix="\n" + prefix)

class HelpFormatter(LeadingBlankLineMixin, argparse.RawDescriptionHelpFormatter):
    """Aligned, wide help with NO metavars shown for any arguments."""
    def __init__(self, prog):
        super().__init__(prog, max_help_position=30, width=100)

    def add_usage(self, usage, actions, groups, prefix=None):
        # Capitalized prefix + leading blank line
        return super().add_usage(usage, actions, groups, prefix="\nUsage: ")

    def _format_action_invocation(self, action):
        # Hide metavars for ALL args (both optionals and positionals)
        if action.option_strings:
            # Show only the flags, e.g. "-m, --method"
            return ", ".join(action.option_strings)
        else:
            # Positional: show just the name without angle brackets/metavar
            return action.dest

    def _format_action(self, action):
        # Force help text to start at a fixed position
        help_position = 25  # Adjust this value to change spacing
        help_width = self._width - help_position

        # Get action invocation string
        action_header = self._format_action_invocation(action)

        # Get help text
        help_text = self._expand_help(action) if action.help else ''

        # Format the action with forced spacing
        if not help_text:
            return f"  {action_header}\n"

        # Calculate padding needed
        action_width = help_position - 2  # -2 for initial indent
        if len(action_header) <= action_width - 2:
            # Action fits on same line as help
            return f"  {action_header:<{action_width-2}}  {help_text}\n"
        else:
            # Action is too long, put help on next line
            return f"  {action_header}\n{' ' * help_position}{help_text}\n"

class DescFirstArgumentParser(argparse.ArgumentParser):
    """Custom parser that shows description before usage."""
    def format_help(self):
        formatter = self._get_formatter()

        # 1) Description (first)
        if self.description:
            formatter.add_text(self.description)
            formatter.add_text("")  # blank line

        # 2) Usage (capitalized)
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups,
                            prefix="Usage: ")

        formatter.add_text("")  # blank line

        # 3) Argument groups (in declared order)
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # 4) Epilog (if any)
        if self.epilog:
            formatter.add_text(self.epilog)

        return formatter.format_help()

def main():
    """Main function with optimized file handling."""
    try:
        # Start main processing
        if '--ascii-art' in sys.argv:
            ascii_art.print_scythe()
            sys.exit()

        # If no arguments provided, show help
        if len(sys.argv) == 1:
            sys.argv.append('--help')

        # Only show banner when --help or -h is used
        if ('--help' in sys.argv or '-h' in sys.argv) and '--quiet' not in sys.argv and '-q' not in sys.argv:
            banner.print_banner()

            # Show Hashcat availability
            if HASHCAT_AVAILABLE:
                available_tools = [tool for tool, available in HASHCAT_UTILS.items() if available]
                print()
            else:
                print(f"{RED}Utilities not found. Please ensure they exist in the ./bin directory.{RESET}")
                print(f"{RED}Required utilities: permute.bin, combinator.bin, mp64.bin (or mp32.bin){RESET}")
                print()

        parser = DescFirstArgumentParser(
            prog="wordreaper",
            formatter_class=HelpFormatter,
            add_help=False,
            usage="%(prog)s [OPTIONS]... FILE",
        )

        # Main Options
        main_group = parser.add_argument_group('Main Options')
        main_group.add_argument('-m', '--method', help='Scraping method: html, github, text, file')
        main_group.add_argument('-u', '--url', help='Target URL to scrape')
        main_group.add_argument('-i', '--input', help='Local file to load wordlist from')
        main_group.add_argument('-o', '--output', default='wordlist.txt', help='Output file name')

        # HTML Scraping Options
        html_group = parser.add_argument_group('HTML Scraping')
        html_group.add_argument('-s', '--selector', help='CSS selector for precise HTML element targeting (preferred)')
        html_group.add_argument('--href', help='Filter: only keep links where href contains this text')
        html_group.add_argument('--regex', help='Filter: only keep text matching this regex pattern')
        html_group.add_argument('-t', '--tags', nargs='+', help='List of HTML tags to scrape from')
        html_group.add_argument('--min-length', type=int, default=1, help='Minimum word length to include')
        html_group.add_argument('--max-length', type=int, help='Maximum word length to include')
        html_group.add_argument('-p', '--preserve', action='store_true', help='Preserve original formatting when scraping')

        # Word manipulation options
        mutation_group = parser.add_argument_group('Word Manipulation')
        mutation_group.add_argument('-x', '--mutate', action='store_true', help='Mutate words using mutation levels')
        mutation_group.add_argument('--mutation-level', type=int, choices=[1, 2, 3], help='Mutation complexity: 1=(~60/word), 2=(~350/word), 3=(~24k/word)')

        # Transform Options
        transform_group = parser.add_argument_group('Transform Options')
        transform_group.add_argument('--selective-leet', type=int, metavar='MAX_SUBS', help='Use selective leet with max substitutions')
        transform_group.add_argument('--reverse', action='store_true', help='Reverse each word')
        transform_group.add_argument('--separators', type=str, metavar='CHAR', help='Add separator between words')
        transform_group.add_argument('--custom-mask', type=str, help='Generate words from custom mask pattern')

        # Case conversion
        case_group = parser.add_argument_group('Case Conversion')
        case_group.add_argument('-c', '--convert', nargs='*', metavar='CASE',
                               choices=['lower', 'upper', 'pascal', 'sentence', 'all'],
                                help='Convert case of words: lower, upper, pascal, sentence, all')

        # Hashcat Integration
        wordlist_group = parser.add_argument_group('Integrate Hashcat')
        wordlist_group.add_argument('--append-mask', type=str, help='Append a hashcat-style mask')
        wordlist_group.add_argument('--prepend-mask', type=str, help='Prepend a hashcat-style mask')
        wordlist_group.add_argument('--increment', action='store_true', help='Apply incremental mask lengths')
        wordlist_group.add_argument('--merge', nargs='+', help='Merge and deduplicate multiple wordlists')
        wordlist_group.add_argument('--combinator', nargs=2, metavar=('file1', 'file2'), help='Combine words from two files')
        wordlist_group.add_argument('-r', '--rules', help='Apply Hashcat rules to input wordlist')

        # General
        general_group = parser.add_argument_group('General')
        general_group.add_argument('-q', '--quiet', action='store_true', help='Suppress most output except errors and results')
        general_group.add_argument('--ascii-art', action='store_true', help='Display the reaper ASCII art')
        general_group.add_argument('-h', '--help', action='help', help='Show this help message and exit')

        args = parser.parse_args()

        # Validation logic
        if args.method in ['html', 'github', 'text'] and not args.url:
            print(f"\n{RED}Error:{RESET} --url is required when using --method {args.method}\n")
            sys.exit(1)
            
        if args.method == 'file' and not args.input:
            print(f"\n{RED}Error:{RESET} --input is required when using --method file\n")
            sys.exit(1)

        if args.method == 'html':
            # Require either --selector or --tags for HTML scraping
            if not args.selector and not args.tags:
                print(f"\n{RED}Error:{RESET} Either --selector or --tags is required for HTML scraping\n")
                sys.exit(1)

        # Validate --rules requires --input
        if args.rules and not args.input:
            print(f"\n{RED}Error:{RESET} --rules requires a rules file and --input\n")
            sys.exit(1)

        # Validate transform options require --input
        if args.selective_leet and not args.input:
            print(f"\n{RED}Error:{RESET} --selective-leet requires --input\n")
            sys.exit(1)

        if args.reverse and not args.input:
            print(f"\n{RED}Error:{RESET} --reverse requires --input\n")
            parser.print_help()
            sys.exit(1)

        if args.separators is not None and not args.input:
            print(f"\n{RED}Error:{RESET} --separators requires --input\n")
            sys.exit(1)

        # Validate --convert requires --input and at least one suboption
        if args.convert is not None:
            if not args.input:
                print(f"\n{RED}Error:{RESET} --convert requires --input\n")
                sys.exit(1)
            if len(args.convert) == 0:
                print(f"\n{RED}Error:{RESET} --convert requires at least one suboption (lower, upper, pascal, sentence, all)\n")
                sys.exit(1)

        # Validate --mutate requires --input and --mutation-level
        if args.mutate:
            if not args.input:
                print(f"\n{RED}Error:{RESET} --mutate requires --input\n")
                sys.exit(1)
            if args.mutation_level is None:
                print(f"\n{RED}Error:{RESET} --mutate requires --mutation-level {1,2,3}\n")
                sys.exit(1)

        # Validate mask operations require --input
        if (args.append_mask or args.prepend_mask) and not args.input:
            print(f"\n{RED}Error:{RESET} Mask operations require --input\n")
            sys.exit(1)

        # Handle direct mask generation
        if args.custom_mask:
            # Validate mask pattern is not empty
            if not args.custom_mask.strip():
                print(f"{RED}Error:{RESET} Custom mask pattern cannot be empty")
                sys.exit(1)

            if not HASHCAT_UTILS["maskprocessor"]:
                print(f"{RED}Error:{RESET} mp64.bin not found but required for mask operations.")
                sys.exit(1)

            if not args.quiet:
                print(f"\nGenerating words from custom mask pattern: {RED}{args.custom_mask}{RESET}\n")
            
            # Use direct mask generation
            success = permutator.generate_from_mask(args.custom_mask, args.output, silent=args.quiet)
            
            if not success:
                print(f"{RED}Error: Mask generation failed.{RESET}")
                sys.exit(1)
            
            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle merge operation
        if args.merge:
            if not args.quiet:
                print(f"\nMerging {RED}{len(args.merge)}{RESET} wordlists...\n")
            
            # To optimize merging, write directly to output file
            output_set = set()
            
            # Process each file
            for file_path in args.merge:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            word = line.strip()
                            if word:
                                output_set.add(word)
                except FileNotFoundError:
                    print(f"{RED}Error: File not found: {file_path}{RESET}")
            
            # Write merged words directly to output file
            with open(args.output, 'w', encoding='utf-8') as f:
                for word in sorted(output_set):
                    f.write(f"{word}\n")
            
            if not args.quiet:
                print(f"Merged {RED}{len(output_set)}{RESET} unique words to output...")
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle combinator operation
        if args.combinator:
            if not HASHCAT_UTILS["combinator"]:
                print(f"{RED}Error: combinator.bin not found but required for --combinator option.{RESET}")
                sys.exit(1)
                
            # Use direct hashcat implementation
            combinatorize(
                file1_path=args.combinator[0],
                file2_path=args.combinator[1],
                output_path=args.output,
                silent=args.quiet
            )
            
            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --rules operation (standalone)
        if args.rules:
            from word_reaper.utils.hashcat_utils import apply_custom_rules_file
            if not args.quiet:
                print(f"\nApplying Hashcat rules from: {RED}{args.rules}{RESET}")
            success = apply_custom_rules_file(args.input, args.rules, args.output, args.quiet)
            if not success:
                print(f"{RED}Error: Rules application failed.{RESET}")
                sys.exit(1)
            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --selective-leet operation
        if args.selective_leet:
            from word_reaper.utils.transform import apply_selective_leet_transform

            if not args.quiet:
                print(f"\nApplying selective leetspeak with max {RED}{args.selective_leet}{RESET} substitutions...\n")

            success = apply_selective_leet_transform(args.input, args.output, args.selective_leet, args.quiet)

            if not success:
                print(f"{RED}Error: Selective leet operation failed.{RESET}")
                sys.exit(1)

            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --reverse operation
        if args.reverse:
            from word_reaper.utils.transform import apply_reverse_transform

            if not args.quiet:
                print(f"\nReversing words...\n")

            success = apply_reverse_transform(args.input, args.output, args.quiet)

            if not success:
                print(f"{RED}Error: Reverse operation failed.{RESET}")
                sys.exit(1)

            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --separators operation
        if args.separators is not None:
            from word_reaper.utils.transform import apply_separators_transform

            if not args.quiet:
                if args.separators == "":
                    print(f"\nRemoving spaces from words...\n")
                else:
                    print(f"\nAdding '{RED}{args.separators}{RESET}' separators between words...\n")

            success = apply_separators_transform(args.input, args.output, args.separators, args.quiet)

            if not success:
                print(f"{RED}Error: Separators operation failed.{RESET}")
                sys.exit(1)

            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --convert operation
        if args.convert is not None:
            from word_reaper.utils.transform import apply_case_conversion

            success = apply_case_conversion(
                input_file=args.input,
                output_file=args.output,
                case_options=args.convert,
                silent=args.quiet
            )

            if not success:
                print(f"{RED}Error: Case conversion failed.{RESET}")
                sys.exit(1)

            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle --mutate operation
        if args.mutate:
            from word_reaper.utils.wordreaper_mutator import mutate_wordlist_file
            if not args.quiet:
                level_names = {1: "Basic", 2: "Intermediate", 3: "Advanced"}
                print(f"\nApplying {level_names[args.mutation_level]} mutations ({RED}level {args.mutation_level}{RESET})...\n")
            success = mutate_wordlist_file(
                input_file=args.input,
                output_file=args.output,
                level=args.mutation_level,
                silent=args.quiet
            )
            if not success:
                print(f"{RED}Error: Mutation failed.{RESET}")
                sys.exit(1)
            if not args.quiet:
                print(f"Wordlist saved to: {RED}{args.output}{RESET}")
            return

        # Handle standalone mask operations
        if args.append_mask or args.prepend_mask:
            from word_reaper.utils.hashcat_utils import apply_mask

            # Check for required utilities
            if not HASHCAT_UTILS["maskprocessor"]:
                print(f"{RED}Error: mp64.bin/mp32.bin not found but required for mask operations.{RESET}")
                sys.exit(1)
            if not HASHCAT_UTILS["combinator"]:
                print(f"{RED}Error: combinator.bin not found but required for mask operations.{RESET}")
                sys.exit(1)

            current_file = args.input
            temp_file = None

            try:
                # Handle prepend mask
                if args.prepend_mask:
                    if args.append_mask:
                        # Need temp file for prepend, then append
                        from word_reaper.utils.hashcat_utils import create_hidden_temp_file
                        temp_file = create_hidden_temp_file(prefix="wordreaper_prepend_", suffix=".tmp")
                        if not apply_mask(current_file, args.prepend_mask, temp_file, append=False, silent=args.quiet, increment=args.increment):
                            sys.exit(1)
                        current_file = temp_file
                    else:
                        # Only prepend
                        if not apply_mask(current_file, args.prepend_mask, args.output, append=False, silent=args.quiet, increment=args.increment):
                            sys.exit(1)
                        if not args.quiet:
                            print(f"Wordlist saved to: {RED}{args.output}{RESET}")
                        return

                # Handle append mask
                if args.append_mask:
                    if not apply_mask(current_file, args.append_mask, args.output, append=True, silent=args.quiet, increment=args.increment):
                        sys.exit(1)
                    if not args.quiet:
                        print(f"Wordlist saved to: {RED}{args.output}{RESET}")
                    return

            finally:
                # Clean up temp file
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)

        # Check if method is required
        if not args.method:
            print(f"\n{RED}Error:{RESET} --method is required unless using --rules, --selective-leet, --reverse, --separators, --convert, --mutate, --combinator, --merge, --custom-mask, --prepend-mask, --append-mask, or --ascii-art\n")
            sys.exit(1)

        # Process based on method
        raw_words = []
        if args.method == 'html':
            raw_words = html_scraper.scrape(
                args.url,
                selector=args.selector,
                href_contains=args.href,
                text_regex=args.regex,
                tags=args.tags,
                min_length=args.min_length,
                max_length=args.max_length,
                silent=args.quiet,
                preserve=args.preserve
            )
        elif args.method == 'github':
            raw_words = github_scraper.scrape(args.url, silent=args.quiet, preserve=args.preserve)
        elif args.method == 'file':
            if not args.input:
                print(f"\n{RED}Error:{RESET} --input is required when using --method file\n")
                sys.exit(1)

            # Load the file
            raw_words = file_loader.load(args.input, silent=args.quiet, preserve=args.preserve)
        elif args.method == 'text':
            if not args.url:
                print(f"\n{RED}Error:{RESET} --url is required when using --method text\n")
                sys.exit(1)
            raw_words = text_scraper.extract_text_wordlist(args.url, silent=args.quiet, preserve=args.preserve)
        else:
            print(f"\n{RED}Error:{RESET} Unsupported method '{args.method}'. Valid methods: html, github, text, file\n")
            sys.exit(1)
        
        # Clean the words
        cleaned_words = cleaner.clean_words(raw_words, silent=args.quiet, preserve=args.preserve)
        
        # Write directly to output file in an efficient way
        formatter.save_to_file_fast(cleaned_words, args.output, silent=args.quiet)
        
        if not args.quiet:
            print(f"Wordlist saved to: {RED}{args.output}{RESET}")
    
    except Exception as e:
        print(f"\n{RED}Error:{RESET} {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def run_with_error_handling():
    """Run the main function with error handling."""
    try:
        # Run main function
        main()
    except KeyboardInterrupt:
        print(f"\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n{RED}Error:{RESET} {e}")
        return 3
    
    return 0

if __name__ == '__main__':
    sys.exit(run_with_error_handling())
