# Word Reaper Usage Examples

This document provides comprehensive usage examples for Word Reaper, organized by functionality.

## Table of Contents
- [Web Scraping](#web-scraping)
  - [Precision CSS Selector Scraping](#precision-css-selector-scraping)
  - [Tag-Based Scraping](#tag-based-scraping)
  - [Advanced Filtering](#advanced-filtering)
  - [Other Scraping Methods](#other-scraping-methods)
- [Hashcat Rules](#hashcat-rules)
- [Transform Operations](#transform-operations)
- [Case Conversion](#case-conversion)
- [Mutations](#mutations)
- [Mask Operations](#mask-operations)
- [Wordlist Operations](#wordlist-operations)

---

## Web Scraping

### Precision CSS Selector Scraping

Extract specific elements from web pages using CSS selectors:

```bash
# Scrape Pokémon names from Bulbapedia
wordreaper --method html --url https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_name \
           --selector "table.roundy a" --href "_(Pok%C3%A9mon)" -o pokemon.txt

# Scrape dragon names from Wikipedia
wordreaper -m html -u https://en.wikipedia.org/wiki/List_of_dragons_in_popular_culture \
           -s "table.wikitable tbody tr td:first-child" -o dragons.txt

# Scrape multiple selectors (comma separated)
wordreaper -m html -u https://the.greatest.website/stuff -s "h1, h2, h3" -o wordlist.txt
```

### Tag-Based Scraping

Scrape content from specific HTML tags:

```bash
# Scrape links, paragraphs, list items, and headings
wordreaper --method html --url https://example.com --tags a p li h1 h2 -o wordlist.txt

# Scrape from multiple inline elements with minimum length filter
wordreaper -m html -u https://example.com -t a span div --min-length 3 -o words.txt
```

### Advanced Filtering

Combine selectors with regex patterns and length constraints:

```bash
# Scrape list items and table cells, filter with regex and length constraints
wordreaper --method html --url https://example.com --selector "li, td" \
           --regex "^[A-Z][a-z]+$" --min-length 3 --max-length 20
```

### Other Scraping Methods

```bash
# Scrape from GitHub raw or gist files
wordreaper --method github --url https://raw.githubusercontent.com/user/repo/file.txt

# Scrape plain text wordlists from URLs
wordreaper -m text -u https://example.com/wordlist.txt

# Load wordlist from local file
wordreaper -m file -i local_file.txt
```

---

## Hashcat Rules

Apply Hashcat rule files to transform wordlists:

```bash
# Apply best66 rule set
wordreaper --rules path/to/hashcat/rules/best66.rule -i input.txt -o output.txt

# Apply custom rule file
wordreaper -r /path/to/custom.rule -i words.txt -o custom.txt
```

---

## Transform Operations

### Selective Leetspeak

Apply selective leetspeak transformations with controlled substitution limits:

```bash
# Apply selective leet with maximum 2 substitutions per word
wordreaper --selective-leet 3 -i input.txt -o selective.txt
```

### Reverse Words

```bash
# Reverse each word in the wordlist
wordreaper --reverse -i input.txt -o reversed.txt
```

### Add Separators

```bash
# Add underscore separators between word segments
wordreaper --separators "_" -i input.txt -o underscores.txt
wordreaper --separators "." -i input.txt -o decimals.txt
wordreaper --separators "-" -i input.txt -o hyphens.txt
wordreaper --separators "$" -i input.txt -o dollar_signs.txt

# Remove spaces with empty string
wordreaper --separators "" -i input.txt -o spaces_removed.txt
```

---

## Case Conversion

Convert wordlists to different case formats:

```bash
# Convert to lowercase
wordreaper --convert lower -i input.txt -o lowercase.txt

# Convert to uppercase
wordreaper --convert upper -i input.txt -o uppercase.txt

# Convert to PascalCase
wordreaper --convert pascal -i input.txt -o pascalcase.txt

# Convert to Sentence case
wordreaper --convert sentence -i input.txt -o sentencecase.txt

# Generate multiple case variants
wordreaper --convert lower upper pascal sentence -i input.txt -o all_cases.txt

# Generate all case variants at once
wordreaper -c all -i input.txt -o all_cases.txt
```

---

## Mutations

Apply mutation levels to generate password variations:

```bash
# Basic mutations (~60 variations per word)
wordreaper --mutate --mutation-level 1 -i input.txt -o basic.txt

# Intermediate mutations (~350 variations per word)
wordreaper --mutate --mutation-level 2 -i input.txt -o intermediate.txt

# Advanced mutations (~24,000 variations per word)
wordreaper -x --mutation-level 3 -i input.txt -o advanced.txt
```

---

## Mask Operations

### Append and Prepend Masks

Add hashcat-style masks to existing wordlists:

```bash
# Append three digits to each word
wordreaper --append-mask ?d?d?d -i input.txt -o append.txt

# Prepend uppercase + lowercase characters
wordreaper --prepend-mask ?u?l -i input.txt -o prepend.txt

# Both prepend and append masks
wordreaper --prepend-mask ?d?d --append-mask ?s?s -i input.txt -o both.txt
```

### Custom Mask Generation

Generate wordlists from custom mask patterns:

```bash
# Generate CTF flag patterns
wordreaper --custom-mask "CTF-?uS?u?u-1337" -o flag_patterns.txt
```

### Incremental Masks

```bash
# Apply incremental mask lengths when appending
wordreaper --append-mask ?d?d?d --increment -i input.txt -o incremental.txt
```

---

## Wordlist Operations

### Merge Multiple Wordlists

Combine and deduplicate multiple wordlists:

```bash
# Merge three wordlists into one
wordreaper --merge file1.txt file2.txt file3.txt -o merged.txt
```

### Combinator

Combine words from two files using Hashcat's combinator:

```bash
# Combine adjectives with nouns
wordreaper --combinator adjectives.txt nouns.txt -o combos.txt
```

---

## Advanced Workflows

### Multi-Step Processing

You can chain Word Reaper commands for complex workflows:

```bash
# Step 1: Scrape website
wordreaper -m html -u https://example.com --tags h1 h2 h3 -o raw.txt

# Step 2: Apply mutations
wordreaper --mutate --mutation-level 2 -i raw.txt -o mutated.txt

# Step 3: Add year suffixes
wordreaper --append-mask ?d?d?d?d -i mutated.txt -o final.txt
```

### Combining Multiple Techniques

```bash
# Scrape, filter, and transform in stages
wordreaper -m html -u https://example.com --selector "li" --min-length 4 -o stage1.txt
wordreaper --convert all -i stage1.txt -o stage2.txt
wordreaper --append-mask ?d?d -i stage2.txt -o final.txt
```

---

## Tips and Best Practices

1. **Start Small**: Test your selectors and filters on a small dataset first
2. **Use Mutations Wisely**: Level 2 mutations can generate massive wordlists
3. **Combine Operations**: Chain commands for complex transformations
4. **Filter Early**: Apply min/max length filters during scraping to reduce processing
5. **Silent Mode**: Use `--quiet` flag for cleaner output in scripts

---

## Need Help?

For more information, run:
```bash
wordreaper --help
```

For feature requests or bug reports, visit:
https://github.com/yourusername/word-reaper
