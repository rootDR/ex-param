# ex-param
ex-param is an automated tool designed for finding reflected parameters for XSS vulnerabilities. It crawls a target website, extracts GET parameters, and tests them for reflected input. The tool helps bug bounty hunters and penetration testers quickly identify potential reflected XSS flaws, offering fast and reliable results.

A fast and efficient tool to identify reflected parameters on websites, potentially indicating Cross-Site Scripting (XSS) vulnerabilities. The tool crawls the main domain (and optionally subdomains) to discover and test GET parameters for reflection, offering real-time feedback and saving results for later review.

Key Features
Domain Crawling: Automatically crawls the target domain to discover pages and GET parameters.
Subdomain Crawling: Optionally crawl subdomains for a more comprehensive scan.
Reflected Parameter Testing: Automatically tests GET parameters for potential reflected XSS vulnerabilities by injecting a test payload (reflect_test_parameter).
Real-Time Results: Displays the results of the reflected parameter test as soon as they are found.
Save Crawled Data: Saves crawled pages and reflected parameters in a structured folder for later review.
Multithreaded Performance: Optimized crawling and testing with multithreading to maximize speed.

# Installation
Clone the repository:
`git clone https://github.com/rootDR/ex-param.git`

# Install dependencies:

Ensure that Python 3.x is installed, then run the following command to install the required dependencies:

`pip install -r requirements.txt`

Usage
The tool accepts the following arguments:

1. Crawl the main domain (default)

`python ex-param.py -t https://example.com`
This command will crawl the specified domain (https://example.com) and find GET parameters, testing them for reflection. Only the main domain will be crawled.

2. Crawl the domain along with subdomains
To include subdomains in the crawl, use the -s flag:


`python ex-param.py -t https://example.com -s`
This command will crawl https://example.com and any subdomains (e.g., sub.example.com, another.example.com).

Flags and Arguments:

-t (required): The target domain URL to crawl. This is the only required argument. Example: https://example.com

-s (optional): If provided, the tool will crawl not only the main domain but also its subdomains (e.g., sub.example.com, another.example.com). If this flag is omitted, only the main domain will be crawled.
