# -*- coding: cp1252 -*-
#!/usr/bin/python


import bs4
import urllib 
import os
import re
import requests
import sys
import time

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
def securityCheck(baseLink,depth,dictLinks,domain):
    # Checks the depth we are at
    if depth <= 0:
        return False
    # Checks if there is to much links in the dictionnary
    if len(dictLinks) > 10000:
        print ("Too much links in list -> stoping crawling")
        return False
    # Checks if the provided link is correct
    if not linkCheck(baseLink):
        return False
    # Checks if the link is in the base domain
    if not has_domain(baseLink,domain):
        return False
    # Checks if the link is already in the dictionnary and if has been visited
    if baseLink in dictLinks:
        if dictLinks[baseLink]:
            return False
    return True

# Constructs the links dictionnary
def constructTreeLink(baseLink,depth,dictLinks,domain):
    if not securityCheck(baseLink,depth,dictLinks,domain):
        return
    try :
        page = urllib2.urlopen(baseLink)        
    except Exception :
        return
    read = page.read()
    #read = FromRaw(read)
    soup = bs4.BeautifulSoup(read,"html.parser")
    links = soup.findAll("a")
    for link in links:
        cleanString = link.get('href','/').replace("%20"," ")
        downloadLink = urlparse.urljoin(baseLink,cleanString)
        # Checks if we do not go back in the website
        if not len(downloadLink) < len(baseLink):
            # Avoid strange links
            if not "?" in downloadLink:
                if downloadLink not in dictLinks:
                    downloadLink = re.sub(r"[\t\n]","",downloadLink)
                    dictLinks[downloadLink] = False
                    print (downloadLink)
                constructTreeLink(downloadLink,depth-1)
                dictLinks[downloadLink] = True
    return dictLinks

# Constructs the links dictionnary
def constructTreeLinkNoRecursive(baseLink,depth,dictLinks,domain):
	


    if not securityCheck(baseLink,depth,dictLinks,domain):
        return
    try :
        page = urllib2.urlopen(baseLink)        
    except Exception :
        return
    read = page.read()
    #read = FromRaw(read)
    soup = bs4.BeautifulSoup(read,"html.parser")
    links = soup.findAll("a")
    for link in links:
        cleanString = link.get('href','/').replace("%20"," ")
        downloadLink = urlparse.urljoin(baseLink,cleanString)
        # Checks if we do not go back in the website
        if not len(downloadLink) < len(baseLink):
            # Avoid strange links
            if not "?" in downloadLink:
                if downloadLink not in dictLinks:
                    downloadLink = re.sub(r"[\t\n]","",downloadLink)
                    dictLinks[downloadLink] = False
                    print (downloadLink)
                constructTreeLink(downloadLink,depth-1)
                dictLinks[downloadLink] = True
    return dictLinks

# Downloads only the files with the specific file extensions 
def download_All_Specific(links,extensions):
    folder = "default"
    for extension in extensions:    
        pattern_filename = re.compile('[^/,]+\.'+extension+'$')
        for link in links:
            name = pattern_filename.search(link)
            if name:
                m = re.search("http:\/\/(.*\/)",link)
                if m:
                    folder = m.group(1)
                create_folder(folder)                
                print (link)
                r = requests.get(link, stream=True)
                with open(folder+"/"+name.group(0),"wb") as f:
                    for chunk in r:
                        f.write(chunk)
                        f.flush()


# Downloads everything in the links provided
def download_All(links):
    pattern_filename = re.compile('(\w+)(\.\w+)+(?!.*(\w+)(\.\w+)+)$')
    folder = "default"    
    for link in links:
        name = link.split('/').pop()
        if pattern_filename.search(name):
            m = re.search("http:\/\/(.*\/)",link)
            if m:
                folder = m.group(1)
            create_folder(folder)                
            print (link)
            r = requests.get(link, stream=True)
            with open(folder+"/"+name,"wb") as f:
                for chunk in r:
                    f.write(chunk)
                    f.flush()


# If a folder doesn't exist, it's created
def create_folder(name):
    if not os.path.exists(name):
        print ("Creating folder "+name)                  
        os.makedirs(name)


# Verify if the given url is in the start domain
def has_domain(url,domain):
    return urlparse.urlparse(url).hostname in domain
    
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

#Asks the user the base url he wants
def askUrl():
    baseurl = ""
    while baseurl == "" or not linkCheck(baseurl):
        baseurl = input("Enter the URL : ")
        if "http://" not in baseurl and "https://" not in baseurl :
            baseurl = "http://"+baseurl
    return baseurl

#Asks the user if he wants files with specific extensions or everything  
def askSpecific():
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
def askDepth():
    depth = ""
    while True:
        depth = input("Enter the depth you wish to attain : ")
        if not depth.isdigit():
            continue
        if int(depth) > 0:
            break
    return int(depth)

#Asks the user if he wants to restart on another url or stop the program
def askEnd(dictLinks):
    end = ""
    while (end !="y" and end !="n"):
        end = input("Do you wish to restart on another URL ? y/n\n")
        if end == "y":
            dictLinks = {}
            return True              
        elif end == "n":
            print ("Leaving program\n")
            sys.exit(0)

#Asks the user if he wants to start the crawling        
def askStart():
    wantStart = ""
    while (wantStart !="y" and wantStart !="n" and wantStart !="r"):
        wantStart = input("Enter :\ny -> Start the crawler\nr -> Restart the program\nn -> Exit the program\n")
        if wantStart == "n":
            print ("Leaving program")
            sys.exit(0)
        elif wantStart == "r":
            print ("Restarting program")
    return wantStart == "y"


if __name__ == '__main__':
    try:
        import bs4
        print ("BeautifulSoup4 is there, starting program")
    except ImportError:
        print ("BeautifulSoup4 not installed, please install before using the script")
        print ("Instructions in README file")
        print ("Leaving program")
        sys.exit(1)

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
        t = constructTreeLink(baseurl,int(depth),dictLinks,domain)
        print ("######## Crawling END   ##########")
        t = keepUniqueOrdered(list(t))
        print ("######## Download START ########## ")
        if extensions:
            download_All_Specific(t,extensions)
        else :
            download_All(t);
        print ("######## Download END   ########## ")
        if askEnd(dictLinks):
            continue
        
