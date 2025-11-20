# Word Reaper Usage Examples

This document provides comprehensive usage examples for Word Reaper, organized by functionality.

## Table of Contents
- [Web Scraping](#web-scraping)
  - [Precision CSS Selector Scraping](#precision-css-selector-scraping)
  - [Tag-Based Scraping](#tag-based-scraping)
  - [Advanced Filtering](#advanced-filtering)
  - [Pagination Support](#pagination-support)
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

# Scrape elements while using :first-child, :last-child, :nth-child(), etc
wordreaper -m html -u https://en.wikipedia.org/wiki/List_of_dragons_in_popular_culture \
           -s "table.wikitable tbody tr td:first-child" -o dragons.txt

# Combine :not(), :nth-child(), classes, attributes, --href and --regex for surgical precision
wordreaper -m html -u https://harrypotter.fandom.com/wiki/Password \
           -s "h4 + table.fandom-table tbody tr td:not([rowspan])"
           --regex "^(?\!\d)(?\!Latin).*" -o dorm_passwords.txt
```

### Tag-Based Scraping

Scrape content from specific HTML tags:

```bash
# Scrape links, paragraphs, list items, and headings
wordreaper --method html --url https://example.com --tags a p li h1 h2 -o wordlist.txt

# Scrape from multiple inline elements with minimum length filter
wordreaper -m html -u https://example.com -t a span div --min-length 3 -o words.txt
```

### Batch Scraping with HTML

```bash
# Use --url-file 'urls.txt' to scrape numerous sites at once with different selectors
wordreaper --method html --url-file urls.txt -o wordlist.txt
```

### GitHub Scraping CSV files to extract specified columns using zero-based indexing

```bash
# Extract first column (index 0) from CSV file
wordreaper --method github --url https://raw.githubusercontent.com/danielschuster-muc/scrabby/refs/heads/main/data/characters.csv \
           -e csv -z 0 -o character_names.txt

# Extract second column (index 1)
wordreaper -m github -u https://raw.githubusercontent.com/danielschuster-muc/scrabby/refs/heads/main/data/characters.csv \
           -e csv -z 1 -o character_slugs.txt

# Extract column with preserved formatting (keeps original case and spacing)
wordreaper -m github -u https://raw.githubusercontent.com/user/repo/data.csv \
           -e csv -z 2 --preserve -o preserved_column.txt

# Real-world example: Extract email domains from user data
wordreaper -m github -u https://raw.githubusercontent.com/company/data/users.csv \
           -e csv -z 3 -o email_domains.txt
```

### Advanced Filtering

Combine selectors with regex patterns and length constraints:

```bash
# Scrape list items and table cells, filter with regex and length constraints
wordreaper --method html --url https://example.com --selector "li, td" \
           --regex "^[A-Z][a-z]+$" --min-length 3 --max-length 20
```

### Pagination Support

Automatically scrape multiple pages by following pagination links. The tool auto-detects whether your identifier is a CSS selector, URL 
pattern, or link text.

#### CSS Selector Pagination

Use CSS selectors to target the "Next" button element:
 
```bash
# Fandom pagination example (up to 5 pages)
wordreaper -m html \
-u "https://harrypotter.fandom.com/wiki/Category:Potion_ingredients" \
-s "a.category-page__member-link" \
-n 5 "a.category-page__pagination-next" \
-o ingredients.txt

# Wikipedia category pagination
wordreaper -m html \
-u "https://en.wikipedia.org/wiki/Category:Example" \
-s "div.mw-category-group li a" \
-n 10 "a:contains('next page')" \
-o wikipedia_terms.txt
```

#### URL Pattern Pagination

Use wildcards (`*`) to match URL patterns:

```bash
# Match query parameter patterns
wordreaper -m html \
-u "https://example.com/items?page=1" \
-s "div.item-name" \
-n 10 "*?page=*" \
-o items.txt

# Match path-based pagination
wordreaper -m html \
-u "https://example.com/archive/page/1" \
-s "article h2" \
-n 20 "*/page/*" \
-o archive.txt

# Match specific parameter names
wordreaper -m html \
-u "https://api.example.com/data?from=0" \
-s "span.data-item" \
-n 15 "*?from=*" \
-o api_data.txt
```

#### Link Text Pagination

Search for links containing specific text:

```bash
# Common "Next" button text
wordreaper -m html \
-u "https://example.com/episodes" \
-s "h2.episode-title" \
-n 8 "Next" \
-o episodes.txt

# Alternative pagination text
wordreaper -m html \
-u "https://blog.example.com" \
-s "article.post-title" \
-n 12 "Older Posts" \
-o blog_posts.txt

# Unicode symbols
wordreaper -m html \
-u "https://example.com/list" \
-s "span.name" \
-n 3 "→" \
-o names.txt

# Language-specific pagination
wordreaper -m html \
-u "https://example.fr/articles" \
-s "div.article-content" \
-n 5 "Suivant" \
-o french_articles.txt
```

#### Pagination with Filters

Combine pagination with other filters for precise scraping:

```bash
# Pagination with href filtering
wordreaper -m html \
-u "https://example.com/products?page=1" \
-s "a.product-link" \
--href "/product/" \
-n 20 "Next Page" \
-o products.txt

# Pagination with regex filtering
wordreaper -m html \
-u "https://example.com/names?p=1" \
-s "li.name" \
--regex "^[A-Z][a-z]+$" \
-n 15 "*?p=*" \
-o filtered_names.txt

# Pagination with length constraints
wordreaper -m html \
-u "https://example.com/words" \
-s "span.word" \
--min-length 5 \
--max-length 15 \
-n 10 "Next" \
-o medium_words.txt
```

#### Pagination Behavior

The pagination feature includes several safety mechanisms:

- **Automatic stopping conditions:**
- Maximum pages reached
- No next link found
- Dead link encountered
- Circular pagination detected

- **Politeness features:**
- 1-second delay between requests (configurable)
- Referrer header set to previous page
- Handles relative and absolute URLs

- **Result handling:**
- Results from all pages are combined
- Automatically deduplicated (unless `--preserve` is used)
- All existing filters apply to each page

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
