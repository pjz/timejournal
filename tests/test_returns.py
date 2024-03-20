import re
from itertools import pairwise

import pytest

from timejournal.cli import headers_and_match


test_md = """
# 1
    ## 11
        ### 111
        ### 112
        ### 113
        ### 114
    ## 12
        ### 121
        ### 122
        ### 123
        ### 124
    ## 13
        ### 131
        ### 132
        ### 133
        ### 134
    ## 14
        ### 141
        ### 142
        ### 143
        ### 144
"""


def assert_test_md_headers_result_valid(headers: list[str]):
    for hpre, h in pairwise(headers):
        assert h[:-1] == hpre


def test_headers_and_match():
    KW = 'foo'
    kwpat = re.compile(KW)
    tmd = test_md.splitlines()
    for i in range(len(tmd) + 2):
        one_tmd = list(tmd)
        one_tmd[:i] = [KW]
        test_text = '\n'.join(one_tmd)
        print(f"{test_text=}")
        result = headers_and_match(test_text, kwpat)
        assert result
        assert result[-1] == KW
        headers = [h.strip() for h in result[:-1]]
        assert_test_md_headers_result_valid(headers)



