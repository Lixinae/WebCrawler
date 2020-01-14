import pytest
import os

from WebCrawlerUpdate import createFolder,keepUniqueOrdered

@pytest.mark.crazy
def test_keepUniqueOrdered():
    testList = [0,1,4,5,4,7,6,5,4,3,2,1]
    expectedList = [0,1,4,5,7,6,3,2]
    assert expectedList == keepUniqueOrdered(testList)

@pytest.mark.crazy
def test_security_check():
    #securityCheck(link,depth,dictLinks,domain) -> bool
    pass

@pytest.mark.crazy
def test_createFolder():
    name = "test"
    createFolder(name)
    assert os.path.exists(name)   

@pytest.mark.crazy
def test_askEnd():
    # askEnd() -> bool
    pass

