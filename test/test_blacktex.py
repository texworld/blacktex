import pytest

import blacktex


def test_readme():
    input_string = (
        "Because   of $$a+b=c$$ ({\\it Pythogoras}),\n"
        "% @johnny remember to insert name,\n"
        "and $y=2^ng$ with $n=1,...,10$, we have ${\\Gamma \\over 2}=8.$"
    )

    out = blacktex.clean(input_string)
    assert out == (
        "Because of\n"
        "\\[\n"
        "a+b = c\n"
        "\\]\n"
        "(\\textit{Pythogoras}),\n"
        "and $y = 2^n g$ with $n = 1,\\dots,10$, we have $\\frac{\\Gamma}{2} = 8$."
    )


def test_text_mods():
    input_string = "{\\em it's me!}"
    out = blacktex.clean(input_string)
    assert out == "\\emph{it's me!}"


def test_comments():
    input_string = "lorem  %some comment  \n %sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem"

    input_string = "% lorem some comment  \n sit amet"
    out = blacktex.clean(input_string)
    assert out == " sit amet"

    input_string = "A % lorem some comment  \n sit amet"
    out = blacktex.clean(input_string)
    assert out == "A\n sit amet"


def test_multiple_comment_lines():
    input_string = "A\n%\n%\nB"
    out = blacktex.clean(input_string)
    assert out == "A\nB"


def test_trailing_whitespace():
    input_string = "lorem    \n sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem\n sit amet"


def test_obsolete_text_mod():
    input_string = "lorem {\\it ipsum dolor} sit amet"
    out = blacktex.clean(input_string)
    assert out == "lorem \\textit{ipsum dolor} sit amet"


def test_multiple_spaces():
    input_string = "lorem   ipsum dolor sit  amet"
    out = blacktex.clean(input_string)
    assert out == "lorem ipsum dolor sit amet"

    # It's allowed as indentation at the beginning of lines
    input_string = "a\n    b\nc"
    out = blacktex.clean(input_string)
    assert out == "a\n    b\nc"

    input_string = "\\[\n  S(T)\\leq S(P_n).\n\\]\n"
    out = blacktex.clean(input_string)
    assert out == "\\[\n  S(T)\\leq S(P_n).\n\\]\n"


def test_spaces_with_brackets():
    input_string = "( 1+2 ) { 3+4 } \\left( 5+6 \\right)"
    out = blacktex.clean(input_string)
    assert out == "(1+2) {3+4} \\left(5+6\\right)"


def test_multiple_newlines():
    input_string = "lorem  \n\n\n\n ipsum dolor sit  amet"
    out = blacktex.clean(input_string)
    assert out == "lorem\n\n\n ipsum dolor sit amet"


def test_dollar_dollar():
    input_string = "a $$a + b = c$$ b"
    out = blacktex.clean(input_string)
    assert out == "a\n\\[\na + b = c\n\\]\nb"


def test_whitespace_after_curly():
    input_string = "\\textit{ \nlorem  \n\n\n ipsum dolor sit  amet}"
    out = blacktex.clean(input_string)
    assert out == "\\textit{lorem\n\n\n ipsum dolor sit amet}"


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

    input_string = "$(n^3)$."
    out = blacktex.clean(input_string)
    assert out == "$(n^3)$."

    input_string = "n^\\alpha"
    out = blacktex.clean(input_string)
    assert out == "n^\\alpha"


def test_triple_dots():
    input_string = "a,...,b"
    out = blacktex.clean(input_string)
    assert out == "a,\\dots,b"


def test_punctuation_outside_math():
    input_string = "$a+b.$"
    out = blacktex.clean(input_string)
    assert out == "$a+b$."


def test_whitespace_before_punctuation():
    input_string = "Some text ."
    out = blacktex.clean(input_string)
    assert out == "Some text."


def test_nbsp_before_ref():
    input_string = "Some text \\ref{something}."
    out = blacktex.clean(input_string)
    assert out == "Some text~\\ref{something}."


def test_double_nbsp():
    input_string = "Some~~text."
    out = blacktex.clean(input_string)
    assert out == "Some\\quad text."


def test_over_frac():
    input_string = "Some ${2\\over 3^{4+x}}$ equation ${\\pi \\over4}$."
    out = blacktex.clean(input_string)
    assert out == "Some $\\frac{2}{3^{4+x}}$ equation $\\frac{\\pi}{4}$."


def test_over_frac_warn():
    input_string = "Some $2\\over 3^{4+x}$."
    with pytest.warns(UserWarning):
        out = blacktex.clean(input_string)
    assert out == "Some $2\\over 3^{4+x}$."


