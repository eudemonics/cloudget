#!/usr/bin/env python
# cloudget v0.1
# author: vvn < lost @ nobody . ninja >

import sys, getopt, subprocess, os
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

global cfurl
global usecurl
global writeout
global curldl
usecurl = 0
writeout = 0

try:
   opts, args = getopt.getopt(sys.argv[1:],"hu:oc",["help","url=","out","curl"])
   
except getopt.GetoptError:
   print('cloudget.py [-c] [-o] -u <url> \n')
   print('-c, --curl: use cURL')
   print('-o, --out: save output')
   print('-u, --url <url>: cloudflare URL to get [REQUIRED]')
   sys.exit(2)

for opt, arg in opts:
   if opt in ("-h", "--help"):
      print('cloudget.py [-c] [-o] -u <url> \n')
      print('-c, --curl: use cURL without downloading')
      print('-o, --out: save output')
      print('-u, --url <url>: cloudflare URL to get [REQUIRED]')
      sys.exit()
   elif opt in ("-o", "--out"):
      writeout = 1
   elif opt in ("-u", "--url"):
      cfurl = arg
   elif opt in ("-c", "--curl"):
      usecurl = 1

checkcurl = ''

if usecurl == 1:
   checkcurl = 'yes'
else:
   checkcurl = 'no'
print("using curl: %s \n" % checkcurl)

if writeout == 1:
   global outfile
   outfile = cfurl.split('/')[-1]
   print("output file: %s \n" % outfile)

print("creating new session..\n")
scraper = cfscrape.create_scraper() # returns a requests.Session object

try:
   if usecurl == 1 and writeout == 1:
      r = scraper.get(cfurl, stream=True)
      print("status: ")
      print(r.status_code)
      print("\nheaders: ")
      print(r.headers)
      print("\nfetching cookies for %s.. \n" % cfurl)
      cookie_arg = cfscrape.get_cookie_string(cfurl)
      print("trying to download using cURL to %s.. \n" % outfile)
      command_text = 'curl -# --no-keepalive -L --cookie ' + cookie_arg + ' -O ' + cfurl
      output = Popen(command_text, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
      response, errors = output.communicate()
      print("response: " + str(response))
      print("errors: " + str(errors))
   
   elif usecurl == 1 and writeout == 0:
      print("status: ")
      print(scraper.get(cfurl).status_code)
      print("\nheaders: ")
      print(scraper.get(cfurl).headers)
      print("getting cookies for url: %s \n" % cfurl)
      cookie_arg = cfscrape.get_cookie_string(cfurl)
      print(cookie_arg)
      print("checking cURL output...\n")
      result = subprocess.check_output(["curl", "--cookie", cookie_arg, "-L", "--no-keepalive", cfurl])
      print(result)
   
   elif usecurl == 0 and writeout == 1:
      print("getting %s... \n" % cfurl)
      r = scraper.get(cfurl, stream=True)
      print("status: ")
      print(r.status_code)
      print("\nheaders: ")
      print(r.headers)
      if not os.path.exists('download'):
         os.makedirs('download')
      savefile = os.path.join('download', outfile)
      print("\nsaving content to %s \n" % savefile)

      with open(savefile, 'wb+') as dlfile:
         for chunk in r.iter_content(chunk_size=4096):
            if chunk:
               dlfile.write(chunk)
               dlfile.flush()
               os.fsync(dlfile.fileno())
         dlfile.close()
      print("file saved! \n")
      
   else:
      print("getting %s... \n" % cfurl)
      print(scraper.get(cfurl).content)

except Exception, e:
   print("an error has occurred: %s \n" % str(e))
   sys.exit(1)

finally:   
   print("exiting.. \n")
   sys.exit(0)

sys.exit()
