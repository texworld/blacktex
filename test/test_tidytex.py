# -*- coding: utf-8 -*-
#
import tidytex


def test_comments():
    input_string = """lorem  %some comment  \n %sit amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem\n"""
    return


def test_comment_lines():
    input_string = """% lorem some comment  \n sit amet"""
    out = tidytex.clean(input_string)
    assert out == """ sit amet"""
    return


def test_trailing_whitespace():
    input_string = """lorem    \n sit amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem\n sit amet"""
    return


def test_obsolete_text_mod():
    input_string = """lorem {\\it ipsum dolor} sit amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem \\textit{ipsum dolor} sit amet"""
    return


def test_multiple_spaces():
    input_string = """lorem   ipsum dolor sit  amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem ipsum dolor sit amet"""
    return


def test_multiple_newlines():
    input_string = """lorem  \n\n\n ipsum dolor sit  amet"""
    out = tidytex.clean(input_string)
    assert out == """lorem\n\n ipsum dolor sit amet"""
    return


def test_dollar_dollar():
    input_string = """some statement
$$a + b = c$$
more text"""
    out = tidytex.clean(input_string)
    assert (
        out
        == """some statement
\\[
a + b = c
\\]
more text"""
    )
    return


def test_whitespace_after_curly():
    input_string = """\\textit{ \nlorem  \n\n\n ipsum dolor sit  amet}"""
    out = tidytex.clean(input_string)
    assert out == """\\textit{lorem\n\n ipsum dolor sit amet}"""
    return


def test_exponent_space():
    input_string = "2^ng"
    out = tidytex.clean(input_string)
    assert out == "2^n g"
    return


def test_triple_dots():
    input_string = "a,...,b"
    out = tidytex.clean(input_string)
    assert out == "a,\dots,b"
    return


def test_ldots_cdots():
    input_string = "Some $1,\cdots,n$ or $1,\ldots,n$."
    out = tidytex.clean(input_string)
    assert out == "Some $1,\dots,n$ or $1,\dots,n$."
    return


def test_punctuation_outside_math():
    input_string = "$a+b=c.$"
    out = tidytex.clean(input_string)
    assert out == "$a+b=c$."
    return


def test_whitespace_before_punctuation():
    input_string = "Some text ."
    out = tidytex.clean(input_string)
    assert out == "Some text."
    return


def test_nbsp_before_ref():
    input_string = "Some text \\ref{something}."
    out = tidytex.clean(input_string)
    assert out == "Some text~\\ref{something}."
    return


def test_double_nbsp():
    input_string = "Some~~text."
    out = tidytex.clean(input_string)
    assert out == "Some\quad text."
    return


def test_over_frac():
    input_string = "Some ${2\\over 3^{4+x}}$ equation ${\\pi \\over4}$."
    out = tidytex.clean(input_string)
    assert out == "Some $\\frac{2}{3^{4+x}}$ equation $\\frac{\\pi}{4}$."
    return


def test_linebreak_after_double_backslash():
    input_string = "Some $2\\\\3 4\\\\\n6$."
    out = tidytex.clean(input_string)
    assert out == "Some $2\\\\\n3 4\\\\\n6$."
    return


def test_nbsp_space():
    input_string = "Some ~thing."
    out = tidytex.clean(input_string)
    assert out == "Some thing."
    return


def test_keywords_without_backslash():
    input_string = "maximum and logarithm $max_x log(x)$"
    out = tidytex.clean(input_string)
    assert out == "maximum and logarithm $\\max_x \\log(x)$"
    return