def test_overline_warn():
    input_string = "\\overline"
    out = blacktex.clean(input_string)
    assert out == "\\overline"


def test_linebreak_after_double_backslash():
    input_string = "Some $2\\\\3 4\\\\\n6\\\\[2mm]7$."
    out = blacktex.clean(input_string)
    assert out == "Some $2\\\\\n3 4\\\\\n6\\\\\n[2mm]7$."


def test_nbsp_space():
    input_string = "Some ~thing."
    out = blacktex.clean(input_string)
    assert out == "Some thing."


def test_keywords_without_backslash():
    input_string = "maximum and logarithm $max_x log(x)$"
    out = blacktex.clean(input_string)
    assert out == "maximum and logarithm $\\max_x \\log(x)$"


def test_curly_around_round_with_exponent():
    input_string = "$(a+b)^n \\left(a+b\\right)^{n+1}$"
    out = blacktex.clean(input_string)
    assert out == "${(a+b)}^n {\\left(a+b\\right)}^{n+1}$"


def test_def_newcommand():
    input_string = "\\def\\e{\\text{r}}"
    out = blacktex.clean(input_string)
    assert out == "\\newcommand{\\e}{\\text{r}}"


def test_linebreak_around_begin_end():
    input_string = (
        "A\\begin{equation}a+b\\end{equation} B \n\\begin{a}\nd+e\n\\end{a}\nB"
    )
    out = blacktex.clean(input_string)
    ref = "A\n\\begin{equation}\na+b\n\\end{equation}\nB\n\\begin{a}\nd+e\n\\end{a}\nB"
    assert out == ref

    # indentation is okay
    input_string = "A\n  \\begin{equation}\n  a+b\n  \\end{equation}"
    out = blacktex.clean(input_string)
    assert out == "A\n  \\begin{equation}\n  a+b\n  \\end{equation}"


def test_centerline():
    input_string = "\\centerline{foobar}"
    out = blacktex.clean(input_string)
    assert out == "{\\centering foobar}"


def test_eqnarray_align():
    input_string = "A\\begin{eqnarray*}a+b\\end{eqnarray*}F"
    out = blacktex.clean(input_string)
    assert out == "A\n\\begin{align*}\na+b\n\\end{align*}\nF"


def test_env_label():
    input_string = "A\n\\begin{lemma}\n\\label{lvalpp}"
    out = blacktex.clean(input_string)
    assert out == "A\n\\begin{lemma}\\label{lvalpp}"

    input_string = "A\n\\section{Intro}\n\\label{lvalpp}"
    out = blacktex.clean(input_string)
    assert out == "A\n\\section{Intro}\\label{lvalpp}"

    input_string = "A\n\\subsection{Intro}\n\\label{lvalpp}"
    out = blacktex.clean(input_string)
    assert out == "A\n\\subsection{Intro}\\label{lvalpp}"


def test_coloneqq():
    input_string = "A:=b+c"
    out = blacktex.clean(input_string)
    assert out == "A\\coloneqq b+c"

    input_string = "A := b+c"
    out = blacktex.clean(input_string)
    assert out == "A \\coloneqq b+c"

    input_string = "A : = b+c"
    out = blacktex.clean(input_string)
    assert out == "A \\coloneqq b+c"

    input_string = "b+c =  : A"
    out = blacktex.clean(input_string)
    assert out == "b+c \\eqqcolon A"


def test_tabular_column_spec():
    input_string = "\\begin{tabular} \n {ccc}\ncontent"
    out = blacktex.clean(input_string)
    assert out == "\\begin{tabular}{ccc}\ncontent"


def test_env_option_spec():
    input_string = "\\begin{table} \n [h!]G"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\nG"

    input_string = "\\begin{table}   [h!]G"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\nG"

    input_string = "\\begin{table}   [h!]\nG"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\nG"

    input_string = "\\begin{table} \n [h!]G"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\nG"

    input_string = "\\begin{table} \n [h!]\\label{foo}"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\\label{foo}"

    input_string = "\\begin{table} \n [h!]\\label{foo}\nG"
    out = blacktex.clean(input_string)
    assert out == "\\begin{table}[h!]\\label{foo}\nG"


def test_space_around_operators():
    input_string = "a+b=c"
    out = blacktex.clean(input_string)
    assert out == "a+b = c"

    input_string = "a+b&=&c"
    out = blacktex.clean(input_string)
    assert out == "a+b &=& c"


if __name__ == "__main__":
    test_linebreak_after_double_backslash()
