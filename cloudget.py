#!/usr/bin/env python
# cloudget v0.72
# release date: October 21, 2015
# author: vvn < lost @ nobody . ninja >

import sys, argparse, codecs, subprocess, os, re, random, requests, string, time, traceback
from datetime import date, datetime
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

intro = '''\n
\033[40m\033[34m=============================================================\033[0m
\033[40m\033[32m=============================================================\033[0m
\033[40m\033[90;1m---------------------- CLOUDGET v0.72 -----------------------\033[0m
\033[40m\033[34;21m=============================================================\033[0m
\033[40m\033[32m=============================================================\033[0m
\033[40m\033[35;1m----------------------- author : vvn ------------------------\033[0m
\033[40m\033[35m--------------- lost [at] nobody [dot] ninja ----------------\033[0m
\033[40m\033[34;1m=============================================================\033[0m
\033[40m\033[37;21m---------------- support my work: buy my EP! ----------------\033[0m
\033[40m\033[35m-------------------- http://dreamcorp.us --------------------\033[0m
\033[40m\033[35m--------------- facebook.com/dreamcorporation ---------------\033[0m
\033[40m\033[37;1m------------------ thanks for the support! ------------------\033[0m
\033[40m\033[34;1m=============================================================\033[0m
\033[21m\n'''

if os.name == 'nt' or sys.platform == 'win32':
   intro = '''\n
   =============================================================
   =============================================================
   ---------------------- CLOUDGET v0.72 -----------------------
   =============================================================
   =============================================================
   ----------------------- author : vvn ------------------------
   --------------- lost [at] nobody [dot] ninja ----------------
   =============================================================
   ---------------- support my work: buy my EP! ----------------
   -------------------- http://dreamcorp.us --------------------
   --------------- facebook.com/dreamcorporation ---------------
   ------------------ thanks for the support! ------------------
   =============================================================
   \n'''

print(intro)

try:
   from bs4 import BeautifulSoup, UnicodeDammit
except:
   pass
   try:
      os.system('pip install BeautifulSoup')
      from bs4 import BeautifulSoup
   except:
      print('BeautifulSoup module is required to run the script.')
      sys.exit(1)

global cfurl
global usecurl
global writeout
global depth
global useproxy
global debug
global depth
global finished
global firsturl
usecurl = 0
writeout = 0
depth = 0
useproxy = 0
debug = 0
depth = 0
links = 0
finished = []

parser = argparse.ArgumentParser(description="a script to automatically bypass anti-robot measures and download links from servers behind a cloudflare proxy")

parser.add_argument('-u', '--url', action='store', help='[**REQUIRED**] full cloudflare URL to retrieve, beginning with http(s)://', required=True)
parser.add_argument('-o', '--out', help='save returned content to \'download\' subdirectory', action='store_true', required=False)
parser.add_argument('-l', '--links', help='scrape content returned from server for links', action='store_true', required=False)
parser.add_argument('-c', '--curl', nargs='?', default='empty', const='curl', dest='curl', metavar='CURL_OPTS', help='use cURL. use %(metavar)s to pass optional cURL parameters. (for more info try \'curl --manual\')', required=False)
parser.add_argument('-p', '--proxy', action='store', metavar='PROXY_SERVER:PORT', help='use a proxy to connect to remote server at [protocol]://[host]:[port] (example: -p http://localhost:8080) **only use HTTP or HTTPS protocols!', required=False)
parser.add_argument('-d', '--debug', help='show detailed stack trace on exceptions', action='store_true', required=False)
parser.add_argument('--version', action='version', version='%(prog)s v0.70 by vvn <lost@nobody.ninja>, released October 12, 2015.')

args = parser.parse_args()
if args.out:
   writeout = 1
if args.links:
   links = 1
if args.debug:
   debug = 1
if args.proxy:
   useproxy = 1
   proxy = args.proxy
   if not re.search(r'^(http[s]?|socks(4[a]?|5)?)', proxy):
      print("\ninvalid argument supplied for proxy server. must specify as [protocol]://[server]:[port], where [protocol] is either http or https. (for example, http://127.0.0.1:8080) \n")
      sys.exit(1)
   x = urlparse(args.proxy)
   proxyhost = str(x.netloc)
   proxytype = str(x.scheme)
if args.curl in 'empty':
   usecurl = 0
elif args.curl is 'curl':
   usecurl = 1
else:
   usecurl = 1
   global curlopts
   curlopts = args.curl

cfurl = args.url
firsturl = cfurl

print("\nURL TO FETCH: %s \n" % cfurl)

if 'proxy' in locals():
   if 'https' in proxytype:
      proxystring = {'https': '%s' % proxyhost}
   else:
      proxystring = {'http': '%s' % proxyhost}
   print("using %s proxy server: %s \n" % (str(proxytype.upper()), str(proxyhost)))
else:
   proxystring = None
   print("not using proxy server \n")

if not re.match(r'^http$', cfurl[:4]):
   print("incomplete URL provided: %s \r\ntrying with http:// prepended..")
   cfurl = "http://" + cfurl

depth = 0

