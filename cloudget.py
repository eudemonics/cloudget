#!/usr/bin/env python
# cloudget v0.3
# release date: July 11, 2015
# author: vvn < lost @ nobody . ninja >

import sys, argparse, subprocess, os, re, random, string, time
from urlparse import urlparse
from subprocess import PIPE, check_output, Popen
try:
   import cfscrape
except:
   pass
   try:
      os.system('pip install cfscrape')
      import cfscrape
   except:
      print('unable to install the cfscrape module via pip. this script requires cfscrape to run. get it here: https://github.com/Anorov/cloudflare-scrape')
      sys.exit(1)


intro = '''
=====================================
----------- CLOUDGET v0.3 -----------
-------------------------------------
----------- author : vvn ------------
--------- lost@nobody.ninja ---------
=====================================
---- support my work: buy my EP! ----
-------- http://dreamcorp.us --------
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
'''

print(intro)

try:
   from BeautifulSoup import BeautifulSoup
except:
   pass
   try:
      os.system('pip install BeautifulSoup')
      from BeautifulSoup import BeautifulSoup
   except:
      print('BeautifulSoup module is required to run the script.')
      sys.exit(1)

global cfurl
global usecurl
global writeout
global links
usecurl = 0
writeout = 0
links = 0

parser = argparse.ArgumentParser(description="a script to automatically bypass anti-robot measures and download links from servers behind a cloudflare proxy")
 
parser.add_argument('-u', '--url', action='store', help='[**REQUIRED**] full cloudflare URL to retrieve, beginning with http(s)://', required=True)
parser.add_argument('-o', '--out', help='save output to \'download\' directory', action='store_true', required=False)
parser.add_argument('-l', '--links', help='harvest links found in response', action='store_true', required=False)
parser.add_argument('-c', '--curl', nargs='?', default='empty', const='curl', dest='curl', metavar='CURL_OPTS', help='use cURL. use %(metavar)s to pass optional cURL parameters. (for more info try \'curl --manual\')', required=False)
parser.add_argument('--version', action='version', version='%(prog)s 0.3 by vvn <lost@nobody.ninja>')

args = parser.parse_args()
if args.out:
   writeout = 1
if args.links:
   links = 1
if args.curl in 'empty':
   usecurl = 0
elif args.curl is 'curl':
   usecurl = 1
else:
   usecurl = 1
   global curlopts
   curlopts = args.curl
cfurl = args.url

