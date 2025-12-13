import requests
from tqdm import tqdm
import csv
from io import StringIO

# ANSI bright red
RED = '\033[91m'
RESET = '\033[0m'

# Default headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "max-age=0",
    "Priority": "u=0, i",
    "Referer": "https://www.google.com/",
    "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "Upgrade-Insecure-Requests": "1",
}

def scrape(url, silent=False, preserve=False, extension=None, column_index=None):
    print(f"\nScraping GitHub source: {url}")

    words = []

    if "raw.githubusercontent.com" in url or "gist.githubusercontent.com" in url:
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            content = response.text

            # Check if we're parsing a CSV file
            if extension == 'csv' and column_index is not None:
                # Parse as CSV file
                print(f"Parsing CSV file and extracting column {RED}{column_index}{RESET}...\n")

                # Use csv.reader to properly parse CSV data
                csv_reader = csv.reader(StringIO(content))
                rows = list(csv_reader)

                if not rows:
                    print(f"{RED}WARNING: CSV file is empty{RESET}")
                    return words

                # Process each row with progress bar
                for row in tqdm(
                    rows,
                    desc="Parsing CSV rows",
                    unit="row",
                    ncols=80,
                    ascii=(" ", "#"),
                    bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]"
                ):
                    # Check if the column index exists in this row
                    if len(row) > column_index:
                        cell_value = row[column_index].strip()
                        if cell_value:
                            words.append(cell_value)
                    else:
                        # Skip rows that don't have enough columns
                        continue

                if not words:
                    print(f"{RED}WARNING: No data found in column {column_index}{RESET}")
                    print(f"{RED}The CSV file has {len(rows[0]) if rows else 0} columns (indices 0-{len(rows[0])-1 if rows else 0}){RESET}")
            else:
                # Standard line-by-line parsing for non-CSV files
                lines = content.splitlines()

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

        except requests.RequestException as e:
            print(f"{RED}Failed to fetch raw GitHub file: {e}{RESET}")
    else:
        print(f"{RED}Please make sure that you are using a valid URL.{RESET}")
        print("GitHub scraping requires raw URLs (raw.githubusercontent.com or gist.githubusercontent.com)")
        if extension == 'csv':
            print("For CSV files, ensure the URL points directly to the raw CSV file.")
        exit(0)
    
    # Make sure we're not returning an empty list
    if not words:
        print(f"{RED}WARNING: No words were extracted from the GitHub URL{RESET}")
        exit() 
    return words
