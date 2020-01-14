# -*- coding: cp1252 -*-
#!/usr/bin/python

import sys
import os
import re
import requests

try:
    import bs4
    print ("BeautifulSoup4 is there, starting program")
except ImportError:
    print ("BeautifulSoup4 not installed, please install before using the script")
    print ("Instructions in README file")
    print ("Leaving program")
    sys.exit(1)

from typing import Dict, List

# Compatibility between python 2 and 3
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse


# Evite les erreurs de unicode
# Bug parfois
#FromRaw = lambda r: r if isinstance(r, unicode) else r.decode('utf-8', 'ignore')

# Keeps the distinct elements in a list, in the same order as the start
def keepUniqueOrdered(myList):
    return [x for i,x in enumerate(myList) if x not in myList[:i]]

# Security checks for the link provided
def securityCheck(link,depth,dictLinks,domain) -> bool:
    # Checks the depth we are at
    if depth <= 0:
        return False
    # Checks if there is to much links in the dictionnary
    if len(dictLinks) > 10000:
        print ("Too much links in list -> stoping crawling")
        return False
    # Checks if the provided link is correct
    if not linkCheck(link):
        return False
    # Checks if the link is in the base domain
    if not hasDomain(link,domain):
        return False
    # Checks if the link is already in the dictionnary and if has been visited
    if link in dictLinks:
        if dictLinks[link]:
            return False
    return True

# Constructs the links dictionnary
def constructTreeLink(baseLink,depth,dictLinks,domain) -> Dict[str,bool]:
    if not securityCheck(baseLink,depth,dictLinks,domain):
        return
    try :
        page = urllib2.urlopen(baseLink)
    except Exception :
	    print("Could not open link :" + baseLink)
	    return
    # Tels if we already visited the link
    # Plus logique ici que dans la boucle
    dictLinks[baseLink] = True

    read = page.read()
    #read = FromRaw(read)
    soup = bs4.BeautifulSoup(read,"html.parser")
    linksA = soup.findAll("a")
    for linkA in linksA:
        cleanString = linkA.get('href','/').replace("%20"," ")
        downloadLink = urlparse.urljoin(baseLink,cleanString)
        # Checks if we do not go back in the website
        if not len(downloadLink) < len(baseLink):
            # Avoid strange links
            if "?" not in downloadLink:
                if downloadLink not in dictLinks:
                    downloadLink = re.sub(r"[\t\n]","",downloadLink)
                    # Add the link to the dictionnary, indicating it's not yet visited
                    dictLinks[downloadLink] = False
                    print (downloadLink)
                constructTreeLink(downloadLink,depth-1,dictLinks,domain)
                # Tels if we already visited the link
                # dictLinks[downloadLink] = True
    return dictLinks

# Constructs the links dictionnary
def constructTreeLinkNoRecursive(baseLink,depth,dictLinks,domain):
	pass
	# Todo -> Find a way to make it iterative

    #return dictLinks

# Downloads only the files with the specific file extensions
def downloadAllSpecific(links,extensions):
    folder = "default"
    for extension in extensions:
        patternFilename = re.compile('[^/,]+\.'+extension+'$')
        for link in links:
            # Todo -> Factoriser le code, code dupliqué ligne 129
            name = patternFilename.search(link)
            if name:
                m = re.search("http:\/\/(.*\/)",link)
                if m:
                    folder = m.group(1)
                createFolder(folder)
                print (link)
                r = requests.get(link, stream=True)
                with open(folder+"/"+name.group(0),"wb") as f:
                    for chunk in r:
                        f.write(chunk)
                        f.flush()

# Downloads everything in the links provided
def downloadAll(links):
    patternFilename = re.compile('(\w+)(\.\w+)+(?!.*(\w+)(\.\w+)+)$')
    folder = "default"    
    for link in links:
        name = link.split('/').pop()
        # Todo -> Factoriser le code, code dupliqué ligne 109
        if patternFilename.search(name):
            m = re.search("http:\/\/(.*\/)",link)
            if m:
                folder = m.group(1)
            createFolder(folder)                
            print (link)
            r = requests.get(link, stream=True)
            with open(folder+"/"+name,"wb") as f:
                for chunk in r:
                    f.write(chunk)
                    f.flush()

