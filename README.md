

<h1 align="left">Word Reaper v2.2.0 <img src="assets/scythe.png" width="64"/></h1>




⚠️ **NOTICE: This project is in early development and not yet ready for production use. Features may change, break, or be incomplete. Use at your own risk.**


> Reap & Forge Wordlists for Password Cracking  
> By `d4rkfl4m3z`


---

## 💡 What is Word Reaper?

**Word Reaper** is a powerful, modular tool for generating, mutating, and combining wordlists — ideal for use in cracking passwords. 
This tool was developed with NCL password-cracking challenges in mind.

It supports:

- 🕸️ HTML scraping (with precision CSS selectors)
- 🐙 GitHub/Gist/CVS wordlist pulling
- 👻 Plaintext scraping from simple lists
- 📁 File loading from local environment
- 🧪 Common mutations with varying complexities
- 🍺 Hashcat-style mask-based permutations
- 💎 Prepend/Append simultaneously with or without increment
- ⚔️ Merging and combining (combinator) wordlists
- 🐱 Hashcat-style rules or custom rules
- 💼 Case conversion to lower, upper, pascal, sentence
- 👽 Transform with selective leet, reverse, separators
- 🚩 Use custom masks to output flag patterns for CTFs

---

## 🚀 Install

### 🔧 Clone & Install Locally

```bash
git clone https://github.com/Nemorous/wordreaper.git
cd wordreaper
pip install .
```

---

## ⚙️ Usage

### 📥 HTML Scraping with CSS Selectors
```bash
# Combine :not(), :nth-child(), classes, attributes, --href and --regex for surgical precision
wordreaper --method html --url https://example.com --selector "a.content"
wordreaper --method html --url https://example.com --selector "li, td" \
           --regex "^[A-Z][a-z]+$" --min-length 3 --max-length 20
wordreaper --method html --url https://bulbapedia.bulbagarden.net/wiki/List_of_Pokémon_by_name \
           --selector "table.roundy a" --href "_(Pok%C3%A9mon)" -o pokemon.txt
wordreaper -m html -u https://en.wikipedia.org/wiki/List_of_dragons_in_popular_culture \
           -s "table.wikitable tbody tr td:first-child" -o dragons.txt
wordreaper -m html -u https://harrypotter.fandom.com/wiki/Password \
           -s "h4 + table.fandom-table tbody tr td:not([rowspan])"
           --regex "^(?\!\d)(?\!Latin).*" -o dorm_passwords.txt
```

### 📥 HTML Scraping with Tags
Scrape from multiple HTML tag types:
```bash
wordreaper --method html --url https://example.com --tags a p li h1 h2 -o wordlist.txt
wordreaper -m html -u https://example.com --tags a span div --min-length 3 -o words.txt
```

### 🥣 Batch Scraping with HTML
```bash
wordreaper --method html --url-file urls.txt -o words.txt
```

### 🐙 GitHub Scraping
Supports both GitHub raw and Gist raw URLs:
```bash
wordreaper --method github --url https://raw.githubusercontent.com/username/repo/main/file.txt
wordreaper -m github -u https://gist.githubusercontent.com/username/gistid/raw/commitid/file.txt

# Use GitHub scraper to extract specified column from a CSV file
wordreaper --method github --url https://raw.githubusercontent.com/example/file.csv \
           --extension csv --zero-index 0 -o output.txt

# Extract third column (index 2) with preserved formatting
wordreaper -m github -u https://raw.githubusercontent.com/user/repo/data.csv \
           -e csv -z 2 --preserve -o column3.txt
```

### 📁 Local File Loading
```bash
wordreaper --method file --input wordlist.txt
```

---

## 🧠 Word Transformations & Mutations

### Hashcat Rules (Standalone)
Apply any Hashcat rules file directly to your wordlist:
```bash
wordreaper --rules /path/to/hashcat/rules/best66.rule -i input.txt -o output.txt
wordreaper --rules /path/to/custom.rule -i words.txt -o custom.txt
```

### 🛠️ Transform Operations
```bash
# Selective leetspeak with max substitutions
wordreaper --selective-leet 3 -i input.txt -o selective.txt

# Reverse words
wordreaper --reverse -i input.txt -o reversed.txt

# Add separators between word segments
wordreaper --separators "_" -i input.txt -o underscores.txt
wordreaper --separators "-" -i input.txt -o hyphens.txt
wordreaper --separators "." -i input.txt -o decimals.txt
```

### 🔠 Case Conversion
```bash
# Convert to lowercase
wordreaper --convert lower -i input.txt -o lowercase.txt

# Convert to UPPERCASE
wordreaper --convert upper -i input.txt -o uppercase.txt

# Convert to PascalCase (uses word segmentation)
wordreaper --convert pascal -i input.txt -o PascalCase.txt

# Convert to Sentencecase
wordreaper --convert sentence -i input.txt -o Sentencecase.txt

# Apply all case conversions
wordreaper -c all -i input.txt -o all_cases.txt
```

### 🧪 Mutations with Complexity Levels
```bash
# Basic mutations (~60 mutations/word)
wordreaper --mutate --mutation-level 1 -i input.txt -o basic.txt

# Intermediate mutations (~350 mutations/word)
wordreaper --mutate --mutation-level 2 -i input.txt -o intermediate.txt

# Advanced mutations (~24k mutations/word)
wordreaper -x --mutation-level 3 -i input.txt -o advanced.txt
```

### 🎭 Hashcat-style Mask Operations
```bash
# Append masks
wordreaper --append-mask ?d?d?d -i input.txt -o append.txt

# Prepend masks
wordreaper --prepend-mask ?a?a?a --increment -i input.txt -o prepend.txt

# Both prepend and append
wordreaper --prepend-mask ?d?d --append-mask ?s?s -i input.txt -o both.txt

# Append & Prepend while using increment
wordreaper --prepend-mask ?s?s --append-mask ?d?d?d?d --increment -i input.txt -o output.txt

# Custom mask patterns
wordreaper --custom-mask "CTF-?uS?u?u-1337" -o flag_patterns.txt
```

---

## 🧰 Other Features

### 🪓 Reaper ASCII Art
```bash
wordreaper --ascii-art
```

### 📦 Merge Multiple Wordlists
```bash
wordreaper --merge file1.txt file2.txt file3.txt ... -o merged.txt
```

### ⚔️ Combinator
```bash
wordreaper --combinator adjectives.txt nouns.txt -o combos.txt
```

---

## 📝 Changelog

See [`CHANGELOG.md`](CHANGELOG.md)

---

## 📁 License

MIT

---

## 🤝 Contributions

PRs and issues welcome! Add new scrapers, modules, or mutation strategies.

Made with ☕ and 🔥 By d4rkfl4m3z