def getCF(cfurl, links):

   checkcurl = ''
   checklinks = ''
   if links == 1:
      checklinks = 'yes'
      global followdirs
   else:
      checklinks = 'no'
   if usecurl == 1:
      checkcurl = 'yes'
   else:
      checkcurl = 'no'

   if debug == 1:
      print("\n\033[32;1mlocals: \n\033[0m")
      for name, val in locals().iteritems():
         print("\033[35;1m%s:\033[32;21m %s \033[0m" % (str(name), str(val)))
      print("\n\033[32;1mglobals: \n\033[0m")
      for name, val in globals().iteritems():
         print("\n\033[35;1m%s:\033[36;21m %s \033[0m" % (str(name), str(val)))
      print('\033[0m\r\n')
      print("\n\033[31;1musing curl:\033[31;21m\033[33m %s \033[0m\n" % checkcurl)
      print("\n\033[34;1mharvesting links:\033[34;21m\033[33m %s \033[0m\n" % checklinks)

   p = urlparse(cfurl)
   part = p.path.split('/')[-1]
   path = p.path.strip(part)
   if '/' not in path[:1]:
      path = '/' + path
   urlfqdn = p.scheme + '://' + p.netloc
   parent = urlfqdn + path
   childdir = path.strip('/')
   domaindir = os.path.join('download', p.netloc)
   parentdir = os.path.join(domaindir, childdir)
   
   if firsturl in finished and cfurl in firsturl:
      print('\nABORTING: already retrieved %s!\n') % firsturl
      sys.exit(1)

   global outfile
   outfile = cfurl.split('?')[0]
   outfile = outfile.split('/')[-1]

   if writeout == 1:
      global existing
      global checkresume
      p = urlparse(cfurl)
      if not os.path.exists('download'):
         os.makedirs('download')
      if not os.path.exists(domaindir):
         os.makedirs(domaindir)
      filename = cfurl.lstrip('https:').strip('/')
      filename = filename.rstrip(outfile)
      dirs = filename.split('/')
      a = 'download'
      i = 1
      for dir in dirs:
         while i < len(dirs):
            if not re.search(r'^(.*)\.[.]+$', dir):
               a = os.path.join(a, dir)
               if not os.path.exists(a):
                  os.makedirs(a)
               i += 1
            else:
               break
      if len(outfile) < 1 or outfile in p.netloc:
         outfile = 'index.html'
         outdir = filename.strip()
      elif '.' not in outfile:
         part = outfile
         outfile = outfile + '.html'
         outdir = filename.rstrip(part)
      else:
         part = outfile
         outdir = filename.rstrip(part)
      fulloutdir = os.path.join('download', outdir)
      outfile = outfile.strip('/')
      if not os.path.exists(fulloutdir):
         os.makedirs(fulloutdir)
      print("output file: %s \n" % outfile)
      global savefile
      savefile = os.path.join(fulloutdir, outfile)
      cwd = os.getcwd()
      fullsavefile = os.path.join(cwd, savefile)
      print("full path to output file: %s \n" % fullsavefile)
      
   else:
      if len(outfile) < 1 or outfile in p.netloc:
         outfile = 'index.html'

   scraper = cfscrape.create_scraper()
   ualist = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
