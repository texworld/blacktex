# -*- coding: utf-8 -*-
#
import tidytex


def test_plain():
    input_string = """lorem {\\it ipsum dolor} sit amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem \\itshape{ipsum dolor} sit amet"""
    return
