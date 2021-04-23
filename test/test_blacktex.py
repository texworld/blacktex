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
        "and \\(y = 2^n g\\) with \\(n = 1,\\dots,10\\), we have "
        "\\(\\frac{\\Gamma}{2} = 8\\)."
    )


@pytest.mark.parametrize(
    "string, out",
    [
        # dollar replacement:
        ("a $a + b = c$ b", r"a \(a + b = c\) b"),
        (r"a \$a + b = c\$ b", r"a \$a + b = c\$ b"),
        (r"a \\$a + b = c\\$ b", "a \\\\\n\\(a + b = c\\\\\n\\) b"),
        # text mods:
        ("{\\em it's me!}", "\\emph{it's me!}"),
        # comments:
        ("lorem  %some comment  \n %sit amet", "lorem"),
        ("% lorem some comment  \n sit amet", " sit amet"),
        ("A % lorem some comment  \n sit amet", "A\n sit amet"),
        ("{equation}%comment", "{equation}"),
        # multiple comment lines:
        ("A\n%\n%\nB", "A\nB"),
        # comment last:
        ("somemacro{%\n" "foobar% \n" "}", "somemacro{%\nfoobar%\n}"),
        # trailing whitespace:
        ("lorem    \n sit amet", "lorem\n sit amet"),
        # obsolete text mod:
        ("lorem {\\it ipsum dolor} sit amet", "lorem \\textit{ipsum dolor} sit amet"),
        # multiple spaces:
        ("lorem   ipsum dolor sit  amet", "lorem ipsum dolor sit amet"),
        # It's allowed as indentation at the beginning of lines:
        ("a\n    b\nc", "a\n    b\nc"),
        ("\\[\n  S(T)\\leq S(P_n).\n\\]\n", "\\[\n  S(T)\\leq S(P_n).\n\\]\n"),
        # spaces with brackets:
        ("( 1+2 ) { 3+4 } \\left( 5+6 \\right)", "(1+2) {3+4} \\left(5+6\\right)"),
        # multiple newlines:
        ("lorem  \n\n\n\n\n\n ipsum dolor   sit", "lorem\n\n\n ipsum dolor sit"),
        # $$:
        ("a $$a + b = c$$ b", "a\n\\[\na + b = c\n\\]\nb"),
        # whitespace after curly:
        ("\\textit{ \nlorem  \n\n\n ipsum   dol}", "\\textit{\nlorem\n\n\n ipsum dol}"),
        # sub/superscript space:
        ("2^ng", "2^n g"),
        ("1/n^3", "1/n^3"),
        ("n^3", "n^3"),
        ("(n^3)", "(n^3)"),
        ("n^\\alpha", "n^\\alpha"),
        ("a^2_PP^2", "a^2_PP^2"),
        # Underscore separation just produces too many false positives. Leave as is.
        ("2_ng", "2_ng"),
        # dots:
        ("a,...,b", "a,\\dots,b"),
        ("a,\\cdots,b", "a,\\dots,b"),
        # punctuation outside math:
        ("$a+b.$", "\\(a+b\\)."),
        # whitespace before punctuation:
        ("Some text .", "Some text."),
        # nbsp before ref:
        ("text \\ref{something}", "text~\\ref{something}"),
        # nbsp space:
        ("Some ~thing.", "Some thing."),
        # double nbsp:
        ("Some~~text.", "Some\\quad text."),
        # \over to \frac:
        ("{2\\over 3^{4+x}}", "\\frac{2}{3^{4+x}}"),
        ("{\\pi \\over4}", "\\frac{\\pi}{4}"),
        # overline warn:
        ("\\overline", "\\overline"),
        # linebreak after double backslash:
        ("T $2\\\\3 4\\\\\n6\\\\[2mm]7$.", "T \\(2\\\\\n3 4\\\\\n6\\\\\n[2mm]7\\)."),
        # keywords without backslash:
        (
            "maximum and logarithm $max_x log(x)$",
            "maximum and logarithm \\(\\max_x \\log(x)\\)",
        ),
        # curly around round with exponent:
        (
            "$(a+b)^n \\left(a+b\\right)^{n+1}$",
            r"\({(a+b)}^n {\left(a+b\right)}^{n+1}\)",
        ),
        # def vs. newcommand
        ("\\def\\e{\\text{r}}", "\\newcommand{\\e}{\\text{r}}"),
        # linebreak around begin/end:
        (
            "A\\begin{equation}a+b\\end{equation} B \n\\begin{a}\nd+e\n\\end{a}\nB",
            "A\n\\begin{equation}\na+b\n\\end{equation}\nB\n\\begin{a}\nd+e\n\\end{a}\nB",
        ),
        # indentation is okay
        (
            "A\n  \\begin{equation}\n  a+b\n  \\end{equation}",
            "A\n  \\begin{equation}\n  a+b\n  \\end{equation}",
        ),
        # centerline:
        ("\\centerline{foobar}", "{\\centering foobar}"),
        # eqnarray align:
        (
            "A\\begin{eqnarray*}a+b\\end{eqnarray*}F",
            "A\n\\begin{align*}\na+b\n\\end{align*}\nF",
        ),
        # env label:
        ("A\n\\begin{lemma}\n\\label{lvalpp}", "A\n\\begin{lemma}\\label{lvalpp}"),
        ("A\n\\section{Intro}\n\\label{lvalpp}", "A\n\\section{Intro}\\label{lvalpp}"),
        (
            "A\n\\subsection{Intro}\n\\label{lvalpp}",
            "A\n\\subsection{Intro}\\label{lvalpp}",
        ),
        # coloneqq
        ("A:=b+c", "A\\coloneqq b+c"),
        ("A := b+c", "A \\coloneqq b+c"),
        ("A : = b+c", "A \\coloneqq b+c"),
        ("b+c =  : A", "b+c \\eqqcolon A"),
        # tabular column spec:
        ("\\begin{tabular} \n {ccc}\ncontent", "\\begin{tabular}{ccc}\ncontent"),
        # env option spec:
        ("\\begin{table} \n [h!]G", "\\begin{table}[h!]\nG"),
        ("\\begin{table}   [h!]G", "\\begin{table}[h!]\nG"),
        ("\\begin{table}   [h!]\nG", "\\begin{table}[h!]\nG"),
        ("\\begin{table} \n [h!]G", "\\begin{table}[h!]\nG"),
        ("\\begin{table} \n [h!]\\label{foo}", "\\begin{table}[h!]\\label{foo}"),
        ("\\begin{table} \n [h!]\\label{foo}\nG", "\\begin{table}[h!]\\label{foo}\nG"),
        # space around operators:
        ("a+b=c", "a+b = c"),
        ("a+b&=&c", "a+b &=& c"),
        # SI percentage:
        ("20\\% \\SI{30}{\\%}", "\\SI{20}{\\%} \\SI{30}{\\%}"),
        # escaped percentage sign:
        ("25\\% gain", "\\SI{25}{\\%} gain"),
    ],
)
def test_compare(string, out):
    assert blacktex.clean(string) == out


def test_over_frac_warn():
    input_string = "Some $2\\over 3^{4+x}$."
    with pytest.warns(UserWarning):
        out = blacktex.clean(input_string, keep_dollar=True)
    assert out == "Some $2\\over 3^{4+x}$."