'Mozilla/5.0 (compatible; MSIE 9.0; AOL 9.7; AOLBuild 4343.19; Windows NT 6.1; WOW64; Trident/5.0; FunWebProducts)',
'Mozilla/5.0 (Windows NT 6.3; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1 WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
'Mozilla/5.0 (X11; SunOS i86pc; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; FreeBSD amd64; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; FreeBSD i386; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; Linux i586; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; OpenBSD amd64; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; OpenBSD alpha; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; OpenBSD sparc64; rv:38.0) Gecko/20100101 Firefox/38.0',
'Mozilla/5.0 (X11; Linux x86_64; rv:17.0) Gecko/20121202 Firefox/17.0 Iceweasel/17.0.1',
'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16',
'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14 Mozilla/5.0 (Windows NT 6.0; rv:2.0) Gecko/20100101 Firefox/4.0 Opera 12.14',
'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14'
]
   n = random.randint(0,len(ualist)) - 1
   ua = ualist[n].strip()
   
   def cfcookie(cfurl):
      sess = requests.session()
      p = urlparse(cfurl)
      mnt = p.scheme + '://'
      sess.mount(mnt, cfscrape.CloudflareAdapter())
      sess.get(cfurl)
      #sess.cookies
      l = sess.get(cfurl)
      b = sess.cookies
      if b:
         c = b.items()
         for s, t in c:
            cs = u''.join(s).encode('utf-8').strip()
            ct = u''.join(t).encode('utf-8').strip()
            print('\033[34;1m' + str(cs) + '\033[0m')
            print('\033[32;1m' + str(ct) + '\033[0m')
         cookies = "\"cf_clearance\"=\"%s\"" % sess.cookies.get('cf_clearance')
         if sess.cookies.get('__cfduid'):
            cookies = cookies + ";\"__cfduid\"=\"%s\"" % sess.cookies.get('__cfduid')
      else:
         cookies = None
      return cookies

   def getpage(cfurl):      
      r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      if 'text' in r.headers.get('Content-Type'):
         #rt = unicode(r.content.lstrip(codecs.BOM_UTF8), 'utf-8')
         #rt = UnicodeDammit.detwingle(r.text)
         html = BeautifulSoup(r.text, "html.parser")
         print('\r\n--------------------------------------------------------\r\n')
         if debug == 1:
            orenc = str(html.original_encoding)
            print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
         bs = html.prettify(formatter=None)
         bsu = u''.join(bs).encode('utf-8').strip()
         print(bsu)
         print('\r\n--------------------------------------------------------\r\n')
      else:
         found = -1
      
      if debug == 1:
         print('\n\033[34mDEBUG: finished list length: \033[37;1m%d \033[0m\n' % len(finished))
         
   # cURL request - using cURL for cloudflare URLs doesn't seem to work
   if usecurl == 1:

      r = scraper.get(cfurl, stream=True, verify=False, allow_redirects=True, proxies=proxystring)
      print("status: ")
      print(r.status_code)
      print("\ngetting cookies for %s.. \n" % cfurl)
      req = "GET / HTTP/1.1\r\n"
      cookie_arg = cfcookie(cfurl)
      if cookie_arg:
         req += "Cookie: %s\r\nUser-Agent: %s\r\n" % (cookie_arg, ua)
         houtput = check_output(["curl", "--cookie", cookie_arg, "-A", ua, "-s", cfurl])
         curlstring = '--cookie \'' + cookie_arg + '\' -A \'' + ua + '\' -k '
         if 'curlopts' in locals():
            curlstring = '--cookie \'' + cookie_arg + '\' ' + curlopts + ' -A \'' + ua + '\' -k '
      else:
         cookie_arg = cfscrape.get_cookie_string(cfurl)
         curlstring = '-A \'' + ua + '\' -k '
         if 'curlopts' in locals():
            curlstring = '-# ' + curlopts + ' -A \'' + ua + '\' -k '
         if proxy:
            curlstring += '-x %s ' % proxy
         if cookie_arg:
            curlstring += '--cookie \'' + cookie_arg + '\' '
            req += "Cookie: %s\r\nUser-Agent: %s\r\n" % (cookie_arg, ua)
            houtput = check_output(["curl", "-A", ua, "--cookie", cookie_arg, "-s", cfurl])
         else:
            req += "User-Agent: %s\r\n" % ua
            houtput = check_output(["curl", "-A", ua, "i", "-s", cfurl])
      
      print('\n\033[34;1msubmitting headers:\n\033[21m\033[37m%s \033[0m\n' % req)
      print("\nRESPONSE: \n%s \n" % str(houtput))
      msg = "\nfetching %s using cURL.. \n" % cfurl
      if writeout == 1:
         if os.path.exists(savefile):
            resumesize = os.path.getsize(savefile)
            print("\n%s already exists! \n" % outfile)
            print("\nlocal file size: %s bytes \n" % str(resumesize))
            if 'existing' not in globals():
               existing = 0
            if existing == 0:
               checkresume = raw_input('choose an option [1-3]: 1) resume download, 2) start new download, 3) skip. --> ')
               while not re.match(r'^[1-3]$', checkresume):
                  checkresume = raw_input('invalid input. enter 1 to resume, 2 to start new, or 3 to skip --> ')
               checkexist = raw_input('\ndo this for all downloads? Y/N --> ')
               while not re.match(r'^[YyNn]$', checkexist):
                  checkexist = raw_input('invalid entry. enter Y to use same action on existing files or N to always ask --> ')
               if checkexist.lower() == 'y':
                  existing = 1
               else:
                  existing = 0
            if checkresume == '1':
               curlstring = curlstring + '-C - -o \'' + savefile + '\' '
               msg = "\ntrying to resume download using cURL to %s.. \n" % savefile
            elif checkresume == '2':
               curlstring = curlstring + '-O '
               msg = "\nstarting new download to %s.. \n" % savefile
            else:
               msg = "\nskipping download for %s \n" % outfile
         else:
            curlstring = curlstring + '-O '
            msg = "\ntrying to download using cURL to %s.. \n" % savefile
         #command_text = 'cd download && { curl ' + curlstring + cfurl + ' ; cd -; }'
      else:
         msg = "\nfetching %s using cURL.. \n" % cfurl
      command_text = 'curl ' + curlstring + '-s ' + cfurl
      print(msg)
      print("\nsubmitting cURL command string: \n%s \n" % command_text)
      output = Popen(command_text, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
      result, errors = output.communicate()
      if result is not None:
         if writeout == 1 and not re.search(r'(\.(htm)l?|\.php|\.txt|\.xml|\.[aj](sp)x?|\.cfm|\.do|\.md|\.json)$',outfile):
            print('\nsaved file: %s \n' % outfile)
         else:
            ht = BeautifulSoup(r.content, "html.parser")
            htpr = ht.prettify(formatter=None)
            htpr = u''.join(htpr).encode('utf-8').strip()
            print(htpr)
      else:
         if errors:
            print("\nerror: %s\n" % str(errors))
      finished.append(cfurl)

   elif usecurl == 0 and writeout == 1:
      getkb = lambda a: round(float(float(a)/1000),2)
      getmb = lambda b: round(float(float(b)/1000000),2)
      getsecs = lambda s: round(float(time.mktime(s.timetuple())),2)
      print("\ngetting %s... \n" % cfurl)
      if os.path.exists(savefile): # FOUND SAVED FILE
         # GET SIZE OF EXISTING LOCAL FILE
         resumesize = os.path.getsize(savefile)
         ksize = getkb(resumesize)
         msize = getmb(resumesize)
         sizeqt = 'kb'
         fsize = ksize
         if msize > 1:
            sizeqt = 'mb'
            fsize = msize
         existsize = str(fsize) + ' ' + sizeqt
         print("\n%s already exists! \n" % outfile)
         print("\nlocal file size: %s \n" % existsize)
         if 'existing' not in globals():
            existing = 0
         if existing == 0:
            checkresume = raw_input('choose an option [1-3]: 1) resume download, 2) start new download, 3) skip. --> ')
            while not re.match(r'^[1-3]$', checkresume):
               checkresume = raw_input('invalid input. enter 1 to resume, 2 to start new, or 3 to skip --> ')
            checkexist = raw_input('\ndo this for all downloads? Y/N --> ')
            while not re.match(r'^[YyNn]$', checkexist):
               checkexist = raw_input('invalid entry. enter Y to use same action on existing files or N to always ask --> ')
            if checkexist.lower() == 'y':
               existing = 1
            else:
               existing = 0

         if checkresume == '1': # RESUME DOWNLOAD AT LAST LOCAL BYTE
            dld = int(resumesize)
            resumeheader = {'Range': 'bytes=%s-' % str(dld)}
            dlmsg = "\nattempting to resume download for %s. this may take awhile depending on file size... \n" % outfile
            df = open(savefile, 'a+b')
         elif checkresume == '2': # DISREGARD SAVED FILE, START DOWNLOAD FROM TOP
            resumeheader = None
            dlmsg = "\nwriting content to \'download\' directory as file %s. this may take awhile depending on file size... \n" % outfile
            df = open(savefile, 'wb+')
         else: # SKIPPING DOWNLOAD
            resumeheader = None
            df = open(savefile, 'r+')
            dlmsg = "\nskipping download for %s\n" % outfile

      else: # NEW DOWNLOAD REQUEST
         checkresume = '2'
         dld = 0
         df = open(savefile, 'wb+')
         resumeheader = None
         dlmsg = "\nwriting content to \'download\' directory as file %s. this may take awhile depending on file size... \n" % outfile

      print(dlmsg)

      if not checkresume == '3': # IF NOT SKIPPING
         r = scraper.get(cfurl, stream=True, headers=resumeheader, verify=False, allow_redirects=True, proxies=proxystring)
         filesize = r.headers.get('Content-Length')
         if checkresume == '1' and filesize is not None:
            filesize = int(filesize) + int(resumesize)
         filetype = r.headers.get('Content-Type')
         start = getsecs(datetime.now())
         time.sleep(1)
         #today = datetime.now()
         #startdate = date.strftime(today,"%m-%d-%Y %H:%M:%S ")
         #print("start time: %s \n" % startdate)
         with df as dlfile:
            if filesize is not None and 'text' not in filetype:
               bytesize = int(filesize)
               kbsize = getkb(bytesize)
               mbsize = getmb(bytesize)
               qt = 'bytes'
               size = bytesize
               if kbsize > 10:
                  qt = 'kb'
                  size = kbsize
                  if mbsize > 1 :
                     qt = 'mb'
                     size = mbsize
               print('\nfile size: %d %s \n' % (size, qt))
               for chunk in r.iter_content(chunk_size=2048):
                  if chunk:
                     dld += len(chunk)
                     dlfile.write(chunk)
                     done = int((50 * int(dld)) / int(filesize))
                     dldkb = getkb(dld)
                     dldmb = getmb(dld)
                     unit = 'b   '
                     prog = str(round(dld,2))
                     if dldkb > 1:
                        unit = 'kb   '
                        prog = str(round(dldkb,2))
                        if dldmb > 1:
                           unit = 'mb   '
                           prog = str(round(dldmb,2))
                     sys.stdout.write("\rdownloaded: %s %s   [%s%s] %d kbps    \r" % (prog, unit, '#' * done, ' ' * (50 - done), 0.001 * (dld / ((getsecs(datetime.now()) - start) + 0.1))))
                     dlfile.flush()
                     os.fsync(dlfile.fileno())
                  else:
                     break
            elif filesize and 'text' in filetype:
               dlfile.write(r.content)
               dlfile.flush()
               os.fsync(dlfile.fileno())
            else:
               for chunk in r.iter_content(chunk_size=1024):
                  if chunk:
                     dld += len(chunk)
                     dlfile.write(chunk)
                     dlfile.flush()
                     os.fsync(dlfile.fileno())
                  else:
                     break
         print("\r\nfile %s saved! \n" % outfile)
         endclock = getsecs(datetime.now())
         fin = endclock - start
         totalsecs = fin
         if debug == 1:
            print("\n\033[34;1mSTART: \033[35;1m %s \033[0;21m\n" % str(start))
            print("\n\033[34;1mEND: \033[35;1m %s \033[0;21m\n" % str(endclock))
         elapsed = "%s seconds " % str(totalsecs)
         if totalsecs > 60:
            totalmins = float(totalsecs / 60)
            mins = int(totalmins)
            if mins == 1:
               unitmin = "minute"
            else:
               unitmin = "minutes"
            strmin = str(mins) + " " + str(unitmin)
            secs = round((totalsecs % 60), 4)
            elapsed = str(strmin) + " " + str(secs) + " seconds"
            if totalmins > 60:
               totalhours = float(totalmins / 60 )
               hours = int(totalmins / 60)
               if hours == 1:
                  unithr = "hour"
               else:
                  unithr = "hours"
               strhr = str(hours) + " " + str(unithr)
               mins = round((totalmins % 60),3)
               elapsed = "%s, %s mins, %s secs" % (strhr, mins, secs)
            else:
               hours = 0
         else:
            hours = 0
            mins = 0
            secs = round(totalsecs,3)
            elapsed = "%s seconds" % str(secs)
         #ended = datetime.now()
         #enddate = date.strftime(ended,"%m-%d-%Y %H:%M:%S ")
         #print("end time: %s \n" % enddate)
         print("\ndownload time elapsed: %s \n" % str(elapsed))
         time.sleep(2)
         print('\r\n--------------------------------------------------------\r\n')

      else:
         print("\nskipped download from %s.\r\nfile has not been modified.\n" % cfurl)
      
      getpage(cfurl)
      finished.append(cfurl)
      
   else:
      getpage(cfurl)
      finished.append(cfurl)

   def getlinks(cfurl):
      r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      html = BeautifulSoup(r.text, "html.parser")
      if debug == 1:
         orenc = str(html.original_encoding)
         print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
      bs = html.prettify(formatter=None)
      linkresult = html.findAll('a')
      if len(linkresult) > 0:
         foundlinks = len(linkresult)
         print('\nFOUND %s LINKS AT %s:\n' % (str(foundlinks), cfurl))
         for link in linkresult:
            b = link.get('href')
            b = str(b)
            if b not in cfurl and not re.match(r'^(\.\.)?\/$', b) and '#' not in str(b):
               print(b)
         print('')
      else:
         print('\nNO LINKS FOUND.\n')
         foundlinks = 0
      time.sleep(3)
      return foundlinks

   def selectdir(geturl):
      r = scraper.get(geturl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      html = BeautifulSoup(r.text, "html.parser")
      if debug == 1:
         orenc = str(html.original_encoding)
         print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
      findlinks = html.findAll('a')
      dirlist = []
      for link in findlinks:
         b = link.get('href')
         if not re.match(r'^((\.\.)?\/)$', str(b)) and '#' not in str(b):
            if re.search(r'^(.*)(\/)$', str(b)):
               dirlist.append(b)

      p = urlparse(geturl)
      part = p.path.split('/')[-1]
      path = p.path.rstrip(part)
      if '/' not in path[:1]:
         path = '/' + path
      urlfqdn = p.scheme + '://' + p.netloc
      parent = urlfqdn + path

      i = 0
      dirtotal = len(dirlist)
      if dirtotal > 0:
         print('\nFOUND %d DIRECTORIES: \n' % dirtotal)
         while i < dirtotal:
            sel = i + 1
            print(str(sel) + ' - ' + str(dirlist[i]))
            i += 1
         print('')
         lim = dirtotal + 1
         matchtop = r'^(%s)(\/)?$' % urlfqdn
         if not re.match(matchtop,geturl):
            print('0 - BACK TO PARENT DIRECTORY \n')
            startsel = '0-%d' % dirtotal
         else:
            startsel = '1-%d' % dirtotal
         selectdir = raw_input('make a selection [%s] --> ' % startsel)
         if not int(selectdir) in range(0, lim):
            selectdir = raw_input('invalid entry. please enter a selection %s --> ' % startsel)
         if selectdir == '0':
            geturl = parent
            subcont = 0
         else:
            n = int(selectdir) - 1
            usedir = dirlist[n]
            geturl = parent + usedir
            subcont = 1
      else:
         print('\nNO DIRECTORIES FOUND. using current directory.. \n')
         subcont = 0
         geturl = parent + part
      return geturl, subcont, parent
      
   def getparent(cfurl):
      cff = re.match(r'^http:\/\/(.*)(\/\/)(.*)', cfurl)
      if cff:
         cf = 'http://' + str(cff.group(1)) + '/' + str(cff.group(3))
      else:
         cf = str(cfurl)
      p = urlparse(cf)
      if '/' not in p.path[-1:]:
         part = p.path.split('/')[-1]
         path = p.path.rstrip(part)
      else:
         path = p.path
      if '/' not in path[:1]:
         path = '/' + path
      urlfqdn = p.scheme + '://' + p.netloc
      parent = urlfqdn + path + '/'
      return parent

   def followlinks(bx):
      p = urlparse(bx)
      if '/' not in p.path[-1:]:
         part = p.path.split('/')[-1]
         path = p.path.rstrip(part)
      else:
         path = p.path
      if '/' not in path[:1]:
         path = '/' + path
      urlfqdn = p.scheme + '://' + p.netloc
      parent = urlfqdn + path + '/'
      s = scraper.get(bx, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      print('\n----------------------------------------------------------- \n')
      print(s)
      print('\n')
      shtml = BeautifulSoup(s.text, "html.parser")
      if debug == 1:
         orenc = str(shtml.original_encoding)
         print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
      print('\n----------------------------------------------------------- \n')
      sfindlinks = shtml.findAll('a')
      slen = len(sfindlinks)
      sdirs = []
      si = 0
      while si < slen:
         for slink in sfindlinks:
            if debug == 1:
               print('\n\033[34;1mSLINK LOOP\r\n\033[32;21m* si = %d, si < %d\033[0m\n' % (si, slen))
            sl = slink.get('href')
            si += 1
            if sl:
               if not re.search(r'^((\.\.)?\/)$', str(sl)) and '#' not in str(sl):
                  if '/' in bx[-1:]:
                     if 'http' not in sl[:4]:
                        sl = sl.lstrip('/')
                        sx = bx + sl
                     else:
                        sx = sl
                     print(sx)
                     getCF(sx, 0)
                     ss = scraper.get(sx, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
                     bb = BeautifulSoup(ss.text, "html.parser")
                     if bb is not None:
                        if debug == 1:
                           orenc = str(bb.original_encoding)
                           print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
                        if bb.html is not None:
                           pagehead = bb.html.head.contents
                           if pagehead is not None and len(pagehead) > 1:
                              pagehead = u''.join(pagehead).encode('utf-8').strip()
                              pagetitle = re.search(r'<title>(.*)<\/title>', pagehead)
                              pagetitle = str(pagetitle.group(1))
                              bigtitle = pagetitle.upper()
                              titlestars = lambda a: '*' * (len(str(a)) + 4)
                              pagestars = titlestars(pagetitle)
                              print('\n\033[40m\033[33m%s\033[0m\n\033[34;1m* %s *\033[0m \n\033[40m\033[33;21m%s\033[0m\n' % (pagestars, bigtitle, pagestars))
                              
                        sb = bb.find_all('a', href = re.compile(r'.+$'))
                        sblen = len(sb)
                        if sblen > 0:
                           n = 0
                           while n < sblen:
                              for sbl in sb:
                                 if debug == 1:
                                    print('\n\033[35;1mSBL LOOP\r\n\033[37;21m* n = %d, n < %d \033[0m\n' % (n, sblen))
                                 if sbl is not None:
                                    sr = sbl.get('href').strip()
                                    sr = str(sr)
                                    print('\n* %s \n') % sr
                                    if not re.search('http', sr[:4]):
                                       parent = getparent(sx)
                                       srs = sr.lstrip('/')
                                       sr = parent + srs
                                    if re.match(r'([^.]+\/)$', str(sr)):
                                       followlinks(sr)
                                       sdirs.append(sr)
                                    else:
                                       if '/' not in sr[-1:] and '#' not in sr:
                                          getCF(sr, 0)
                                          sdirs.append(sr)
                                    n += 1
                                 else:
                                    n += 1
                                    continue
                     else:
                        n += 1
                        continue
                        
                  elif 'Error-222' in bx:
                     print('\nuh-oh. might have triggered a flag with cloudflare.\n')
                     for i in xrange(10,0,-1):
                        time.sleep(1)        
                        print('delaying request for %d seconds.. \r' % i)
                        sys.stdout.flush()
                     break
                  else:
                     if not re.search('http', str(sl[:4])):
                        parent = getparent(bx)
                        if '/' in sl[:1]:
                           sl = sl.lstrip('/')
                        sx = parent + sl
                     else:
                        sx = str(sl)

                  sx = str(sx)
                  sdirs.append(sx)
                  print(sx)
                  print('\n----------------------------------------------------------- \n')              
                  getCF(sx, 0)
               si += 1

               #if re.search(r'^(.*)(\/)$', str(bx)):
            else:
               print('\nno links found at %s \n' % str(slink))
               si += 1
               continue

      for sd in sdirs:
         if '/' in sd[-1:]:
            print('\nfollowing directory: %s \n' % sd)
            followlinks(sd)
            getCF(sd, 1)
         else:
            print('\nrequesting link: %s \n' % sd)
            getCF(sd, 0)
      return sdirs

   if links == 1:
      if 'found' not in locals():
         found = getlinks(cfurl)
         keep = 1
         depth = 0
      while found > 0 and keep is not 0:
         follow = raw_input('fetch harvested links? enter Y/N --> ')
         while not re.search(r'^[yYnN]$', follow):
            follow = raw_input('invalid entry. enter Y to follow harvested links or N to quit --> ')
         if follow.lower() == 'n':
            break
         elif follow.lower() == 'y':
            r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
            html = BeautifulSoup(r.text, "html.parser")
            findlinks = html.findAll('a')
            s = []
            checkfordirs = 0
            if len(findlinks) > 0:
               for d in findlinks:
                  dd = d.get('href')
                  if re.search(r'^(.*)(\/)$', str(dd)):
                     if not re.match(r'^((\.\.)?\/)$', str(dd)) and dd not in cfurl and '#' not in str(dd):
                        if 'http' not in dd[:4]:
                           dd = parent + dd
                        s.append(str(dd))
                        checkfordirs = 1

            if len(s) > 0 and checkfordirs == 1:
               if 'followdirs' not in locals():
                  followdirs = raw_input('follow directories? enter Y/N --> ')
                  while not re.search(r'^[yYnN]$', followdirs):
                     followdirs = raw_input('invalid entry. enter Y to follow directories or N to only retrieve files --> ')
                  if followdirs.lower() == 'y':
                     depth = 1
                  else:
                     depth = 0
               else:
                  if followdirs.lower() == 'y':
                     depth += 1
            else:
               followdirs = 'n'

            if debug == 1:
               print("\n\033[35;1mdepth:\033[37;21m %d \033[0m\n" % depth)
            if findlinks:
               total = len(findlinks)
            else:
               total = 0
            if writeout == 1:
               if not os.path.exists(parentdir):
                  os.makedirs(parentdir)
            if total > 0:
               if followdirs.lower() == 'n':
                  for link in findlinks:
                     b = link.get('href')
                     if b:
                        if not re.search(r'^(.*)(\/)$', str(b)) and '#' not in str(b):
                           b = parent + b
                           print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % b)
                           try:
                              getCF(b, links)
                           except KeyboardInterrupt:
                              try:
                                 print("\r\nskipping %s... \r\npress CTRL + C again to quit.\n" % b)
                                 time.sleep(2)
                                 continue
                              except KeyboardInterrupt:
                                 print("\r\nrequest aborted by user.\n")
                                 keep = 0
                                 break
                              except Exception, e:
                                 print("\r\nan exception has occurred: %s \n" % str(e))
                                 raise
                           except (KeyboardInterrupt, SystemExit):
                              print("\r\nrequest cancelled by user\n")
                              keep = 0
                              break
                           except Exception, e:
                              print("\r\nan exception has occurred: %s \n" % str(e))
                              raise
                        else:
                           continue
                     else:
                        break
                     total = total - 1
                  links = 1
               elif followdirs.lower() == 'y' and depth > 0:
                  choosedir = raw_input("choose subdirectory? Y/N --> ")
                  while not re.match(r'^[YyNn]$', choosedir):
                     choosedir = raw_input("invalid entry. enter Y to pick subdirectory or N to download everything --> ")
                  if choosedir.lower() == 'n':
                     links = 0
                     for link in findlinks:
                        b = link.get('href')
                        if b:
                           bx = parent + b

                           if not re.match(r'^((\.\.)?\/)$', str(b)) and '#' not in str(b):
                              getdirs = followlinks(bx)
                              while len(getdirs) > 0:
                                 for sd in getdirs:
                                    getdirs = followlinks(sd)
                              print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % bx)
                              try:
                                 getCF(bx, links)
                                 if debug == 1:
                                    print("\nfound: %d \n" % found)
                              except KeyboardInterrupt:
                                 try:
                                    print("\r\nskipping %s...\n press CTRL + C again to quit.\n" % bx)
                                    time.sleep(2)
                                    continue
                                 except KeyboardInterrupt:
                                    print("\r\nrequest aborted by user.\n")
                                    break
                                 except Exception, e:
                                    print("\r\nan exception has occurred: %s \n" % str(e))
                                    raise
                                    sys.exit(1)
                              except (KeyboardInterrupt, SystemExit):
                                 sys.exit("\r\nrequest cancelled by user.\n")
                                 break
                              except Exception, e:
                                 print("\r\nan exception has occurred: %s \n" % str(e))
                                 raise
                                 sys.exit(1)
                     links = 1
                     found = found - 1
                  else:
                     subcont = 1
                     geturl = cfurl
                     while subcont is not 0:
                        depth += 1
                        if subcont < 1:
                           break
                        geturl, subcont, parent = selectdir(geturl)
                        if debug == 1:
                           print("\ndepth: %d \n" % depth)
                        checksubdir = raw_input("enter 1 to select this directory, 2 to choose a subdirectory, or 3 to go back to parent directory --> ")
                        while not re.match(r'^[1-3]$', checksubdir):
                           checksubdir = raw_input("invalid input. enter a value 1-3 --> ")
                        if checksubdir is not 2:
                           if checksubdir == '3':
                              p = urlparse(geturl)
                              droppath = p.path.split('/')[-1]
                              geturl = geturl.rstrip(droppath)
                           break

                     print('\nrequesting harvested URL: %s \r\n(press CTRL + C to skip) \n' % geturl)
                     try:
                        getCF(geturl, links)
                        found = found - 1
                     except KeyboardInterrupt:
                        try:
                           print("\r\nskipping %s... \npress CTRL + C again to quit.\n" % geturl)
                           time.sleep(2)
                           continue
                        except KeyboardInterrupt:
                           print("\r\nrequest aborted by user.\n")
                           keep = 0
                           break
                        except Exception, e:
                           print("\r\nan exception has occurred: %s \n" % str(e))
                           raise
                           sys.exit(1)
                     except (KeyboardInterrupt, SystemExit):
                        print("\r\nrequest cancelled by user\n")
                        keep = 0
                        break
                     except Exception, e:
                        print("\r\nan exception has occurred: %s \n" % str(e))
                        raise
                        sys.exit(1)
                     finally:
                        depth -= 1
                        if debug == 1:
                           print("\ndepth: %d \n" % depth)

               elif followdirs.lower() == 'y' and depth < 1:
                  for link in findlinks:
                     b = link.get('href')
                     if not re.  match(r'^((\.\.)?\/)$', str(b)):
                        bx = parent + b
                        print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % bx)
                        try:
                           getCF(bx, links)
                        except KeyboardInterrupt:
                           try:
                              print("\r\nskipping %s... press CTRL + C again to quit.\n" % bx)
                              time.sleep(2)
                              continue
                           except KeyboardInterrupt:
                              print("\nprogram aborted by user.\n")
                              break
                           except Exception, e:
                              print("\r\nan exception has occurred: %s \n" % str(e))
                              raise
                              sys.exit(1)
                        except (KeyboardInterrupt, SystemExit):
                           print("\r\nrequest cancelled by user\n")
                           break
                        except Exception, e:
                           print("\r\nan exception has occurred: %s \n" % str(e))
                           raise
                           sys.exit(1)
                        finally:
                           links = 0
                     else:
                        continue
                     found = found - 1
                     if debug == 1:
                        print("\nfound: %d \n" % found)

               else:
                  for link in findlinks:
                     b = link.get('href')
                     links = 0
                     if debug == 1:
                        print("\nfound: %d \n" % found)
                     while b:
                        if not re.search(r'^(.*)(\/)$', str(b)):
                           b = parent + b
                           print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % b)
                           try:
                              getCF(b, links)
                           except KeyboardInterrupt:
                              print("\r\nskipping %s...\n" % b)
                              try:
                                 print("\r\npress CTRL + C again to exit.\r\n")
                                 time.sleep(2)
                                 continue
                              except KeyboardInterrupt:
                                 print("\r\nprogram aborted by user.\n")
                                 break
                           except (KeyboardInterrupt, SystemExit):
                              sys.exit("\r\nrequest cancelled by user.\n")
                              break
                           except Exception, e:
                              print("\r\nan exception has occurred: %s \n" % str(e))
                              raise
                        else:
                           continue
                     if debug == 1:
                        found = found - 1
                     print("\nfound: %d \n" % found)
                  links = 1
            else:
               print("\ndid not find any links.\n")
               found = found - 1
               if debug == 1:
                  print("\nfound: %d \n" % found)
               keep = 0
               break

         else:
            cpath = p.path.strip('/')
            cpaths = cpath.split('/')
            lastpath = cpaths[-1]
            if len(lastpath) < 1 and len(cpaths) > 1:
               lastpath = cpaths[-2]
            cfurl = cfurl.strip('/')
            matchtop = r'^(%s)$' % urlfqdn
            if found == 0:
               keep = 0
               print("\nfinished following all links.\n")
            break

      else:
         found = 0

         print("\nno more links to fetch at %s.\n" % cfurl)
         if debug == 1:
            print("\nfound: %d \n" % found)
         cpath = p.path.strip('/')
         cpaths = cpath.split('/')
         lastpath = cpaths[-1]
         if len(lastpath) < 1 and len(cpaths) > 1:
            lastpath = cpaths[-2]
         cfurl = cfurl.strip('/')
         urlfqdn = urlfqdn.strip('/')
         print(urlfqdn)
         matchtop = r'^(%s)$' % urlfqdn
         if re.match(matchtop, cfurl) and found == 0:
            keep = 0
            print("\nfinished following all links.\n")
         else:
            cfurl = cfurl.rstrip(lastpath)
            print('\ntrying %s.. \n' % cfurl)

