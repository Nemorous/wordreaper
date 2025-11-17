import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

# ANSI red for bar only
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

# Default tags that contain meaningful content
DEFAULT_CONTENT_TAGS = ["a", "p", "li", "td", "th", "h1", "h2", "h3", "span"]

def scrape(url, selector=None, href_contains=None, text_regex=None, tags=None,
          min_length=1, max_length=None, silent=False, preserve=False):
    """
    General-purpose HTML scraper with flexible targeting options.

    Args:
        url: URL to scrape
        selector: CSS selector for precise targeting
        href_contains: Filter links by href content
        text_regex: Filter text by regex pattern
        tags: List of tags to scrape (overrides default)
        min_length: Minimum word length to include
        max_length: Maximum word length to include
        silent: Suppress output
        preserve: If True, preserve original formatting (spaces, case, etc.)

    Returns:
        List of extracted words
    """
    if not silent:
        print(f"\nScraping HTML from: {url}")
    
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"{RED}Failed to fetch URL: {e}{RESET}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Determine which elements to extract from
    elements = []

    if selector:
        # Use CSS selector (most flexible)
        elements = soup.select(selector)
        if not silent:
            print(f"Using CSS selector(s): {selector}\n")
    else:
        # Smart default mode - extract from multiple content-rich tags
        target_tags = tags or DEFAULT_CONTENT_TAGS
        for t in target_tags:
            elements.extend(soup.find_all(t))
        if not silent:
            print(f"Using the following tags: {', '.join(target_tags)}\n")
    
    if not elements:
        print(f"{RED}No elements found with the specified criteria{RESET}")
        return []
    
    words = []
    filtered_elements = 0
    
    for elem in tqdm(
        elements,
        desc=f"Extracting elements",
        unit="elem",
        ncols=80,
        ascii=(" ", "#"),
        bar_format="{l_bar}" + f"{RED}" + "{bar}" + f"{RESET}" + "| {n_fmt}/{total_fmt} [{elapsed}]",
        disable=silent
    ):
        # Apply href filter if specified
        if href_contains:
            href = elem.get('href', '')
            if href_contains not in href:
                filtered_elements += 1
                continue
        
        # Extract text from element
        text = elem.get_text(separator=' ', strip=True)
        
        # Apply text regex filter if specified
        if text_regex:
            if not re.search(text_regex, text):
                filtered_elements += 1
                continue
        
        # Keep full text
        if preserve:
            # Preserve original formatting (only strip leading/trailing whitespace)
            if text:
                words.append(text)
        else:
            # Original behavior: remove all spaces
            words.append(text.replace(' ', ''))
    
    if not silent and filtered_elements > 0:
        print(f"Filtered out {filtered_elements} elements based on criteria")

    return words

def batch_scrape(urls, **kwargs):
    """
    Scrape multiple URLs and combine results.

    Args:
        urls: List of URLs to scrape
        **kwargs: Additional arguments passed to scraping function
    """
    all_words = []

    for url in urls:
        print(f"Processing: {url}")
        words = scrape(url, **kwargs)
        all_words.extend(words)

    # Remove duplicates
    return list(set(all_words))
