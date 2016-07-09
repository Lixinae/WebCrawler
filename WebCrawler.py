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

##################################

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



# Retire les doublons d'une liste
def keepUnique(mylist):
    return set(mylist)

treeLinksList = []


# Construit la liste des liens telechargeable
def constructTreeLink(baseLink,depth):
    global treeLinksList
    if depth <= 0:
        return
    if len(treeLinksList) > 200:
        print "Too much links in list -> stoping crawling"
        return
    # fetch all the links on the page
    soup = BeautifulSoup(urllib2.urlopen(baseLink),"html.parser")
    links = soup.findAll("a")
    for link in links[5:]:
        cleanString = link.get('href','/').replace("%20"," ")
        downloadLink = urlparse.urljoin(baseLink,cleanString)        
        tmp = downloadLink[len(downloadLink)-3:]
        if not (tmp == "pdf" or tmp == "odp" or tmp == "txt"):
            constructTreeLink(downloadLink,depth-1)
        else :
            #print downloadLink
            treeLinksList.append(str(downloadLink))
    return treeLinksList

# Telecharge tout ce qui match l'extension "extension dans la liste des fichiers
def download_All_Update(links,folder,extension):
    links = set(links)
    pattern_filename = re.compile('[^/,]+\.'+extension+'$')
    print "Downloading files to folder : "+folder
    for link in links:
        #print link
        name = pattern_filename.search(link)
        if name:
            print name.group(0)
            r = requests.get(link, stream=True)
            with open(folder+"/"+name.group(0),"wb") as f:
                for chunk in r:
                    f.write(chunk)
                    f.flush()
            
# Old version
def download_one_link(link,baseurl,folder,extension):
    patternFolder = re.compile('.+\.'+extension+'$')
    pattern_filename = re.compile('[^/,]+\.'+extension+'$')
    cleanString = link.get('href','/').replace("%20"," ")
    if(patternFolder.match(cleanString)):
        downloadLink = urlparse.urljoin(baseurl,cleanString)
        print downloadLink
        name = pattern_filename.search(downloadLink)
        print name.group(0)
        #pour l'affichage avec bar de progression , propre que en console , pas dans idle
##        r = requests.get(downloadLink, stream=True)
##        with open(folder+"/"+name.group(0),"wb") as f:
##            total_length = int(r.headers.get('content-length'))
##            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
##                if chunk:
##                    f.write(chunk)
##                    f.flush()

        # Version sans la barre            
        r = requests.get(downloadLink, stream=True)
        with open(folder+"/"+name.group(0),"wb") as f:
            for chunk in r:
                f.write(chunk)
                f.flush()

def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)

def download_all_in_url(baseurl,folder,extension):
    create_folder(folder)
    soup = BeautifulSoup(urllib2.urlopen(baseurl),"html.parser")
    links=soup.findAll("a")
    print "Downloading files to folder : "+folder
    for link in links[5:]:
        # For each link , clean the string and then download the content        
        download_one_link(link, baseurl,folder,extension)


def download_all_in_multipleUrl(baseurl,folder,extension,depth):
    constructTreeLink(baseurl,depth)
    for link in links:
        download_all_in_url(link,folder,extension)
    

if __name__ == '__main__':
    baseurl = ""
    while baseurl == "":
        baseurl = raw_input("Enter the URL : ")
    directory = ""
    while directory == "":
        directory = raw_input("Where would you want to save the files ? : ")
    extension = ""
    while extension == "":
        extension = raw_input("Which type of files do you want ?( extensions , like pdf ,txt...whatever) : ")
    depth = -1
    while (depth < 0 or not depth.isdigit()):
        depth = raw_input("Enter the depth you want to crawl too : ")

    create_folder(directory)
    t = constructTreeLink(baseurl,int(depth))
    download_All_Update(t,directory,extension)
    #download_all_in_url(baseurl,directory,extension)
    

#baseurl = "http://www-igm.univ-mlv.fr/~vnozick/teaching/slides/M1_ti/"            
#folder = "./download/TraitementImage"
#extension = "pdf"
#download_all_in_url(baseurl,folder,extension)

