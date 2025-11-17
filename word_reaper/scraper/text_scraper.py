import requests
from tqdm import tqdm

# ANSI red
RED = '\033[91m'
RESET = '\033[0m'

# Default headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def extract_text_wordlist(url, silent=False, preserve=False):
    print(f"\nScraping plaintext from: {url}\n")

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"{RED}Failed to fetch text file: {e}{RESET}")
        return []

    lines = response.text.splitlines()

    # Add debug info
    # print(f"DEBUG: Found {len(lines)} lines in text content")

    words = []
    for line in tqdm(
        lines,
        desc="Processing text lines",
        unit="line",
        ncols=80,
        ascii=(" ", "#"),
        bar_format="{l_bar}" + RED + "{bar}" + RESET + "| {n_fmt}/{total_fmt} [{elapsed}]"
    ):
        line = line.strip()
        if line:
            words.append(line)

    # Add debug info
    # print(f"DEBUG: Extracted {len(words)} words from text content")

    return words

def extract_text_wordlist_stream(url, silent=False):
    """
    Stream-based version of extract_text_wordlist for memory-efficient processing.
    """
    print(f"Streaming Plaintext from: \n{url}\n")

    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"{RED}Failed to fetch text file: {e}{RESET}")
        # Return empty generator instead of crashing
        return iter([])

    lines = response.text.splitlines()

    # Add debug info
    # print(f"DEBUG: Found {len(lines)} lines in text content")
    # print(f"DEBUG: Generating words in streaming mode")

    def generate_words():
        for line in lines:
            word = line.strip()
            if word:
                yield word

    return generate_words()
