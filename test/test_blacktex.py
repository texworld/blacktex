# -*- coding: utf-8 -*-
#
import pytest

import blacktex


def test_comments():
    input_string = "lorem  %some comment  \n %sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem"
    return


def test_comment_lines():
    input_string = "% lorem some comment  \n sit amet"
    out = blacktex.clean(input_string)
    assert out == " sit amet"
    return


def test_multiple_comment_lines():
    input_string = "A\n%\n%\nB"
    out = blacktex.clean(input_string)
    assert out == "A\nB"
    return


def test_trailing_whitespace():
    input_string = "lorem    \n sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem\n sit amet"
    return


def test_obsolete_text_mod():
    input_string = "lorem {\\it ipsum dolor} sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem \\textit{ipsum dolor} sit amet"
    return


def test_multiple_spaces():
    input_string = "lorem   ipsum dolor sit  amet"
    out = blacktex.clean(input_string)
    assert out == "lorem ipsum dolor sit amet"

    # It's allowed as indentation at the beginning of lines
    input_string = "a\n    b\nc"
    out = blacktex.clean(input_string)
    assert out == "a\n    b\nc"

    input_string = "\\[\n  S(T)\leq S(P_n).\n\\]\n"
    out = blacktex.clean(input_string)
    assert out == "\\[\n  S(T)\leq S(P_n).\n\\]\n"
    return


def test_spaces_with_brackets():
    input_string = "( 1+2 ) { 3+4 } \\left( 5+6 \\right)"
    out = blacktex.clean(input_string)
    assert out == "(1+2) {3+4} \\left(5+6\\right)"
    return


def test_multiple_newlines():
    input_string = "lorem  \n\n\n\n ipsum dolor sit  amet"
    out = blacktex.clean(input_string)
    assert out == "lorem\n\n\n ipsum dolor sit amet"
    return


def test_dollar_dollar():
    input_string = "a $$a + b = c$$ b"
    out = blacktex.clean(input_string)
    print(repr(input_string))
    print(repr(out))
    assert out == "a\n\\[\na + b = c\n\\]\nb"
    return


def test_whitespace_after_curly():
    input_string = "\\textit{ \nlorem  \n\n\n ipsum dolor sit  amet}"
    out = blacktex.clean(input_string)
    assert out == "\\textit{lorem\n\n\n ipsum dolor sit amet}"
    return


def test_exponent_space():
    input_string = "2^ng"
    out = blacktex.clean(input_string)
    assert out == "2^n g"

    input_string = "$1/n^3$."
    out = blacktex.clean(input_string)
    assert out == "$1/n^3$."

    input_string = "${n^3}$."
    out = blacktex.clean(input_string)
    assert out == "${n^3}$."

    input_string = "n^\\alpha"
    out = blacktex.clean(input_string)
    assert out == "n^\\alpha"
    return


def test_triple_dots():
    input_string = "a,...,b"
    out = blacktex.clean(input_string)
    assert out == "a,\dots,b"
    return


def test_punctuation_outside_math():
    input_string = "$a+b=c.$"
    out = blacktex.clean(input_string)
    assert out == "$a+b=c$."
    return


def test_whitespace_before_punctuation():
    input_string = "Some text ."
    out = blacktex.clean(input_string)
    assert out == "Some text."
    return


def test_nbsp_before_ref():
    input_string = "Some text \\ref{something}."
    out = blacktex.clean(input_string)
    assert out == "Some text~\\ref{something}."
    return


def test_double_nbsp():
    input_string = "Some~~text."
    out = blacktex.clean(input_string)
    assert out == "Some\quad text."
    return


def test_over_frac():
    input_string = "Some ${2\\over 3^{4+x}}$ equation ${\\pi \\over4}$."
    out = blacktex.clean(input_string)
    assert out == "Some $\\frac{2}{3^{4+x}}$ equation $\\frac{\\pi}{4}$."
    return


def test_over_frac_warn():
    input_string = "Some $2\\over 3^{4+x}$."
    with pytest.warns(UserWarning):
        out = blacktex.clean(input_string)
    assert out == "Some $2\\over 3^{4+x}$."
    return


def test_linebreak_after_double_backslash():
    input_string = "Some $2\\\\3 4\\\\\n6$."
    out = blacktex.clean(input_string)
    assert out == "Some $2\\\\\n3 4\\\\\n6$."
    return


def test_nbsp_space():
    input_string = "Some ~thing."
    out = blacktex.clean(input_string)
    assert out == "Some thing."
    return


def test_keywords_without_backslash():
    input_string = "maximum and logarithm $max_x log(x)$"
    out = blacktex.clean(input_string)
    assert out == "maximum and logarithm $\\max_x \\log(x)$"
    return


def test_curly_around_round_with_exponent():
    input_string = "$(a+b)^n \\left(a+b\\right)^{n+1}$"
    out = blacktex.clean(input_string)
    assert out == "${(a+b)}^n {\\left(a+b\\right)}^{n+1}$"
    return


def test_def_newcommand():
    input_string = "\\def\\e{\\text{r}}"
    out = blacktex.clean(input_string)
    assert out == "\\newcommand{\\e}{\\text{r}}"
    return


def test_linebreak_around_begin_end():
    input_string = (
        "A\\begin{equation}a+b=c\\end{equation} B \n\\begin{a}\nd+e+f\n\\end{a}\nB"
    )
    out = blacktex.clean(input_string)
    ref = "A\n\\begin{equation}\na+b=c\n\\end{equation}\nB\n\\begin{a}\nd+e+f\n\\end{a}\nB"
    assert out == ref

    # indentation is okay
    input_string = "A\n  \\begin{equation}\n  a+b=c\n  \\end{equation}"
    out = blacktex.clean(input_string)
    assert out == "A\n  \\begin{equation}\n  a+b=c\n  \\end{equation}"
    return


def test_centerline():
    input_string = "\\centerline{foobar}"
    out = blacktex.clean(input_string)
    assert out == "{\\centering foobar}"
    return


def test_eqnarray_align():
    input_string = "A\\begin{eqnarray*}a+b\\end{eqnarray*}F"
    out = blacktex.clean(input_string)
    assert out == "A\n\\begin{align*}\na+b\n\\end{align*}\nF"
    return


def test_env_label():
    input_string = "A\n\\begin{lemma}\n\\label{lvalpp}"
    out = blacktex.clean(input_string)
    assert out == "A\n\\begin{lemma}\\label{lvalpp}\n"
    return


def test_coloneqq():
    input_string = "A:=b+c"
    out = blacktex.clean(input_string)
    assert out == "A\\coloneqq b+c"
    return


def test_tabular_column_spec():
    input_string = "\\begin{tabular} \n {ccc}"
    out = blacktex.clean(input_string)
    assert out == "\\begin{tabular}{ccc}\n"
    return
