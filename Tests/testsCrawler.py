#import pytest
import os

from WebCrawlerUpdate import createFolder,keepUniqueOrdered

def test_keepUniqueOrdered():
    testList = [0,1,4,5,4,7,6,5,4,3,2,1]
    expectedList = [0,1,4,5,7,6,3,2]
    assert expectedList == keepUniqueOrdered(testList)

def test_security_check():
    #securityCheck(link,depth,dictLinks,domain) -> bool
    pass

def test_createFolder():
    name = "test"
    createFolder(name)
    assert os.path.exists(name)   

def test_askEnd():
    # askEnd() -> bool
    pass

