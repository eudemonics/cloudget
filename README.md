# cloudget 0.2
#### by vvn [ lost @ nobody . ninja ]

 python script to bypass cloudflare from command line. built upon cfscrape module.

**REQUIRES CFSCRAPE MODULE TO RUN**

get it here:

    https://github.com/Anorov/cloudflare-scrape

or install using pip:

    pip install cfscrape

**USAGE:**

    python cloudget.py [-c] [-o] -u <[url behind cloudflare proxy]>

**MUST USE COMPLETE URL STARTING WITH http://**

#### OPTIONS:

**-u | --url <[url]>:**
REQUIRED - url behind cloudflare proxy to access

**-o | --out:**
OPTIONAL - download to file

**-c | --curl:**
OPTIONAL - pass cloudflare link through cURL

**-h | --help:**
HELP - show options and exit


**KNOWN BUGS:**

    cURL download (-c -o) is still not fully functional yet. working on it.
