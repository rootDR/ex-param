# ex-param

**ex-param** is an automated tool designed to find **reflected parameters** that may lead to **Cross-Site Scripting (XSS)** vulnerabilities. It crawls a target website, extracts GET parameters, and tests them for reflected input. The tool is optimized for **bug bounty hunters** and **penetration testers**, offering fast and reliable results to identify potential XSS flaws.

A fast and efficient tool to identify reflected parameters on websites, potentially indicating **Cross-Site Scripting (XSS)** vulnerabilities. The tool crawls the main domain (and optionally subdomains) to discover and test GET parameters for reflection, offering real-time feedback and saving results for later review.

## Key Features

- **Domain Crawling**: Automatically crawls the target domain to discover pages and GET parameters.
- **Subdomain Crawling**: Optionally crawl subdomains for a more comprehensive scan.
- **Reflected Parameter Testing**: Automatically tests GET parameters for potential reflected XSS vulnerabilities by injecting a test payload (`reflected-parameter-test`).
- **Real-Time Results**: Displays the results of the reflected parameter test as soon as they are found.
- **Save Crawled Data**: Saves crawled URLs and reflected parameters in a structured folder for later review.
- **Multithreaded Performance**: Optimized crawling and testing with multithreading to maximize speed.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rootDR/ex-param.git
cd ex-param
pip install -r requirements.txt
```
## Usage

### Basic Usage
Crawl the main domain and test for reflected parameters:
```bash
python ex-param.py -t https://example.com
```

To include subdomains in the crawl, use the -s flag:

```bash

python ex-param.py -t https://example.com -s
```

## Flags and Arguments

| Flag          | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `-t`          | **(Required)** The target domain URL to crawl (e.g., `https://example.com`).|
| `-s`          | **(Optional)** Crawl subdomains in addition to the main domain.             |
| `-d`          | **(Optional)** Set the maximum crawling depth (default: `3`).               |
| `-p`          | **(Optional)** Use a custom payload for reflection testing.                 |
| `-f`          | **(Optional)** Output format for results (`txt`, `json`, or `csv`).         |
| `--delay`     | **(Optional)** Delay between requests in seconds (default: `0.5`).          |
| `--blacklist` | **(Optional)** Comma-separated list of parameters to exclude (e.g., `utm_source,ref`). |
| `--whitelist` | **(Optional)** Comma-separated list of parameters to include (e.g., `q,search,id`). |

## Example Commands

### 1. Basic Crawl
Crawl the main domain and test for reflected parameters:
```bash
python ex-param.py -t http://testphp.vulnweb.com
```
### 2. Crawl with Subdomains
Crawl the domain and its subdomains (if any):
```bash
python ex-param.py -t http://testphp.vulnweb.com -s
```
### 3. Crawl with Custom Depth
```bash
python ex-param.py -t http://testphp.vulnweb.com -d 5
```

### 4. Crawl with Custom Payload
```bash
python ex-param.py -t http://testphp.vulnweb.com -p "<script>alert(1)</script>"
```

### 5. Crawl with JSON Output
```bash
python ex-param.py -t http://testphp.vulnweb.com -f json
```

### 6. Crawl with Delay
```bash
python ex-param.py -t http://testphp.vulnweb.com --delay 1
```

### 7. Crawl with Blacklist
```bash
python ex-param.py -t http://testphp.vulnweb.com --blacklist "utm_source,ref"
```

### 8. Crawl with Whitelist
```bash
python ex-param.py -t http://testphp.vulnweb.com --whitelist "q,search,id"
```

### 9. Crawl with Whitelist
```bash
python ex-param.py -t http://testphp.vulnweb.com -s -d 5 -p "<script>alert(1)</script>" -f json
```

### 10. Full Example
```bash
python ex-param.py -t http://testphp.vulnweb.com -s -d 5 -p "<script>alert(1)</script>" -f json
```

