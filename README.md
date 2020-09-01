# cloudget REBIRTH! 0.77 (HELLO 2020!)
#### by vvn [ vvn @ eudemonics . org ]
#### release date: August 27, 2020! (from southern california on fire with love, socially-distanced, where every day is pandemic day. happy pandemic day, america!)
#### previous release date (version 0.76): July 17, 2016 (cringe, how much things have changed since then.)

**WHAT IS CLOUDGET?**

cloudget is a python script to bypass cloudflare from command line, with extensive scraping, link harvesting, and recursive directory downloading. built upon cfscrape module. code fixed to run on python 3 in 2020 after originally written in python 2.x
in 2016 (hence REBIRH!).

**REQUIRES CFSCRAPE AND BEAUTIFULSOUP MODULES TO RUN**

get cfscrape here:

    https://github.com/Anorov/cloudflare-scrape

get BeautifulSoup here (yes, the script uses the outdated version, sorry):

    http://www.crummy.com/software/BeautifulSoup/

or install using pip:

    pip install cfscrape
    pip install BeautifulSoup

**USAGE:**

    python cloudget.py [-c] [-o] [-l] [-d] [-p <[proxy server]>] -u <[url behind cloudflare proxy]>

**MUST USE COMPLETE URL STARTING WITH http://**

#### OPTIONS:

**-u | --url <[url]>:**
REQUIRED - url behind cloudflare proxy to access

**-o | --out:**
OPTIONAL - download to file

**-c | --curl:**
OPTIONAL - pass URL through cURL

**-l | --links:**
OPTIONAL - find all links in response at URL

**-p | --proxy <[proxy server]>:**
OPTIONAL - connect through HTTP/HTTPS proxy server at http(s)://[host]:[port]
(example: --proxy http://localhost:8080)

**-d | --debug:**
OPTIONAL - turn verbose errors on for debugging, show detailed script info

**-h | --help:**
HELP - show options and exit

**--version:**
OPTIONAL - show version information

**KNOWN BUGS:**

    cURL option (-c) most likely doesn't work with cloudflare URLs.
    for cloudflare URL support don't use -c.

#### if you want this free script to be updated more than once every 5 years,
consider sending a donation to motivate me to keep its development active:

    paypal: paypal.me/eudemonics
    cash app: $lvvn
    venmo app: $eudemonics
    bitcoin address: 1KQvnea8VtnXFEwynVQ8kgeqjsS4rQZFUR

#### STAY SAFE. WEAR A MASK, WASH YOUR HANDS, DON'T BE A JERK.

