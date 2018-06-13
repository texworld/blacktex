# -*- coding: utf-8 -*-
#
import pytest

import tablify


def test_plain():
    data = """A  1.34  -214.1\nCCCC 55.534 1131.1"""
    ref = """A     1.34  -214.1\nCCCC 55.534 1131.1"""
    assert tablify.tablify(data) == ref
    return