try:
   getCF(cfurl, links)

except (KeyboardInterrupt, SystemExit):
   print("\r\nrequest cancelled by user\n")
   print("\r\nhit CTRL + C again to exit program, or it will automatically continue in 10 seconds.\n")
   try:
      for i in xrange(10,0,-1):
         time.sleep(1)
         sys.stdout.write("\r%s..\r" % str(i))
         sys.stdout.flush()
   except KeyboardInterrupt:
      sys.exit("\r\nrequest aborted by user.\n")
   except (KeyboardInterrupt, SystemExit):
      sys.exit("\r\nrequest cancelled by user.\n")
   except Exception, exc:
      print("\nan error has occurred: %s \n" % str(exc))
      sys.exit("unable to continue. check the URL and try again.\n")
      raise
except requests.exceptions.ConnectionError, e:
   print("\na connection error occurred: %s \n" % str(e))
   pass
   time.sleep(7)
   print("\nattempting to reconnect to %s...\n" % cfurl)
   try:
      getCF(cfurl, links)
   except Exception, exc:
      print("\nan exception has occurred %s \n" % str(exc))
      raise

except RuntimeError, e:
   print("\na runtime error has occurred: %s \n" % str(e))
   raise

except SyntaxError, e:
   print("\na typo is a silly reason to force a program to terminate..\n")
   print("\nespecially this one:\n %s \n" % str(e))
   raise