# If a folder doesn't exist, it's created
def createFolder(name):
    if not os.path.exists(name):
        print ("Creating folder "+name)
        os.makedirs(name)

# Verify if the given url is in the start domain
def hasDomain(url,domain) -> bool:
    return urlparse.urlparse(url).hostname in domain
    
# Tests if the link provided is a correct url
# Regexp made by @dperini ported by @adamrofer on github
def linkCheck(link) -> bool:
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

#Asks the user the base url he wants
def askUrl() -> str:
    baseurl = ""
    while baseurl == "" or not linkCheck(baseurl):
        baseurl = input("Enter the URL : ")
        if "http://" not in baseurl and "https://" not in baseurl :
            baseurl = "http://"+baseurl
    return baseurl

#Asks the user if he wants files with specific extensions or everything
def askSpecific() -> List[str]:
    specificFiles = ""
    extensions = []
    endAddExt = ""
    while (specificFiles != "y" and specificFiles != "n"):
        specificFiles = input("Enter :\ny -> if you wish to download files with specific extensions\nn -> download all files in the link\n")
        if specificFiles == "y":
            #If he wants specific file extensions, we ask for them
            while True:
                endAddExt = input("Enter :\nA file extension you want to download(pdf,odp...whatever you want)\n/end -> Stop asking for extensions\n")
                if endAddExt == "/end":
                   break;
                else :
                   if len(endAddExt) == 3:
                       extensions.append(endAddExt)
                   else :
                       print ("File extensions must be only 3 caracters\n")
            print ("You asked for these extensions:")
            print (" | ".join(extensions))
            if extensions == []:
                print ("List of extensions empty, switching to non specific mod")
            break
        elif specificFiles == "n":
            break
    return extensions

#Asks the user for the maximum depth he wants to crawl too
def askDepth() -> int:
    depth = ""
    while not depth.isdigit():
        depth = input("Enter the depth you wish to attain, it must be strictly superior to 0 : ")
        if int(depth) > 0:
            break
    return int(depth)

#Asks the user if he wants to restart on another url or stop the program
def askEnd() -> bool:
    end = ""
    while (end !="y" and end !="n"):
        end = input("Do you wish to restart on another URL ? y/n\n")
        if end == "y":
            return True              
        elif end == "n":
            return False

#Asks the user if he wants to start the crawling
def askStart() -> bool:
    wantStart = ""
    while (wantStart !="y" and wantStart !="n" and wantStart !="r"):
        wantStart = input("Enter :\ny -> Start the crawler\nr -> Restart the program\nn -> Exit the program\n")
        if wantStart == "n":
            print ("Leaving program")
            sys.exit(0)
        elif wantStart == "r":
            print ("Restarting program")
    return wantStart == "y"

# Main of the program
if __name__ == '__main__':

    dictLinks = {}
    domain = ""
    while True:
        while True:
            baseurl = askUrl()
            domain = baseurl.split("/")[2]
            extensions = askSpecific()
            depth = askDepth()
            if askStart():
                break
            else :
                continue
        print ("######## Crawling START ##########" )      
        dictLinksList = constructTreeLink(baseurl,int(depth),dictLinks,domain)
        print ("######## Crawling END   ##########")
        dictLinksList = keepUniqueOrdered(list(dictLinksList))
        print ("######## Download START ########## ")
        if extensions:
            downloadAllSpecific(dictLinksList,extensions)
        else :
            downloadAll(dictLinksList);
        print ("######## Download END   ########## ")
        if askEnd():
            dictLinks = {}
        else:
            print ("Leaving program\n")
            sys.exit(0)    
        
