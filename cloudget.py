#!/usr/bin/env python
# cloudget v0.3
# release date: July 12, 2015
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
   uafile = open('useragents.txt', 'r+')
   ualist = uafile.readlines()
   n = random.randint(0,len(ualist))
   ua = ualist[n].strip()
   #ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36'
   try:
      if usecurl == 1:
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\ngetting cookies for %s.. \n" % cfurl)
         cookie_arg = cfscrape.get_cookie_string(cfurl)
         print(cookie_arg)
         header = 'curl --cookie \'' + cookie_arg + '\' -I -L ' + cfurl
         houtput = subprocess.Popen(header, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
         hresponse, herrors = houtput.communicate()
         print("\nheaders: \n%s \n" % str(hresponse))
         curlstring = 'curl -# --cookie \'' + cookie_arg + '\' -A \'' + ua + '\' --no-keepalive --ignore-content-length -k '
         if 'curlopts' in locals():
            curlstring = 'curl -# --cookie \'' + cookie_arg + '\' ' + curlopts + ' -A \'' + ua + ' -k --ignore-content-length '
         if writeout == 1:
            curlstring = curlstring + '-O '
            msg = "\ntrying to download using cURL to %s.. \n" % outfile
         else:
            msg = "\nfetching %s using cURL.. \n" % cfurl
         print(msg)
         command_text = curlstring + cfurl
         print(command_text)
         output = subprocess.Popen(command_text, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
         result, errors = output.communicate()
         if result is not None:
            ht = BeautifulSoup(str(result))
            cloudpass = ht.find('input', {'name': 'pass'}).get('value')
            cloudsch = ht.find('input', {'name': 'jschl_vc'}).get('value')
            print("pass: %s \n" % cloudpass)
            if cloudpass:
               reurl = ht.find('form').get('action')
               print("form action: %s \n" % reurl)
               p = urlparse(cfurl)
               part = p.path.split('/')[-1]
               path = p.path.strip(part)
               if '/' in path[:1]:
                  path = path[1:]
               parent = p.scheme + '://' + p.netloc + path
               go = parent + reurl
               cs = curlstring + '--retry 1 --retry-delay 5 -G --data \'pass=' + cloudpass + '&jschl_vc=' + cloudsch + '&challenge-form=submit&jschl-answer\' -e ' + p.netloc + ' -L '
               if writeout == '0':
                  cs = cs + '-v '
               command = cs + go + '?pass=' + cloudpass
            else:
               print(ht.prettify())
         else:
            command = curlstring + ' -L -i ' + cfurl
         print(command)
         output = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
         response, errors = output.communicate()
         print("\nresponse: \n %s \n" % str(response))

      elif usecurl == 0 and writeout == 1:
         print("getting %s... \n" % cfurl)
         r = scraper.get(cfurl, stream=True)
         print("\nSTATUS: ")
         print(r.status_code)
         print("\nHEADERS: \n")
         for key in r.headers.keys():
            print(str(key) + ": " + str(r.headers[key]))
         print('')
         print("\nsaving content to \'download\' directory as %s. this may take awhile depending on file size... \n" % outfile)
         start = time.clock()
         filesize = r.headers.get('Content-Length')
         dld = 0
         with open(savefile, 'wb+') as dlfile:
            if filesize is None:
               dlfile.write(r.content)
            else:
               print('\nfilesize: %s bytes \n' % str(filesize))
               filesize = int(filesize)
               for chunk in r.iter_content(chunk_size=1024):
                  if chunk:
                     dld += len(chunk)
                     dlfile.write(chunk)
                     done = int((50 * dld) / filesize)
                     sys.stdout.write("\rdownloaded: %d bytes   [%s%s] %s kb/s" % (dld, '#' * done, ' ' * (50 - done), 0.000125 * (dld / (time.clock() - start))))
                     dlfile.flush()
                     os.fsync(dlfile.fileno())
                  else:
                     break
               print("\nfile saved! \n")
            dlfile.close()
         elapsed = time.clock() - start
         print("\ntime elapsed: %s \n" % str(elapsed))
         html = BeautifulSoup(r.text)
         if re.search(r'(\.htm[l]?|\.php|\.[aj]sp[x]?|\.cfm|\/)$',cfurl):
            bs = html.prettify()
            print(bs)

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