except IOError, e:
   print("\na connection error has occurred: %s \n" % str(e))
   pass
   time.sleep(7)
   print("\nattempting to reconnect to %s...\n" % cfurl)
   try:
      getCF(cfurl, links)
   except Exception, exc:
      print("\nan exception has occurred %s \n" % str(exc))
      print("unable to continue. please restart the program.\n")
      raise
      exit(1)

except Exception, e:
   print("\nan error has occurred: %s \n" % str(e))
   print("unable to continue. check the parameters and try again.\n")
   raise
   if debug == 1:
      traceback_template = '''Traceback (most recent call last):
      File "%(filename)s", line %(lineno)s, in %(name)s
   %(type)s: %(message)s\n'''
      traceback_details = {
                            'filename': sys.exc_info()[2].tb_frame.f_code.co_filename,
                            'lineno'  : sys.exc_info()[2].tb_lineno,
                            'name'    : sys.exc_info()[2].tb_frame.f_code.co_name,
                            'type'    : sys.exc_info()[0].__name__,
                            'message' : sys.exc_info()[1].message,
                           }
      print
      print(traceback.format_exc())
      #print(traceback.extract_tb(sys.exc_info()[2]))
      print(traceback_template % traceback_details)
   sys.exit(1)

print("\nexiting..\n")
sys.exit(0)
