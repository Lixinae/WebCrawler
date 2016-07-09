# -*- coding: cp1252 -*-
#!/usr/bin/python
"""
(Windows)
How to Install pip:

    Download https://raw.github.com/pypa/pip/master/contrib/get-pip.py.
    Remember to save it as "get-pip.py"

    Now go to the download folder. Right click on get-pip.py then open with python.exe.

    You can add system variable by
    (by doing this you can use pip and easy_install without specifying path)

    1 Clicking on Properties of My Computer
    2 Then chose Advanced System Settings
    3 Click on Advanced Tab
    4 Click on Environment Variables
    5 From System Variables >>> select variable path.
    6 Click edit then add the following lines at the end of it
     ;c:\Python27;c:\Python27\Scripts
    (please dont copy this, just go to your python directory and copy the paths similar to this)
    NB:- you have to do this once only.


Requires BeautifulSoup
    Install :
		pip install beautifulsoup4

"""

from bs4 import BeautifulSoup

import urllib 
import urllib2
import urlparse
import os
import re
import requests
import sys
import time


dictLinks = {}

# Retire les doublons d'une liste
def keepUnique(mylist):
    return list(set(mylist))

#Evite les erreurs de unicode
FromRaw = lambda r: r if isinstance(r, unicode) else r.decode('utf-8', 'ignore')


# Construit la liste des liens telechargeable
def constructTreeLink(baseLink,depth):
    global dictLinks
    if depth <= 0:
        return
    if len(dictLinks) > 1000:
        print "Too much links in list -> stoping crawling"
        return
    if not has_domain(baseLink):
        #print "Url : "+baseLink+" not in domain"
        return 
    if baseLink in dictLinks:
        #print "Link "+baseLink +" already visited"
        if dictLinks[baseLink]:
            return
        else :
            print baseLink
    if not linkCheck(baseLink):
        return
    try :
        page = urllib2.urlopen(baseLink)        
    except Exception,e :
        return
    read = page.read()
    read = FromRaw(read)
    soup = BeautifulSoup(read,"html.parser")
    links = soup.findAll("a")
    for link in links:
        cleanString = link.get('href','/').replace("%20"," ")
        downloadLink = urlparse.urljoin(baseLink,cleanString)
        #tmp = downloadLink[len(downloadLink)-3:]
        if downloadLink not in dictLinks:
            downloadLink = re.sub(r"[\t\n]","",downloadLink)
            #print downloadLink
            dictLinks[downloadLink] = False
        constructTreeLink(downloadLink,depth-1)
        dictLinks[downloadLink] = True
                
##        if not (tmp == "pdf" or tmp == "odp" or tmp == "txt" or tmp == "zip"):
##            constructTreeLink(downloadLink,depth-1)
##        else :
##            if downloadLink not in dictLinks:
##                downloadLink = re.sub(r"[\t\n]","",downloadLink)
##                #print downloadLink
##                dictLinks[downloadLink] = True
    return dictLinks


# Telecharge tout ce qui match l'extension "extension dans la liste des fichiers
def download_All_Update(links,extension):
    links = set(links)
    pattern_filename = re.compile('[^/,]+\.'+extension+'$')
    folder = "default"
    print "######## Download START ########## "
    for link in links:
        name = pattern_filename.search(link)
        if name:
            m = re.search("http:\/\/(.*\/)",link)
            if m:
                folder = m.group(1)
            create_folder(folder)                
            print link
            r = requests.get(link, stream=True)
            with open(folder+"/"+name.group(0),"wb") as f:
                for chunk in r:
                    f.write(chunk)
                    f.flush()
    print "######## Download END   ########## "


def create_folder(name):
    if not os.path.exists(name):
        print "Creating folder "+name                  
        os.makedirs(name)

domain = ""

# Verify if the given url is in the start domain
def has_domain(url):
    p = urlparse.urlparse(url)
    if p.hostname in domain:
        return True
    else:
        return False
    
# Tests if the link provided is a correct url
# Regexp made by @dperini ported by @adamrofer on github
def linkCheck(link):
    return re.search(re.compile(
    u"^"
    # protocol identifier
    u"(?:(?:https?|ftp)://)"
    # user:pass authentication
    u"(?:\S+(?::\S*)?@)?"
    u"(?:"
    # IP address exclusion
    # private & local networks
    u"(?!(?:10|127)(?:\.\d{1,3}){3})"
    u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    u"|"
    # host name
    u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
    # domain name
    u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
    # TLD identifier
    u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
    u")"
    # port number
    u"(?::\d{2,5})?"
    # resource path
    u"(?:/\S*)?"
    u"$"
    , re.UNICODE),link)


if __name__ == '__main__':
    while True:
        global domain
        global dictLinks
        start = False
        while not start:
            baseurl = ""
            while baseurl == "" or not linkCheck(baseurl):
                baseurl = raw_input("Enter the URL : ")
                if "http://" not in baseurl and "https://" not in baseurl :
                    baseurl = "http://"+baseurl
                    
            extension = ""
            while extension == "":
                extension = raw_input("Which type of files do you want ?( extensions , like pdf ,txt...whatever) : ")
                
            depth = -1
            while (depth < 0 or not depth.isdigit()):
                depth = raw_input("Enter the depth you want to crawl too : ")
            domain = baseurl.split("/")[2]
            print "Domain name is "+domain
            wantStart = ""
            while (wantStart !="y" and wantStart !="n" and wantStart !="r"):
                wantStart = raw_input("Enter :\ny -> if you wish to start the crawler\nr -> to restart the program\nn -> Exit the program\n")
                if wantStart == "y":
                    start = True
                elif wantStart == "n":
                    print "Leaving program"
                    sys.exit(0)
                elif wantStart == "r":
                    break
                    continue
        print "######## Crawling START ##########"       
        t = constructTreeLink(baseurl,int(depth))
        print "######## Crawling END   ##########"
        download_All_Update(t,extension)
        end = ""
        while (end !="y" and end !="n"):
            end = raw_input("Do you wish to restart on another url ? y/n\n")
            if end == "y":
                dictLinks = {}
                break                
                continue
            elif end == "n":
                print "Leaving program\n"
                sys.exit(0)
    


