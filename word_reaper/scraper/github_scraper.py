import requests
from tqdm import tqdm

# ANSI bright red
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

def scrape(url, silent=False, preserve=False):
    print(f"\nScraping GitHub source: {url}\n")

    words = []

    if "raw.githubusercontent.com" in url or "gist.githubusercontent.com" in url:
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            content = response.text
            lines = content.splitlines()

            # Add debug print to see what we're getting
            # print(f"DEBUG: Found {len(lines)} lines in GitHub content")

            for line in tqdm(
                lines,
                desc="Parsing GitHub lines",
                unit="line",
                ncols=80,
                ascii=(" ", "#"),
                bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]"
            ):
                # Keep entire line as a single entry (like HTML scraper does)
                stripped_line = line.strip()
                if stripped_line:
                    words.append(stripped_line)

            # Add debug to show final count
            # print(f"DEBUG: Extracted {len(words)} words from GitHub content")

        except requests.RequestException as e:
            print(f"{RED}Failed to fetch raw GitHub file: {e}{RESET}")
    else:
        print(f"{RED}Please make sure that you are using a valid URL.{RESET}") 
        print("Non-raw URLs in github mode are not fully supported yet. Try linking to raw.githubusercontent.com or gist.githubusercontent.com.")
        exit(0)
    
    # Make sure we're not returning an empty list
    if not words:
        print(f"{RED}WARNING: No words were extracted from the GitHub URL{RESET}")
        exit() 
    return words