def getCF(cfurl):

   checkcurl = ''

   if usecurl == 1:
      checkcurl = 'yes'
   else:
      checkcurl = 'no'
   print("using curl: %s \n" % checkcurl)
   
   if links == 1:
      checklinks = 'yes'
   else:
      checklinks = 'no'
   print("harvesting links: %s \n" % checklinks)

   if writeout == 1:
      global outfile
      p = urlparse(cfurl)
      outfile = cfurl.split('?')[0]
      outfile = outfile.split('/')[-1]
      if len(outfile) < 1:
         outfile = cfurl.lstrip('http:').strip('/') + '.html'
      if p.netloc in outfile:
         outfile = outfile + '.html'
      print("output file: %s \n" % outfile)
      if not os.path.exists('download'):
         os.makedirs('download')
      global savefile
      savefile = os.path.join('download', outfile)

   print("creating new session..\n")
   scraper = cfscrape.create_scraper() # returns a requests.Session object

   try:
      if usecurl == 1 and writeout == 1:
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\nheaders: ")
         print(r.headers)
         print("\ngetting cookies for %s.. \n" % cfurl)
         cookie_arg = cfscrape.get_cookie_string(cfurl)
         print(cookie_arg)
         print("\ntrying to download using cURL to %s.. \n" % outfile)
         command_text = 'curl -# --no-keepalive --ignore-content-length -L -k -O --cookie \'' + cookie_arg + '\' ' + cfurl
         if 'curlopts' in locals():
            command_text = 'curl -# --cookie \'' + cookie_arg + '\' ' + curlopts + ' --no-keepalive -O ' + cfurl
         print(command_text)
         output = subprocess.Popen(command_text, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
         response, errors = output.communicate()
         print("\nresponse: " + str(response))
         print("\nerrors: " + str(errors))

      elif usecurl == 1 and writeout == 0:
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\nheaders: ")
         print(r.headers)
         print("\ngetting cookies for url: %s \n" % cfurl)
         cookie_arg = cfscrape.get_cookie_string(cfurl)
         print(cookie_arg)
         print("\nchecking cURL output...\n")
         if 'curlopts' in locals():
            command_text = 'curl -# --cookie \'' + cookie_arg + '\' ' + curlopts + ' --no-keepalive -O ' + cfurl
            output = subprocess.Popen(command_text, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            response, errors = output.communicate()
            print("\nresponse: %s \n" % str(response))
         else:
            result1 = check_output(["curl", "-#", "--cookie", cookie_arg, cfurl])
            time.sleep(5)
            result = check_output(["curl", "-#", "--cookie", cookie_arg, "-L", "-k", "--no-keepalive", cfurl])
            print(result)

      elif usecurl == 0 and writeout == 1:
         print("getting %s... \n" % cfurl)
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\nheaders: ")
         print(r.headers)
         if re.search(r'(\.htm[l]?|\.php|\.[aj]sp[x]?|\.cfm|\/)$',cfurl):
            print(bs)
         print("\nsaving content to \'download\' directory as %s. this may take awhile depending on file size... \n" % outfile)
         start = time.clock()
         filesize = r.headers.get('Content-Length')
         dld = 0
         progress = lambda a: a - start
         with open(savefile, 'wb+') as dlfile:
            if filesize is None:
               dlfile.write(r.content)
            else:
               print('\nfilesize: %s bytes \n' % str(filesize))
               filesize = int(filesize)
               for chunk in r.iter_content(chunk_size=2048):
                  if chunk:
                     dld += len(chunk)
                     dlfile.write(chunk)
                     done = int((50 * dld) / filesize)
                     sys.stdout.write("\rdownloaded: %d bytes   [%s%s] %s kb/s" % (dld, '#' * done, ' ' * (50 - done), 0.000125 * (dld / (time.clock() - start))))
                     dlfile.flush()
                     os.fsync(dlfile.fileno())
            dlfile.close()
         elapsed = time.clock() - start
         print("\ntime elapsed: %s \n" % str(elapsed))
         print("\nfile saved! \n")

      else:
         print("getting %s... \n" % cfurl)
         #print(scraper.get(cfurl).content)
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\nheaders: ")
         print(r.headers)
         print('')
         time.sleep(5)
         s = scraper.get(cfurl, stream=True)
         html = BeautifulSoup(s.text)
         bs = html.prettify()
         if re.search(r'^(.*)(\.html?|\.php|\.[aj]spx?|\.cfm)|(\/)$',cfurl):
            print(bs)

      def getlinks(cfurl):
         r = scraper.get(cfurl, stream=True)
         html = BeautifulSoup(r.text)
         bs = html.prettify()
         print('\nFOUND LINKS:\n')
         for link in html.findAll('a'):
            b = link.get('href')
            b = str(b)
            print(b)
         print('')

      if links == 1:
         getlinks(cfurl)
         follow = raw_input('fetch harvested links? enter Y/N --> ')
         while not re.search(r'^[yYnN]$', follow):
            follow = raw_input('invalid entry. enter Y to follow harvested links or N to quit --> ')

         if follow.lower() == 'y':
            if 'dirs' not in locals():
               dirs = raw_input('follow directories? enter Y/N --> ')
               while not re.search(r'^[yYnN]$', dirs):
                  dirs = raw_input('invalid entry. enter Y to follow directories or N to only retrieve files --> ')
            r = scraper.get(cfurl, stream=True)
            html = BeautifulSoup(r.text)
            findlinks = html.findAll('a')
            p = urlparse(cfurl)
            part = p.path.split('/')[-1]
            path = p.path.strip(part)
            if '/' not in path[:1]:
               path = '/' + path
            parent = p.scheme + '://' + p.netloc + path
            total = len(findlinks)
            if dirs.lower() == 'y':
               for link in findlinks:
                  b = link.get('href')
                  if not re.match(r'^(\.\.\/)$', str(b)):
                     b = parent + b
                     print("\nrequesting harvested URL: %s \n" % b)
                     getCF(b)
                     getlinks(b)
                  else:
                     continue
            else:
               for link in findlinks:
                  b = link.get('href')
                  if not re.search(r'^(.*)(\/)$', str(b)):
                     b = parent + b
                     print("\nrequesting harvested URL: %s \n" % b)
                     getCF(b)
                  else:
                     continue

   except Exception, e:
      print("\nan error has occurred: %s \n" % str(e))
      raise Exception
      sys.exit(1)

getCF(cfurl)

print("exiting..")
sys.exit(0)
