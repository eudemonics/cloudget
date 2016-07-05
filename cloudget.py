#!/usr/bin/env python
# cloudget v0.74
# release date: July 4, 2016
# author: vvn < root @ nobody . ninja >
#####
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2015-2016  vvn < root @ nobody . ninja >
##### 
##### This program is FREE software: you can use it, redistribute it and/or modify
##### it as you wish. Copying and distribution of this file, with or without modification,
##### are permitted in any medium without royalty provided the copyright
##### notice and this notice are preserved. This program is offered AS-IS,
##### WITHOUT ANY WARRANTY; without even the implied warranty of
##### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##### GNU General Public License for more details.
##### 
##### For more information, please refer to the "LICENSE AND NOTICE" file that should
##### accompany all official download releases of this program. 
#####
## latest updates to program will always be found here:
## https://github.com/eudemonics/cloudget
##
## to update: from program folder in terminal or git shell, enter 'git pull'
##### enjoy!


import sys, argparse, subprocess, os, re, random, requests, string, time, traceback
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
      print('\nunable to install the cfscrape module via pip. this script requires cfscrape to run. get it here: https://github.com/Anorov/cloudflare-scrape \n')
      sys.exit(1)

intro = '''\n
\033[40m\033[34m=============================================================\033[0m
\033[40m\033[32m=============================================================\033[0m
\033[40m\033[90;1m---------------------- CLOUDGET v0.74 -----------------------\033[0m
\033[40m\033[34;21m=============================================================\033[0m
\033[40m\033[32m=============================================================\033[0m
\033[40m\033[35;1m----------------------- author : vvn ------------------------\033[0m
\033[40m\033[35m--------------- root [at] nobody [dot] ninja ----------------\033[0m
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
   ---------------------- CLOUDGET v0.74 -----------------------
   =============================================================
   =============================================================
   ----------------------- author : vvn ------------------------
   --------------- root [at] nobody [dot] ninja ----------------
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
global img
global imgdone
usecurl = 0
writeout = 0
depth = 0
useproxy = 0
debug = 0
depth = 0
links = 0
img = 0
imgdone = 0
finished = []

parser = argparse.ArgumentParser(description="a script to automatically bypass anti-robot measures and download links from servers behind a cloudflare proxy")

parser.add_argument('-u', '--url', action='store', help='[**REQUIRED**] full cloudflare URL to retrieve, beginning with http(s)://', required=True)
parser.add_argument('-o', '--out', help='save returned content to \'download\' subdirectory', action='store_true', required=False)
parser.add_argument('-l', '--links', help='scrape content returned from server for links', action='store_true', required=False)
parser.add_argument('-c', '--curl', nargs='?', default='empty', const='curl', dest='curl', metavar='CURL_OPTS', help='use cURL. use %(metavar)s to pass optional cURL parameters. (for more info try \'curl --manual\')', required=False)
parser.add_argument('-p', '--proxy', action='store', metavar='PROXY_SERVER:PORT', help='use a proxy to connect to remote server at [protocol]://[host]:[port] (example: -p http://localhost:8080) **only use HTTP or HTTPS protocols!', required=False)
parser.add_argument('-i', '--img', help='scrape page for image files and save to \'img\' subdirectory', action='store_true', required=False)
parser.add_argument('-d', '--debug', help='show detailed stack trace on exceptions', action='store_true', required=False)
parser.add_argument('--version', action='version', version='%(prog)s v0.74 by vvn <root@nobody.ninja>, released January 21, 2016.')

args = parser.parse_args()
if args.out:
   writeout = 1
if args.links:
   links = 1
if args.img:
   img = 1
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
#cfurl = cfurl.strip('/')
firsturl = cfurl.strip('/')

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
   
quittext = '''
*******************************************

thanks for using CLOUDGET! <3
for help, suggestions, or other inquiries,
or to report an error, contact vvn at:

root @ nobody [dot] ninja

*******************************************

