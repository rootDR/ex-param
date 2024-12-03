import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os

# Reflected Parameter payload marker
REFLECTION_MARKER = "reflect_test_parameter"


def print_banner():
    """Print the banner for the tool."""
    banner = r"""
                                                                  
                                                              
    ____  .    ,          ____     ____      ____     ____     ,__________ 
   /'    )  \  /         /'    )--/'    )   )'    )--/'    )   /'    )     )
 /(___,/'    \'        /'    /' /'    /'  /'       /'    /'  /'    /'    /' 
(__________/' \_     /(___,/'  (___,/(__/'        (___,/(__/'    /'    /(__ 
                   /'                                                       
                 /'                                                         

    Automated Reflected Parameter Finder Tool
    Author: rootdr | Twitter: @R00TDR , Telegram: https://t.me/RootDr
    """
    print(colored(banner, "red"))


def fetch_url(target):
    """Send a GET request to fetch a URL's content."""
    try:
        response = requests.get(target, timeout=5)
        return response.text
    except requests.exceptions.RequestException:
        return None


def is_internal_url(url, target_domain):
    """Check if the URL is internal (belongs to the same domain)."""
    parsed_url = urlparse(url)
    return parsed_url.netloc.endswith(target_domain)


def crawl_domain(target, crawl_subdomains=False):
    """Crawl the domain and extract unique pages and their GET parameters."""
    print(colored("[*] Crawling the domain for pages and parameters...", "yellow"))
    crawled_urls = set()
    parameters = set()
    to_visit = {target}

    target_domain = urlparse(target).netloc

    # Create target folder for saving pages and results
    target_folder = target_domain.replace(".", "_")
    os.makedirs(target_folder, exist_ok=True)

    try:
        while to_visit:
            url = to_visit.pop()
            if url in crawled_urls:
                continue

            crawled_urls.add(url)
            response = fetch_url(url)
            if not response:
                continue

            # Save crawled page to file
            page_filename = os.path.join(target_folder, urlparse(url).path.replace("/", "_") or "index.html")
            with open(page_filename, "w", encoding="utf-8") as page_file:
                page_file.write(response)

            # Parse the page and extract links
            soup = BeautifulSoup(response, "html.parser")
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])

                # Only crawl internal URLs, avoid subdomains unless -s is used
                if crawl_subdomains or is_internal_url(full_url, target_domain):
                    to_visit.add(full_url)

                # Extract GET parameters
                parsed = urlparse(full_url)
                query_params = parse_qs(parsed.query)
                for param in query_params.keys():
                    parameters.add((full_url.split("?")[0], param))  # (base_url, parameter)

    except KeyboardInterrupt:
        print(colored("[!] Crawling stopped by user.", "red"))

    return crawled_urls, parameters, target_folder


def check_reflected_parameter(base_url, param):
    """Test if a parameter reflects its input by using a simple payload."""
    test_value = REFLECTION_MARKER
    query = {param: test_value}
    try:
        response = requests.get(base_url, params=query, timeout=5)
        if test_value in response.text:
            return f"{base_url}?{param}={test_value}"  # Found reflection
    except requests.exceptions.RequestException:
        pass  # Ignore request errors
    return None


def main():
    # Print banner
    print_banner()

    # Parse arguments
    parser = argparse.ArgumentParser(description="Automated Reflected Parameter Finder Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain to crawl (e.g., http://example.com)")
    parser.add_argument("-s", "--subdomains", action="store_true", help="Crawl subdomains as well")
    args = parser.parse_args()

    target = args.target
    crawl_subdomains = args.subdomains

    if not target.startswith("http://") and not target.startswith("https://"):
        print(colored("[!] Target URL must start with http:// or https://", "red"))
        return

    # Crawl the domain and extract parameters
    crawled_urls, parameters, target_folder = crawl_domain(target, crawl_subdomains)
    print(colored(f"[*] Crawled {len(crawled_urls)} unique pages.", "yellow"))
    print(colored(f"[*] Found {len(parameters)} unique parameters.", "yellow"))

    # Check reflected parameters
    print(colored("[*] Testing for reflected parameters...", "yellow"))
    reflected_results = []
    with tqdm(total=len(parameters), desc="Testing Parameters", unit="param") as progress_bar:
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(check_reflected_parameter, base_url, param)
                for base_url, param in parameters
            ]
            for future in as_completed(futures):
                progress_bar.update(1)
                result = future.result()
                if result:
                    reflected_results.append(result)

    # Output results
    if reflected_results:
        print(colored("\n[+] Reflected Parameters Found:", "green"))
        for result in reflected_results:
            print(colored(f"[Reflected] {result}", "green"))
            # Save reflected results to a file
            with open(os.path.join(target_folder, "reflected_parameters.txt"), "a", encoding="utf-8") as result_file:
                result_file.write(result + "\n")
    else:
        print(colored("\n[-] No reflected parameters found.", "red"))


if __name__ == "__main__":
    main()
