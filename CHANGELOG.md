# Changelog

## [2.3.0] - 2025-11-20
### ✨ New Features
- **Pagination Support**: New `--next-page` / `-n` option for automatic multi-page scraping
- Auto-detects identifier type: CSS selector, URL pattern, or link text
- Supports up to max pages with configurable limit
- Automatically handles relative and absolute URLs
- Sets referrer headers for politeness
- Includes delay between requests (1 second default)
- Detects circular pagination to prevent loops
- Stops gracefully on dead links or missing next links
- Syntax: `--next-page MAX_PAGES "NEXT_IDENTIFIER"`

### 🎯 HTML Scraping Improvements
- Pagination works seamlessly with existing filters (`--href`, `--regex`, `--min-length`, `--max-length`)
- Results from all pages are combined and deduplicated (unless `--preserve` is used)

## [2.2.1] - 2025-11-18
### Added
- Added setuptools to requirements.txt and setup.py
- Replaced deprecated pkg_resources usage with modern importlib
- Changed --rules function to have consistent aesthetics

## [2.2.0] - 2025-11-17
### Updated
- Updated EXAMPLES.md and README.md to reflect recent updates
- Added better default headers to scraper files to mimic a real browser and avoid blocks
- Extended functionality for GitHub Scraper to extract a specified column from CSV files
- Added .exe equivalents of the hashcat binaries for full cross-platform functionality with Windows
- Edited code in hashcat_utils.py to enable full functionality in both Windows and Linux systems

## [2.1.0] - 2025-11-17
### Fixed
- Solved issue causing --min-length and --max-length to not work
- Edited HTML scraper to remove subscript, superscript, citation, and reference when scraping

### Added
- HTML batch scraping added using (-f, --url-file) to scrape from multiple URLs using different selectors

## [2.0.0] - 2025-11-16
### 🚨 Breaking Changes
- **REMOVED**: Legacy HTML scraping options `--tag`, `--class`, `--id` (replaced with `--selector` and `--tags`)
- **REMOVED**: `--scrape-mode smart` and `--scrape-mode targeted` (inaccurate and noisy)
- **REMOVED**: Old transformation flags when used with mutation operations
- **RENAMED**: `--mentalize` → `--mutate` (clearer naming)
- **CHANGED**: `--mutation-level` now directly controls complexity (not based on flag count)

### ✨ Major Features Added
- **Hashcat Rules**: `--rules` runs hashcat rules against wordlists
- **Transform Options**
  - `--selective-leet <MAX>`: Selective leetspeak with max substitutions
  - `--reverse`: Reverse each word
  - `--separators <CHAR>`: Add separators between word segments (using wordninja)
- **Case Conversion**: New `--convert` with sub-options:
  - `lower`: Convert to lowercase
  - `upper`: Convert to UPPERCASE
  - `pascal`: Convert to PascalCase (using wordninja for word segmentation)
  - `sentence`: Convert to Sentencecase
  - `all`: Convert to all case types (lower, upper, pascal, sentence)
- **Standalone Mask Operations**: `--append-mask` and `--prepend-mask` now work without requiring other flags
- **Mutation Levels**: `--mutate --mutation-level {1,2,3}` for precise control:
  - Level 1: ~60 mutations per word (Basic)
  - Level 2: ~350 mutations per word (Intermediate)
  - Level 3: ~24k mutations per word (Advanced)

### 🎯 HTML Scraping Improvements
- Precision CSS selectors with `--selector` (primary method)
- Tag-based scraping with `--tags` for broader capture
- Removed noisy smart/targeted modes for cleaner, more accurate results
- Fixed scraping functionality as to not split words

### 📦 Dependencies
- Added `wordninja` for word segmentation (used in `--separators` and `pascal`)
- Updated all package files to include rules directory

### 🔧 Technical Improvements
- Created new `transform.py` module
- Improved argument validation and mutual exclusivity checks
- Better error messages and user guidance
- Most operations can now work independently (no nested flag requirements)

### 📚 Documentation
- Complete rewrite and reformatting of help text
- Added EXAMPLES.md for thorough usage examples and suggestions
- Updated README.md with all new features and usage examples
- Added tag-based scraping examples

## [1.0.2] - 2025-04-10
### Fixed
- Edited `README.md` banner image link to use raw GitHub URL for PyPI compatibility
- Changed the example usage in the help menu to be more accurate
- Changed version number to 1.0.2 where appropriate

## [1.0.1] - 2025-04-10
### Fixed
- Added support for Gist raw URLs (`gist.githubusercontent.com`) in GitHub scraper.
- Minor improvements to `scrape()` error messaging.
- Added missing dependencies (requests, beautifulsoup4) to install_requires in setup.py
- Restructured GitHub repo to enable full functionality as an installable Python package
- Added setup.py and __init__.py files to appropriate directories to support packaging and module imports
- Added installation instructions to README.md for local and PyPI usage
- Updated usage examples in README.md to reflect correct CLI syntax
- Provided new banner image in README.md with updated usage examples
- Changed version number to 1.0.1 where appropriate

## [1.0.0] - 2025-04-10
### Added
- Initial release of Word Reaper with HTML, GitHub, and Local file scraping
- Wordlist mutation features (leetspeak, case toggles, underscores, spaces, hyphens)
- HTML tag-based scraping with class and ID filtering
- GitHub raw wordlist pulling
- Hashcat-style permutation features (?a ?d ?s ?l ?u)
- Merge unlimited wordlists & sort/clean them on the fly
- Hashcat-style combinator mode to combine words
- Synchronize mode (prepend and append permutation chars at the same time)
- Hashcat-style increment mode
- ASCII art mode

