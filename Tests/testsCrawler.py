import os

import pytest

from WebCrawlerUpdate import create_folder, keepUniqueOrdered


@pytest.mark.crazy
def test_keep_unique_ordered():
    test_list = [0, 1, 4, 5, 4, 7, 6, 5, 4, 3, 2, 1]
    expected_list = [0, 1, 4, 5, 7, 6, 3, 2]
    assert expected_list == keepUniqueOrdered(test_list)


@pytest.mark.crazy
def test_security_check():
    # securityCheck(link,depth,dictLinks,domain) -> bool
    pass


@pytest.mark.crazy
def test_create_folder():
    name = "test"
    create_folder(name)
    assert os.path.exists(name)


@pytest.mark.crazy
def test_ask_end():
    # ask_end() -> bool
    pass
