import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs, unquote
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
import re
import time
import json
import csv
import logging
import warnings
from bs4 import MarkupResemblesLocatorWarning

# Suppress BeautifulSoup warning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Default payload for reflection testing
REFLECTION_MARKER = "reflected-parameter-test"

# Configure logging
logging.basicConfig(filename="reflected_xss.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def print_banner():
    """Print the banner for the tool."""
    banner = r"""
    ███████╗██╗  ██╗   ██████╗ ██████╗  █████╗ ███╗   ███╗
    ██╔════╝╚██╗██╔╝   ██╔══██╗██╔══██╗██╔══██╗████╗ ████║
    █████╗   ╚███╔╝    ██████╔╝██████╔╝███████║██╔████╔██║
    ██╔══╝   ██╔██╗    ██╔═══╝ ██╔══██╗██╔══██║██║╚██╔╝██║
    ███████╗██╔╝ ██╗██╗██║     ██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝
    Automated Reflected Parameter Finder Tool
    Author: rootdr | Twitter: @R00TDR | Telegram: https://t.me/RootDr
    """
    print(colored(banner, "cyan"))

def fetch_url(target):
    """Send a GET request to fetch a URL's content."""
    try:
        response = requests.get(target, timeout=10)  # Increased timeout
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch {target}: {e}")
        return None

def is_internal_link(url, target_domain, crawl_subdomains):
    """
    Check if the URL is internal.
    If crawl_subdomains is True, allow subdomains.
    Otherwise, only allow the exact target domain.
    """
    parsed_url = urlparse(url)
    if crawl_subdomains:
        return parsed_url.netloc == target_domain or parsed_url.netloc.endswith(f".{target_domain}")
    else:
        return parsed_url.netloc == target_domain

def crawl_domain(target, crawl_subdomains=False, depth=3):
    """
    Crawl the domain and extract unique pages and their GET parameters.
    Only URLs that pass the internal check are crawled and have their parameters extracted.
    """
    print(colored("[*] Crawling the domain for pages and parameters...", "yellow"))
    crawled_urls = set()
    parameters = set()
    to_visit = [(target, 0)]  # (url, current_depth)

    target_domain = urlparse(target).netloc

    # Create target folder for saving results
    target_folder = target_domain.replace(".", "_")
    os.makedirs(target_folder, exist_ok=True)

    try:
        while to_visit:
            url, current_depth = to_visit.pop()
            if url in crawled_urls or current_depth > depth:
                continue

            crawled_urls.add(url)
            response = fetch_url(url)
            if not response:
                continue

            # Parse the page and extract links only if they are internal
            soup = BeautifulSoup(response, "html.parser")
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"].lstrip("/"))

                if is_internal_link(full_url, target_domain, crawl_subdomains):
                    to_visit.append((full_url, current_depth + 1))
                    # Extract GET parameters only from in-scope URLs
                    parsed = urlparse(full_url)
                    query_params = {k: v for k, v in parse_qs(parsed.query).items() if any(v)}
                    for param in query_params.keys():
                        parameters.add((full_url.split("?")[0], param))
    except KeyboardInterrupt:
        print(colored("[!] Crawling stopped by user.", "red"))
        return crawled_urls, parameters, target_folder

    return crawled_urls, parameters, target_folder

def check_reflected_parameter(base_url, param, payload=None):
    """Test if a parameter reflects its input by using a simple payload."""
    test_value = payload if payload else REFLECTION_MARKER
    query = {param: test_value}
    try:
        response = requests.get(base_url, params=query, timeout=10)  # Increased timeout
        response_text = unquote(response.text)

        # Check if the payload is reflected in the response
        if test_value in response_text:
            # Use BeautifulSoup to check if the reflection is in a dangerous context
            soup = BeautifulSoup(response_text, "html.parser")

            # Check if the payload is reflected in HTML attributes
            for tag in soup.find_all():
                for attr in tag.attrs:
                    if isinstance(tag[attr], list):
                        for value in tag[attr]:
                            if test_value in value:
                                return f"{base_url}?{param}={test_value}"  # Found reflection in attribute
                    elif test_value in tag[attr]:
                        return f"{base_url}?{param}={test_value}"  # Found reflection in attribute

            # Check if the payload is reflected in JavaScript or other dangerous contexts
            for script in soup.find_all("script"):
                if script.string and test_value in script.string:
                    return f"{base_url}?{param}={test_value}"  # Found reflection in script

            # Check if the payload is reflected in plain text (less dangerous but still relevant)
            for text in soup.find_all(string=lambda x: test_value in x):
                return f"{base_url}?{param}={test_value}"  # Found reflection in text

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to check {base_url}?{param}={test_value}: {e}")
    return None

def save_results(data, output_format="txt", filename="results", target_folder="results"):
    """Save results in the specified format (txt, json, csv)."""
    os.makedirs(target_folder, exist_ok=True)
    filepath = os.path.join(target_folder, f"{filename}.{output_format}")

    if output_format == "json":
        with open(filepath, "w") as f:
            json.dump(list(data), f, indent=4)
    elif output_format == "csv":
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            if filename == "crawledpages":
                writer.writerow(["URL"])
                for url in data:
                    writer.writerow([url])
            else:
                writer.writerow(["URL", "Parameter"])
                for result in data:
                    writer.writerow(result.split("?"))
    else:
        with open(filepath, "w") as f:
            if filename == "crawledpages":
                for url in data:
                    f.write(url + "\n")
            else:
                for result in data:
                    f.write(result + "\n")

def main():
    # Print banner
    print_banner()

    # Parse arguments
    parser = argparse.ArgumentParser(description="Automated Reflected Parameter Finder Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain to crawl (e.g., http://example.com)")
    parser.add_argument("-s", "--subdomains", action="store_true", help="Crawl subdomains as well")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Maximum crawling depth")
    parser.add_argument("-p", "--payload", help="Custom payload to test for reflection")
    parser.add_argument("-f", "--format", choices=["txt", "json", "csv"], default="txt", help="Output format for results")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests (in seconds)")  # Reduced delay
    parser.add_argument("--blacklist", help="Comma-separated list of parameters to ignore")
    parser.add_argument("--whitelist", help="Comma-separated list of parameters to test")
    args = parser.parse_args()

    target = args.target
    crawl_subdomains = args.subdomains
    depth = args.depth
    payload = args.payload
    output_format = args.format
    delay = args.delay
    blacklist = args.blacklist.split(",") if args.blacklist else []
    whitelist = args.whitelist.split(",") if args.whitelist else []

    if not target.startswith("http://") and not target.startswith("https://"):
        print(colored("[!] Target URL must start with http:// or https://", "red"))
        return

    # Crawl the domain and extract parameters
    crawled_urls, parameters, target_folder = crawl_domain(target, crawl_subdomains, depth)
    print(colored(f"[*] Crawled {len(crawled_urls)} unique pages.", "yellow"))
    print(colored(f"[*] Found {len(parameters)} unique parameters.", "yellow"))

    # Save crawled URLs to a file
    save_results(crawled_urls, output_format, "crawledpages", target_folder)
    print(colored(f"[*] Crawled URLs saved to {target_folder}/crawledpages.{output_format}", "yellow"))

    # Filter parameters based on blacklist/whitelist
    if blacklist or whitelist:
        parameters = {(url, param) for url, param in parameters if (not whitelist or param in whitelist) and param not in blacklist}
        print(colored(f"[*] Filtered to {len(parameters)} parameters.", "yellow"))

    # Check reflected parameters
    print(colored("[*] Testing for reflected parameters...", "yellow"))
    reflected_results = []
    with tqdm(total=len(parameters), desc="Testing Parameters", unit="param") as progress_bar:
        with ThreadPoolExecutor(max_workers=20) as executor:  # Increased threads
            futures = [
                executor.submit(check_reflected_parameter, base_url, param, payload)
                for base_url, param in parameters
            ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        reflected_results.append(result)
                except Exception as e:
                    logging.error(f"Error processing future: {e}")
                progress_bar.update(1)
                time.sleep(delay)  # Add a delay between requests

    # Output results
    if reflected_results:
        print(colored("\n[+] Reflected Parameters Found:", "green"))
        for result in reflected_results:
            print(colored(f"[Reflected] {result}", "green"))
        save_results(reflected_results, output_format, "reflected_parameters", target_folder)
    else:
        print(colored("\n[-] No reflected parameters found.", "red"))

if __name__ == "__main__":
    main()
