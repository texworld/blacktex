# -*- coding: utf-8 -*-
#
import tidytex


def test_itshape():
    input_string = """lorem {\\it ipsum dolor} sit amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem \\itshape{ipsum dolor} sit amet"""
    return


def test_multiple_spaces():
    input_string = """lorem   ipsum dolor sit  amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem ipsum dolor sit amet"""
    return


def test_dollar_dollar():
    input_string = """some statement
$$a + b = c$$
more text"""
    out = tidytex.clean(input_string)
    assert out == """some statement
\\[
a + b = c
\\]
more text"""
    return
