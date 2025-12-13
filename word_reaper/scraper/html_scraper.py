import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import time
from urllib.parse import urljoin, urlparse

# ANSI red for bar only
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

# Default tags that contain meaningful content
DEFAULT_CONTENT_TAGS = ["a", "p", "li", "td", "th", "h1", "h2", "h3", "span"]

# Tags to remove before extracting text (citations, references, superscripts, subscripts)
UNWANTED_TAGS = ["sup", "sub", "cite", "ref"]

def detect_identifier_type(identifier):
    """
    Auto-detect the type of next page identifier.

    Args:
        identifier: The identifier string to detect

    Returns:
        'css' for CSS selector, 'url_pattern' for URL pattern, or 'text' for link text
    """
    # CSS Selector indicators: contains ., #, [, >, or :
    css_indicators = ['.', '#', '[', '>', ':']
    if any(indicator in identifier for indicator in css_indicators):
        return 'css'

    # URL Pattern indicators: contains *, ?, or common pagination parameters
    url_indicators = ['*', '?']
    if any(indicator in identifier for indicator in url_indicators):
        return 'url_pattern'

    # Otherwise, treat as link text
    return 'text'

def find_next_page_url(soup, identifier, current_url, identifier_type=None):
    """
    Find the next page URL based on the identifier.

    Args:
        soup: BeautifulSoup object of the current page
        identifier: CSS selector, URL pattern, or link text
        current_url: Current page URL for resolving relative URLs
        identifier_type: Type of identifier ('css', 'url_pattern', or 'text')

    Returns:
        Absolute URL of the next page, or None if not found
    """
    if identifier_type is None:
        identifier_type = detect_identifier_type(identifier)

    next_link = None

    if identifier_type == 'css':
        # Use CSS selector to find the next link
        elements = soup.select(identifier)
        if elements:
            # Get the first matching element
            element = elements[0]
            next_link = element.get('href')

    elif identifier_type == 'url_pattern':
        # Find links matching the URL pattern
        # Convert pattern to regex (replace * with .*)
        pattern_regex = identifier.replace('*', '.*').replace('?', r'\?')

        # Search all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            # Resolve to absolute URL
            absolute_href = urljoin(current_url, href)

            if re.search(pattern_regex, absolute_href) or re.search(pattern_regex, href):
                next_link = href
                break

    elif identifier_type == 'text':
        # Find link by text content
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if identifier in link_text:
                next_link = link.get('href')
                break

    # Convert relative URL to absolute URL
    if next_link:
        return urljoin(current_url, next_link)

    return None

