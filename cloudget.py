#!/usr/bin/env python
# cloudget v0.2
# release date: July 10, 2015
# author: vvn < lost @ nobody . ninja >

import sys, getopt, subprocess, os, re, random, string, time
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
      

print('''
=====================================
----------- CLOUDGET v0.2 -----------
-------------------------------------
----------- author : vvn ------------
--------- lost@nobody.ninja ---------
=====================================
---- support my work: buy my EP! ----
-------- http://dreamcorp.us --------
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
''')

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
global curldl
global links
usecurl = 0
writeout = 0
links = 0

try:
   opts, args = getopt.getopt(sys.argv[1:],"hu:ocl",["help","url=","out","curl","links"])

except getopt.GetoptError:
   print('cloudget.py [-c] [-o] [-l] -u <url> \n')
   print('-c, --curl: use cURL')
   print('-o, --out: save output')
   print('l, --links: harvest links')
   print('-u, --url <url>: cloudflare URL to get [**REQUIRED**]')
   print('**USE COMPLETE URL beginning with http://**')
   sys.exit(2)

for opt, arg in opts:
   if opt in ("-h", "--help"):
      print('cloudget.py [-c] [-o] [-l] -u <url> \n')
      print('-c, --curl: use cURL without downloading')
      print('-o, --out: save output')
      print('l, --links: harvest links')
      print('-u, --url <url>: cloudflare URL to get [**REQUIRED**]')
      print('**USE COMPLETE URL beginning with http://**')

   elif opt in ("-o", "--out"):
      writeout = 1
   elif opt in ("-u", "--url"):
      cfurl = arg
   elif opt in ("-c", "--curl"):
      usecurl = 1
   elif opt in ("-l", "--links"):
      links = 1

def getCF(cfurl):

   checkcurl = ''

   if usecurl == 1:
      checkcurl = 'yes'
   else:
      checkcurl = 'no'
   print("using curl: %s \n" % checkcurl)


   if writeout == 1:
      global outfile
      outfile = cfurl.split('/')[-1]
      if len(outfile) < 1:
         outfile = cfurl.lstrip('http:').strip('/') + '.html'
      print("output file: %s \n" % outfile)
      if not os.path.exists('download'):
         os.makedirs('download')
      outfile = os.path.join('download', outfile)

   print("creating new session..\n")
   scraper = cfscrape.create_scraper() # returns a requests.Session object

   try:
      if usecurl == 1 and writeout == 1:
         print("PLEASE FIX ME \n")
         r = scraper.get(cfurl, stream=True)
         print("status: ")
         print(r.status_code)
         print("\nheaders: ")
         print(r.headers)
         print("\ngetting cookies for %s.. \n" % cfurl)
         cookie_arg = cfscrape.get_cookie_string(cfurl)
         print("trying to download using cURL to %s.. \n" % outfile)
         command_text = 'curl -# --no-keepalive --ignore-content-length -L -O --cookie \'' + cookie_arg + '\' ' + cfurl
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
         print("\nsaving content to %s \n" % outfile)

         with open(outfile, 'wb+') as dlfile:
            for chunk in r.iter_content(chunk_size=4096):
               if chunk:
                  dlfile.write(chunk)
                  dlfile.flush()
                  os.fsync(dlfile.fileno())
            dlfile.close()
         print("file saved! \n")

      else:
         print("getting %s... \n" % cfurl)
         #print(scraper.get(cfurl).content)
         r = scraper.get(cfurl, stream=True)
         html = BeautifulSoup(r.text)
         bs = html.prettify()
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
            p = urlparse(cfurl)
            part = p.path.split('/')[-1]
            path = p.path.strip(part)
            parent = p.scheme + '://' + p.netloc + path
            for link in html.findAll('a'):
               b = link.get('href')
               if not re.match(r'^(\.\.\/)$', str(b)):
                  b = parent + b
                  print("requesting harvested URL: %s \n" % b)
                  getCF(b)
                  getlinks(b)

   except Exception, e:
      print("an error has occurred: %s \n" % str(e))
      raise Exception
      sys.exit(1)

getCF(cfurl)

print("exiting..")
sys.exit(0)