'''

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
      print("\n\033[36;1mglobals: \n\033[0m")
      for name, val in globals().iteritems():
         print("\n\033[35;1m%s:\033[36;21m %s \033[0m" % (str(name), str(val)))
      print('\033[0m\r\n')
      print("\n\033[31;1musing curl:\033[31;21m\033[33m %s \033[0m\n" % checkcurl)
      print("\n\033[34;1mharvesting links:\033[34;21m\033[33m %s \033[0m\n" % checklinks)

   p = urlparse(cfurl)
   part = p.path.split('/')[-1]
   path = p.path.strip(part)
   if path == cfurl:
      cfurl = cfurl.rstrip('/')
      p = urlparse(cfurl)
      part = p.path.split('/')[-1]
      path = p.path.strip(part)
   urlfqdn = p.scheme + '://' + p.netloc
   childdir = ''
   parent = urlfqdn + childdir + path
   if '/' not in path[:1]:
      parent = p.geturl()
      childdir = ''
   else:
      if len(part) < 1:
         parent = p.geturl()
         childdir = path
      else:
         if path == '/':
            if re.search(r'\.([\w]{2,4})(\?|$)', part):
               parent = urlfqdn
            else:
               parent = urlfqdn + p.path
               childdir = p.path
         else:
            parent = urlfqdn + path
            childdir = path
   childdir = childdir.strip('/')
   domaindir = os.path.join('download', p.netloc)
   parentdir = os.path.join(domaindir, childdir)
   
   if firsturl in finished and cfurl in firsturl:
      print('\nABORTING: already retrieved %s!\n') % firsturl
      sys.exit(1)

   global outfile
   outfile = cfurl.split('?')[0]
   outfile = outfile.split('/')[-1]

   if writeout == 1 or img == 1:
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
         if '/' not in cfurl[-1:]:
            cfurl = cfurl + '/'
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
      
      imgdir = os.path.join('images', outdir)
      if not os.path.exists(imgdir):
         os.makedirs(imgdir)
      
   else:
      if len(outfile) < 1 or outfile in p.netloc:
         outfile = 'index.html'

   scraper = cfscrape.create_scraper()
   ualist = [
# Safari #
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.9 (KHTML, like Gecko) Version/8.0 Safari/600.1.9',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25',
'Mozilla/5.0 (iPad; U; CPU OS 5_1 like Mac OS X; en-us) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
# Google Chrome #
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (Windows NT 6.1 WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (X11; CrOS x86_64 6946.86.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
'Mozilla/5.0 (Linux; Android 4.4; 6 Build/iOS8.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.111 Mobile Safari/537.36',
'Mozilla/5.0 (Linux; Android 5.0.2; iPad Build/LRX22G) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/37.0.0.0 Safari/537.36',
# Internet Explorer/Edge #
'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10136',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0',
'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
'Mozilla/5.0 (compatible; MSIE 10.0; AOL 9.0; AOLBuild 4327.5201; Windows NT 6.1; WOW64; Trident/6.0)',
'Mozilla/5.0 (compatible; MSIE 10.0; AOL 9.7; AOLBuild 4343.19; Windows NT 6.1; WOW64; Trident/5.0; FunWebProducts)',
'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.1; Trident/6.0; vr; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 810)',
'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; SAMSUNG; SGH-T899M)',
# Firefox #
'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (Windows NT 6.3; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; SunOS i86pc; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; FreeBSD amd64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; FreeBSD i386; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; Linux i586; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; OpenBSD amd64; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; OpenBSD alpha; rv:43.0) Gecko/20100101 Firefox/43.0',
'Mozilla/5.0 (X11; OpenBSD sparc64; rv:43.0) Gecko/20100101 Firefox/43.0',
# Other #
'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; Avant Browser)',
'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) FxiOS/1.1 Mobile/13C71 Safari/601.1.46',
'Mozilla/5.0 (iPhone; CPU iPhone OS 9_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/47.0.2526.70 Mobile/13C75',
'Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20121202 Firefox/43.0 Iceweasel/43.0',
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
   
   def getimg(cfurl):
      imgdone = 0
      r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      if 'text' in r.headers.get('Content-Type'):
         soup = BeautifulSoup(r.text, "html.parser")
         if soup is not None:
            links = soup.findAll('img')
            print('\r\n--------------------------------------------------------\r\n')
            bs = soup.prettify(formatter=None)
            bsu = u''.join(bs).encode('utf-8').strip()
            print(bsu)
            print('\r\n--------------------------------------------------------\r\n')
            for link in links:
               #imgurl = link.split("src=")[-1]
               imgurl = link['src']
               imgfile = os.path.basename(imgurl)
               imgfile = imgfile.strip('/')
               fullimgfile = os.path.join(imgdir, imgfile)
               
               getkb = lambda a: round(float(float(a)/1000),2)
               getmb = lambda b: round(float(float(b)/1000000),2)
               getsecs = lambda s: round(float(time.mktime(s.timetuple())),2)
               getdif = lambda x, y: time.strftime('%H:%M:%S', time.gmtime(getsecs(x) - y))
               
               start = getsecs(datetime.now())
               time.sleep(1)
               
               print('\ngetting %s... \n' % str(imgfile))
               
               ext = ['.jpg', '.jpeg', '.png', '.gif', '.tif', '.bmp']
               
               img64 = 1
               for char in ext:
                  if char in imgfile:
                     img64 = 0
                     break
               
               if img64 == '1':
                  rand = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(4)])
                  dt = date.strftime(datetime.now(),"%m.%d.%Y.%H.%M.%S")
                  imgfile = '%s_%s.png' % (str(dt), str(rand))
                  fullimgfile = os.path.join(imgdir, imgfile)
                  imgdl  = open(fullimgfile, 'wb+')
                  imgdl.write(imgurl.decode('base64'))
                  imgdl.close()
               
               else:
                  imgdl = open(fullimgfile, "wb+")
                  download_img = scraper.get(imgurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
                  filesize = download_img.headers.get('Content-Length')
                  dld = 0
                  print('\nFOUND IMAGE: %s \n' % str(imgurl))
               
               
                  with imgdl as dlfile:
                     bytesize = int(filesize)
                     kbsize = getkb(filesize)
                     mbsize = getmb(filesize)
                     qt = 'bytes'
                     size = bytesize
                     if kbsize > 10:
                        qt = 'kb'
                        size = kbsize
                        if mbsize > 1 :
                           qt = 'mb'
                           size = mbsize
                     print('\n\033[33mfile size:\033[31m %s %s \033[0m\n' % (str(size), qt))
                     for chunk in download_img.iter_content(chunk_size=2048):
                        if chunk:
                           dld += len(chunk)
                           dlfile.write(chunk)
                           done = int((30 * int(dld)) / int(filesize))
                           dldkb = getkb(dld)
                           dldmb = getmb(dld)
                           unit = 'b      '
                           prog = str(round(dld,2))
                           if dldkb > 1:
                              unit = 'kb      '
                              prog = str(round(dldkb,2))
                              if dldmb > 1:
                                 unit = 'mb      '
                                 prog = str(round(dldmb,2))
                           sys.stdout.write("\r\033[33mdownloaded: \033[36m%s %s   \033[0m[%s%s]\033[35m %d kbps     \033[0mtime elapsed: \033[34m%s      \033[0m\r" % (prog, unit, '\033[32m#\033[0m' * done, ' ' * (30 - done), 0.001 * (dld / ((getsecs(datetime.now()) - start) + 0.1)), (getdif(datetime.now(), start))))
                           dlfile.flush()
                           os.fsync(dlfile.fileno())
                        else:
                           break
                  imgdl.close()
               
               print('\nimage saved: %s \n' % imgfile)
               imgdone += 1
               print('\nDOWNLOAD COUNT: %d \n' % imgdone)
               
            print('\r\n--------------------------------------------------------\r\n')
         
         print('\n***FINISHED DOWNLOADING ALL IMAGES.***\n')
         print('\nTOTAL IMAGES: %d \n' % imgdone)
            
      else:
         found = -1
         

   def getpage(cfurl):
      r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      if 'text' in r.headers.get('Content-Type'):
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
         print('\n\033[34mDEBUG LN 501: finished list length: \033[37;1m%d \033[0m\n' % len(finished))
   
   if img == 1 and 'imgdone' not in locals():
      getimg(cfurl)
         
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
      getdif = lambda x, y: time.strftime('%H:%M:%S', time.gmtime(getsecs(x) - y)) 
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
            dld = 0
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
         #starttime = date.strftime(datetime.now(), "%H:%M:%S")
         start = getsecs(datetime.now())
         time.sleep(1)
         #today = datetime.now()
         #startdate = date.strftime(today,"%m-%d-%Y %H:%M:%S ")
         #print("start time: %s \n" % startdate)
         with df as dlfile:
            if filesize is not None and 'text' not in filetype:
               bytesize = int(filesize)
               kbsize = getkb(filesize)
               mbsize = getmb(filesize)
               qt = 'bytes'
               size = bytesize
               if kbsize > 10:
                  qt = 'kb'
                  size = kbsize
                  if mbsize > 1 :
                     qt = 'mb'
                     size = mbsize
               print('\n\033[33mfile size:\033[31m %s %s \033[0m\n' % (str(size), qt))
               for chunk in r.iter_content(chunk_size=2048):
                  if chunk:
                     dld += len(chunk)
                     dlfile.write(chunk)
                     done = int((30 * int(dld)) / int(filesize))
                     dldkb = getkb(dld)
                     dldmb = getmb(dld)
                     unit = 'b      '
                     prog = str(round(dld,2))
                     if dldkb > 1:
                        unit = 'kb      '
                        prog = str(round(dldkb,2))
                        if dldmb > 1:
                           unit = 'mb      '
                           prog = str(round(dldmb,2))
                     sys.stdout.write("\r\033[33mdownloaded: \033[36m%s %s  \033[0m[%s%s]\033[35m %d kbps     \033[0mtime elapsed: \033[34m%s      \033[0m\r" % (prog, unit, '\033[32m#\033[0m' * done, ' ' * (30 - done), 0.001 * (dld / ((getsecs(datetime.now()) - start) + 0.1)), (getdif(datetime.now(), start))))
                     dlfile.flush()
                     os.fsync(dlfile.fileno())
                  else:
                     break
            elif filesize and 'text' in filetype:
               dlfile.write(r.content)
               dlfile.flush()
               os.fsync(dlfile.fileno())
            else:
               for chunk in r.iter_content(chunk_size=2048):
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
            secs = round(totalsecs % 60,4)
            elapsed = str(strmin) + " " + str(secs) + " seconds"
            if totalmins > 60:
               totalhours = float(totalmins / 60 )
               hours = int(totalmins / 60)
               if hours == 1:
                  unithr = "hour"
               else:
                  unithr = "hours"
               strhr = str(hours) + " " + str(unithr)
               mins = totalmins % 60
               elapsed = "%s, %s mins, %s secs" % (strhr, mins, secs)
            else:
               hours = 0
         else:
            hours = 0
            mins = 0
            secs = totalsecs
            elapsed = "%s seconds" % str(secs)
         #ended = datetime.now()
         #print("end time: %s \n" % enddate)
         #enddate = date.strftime(ended,"%m-%d-%Y %H:%M:%S ")
         print("\ndownload time elapsed: %s \n" % str(elapsed))
         time.sleep(2)
         print('\r\n--------------------------------------------------------\r\n')

      else:
         print("\nskipped download from %s.\r\nfile has not been modified.\n" % cfurl)
      
      getpage(cfurl)
      cfurl = str(cfurl.strip())
      finished.append(cfurl)
      
   else:
      getpage(cfurl)
      cfurl = str(cfurl.strip())
      finished.append(cfurl)
      
   def getparent(cfurl):
      cff = re.match(r'^http:\/\/(.*)(\/\/)(.*)', cfurl)
      if cff:
         cf = 'http://' + str(cff.group(1)) + '/' + str(cff.group(3))
      else:
         cf = str(cfurl)
      p = urlparse(cf)
      part = p.path.split('/')[-1]
      path = p.path.strip(part)
      if path == cf:
         cf = cf.rstrip('/')
         p = urlparse(cf)
         part = p.path.split('/')[-1]
         path = p.path.strip(part)
      urlfqdn = p.scheme + '://' + p.netloc
      childdir = ''
      parent = urlfqdn + childdir + path
      if '/' not in path[:1]:
         parent = p.geturl()
         childdir = ''
      else:
         if len(part) < 1:
            parent = p.geturl()
            childdir = path
         else:
            if path == '/':
               if re.search(r'\.([\w]{2,4})(\?|$)', part):
                  parent = urlfqdn
               else:
                  parent = urlfqdn + p.path
                  childdir = p.path
            else:
               parevnt = urlfqdn + path
               childdir = path
      if '/' not in parent[-1:]:
         parent = parent + '/'
      return parent

      
   def getlinks(cfurl):
      r = scraper.get(cfurl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      filetype = r.headers.get('Content-Type')
      filetype = str(filetype)
      html = BeautifulSoup(r.text, "html.parser")
      if debug == 1:
         print('\n\033[40m\033[35;1mDEBUG: \nContent-Type: %s \033[0m\n' % filetype)
      if 'text' in filetype:
         bs = html.prettify(formatter=None)
         linkresult = html.findAll('a')
         if len(linkresult) > 0:
            lr = []
            for link in linkresult:
               linkurl = link.get('href')
               matchstr = r'^(\/)?%s(\/)?$' % part
               if not re.search(r'^(#)|((\.\.)?\/)$', linkurl) and not re.match(matchstr, linkurl) and 'javascript' not in linkurl:
                  lr.append(linkurl)
            dl = 1
            lenlinks = len(lr)
            while dl == 1 and lenlinks > 0:
               x = 0
               while x < lenlinks:
                  for l in lr:
                     y = x + 1
                     print('%d - %s' % (y, l))
                     x += 1
               print('0 - CONTINUE OR DOWNLOAD ALL LINKS')
               print('\n')
               linksel = '[1-%d]' % lenlinks
               lim = lenlinks + 1
               selectlink = raw_input('make a selection %s to download the corresponding link. to continue to another directory or download all links, enter 0 --> ' % linksel)
               while not re.match(r'^[0-9]{1,3}$', selectlink):
                  selectlink = raw_input('invalid input. please enter an integer 0-%d --> ' % lenlinks)
               selectlink = int(selectlink)
               while selectlink not in range(0, lim):
                  selectlink = raw_input('invalid selection. please enter value between 0 and %s --> ' % lenlinks)
               if selectlink == 0:
                  dl = 0
                  foundlinks = len(linkresult)
                  print('\ncontinuing.. \n')
                  break
               elif selectlink in range(1, lim):
                  foundlinks = len(linkresult)
                  n = int(selectlink) - 1
                  lnk = lr[n]
                  par = getparent(cfurl)
                  if 'http' not in lnk[:4]:
                     lnk = lnk.lstrip('/')
                     lnk = par + lnk
                  getCF(lnk, 0)
                  another = raw_input('to choose another link to download, enter 1. to continue, enter 2. to quit, enter 3. --> ')
                  while not re.match(r'^[1-3]$', another):
                     another = raw_input('invalid selection. please enter a value 1-3 --> ')
                  if another == '2':
                     dl = 0
                     break
                  elif another == '3':
                     dl = 0
                     print(quittext)
                     time.sleep(3)
                     print('\nexiting program.. \n')
                     sys.exit(0)
                     
                  else:
                     continue
               else:
                  dl = 0
                  break
            foundlinks = len(linkresult)
            print('\nFOUND \033[31m%s \033[0mLINKS AT \033[036m%s\033[0m:\n(hiding shortcuts and parent directories)\n' % (str(foundlinks), cfurl))
            for link in linkresult:
               b = link.get('href')
               b = str(b)
               if b not in cfurl and not re.match(r'^(\.\.)?\/$', b) and '#' not in b and 'javascript' not in str(b):
                  print(b)
            print('\n')
         else:
            print('\nNO LINKS FOUND.\n')
            foundlinks = 0
      else:
         if not re.search(r'^(.*)\.(jpg|mp3|avi|ogg|mp4|mov|gif|png|bmp|tif|wav|flac)$', cfurl):
            print('\nLINKS NOT AVAILABLE FOR %s \n' % cfurl)
         foundlinks = 0
      time.sleep(3)
      return foundlinks

   def selectdir(geturl):
      r = scraper.get(geturl, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      html = BeautifulSoup(r.text, "html.parser")
      filetype = r.headers.get('Content-Type')
      filetype = str(filetype)
      if debug == 1:
         orenc = str(html.original_encoding)
         print('\n\033[40m\033[35;1mORIGINAL ENCODING: %s \033[0m\n' % orenc)
      findlinks = html.findAll('a')
      dirlist = []
      for link in findlinks:
         b = link.get('href')
         if not re.match(r'^((\.\.)?\/)$', str(b)) and '#' not in str(b) and 'javascript' not in str(b) and str(b) not in geturl:
            if re.search(r'^(.*)(\/)$', str(b)):
               dirlist.append(b)

      p = urlparse(geturl)
      
      part = p.path.split('/')[-1]
      path = p.path.strip(part)
      if path == geturl:
         geturl = geturl.rstrip('/')
         p = urlparse(geturl)
         part = p.path.split('/')[-1]
         path = p.path.strip(part)
      urlfqdn = p.scheme + '://' + p.netloc
      loc = geturl.lstrip('https:').strip('/')
      childdir = ''
      dirs = filename.split('/')
      parent = urlfqdn + childdir + path
      if '.' not in part and len(part) > 0 and '/' in p.path and 'text' in filetype:
         childdir = p.path
         if '/' not in part[1:]:
            childdir = childdir + '/'
         parent = urlfqdn + childdir
      if '/' not in path[:1]:
         parent = p.geturl()
         childdir = ''
      else:
         if len(part) < 1:
            parent = p.geturl()
            childdir = path
         else:
            if path == '/':
               if re.search(r'\.([\w]{2,4})(\?|$)', part):
                  parent = urlfqdn
               else:
                  parent = urlfqdn + p.path
                  childdir = p.path
            else:
               parent = urlfqdn + path
               childdir = path
      if '/' not in parent[-1:]:
         parent = parent + '/'
      childdir = childdir.strip('/')
      print('\n\033[40m\033[35;1mPARENT DIRECTORY: %s \033[0m\n' % parent)
      print('\n\033[40m\033[35;1mCHILD DIRECTORY: %s \033[0m\n' % childdir)
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
         while not re.match(r'^[0-9]{1,3}$', selectdir):
            selectdir = raw_input('invalid input. please enter an integer %s --> ' % startsel)
         selectdir = int(selectdir)
         if selectdir not in range(0, lim):
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
      parent = getparent(bx)
      if debug:
         print('\nDEBUG LN 990: \nparent: %s \n' % parent)
      s = scraper.get(bx, stream=True, verify=False, proxies=proxystring, allow_redirects=True)
      filetype = s.headers.get('Content-Type')
      filetype = str(filetype)
      if 'text' in filetype:
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
                  print('\n\033[34;1mSLINK LOOP\r\n\033[32;21m* si = %d, si < %d (found links)\033[0m\n' % (si, slen))
               sl = slink.get('href')
               si += 1
               if sl:
                  if not re.search(r'^((\.\.)?\/)$', str(sl)) and '#' not in str(sl) and 'javascript' not in str(sl) and sl not in bx:
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
                           if bb.html is not None:
                              pagehead = bb.html.head.contents
                              orenc = str(bb.original_encoding[0])
                              if pagehead is not None and len(pagehead) > 1:
                                 pagehead = unicode(pagehead, orenc, "ignore").encode('utf8', 'replace').strip()
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
                                       print('* %s \n') % sr
                                       if not re.search('http', sr[:4]):
                                          parent = getparent(sx)
                                          srs = sr.lstrip('/')
                                          sr = parent + srs
                                       if re.match(r'([^.]+\/)$', str(sr)):
                                          followlinks(sr)
                                          sdirs.append(sr)
                                       else:
                                          if '/' not in sr[-1:] and '#' not in sr and 'javascript' not in sr and sr not in sx:
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

      else:
         print('\ncannot search for links in file type: %s \n' % filetype)
         sdirs = []
      
      return sdirs

   if links == 1:
      if 'depth' not in locals() and 'depth' not in globals():
         depth = 1
      else:
         keep = 0
      if 'found' not in locals() and 'found' not in globals():
         found = getlinks(cfurl)
         keep = 1
         depth = 0
         
      while found > 0 and keep is not 0:
         if 'follow' not in locals():
            follow = raw_input('fetch all harvested links? enter Y/N --> ')
            while not re.search(r'^[yYnN]$', follow):
               follow = raw_input('invalid entry. enter Y to follow harvested links or N to quit --> ')
         elif follow.lower() == 'n':
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
                     if not re.match(r'^((\.\.)?\/)$', str(dd)) and dd not in cfurl and '#' not in str(dd) and 'javascript' not in str(dd):
                        if 'http' not in dd[:4]:
                           dd = parent + dd
                        s.append(str(dd))
                        checkfordirs = 1

            if len(s) > 0 and checkfordirs == 1:
               if 'followdirs' not in locals() and 'followdirs' not in globals():
                  followdirs = raw_input('follow directories? enter Y/N --> ')
                  while not re.search(r'^[yYnN]$', followdirs):
                     followdirs = raw_input('invalid entry. enter Y to follow directories or N to only retrieve files --> ')
                  if followdirs.lower() == 'y':
                     depth = 1
                  else:
                     depth = 0
               else:
                  if followdirs.lower() == 'y':
                     if 'depth' not in locals():
                        depth = 1
                     depth += 1
            else:
               followdirs = 'n'
               depth = 0

            if findlinks:
               total = len(findlinks)
            else:
               total = 0
            if writeout == 1:
               if not os.path.exists(parentdir):
                  os.makedirs(parentdir)
            if total > 0:
               if followdirs.lower() == 'n':
                  
                  findlinks = html.findAll('a')
                  for link in findlinks:
                     b = link.get('href')
                     if b:
                        if not re.search(r'^(.*)(\/)$', str(b)) and '#' not in str(b) and 'javascript' not in str(b):
                           if 'http' not in b[:4]:
                              b = parent + b
                           if debug:
                              print('\nDEBUG: \nparent: %s \nb: %s\n' % (parent, str(b)))
                           if b in finished:
                              keep = 0
                              break
                           try:
                              print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % b)
                              getCF(b, 0)
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
                           if b not in cfurl and '#' not in b and 'javascript' not in str(b):
                              if 'http' not in b[:4]:
                                 bx = parent + b
                              else:
                                 bx = b
                              if debug:
                                 print('\nDEBUG: \nparent: %s \nbx: %s \n' % (parent, bx))
                              if bx in finished:
                                 keep = 0
                                 print('\n%s already fetched \n' % bx)
                                 break
                              if not re.match(r'^((\.\.)?\/)$', str(bx)) and '#' not in str(bx) and str(bx) not in part and 'javascript' not in str(bx):
                                 getdirs = followlinks(bx)
                                 while len(getdirs) > 0:
                                    for sd in getdirs:
                                       getdirs = followlinks(sd)
                                    getdirs = 0
                                 print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % bx)
                                 try:
                                    getCF(bx, 0)
                                    if debug == 1:
                                       print("\nDEBUG LN 1245: \nfound: %d \nlinks: %d \nkeep: %d \ndepth: %d \n" % (found, links, keep, depth))
                                 except KeyboardInterrupt:
                                    try:
                                       print("\r\nskipping %s...\n press CTRL + C again to quit.\n" % bx)
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
                                    keep = 0
                                    sys.exit("\r\nrequest cancelled by user.\n")
                                    break
                                 except Exception, e:
                                    print("\r\nan exception has occurred: %s \n" % str(e))
                                    raise
                                    keep = 0
                                    sys.exit(1)
                        else:
                           break
                     found = found - 1
                     links = 1
                  else:
                     subcont = 1
                     geturl = cfurl
                     while subcont is not 0:
                        depth += 1
                        if subcont < 1:
                           break
                        geturl, subcont, parent = selectdir(geturl)
                        if debug == 1:
                           print("\nDEBUG LN 1281: \nfound: %d \nlinks: %d \nkeep: %d \ndepth: %d \n" % (found, links, keep, depth))
                        checksubdir = raw_input("enter 1 to select this directory, 2 to choose a subdirectory, or 3 to go back to parent directory --> ")
                        while not re.match(r'^[1-3]$', checksubdir):
                           checksubdir = raw_input("invalid input. enter a value 1-3 --> ")
                        if checksubdir is not 2:
                           if checksubdir == '3':
                              p = urlparse(geturl)
                              droppath = p.path.split('/')[-1]
                              geturl = getparent(geturl)
                              depth = depth - 1
                           break

                     if geturl in finished:
                        break
                     try:
                        if debug == 1:
                           print("\nDEBUG LN 1297: \nfound: %d \nlinks: %d \nkeep: %d \ndepth: %d \n" % (found, links, keep, depth))
                           print('FOUND: %s \n' % str(found))
                        print('\nrequesting harvested URL: %s \r\n(press CTRL + C to skip) \n' % geturl)
                        getCF(geturl, links)
                        found -= 1
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
                        links = 1
                        keep = 1
                     if debug == 1:
                        print("\nDEBUG LN 1327: \nfin depth: %d \n" % depth)
                        print("fin found: %d \n" % found)

               elif followdirs.lower() == 'y' and depth < 1:
                  for link in findlinks:
                     b = link.get('href')
                     if not re.match(r'^((\.\.)?\/)$', str(b)):
                        bx = parent + b
                        if bx in finished:
                           keep = 0
                           links = 0
                           break
                        print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % bx)
                        try:
                           getCF(bx, links)
                        except KeyboardInterrupt:
                           try:
                              print("\r\nskipping %s... press CTRL + C again to quit.\n" % bx)
                              time.sleep(2)
                              continue
                           except KeyboardInterrupt:
                              keep = 0
                              print("\nprogram aborted by user.\n")
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
                           links = 0
                     else:
                        continue
                     found -= 1
                     if debug == 1:
                        print("\nDEBUG LN 1369: \nfound: %d \nlinks: %d \nkeep: %d \ndepth: %d \n" % (found, links, keep, depth))

               else:
                  for link in findlinks:
                     b = link.get('href')
                     links = 0
                     if debug == 1:
                        print("\nDEBUG LN 1376: \nfound: %d \n" % found)
                     while b:
                        if not re.search(r'^(.*)(\/)$', str(b)):
                           if 'http' not in b[:4]:
                              b = parent + b
                           if b in finished:
                              keep = 0
                              links = 1
                              break
                           try:
                              print("\nrequesting harvested URL: %s \r\n(press CTRL + C to skip)\n" % b)
                              getCF(b, links)
                           except KeyboardInterrupt:
                              print("\r\nskipping %s...\n" % b)
                              try:
                                 print("\r\npress CTRL + C again to exit.\r\n")
                                 time.sleep(2)
                                 continue
                              except KeyboardInterrupt:
                                 keep = 0
                                 print("\r\nprogram aborted by user.\n")
                                 break
                           except (KeyboardInterrupt, SystemExit):
                              sys.exit("\r\nrequest cancelled by user.\n")
                              keep = 0
                              break
                           except Exception, e:
                              print("\r\nan exception has occurred: %s \n" % str(e))
                              raise
                        else:
                           continue
                     found -= 1
                     if debug == 1:
                        print("\nDEBUG LN 1409: \nfound: %d \nlinks: %d \nkeep: %d \ndepth: %d \n" % (found, links, keep, depth))
                  links = 1
                  keep = 0
            else:
               print("\ndid not find any links.\n")
               found = found - 1
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
               print("\n***finished following all links.***\n")
               links = 0
            break

      else:
         if debug == 1:
            print("\nDEBUG LN 1434: \nFOUND/KEEP > 0: \nfound: %d \ndepth: %d \nsetting found to 0 \n" % (found, depth))
         found = 0
         cpath = p.path.strip('/')
         cpaths = cpath.split('/')
         lastpath = cpaths[-1]
         if len(lastpath) < 1 and len(cpaths) > 1:
            lastpath = cpaths[-2]
         cfurl = cfurl.strip('/')
         urlfqdn = urlfqdn.strip('/')
         print(urlfqdn)
         matchtop = r'^(%s)$' % firsturl
         if re.match(matchtop, cfurl) and found == 0 and len(finished) > 0:
            keep = 0
            print("\nfinished following all links.\n")
            sys.exit('\nexiting program.. \n')
         else:
            cfurl = cfurl.rstrip(lastpath)
            if debug == 1:
               print("\nDEBUG LN 1452: \nLINKS: %d \nKEEP: %d \nFOUND: %d \nDEPTH: %d \n" % (links, keep, found, depth))
            depth = 0
            keep = 0

try:
   print('\ntrying %s.. \n' % cfurl)
   if debug == '1':
      print("\nDEBUG LAST TRY 1459: \nLINKS: %d \nKEEP: %d \nFOUND: %d \n" % (links, keep, found))
   if cfurl in finished and cfurl in firsturl: 
      print("\nfinished following all links.\n")
      sys.exit('\nexiting program.. \n')
   getCF(cfurl, links)

except (KeyboardInterrupt, SystemExit):
   print("\r\nrequest cancelled by user\n")
   print("\r\nhit CTRL + C again to exit program, or it will automatically continue in 10 seconds.\n")
   try:
      for i in xrange(10,0,-1):
         time.sleep(1)
         sys.stdout.write("\r%s..\r" % str(i))
         sys.stdout.flush()
      getCF(cfurl, links)
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

print(quittext)
time.sleep(3)
print('\nexiting program.. \n')
sys.exit(0)
