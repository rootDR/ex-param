# ex-param
ex-param is an automated tool designed for finding reflected parameters for XSS vulnerabilities. It crawls a target website, extracts GET parameters, and tests them for reflected input. The tool helps bug bounty hunters and penetration testers quickly identify potential reflected XSS flaws, offering fast and reliable results.

## Features
- Crawls a target domain to discover all pages and GET parameters.
- Tests each parameter to check if it's reflected in the response.
- Outputs a list of reflected parameters for further exploitation.
- Fast and optimized for bug bounty hunters.
- Easy to use with minimal setup.

## Requirements
- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `termcolor` library
- `tqdm` library

## Installation

1. Clone the repository:

    git clone https://github.com/yourusername/ex-param.git
    cd ex-param


2. Install the required Python packages:
 
    pip install -r requirements.txt


## Usage

To run **ex-param**, use the following command:


python ex-param.py -t <target_url>