def scrape_with_pagination(url, selector=None, href_contains=None, text_regex=None, tags=None,
                          min_length=1, max_length=None, silent=False, preserve=False,
                          max_pages=1, next_identifier=None, delay=1.0):
    """
    Scrape multiple pages following pagination links.

    Args:
        url: Starting URL to scrape
        selector: CSS selector for precise targeting
        href_contains: Filter links by href content
        text_regex: Filter text by regex pattern
        tags: List of tags to scrape (overrides default)
        min_length: Minimum word length to include
        max_length: Maximum word length to include
        silent: Suppress output
        preserve: If True, preserve original formatting (spaces, case, etc.)
        max_pages: Maximum number of pages to scrape
        next_identifier: CSS selector, URL pattern, or link text for finding next page
        delay: Delay in seconds between page requests

    Returns:
        List of extracted words from all pages
    """
    all_words = []
    current_url = url
    pages_scraped = 0
    visited_urls = set()  # Track visited URLs to avoid loops

    # Detect identifier type once
    identifier_type = detect_identifier_type(next_identifier)

    if not silent:
        print(f"\nScraping with pagination (max {RED}{max_pages}{RESET} pages)")
        print(f"Identifier type: {RED}{identifier_type}{RESET}")
        print(f"Identifier: {RED}{next_identifier}{RESET}\n")

    while pages_scraped < max_pages and current_url:
        # Check if we've already visited this URL
        if current_url in visited_urls:
            if not silent:
                print(f"{RED}Stopping: Detected circular pagination{RESET}")
            break

        visited_urls.add(current_url)
        pages_scraped += 1

        if not silent:
            print(f"Page {RED}{pages_scraped}/{max_pages}{RESET}: {current_url}")

        # Fetch the page
        try:
            headers = DEFAULT_HEADERS.copy()
            # Set referrer to previous page (except for first page)
            if pages_scraped > 1:
                headers['Referer'] = list(visited_urls)[-2] if len(visited_urls) >= 2 else url

            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"{RED}Failed to fetch URL: {e}{RESET}")
            if not silent:
                print(f"{RED}Stopping: Dead link encountered{RESET}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Determine which elements to extract from
        elements = []

        if selector:
            elements = soup.select(selector)
        else:
            target_tags = tags or DEFAULT_CONTENT_TAGS
            for t in target_tags:
                elements.extend(soup.find_all(t))

        if not elements:
            if not silent:
                print(f"\n{RED}Warning: No elements found on page {pages_scraped}{RESET}")
        else:
            # Extract words from elements
            page_words = []
            for elem in elements:
                # Apply href filter if specified
                if href_contains:
                    href = elem.get('href', '')
                    if href_contains not in href:
                        continue

                # Remove unwanted tags
                for tag in UNWANTED_TAGS:
                    for unwanted in elem.find_all(tag):
                        unwanted.decompose()

                # Extract text
                text = elem.get_text(separator=' ', strip=True)

                # Apply text regex filter
                if text_regex:
                    if not re.search(text_regex, text):
                        continue

                # Preserve or clean text
                if preserve:
                    if text:
                        page_words.append(text)
                else:
                    page_words.append(text.replace(' ', ''))

            all_words.extend(page_words)

            if not silent:
                print(f"Extracted {RED}{len(page_words)}{RESET} words from page {pages_scraped}")

        # Find next page URL if we haven't reached max pages
        if pages_scraped < max_pages:
            next_url = find_next_page_url(soup, next_identifier, current_url, identifier_type)

            if next_url:
                current_url = next_url
                # Add delay before next request
                if pages_scraped < max_pages:
                    time.sleep(delay)
            else:
                if not silent:
                    print(f"{RED}Stopping: No next link found{RESET}")
                break
        else:
            break

    if not silent:
        print(f"\nTotal pages scraped: {RED}{pages_scraped}{RESET}")
        print(f"Total words extracted (before filtering): {RED}{len(all_words)}{RESET}")

    # Apply length filtering
    if min_length > 1 or max_length is not None:
        import unicodedata

        def get_cleaned_length(word):
            """Calculate length after cleaning (matching cleaner.py behavior)"""
            if preserve:
                return len(word.strip())
            else:
                cleaned = unicodedata.normalize('NFKD', word)
                cleaned = ''.join([c for c in cleaned if not unicodedata.combining(c)])
                cleaned = cleaned.lower()
                cleaned = re.sub(r'[^a-z0-9]', '', cleaned)
                return len(cleaned)

        filtered_words = []
        for word in all_words:
            cleaned_len = get_cleaned_length(word)
            if cleaned_len >= min_length and (max_length is None or cleaned_len <= max_length):
                filtered_words.append(word)
        return filtered_words

    return all_words

def scrape(url, selector=None, href_contains=None, text_regex=None, tags=None,
          min_length=1, max_length=None, silent=False, preserve=False,
          max_pages=None, next_identifier=None, delay=1.0):
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
        max_pages: Maximum number of pages to scrape (for pagination)
        next_identifier: CSS selector, URL pattern, or link text for finding next page
        delay: Delay in seconds between page requests (default: 1.0)

    Returns:
        List of extracted words
    """
    # Check if pagination is enabled
    use_pagination = max_pages is not None and next_identifier is not None

    if use_pagination:
        # Use pagination scraping
        return scrape_with_pagination(
            url=url,
            selector=selector,
            href_contains=href_contains,
            text_regex=text_regex,
            tags=tags,
            min_length=min_length,
            max_length=max_length,
            silent=silent,
            preserve=preserve,
            max_pages=max_pages,
            next_identifier=next_identifier,
            delay=delay
        )

    # Single page scraping (original behavior)
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
            print(f"Using CSS selector(s): {selector}")
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

        # Remove unwanted tags before extracting text
        for tag in UNWANTED_TAGS:
            for unwanted in elem.find_all(tag):
                unwanted.decompose()

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
        print(f"Filtered out {RED}{filtered_elements}{RESET} elements based on criteria")

    # Apply length filtering based on cleaned word length (not raw text)
    # This matches the final output after cleaning removes special characters
    if min_length > 1 or max_length is not None:
        import unicodedata

        def get_cleaned_length(word):
            """Calculate length after cleaning (matching cleaner.py behavior)"""
            if preserve:
                return len(word.strip())
            else:
                # Apply same transformations as cleaner.py
                cleaned = unicodedata.normalize('NFKD', word)
                cleaned = ''.join([c for c in cleaned if not unicodedata.combining(c)])
                cleaned = cleaned.lower()
                cleaned = re.sub(r'[^a-z0-9]', '', cleaned)
                return len(cleaned)

        filtered_words = []
        for word in words:
            cleaned_len = get_cleaned_length(word)
            if cleaned_len >= min_length and (max_length is None or cleaned_len <= max_length):
                filtered_words.append(word)
        return filtered_words

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
