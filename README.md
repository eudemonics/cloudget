# cloudget 0.2
#### by vvn [ lost @ nobody . ninja ]

 python script to bypass cloudflare from command line. built upon cfscrape module.

**REQUIRES CFSCRAPE AND BEAUTIFULSOUP MODULES TO RUN**

get cfscrape here:

    https://github.com/Anorov/cloudflare-scrape

get BeautifulSoup here:

    http://www.crummy.com/software/BeautifulSoup/

or install using pip:

    pip install cfscrape
    pip install BeautifulSoup

**USAGE:**

    python cloudget.py [-c] [-o] -u <[url behind cloudflare proxy]>

**MUST USE COMPLETE URL STARTING WITH http://**

#### OPTIONS:

**-u | --url <[url]>:**
REQUIRED - url behind cloudflare proxy to access

**-o | --out:**
OPTIONAL - download to file

**-c | --curl:**
OPTIONAL - pass URL through cURL

**-h | --help:**
HELP - show options and exit


**KNOWN BUGS:**

    cURL option (-c) most likely doesn't work with cloudflare URLs.
    for cloudflare URL support please don't use -c.
