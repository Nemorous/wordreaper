

<h1 align="left">WordReaper v2.0.0 <img src="assets/scythe.png" width="64"/></h1>




⚠️ **NOTICE: This project is in early development and not yet ready for production use. Features may change, break, or be incomplete. Use at your own risk.**


> Reap & Forge Wordlists for Password Cracking  
> By `d4rkfl4m3z`

![wordreaper help menu](https://raw.githubusercontent.com/Nemorous/word-reaper/main/screenshots/banner.jpg)

---

## 💡 What is Word Reaper?

**WordReaper** is a powerful, modular tool for generating, mutating, and combining wordlists — ideal for use in redteaming and CTFs.

It supports:

- 🕸️ HTML scraping (with precision CSS selectors)
- 🐙 GitHub/Gist wordlist pulling (`raw.githubusercontent.com` and `gist.githubusercontent.com`)
- 📁 Local file loading and mentalist-style mutations
- 🔄 Hashcat-style mask-based permutations
- ⚔️ Merging and combining wordlists like a pro

---

## 🚀 Install

### 🔧 Clone & Install Locally

```bash
git clone https://github.com/Nemorous/word-reaper.git
cd word-reaper
pip install .
```

### 📦 Install via PyPI (Optional)
```bash
pip install word-reaper
```

---

## ⚙️ Usage

### 📥 HTML Scraping with CSS Selectors
```bash
wordreaper --method html --url https://example.com --selector "a.content"
```

### 📥 HTML Scraping with Tags
Scrape from multiple HTML tag types:
```bash
wordreaper --method html --url https://example.com --tags a p li h1 h2 -o wordlist.txt
wordreaper -m html -u https://example.com --tags a span div --min-length 3 -o words.txt
```

### 🐙 GitHub Scraping
Supports both GitHub raw and Gist raw URLs:
```bash
wordreaper --method github --url https://raw.githubusercontent.com/username/repo/main/file.txt
wordreaper --method github --url https://gist.githubusercontent.com/username/gistid/raw/commitid/file.txt
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

### Transform Operations
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

### Case Conversion
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

### Mutations with Levels
```bash
# Basic mutations (~60 mutations/word)
wordreaper --mutate --mutation-level 1 -i input.txt -o basic.txt

# Intermediate mutations (~350 mutations/word)
wordreaper --mutate --mutation-level 2 -i input.txt -o intermediate.txt

# Advanced mutations (~24k mutations/word)
wordreaper -x --mutation-level 3 -i input.txt -o advanced.txt
```

### Mask Operations (Standalone)
```bash
# Append masks
wordreaper --append-mask ?d?d?d -i input.txt -o append.txt

# Prepend masks
wordreaper --prepend-mask ?u?l -i input.txt -o prepend.txt

# Both prepend and append
wordreaper --prepend-mask ?d?d --append-mask ?s?s -i input.txt -o both.txt

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

