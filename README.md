# ex-param
ex-param is an automated tool designed for finding reflected parameters for XSS vulnerabilities. It crawls a target website, extracts GET parameters, and tests them for reflected input. The tool helps bug bounty hunters and penetration testers quickly identify potential reflected XSS flaws, offering fast and reliable results.


Features:
Crawl a target domain and extract GET parameters
Test for reflected parameters in URLs by injecting a test payload (reflect_test_parameter)
Optionally crawl subdomains using the -s flag
Save crawled pages and reflected parameters into a dedicated folder for easy review
Real-time feedback during the testing phase using a progress bar
Optimized crawling and testing using multithreading for faster performance
Installation:
Clone the repository:


git clone https://github.com/yourusername/automated-reflected-parameter-finder.git
Install dependencies:

This project requires Python 3.x and the following libraries:

requests
beautifulsoup4
tqdm
termcolor
You can install them using pip:

pip install -r requirements.txt
Usage:
Crawl only the main domain (default)

python ex-param.py -t https://example.com
This command will crawl the https://example.com domain, extract GET parameters, and test for reflected parameters.

Crawl both the main domain and subdomains

To crawl subdomains as well, use the -s flag:

python ex-param.py -t https://example.com -s
This command will crawl https://example.com and any subdomains, such as sub.example.com.

Output:
The tool will create a folder named after the target domain (e.g., example_com).
Crawled pages will be saved as .html files inside this folder.
Reflected parameters will be saved in a file named reflected_parameters.txt inside the same folder.
Example Output:

$ python ex-param.py -t https://example.com

[*] Crawling the domain for pages and parameters...
[*] Crawled 169 unique pages.
[*] Found 18 unique parameters.
[*] Testing for reflected parameters...

[+] Reflected Parameters Found:
[Reflected] https://example.com/landings/test?utm_source=reflect_test_parameter
[Reflected] https://example.com/login?utm_name=reflect_test_parameter
...
Reflected parameters will be listed along with the URL where they were found.
Flags:
-t (required): The target domain URL to crawl (e.g., https://example.com).
-s: Include subdomains in the crawl. If this flag is omitted, only the main domain is crawled.


