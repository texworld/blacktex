from textwrap import dedent
import pytest

from blacktex.main import (
    TexString,
    RemoveComments,
    RemoveTrailingWhitespace,
    RemoveMultipleSpaces,
    RemoveMultipleNewlines,
    RemoveWhitespaceAroundBrackets,
    ReplaceDoubleDollarInline,
    ReplaceObsoleteTextMods,
    AddSpaceAfterSingleSubsuperscript,
    ReplaceDots,
    ReplacePunctuationOutsideMath,
    RemoveWhitespaceBeforePunctuation,
    AddNonBreakingSpaceBeforeReference,
    ReplaceDoubleNonBreakingSpace,
    ReplaceNonBreakingSpace,
    ReplaceOver,
    AddLineBreakAfterDoubleBackslash,
    AddBackslashForKeywords,
    AddCurlyBracketsAroundRoundBracketsWithExp,
    ReplaceDefWithNewcommand,
    AddLineBreakAroundBeginEnd,
    ReplaceCenterLine,
    ReplaceEqnarray,
    PutSpecOnSameLineAsEnvironment,
    PutLabelOnSameLineAsEnvironment,
    ReplaceColonEqualWithColoneqq,
    RemoveSpaceBeforeTabularColumnSpecification,
    AddSpaceAroundEqualitySign,
)


def check_command_execution(input_string, expected_string, command):
    receiver = TexString(input_string)
    command(receiver).execute()
    assert expected_string == receiver.string


class TestAbstract:
    def run_and_compare(self, input_string, expected_string):
        check_command_execution(
            input_string,
            expected_string,
            command=self.command,
        )


class TestRemoveComments(TestAbstract):
    command = RemoveComments

    def test_both_inline_and_full_line_comments(self):
        input_string = "lorem  %some comment  \n %sit amet"
        expected_string = "lorem  \n"
        self.run_and_compare(input_string, expected_string)

    def test_line_beggining_comment(self):
        input_string = dedent(
            """\
            not comment
            % beggining of line comment
            again not comment
            """
        )

        expected_string = dedent(
            """\
            not comment
            again not comment
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_inline_comment(self):
        input_string = "lorem % some inline comment \n"
        expected_string = "lorem \n"
        self.run_and_compare(input_string, expected_string)

    def test_inline_comment_and_full_line_comment(self):
        input_string = dedent(
            """\
            not comment
            % beggining of line comment
            again not comment
            line with % inline comment"""
        )

        expected_string = dedent(
            """\
            not comment
            again not comment
            line with """
        )
        self.run_and_compare(input_string, expected_string)

    def test_multiple_comment_lines(self):
        input_string = dedent(
            """\
            not comment
            % long-long
            %% long comment
            again not comment
            """
        )

        expected_string = dedent(
            """\
            not comment
            again not comment
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestRemoveTrailingWhitespace(TestAbstract):
    command = RemoveTrailingWhitespace

    def test_one_space(self):
        input_string = "line with space "
        expected_string = "line with space"
        self.run_and_compare(input_string, expected_string)

    def test_multiple_spaces(self):
        input_string = "line with multiple spaces   "
        expected_string = "line with multiple spaces"
        self.run_and_compare(input_string, expected_string)

    def test_multiple_spaces_and_linebreak(self):
        input_string = "line with multiple spaces   \n"
        expected_string = "line with multiple spaces\n"
        self.run_and_compare(input_string, expected_string)

    def test_multiple_lines(self):
        space = " "
        input_string = dedent(
            f"""\
            normal line
            line with trailing space{space}
            again normal line
            line with many trailing spaces{space}{space}{space}
            one more normal line
            """
        )

        expected_string = dedent(
            """\
            normal line
            line with trailing space
            again normal line
            line with many trailing spaces
            one more normal line
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestRemoveMultipleSpaces(TestAbstract):
    command = RemoveMultipleSpaces

    def test_multiple_lines(self):
        input_string = dedent(
            """\
            normal line
            line with   many spaces
            again normal line
              line with indent
            one more normal line
            """
        )

        expected_string = dedent(
            """\
            normal line
            line with many spaces
            again normal line
              line with indent
            one more normal line
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestRemoveMultipleNewlines(TestAbstract):
    command = RemoveMultipleNewlines

    def test_indented_line(self):
        input_string = "first line\n\n\n\n  second indented line\n"
        expected_string = "first line\n\n\n  second indented line\n"
        self.run_and_compare(input_string, expected_string)

    def test_multiple_lines(self):
        input_string = dedent(
            """\
            first line
              second line



                third indented line"""
        )

        expected_string = dedent(
            """\
            first line
              second line


                third indented line"""
        )
        self.run_and_compare(input_string, expected_string)


class TestRemoveWhitespaceAroundBrackets(TestAbstract):
    command = RemoveWhitespaceAroundBrackets

    def test_curly_brackets(self):
        input_string = r"word \ref{ label } another word"
        expected_string = r"word \ref{label} another word"
        self.run_and_compare(input_string, expected_string)

    def test_parens(self):
        input_string = r"word (  description ) means"
        expected_string = r"word (description) means"
        self.run_and_compare(input_string, expected_string)

    def test_parens_one_space(self):
        input_string = r"word (description ) means"
        expected_string = r"word (description) means"
        self.run_and_compare(input_string, expected_string)

    def test_big_parens(self):
        input_string = r"word \left(  description \right) means"
        expected_string = r"word \left(description\right) means"
        self.run_and_compare(input_string, expected_string)


class TestReplaceDoubleDollarInline(TestAbstract):
    command = ReplaceDoubleDollarInline

    def test_with_following_space(self):
        input_string = dedent(
            """\
            preceding line
            equation $$a + b = c$$ like this
            following line
            """
        )
        expected_string = dedent(
            """\
            preceding line
            equation
            \\[
            a + b = c
            \\]
            like this
            following line
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_equation_with_preceding_space(self):
        input_string = dedent(
            """\
            preceding line
            equation $$ a + b = c$$ like this
            following line
            """
        )
        expected_string = dedent(
            """\
            preceding line
            equation
            \\[
            a + b = c
            \\]
            like this
            following line
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_multiple_equations(self):
        input_string = dedent(
            """\
            preceding line
            first $$a + b = c$$ equation
            following line
            $$x + y = z$$ second equation
             last line indented
            """
        )
        expected_string = dedent(
            """\
            preceding line
            first
            \\[
            a + b = c
            \\]
            equation
            following line
            \\[
            x + y = z
            \\]
            second equation
             last line indented
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestReplaceObsoleteTextMods(TestAbstract):
    command = ReplaceObsoleteTextMods

    def test_bold(self):
        input_string = "this line has {\\bf bold} text"
        expected_string = "this line has \\textbf{bold} text"
        self.run_and_compare(input_string, expected_string)

    def test_extra_whitespace_removed(self):
        input_string = "this line has {\\bf   bold with spaces} text"
        expected_string = "this line has \\textbf{bold with spaces} text"
        self.run_and_compare(input_string, expected_string)

    def test_emph(self):
        input_string = "this line has {\\em emphasized} text"
        expected_string = "this line has \\emph{emphasized} text"
        self.run_and_compare(input_string, expected_string)

    def test_italic(self):
        input_string = "this line has {\\it italic} text"
        expected_string = "this line has \\textit{italic} text"
        self.run_and_compare(input_string, expected_string)

    def test_multiple_changes(self):
        input_string = dedent(
            """\
            first line has {\\it italic} text
            second line has {\\bf bold} text
            third line has {\\rm roman} text
            fourth line has {\\sc small caps} text
            fifth line has {\\sl slanted} text
            sixth line has {\\tt typewriter} text
            seventh line has {\\sf sans serif} text
            eighth line has {\\em EMPHASIS} text
            nineth line has {\\bf bold} and {\\rm roman}
            """
        )
        expected_string = dedent(
            """\
            first line has \\textit{italic} text
            second line has \\textbf{bold} text
            third line has \\textrm{roman} text
            fourth line has \\textsc{small caps} text
            fifth line has \\textsl{slanted} text
            sixth line has \\texttt{typewriter} text
            seventh line has \\textsf{sans serif} text
            eighth line has \\emph{EMPHASIS} text
            nineth line has \\textbf{bold} and \\textrm{roman}
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_change_in_subscript(self):
        input_string = dedent("equation $x_{\\rm sub}$ here")
        expected_string = dedent("equation $x_\\textrm{sub}$ here")
        self.run_and_compare(input_string, expected_string)


class TestAddSpaceAfterSingleSubsuperscript(TestAbstract):
    command = AddSpaceAfterSingleSubsuperscript

    def test_superscript(self):
        input_string = "2^ng"
        expected_string = "2^n g"
        self.run_and_compare(input_string, expected_string)

    def test_subscript(self):
        input_string = "2_ng"
        expected_string = "2_n g"
        self.run_and_compare(input_string, expected_string)

    def test_subscript_and_superscript(self):
        input_string = "2^ng_xy"
        expected_string = "2^n g_x y"
        self.run_and_compare(input_string, expected_string)


class TestReplaceDots(TestAbstract):
    command = ReplaceDots

    def test_triple_dots(self):
        input_string = "a,...,b"
        expected_string = "a,\\dots,b"
        self.run_and_compare(input_string, expected_string)

    def test_cdots(self):
        input_string = "a,\\cdots,b"
        expected_string = "a,\\dots,b"
        self.run_and_compare(input_string, expected_string)


class TestReplacePunctuationOutsideMath(TestAbstract):
    command = ReplacePunctuationOutsideMath

    def test_one_line(self):
        input_string = "$a+b.$"
        expected_string = "$a+b$."
        self.run_and_compare(input_string, expected_string)


class TestRemoveWhitespaceBeforePunctuation(TestAbstract):
    command = RemoveWhitespaceBeforePunctuation

    def test_dot(self):
        input_string = "End of sentence .  Another sentence."
        expected_string = "End of sentence.  Another sentence."
        self.run_and_compare(input_string, expected_string)

    def test_all_signs(self):
        input_string = dedent(
            """\
            Some text , new text  ;
            yet another text . And question  ?
            Exclamation  !  mark
            """
        )
        expected_string = dedent(
            """\
            Some text, new text;
            yet another text. And question?
            Exclamation!  mark
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestAddNonBreakingSpaceBeforeReference(TestAbstract):
    command = AddNonBreakingSpaceBeforeReference

    def test_reference(self):
        input_string = "Some text \\ref{something}."
        expected_string = "Some text~\\ref{something}."
        self.run_and_compare(input_string, expected_string)

    def test_eqref(self):
        input_string = "Some Equation \\eqref{something}."
        expected_string = "Some Equation~\\eqref{something}."
        self.run_and_compare(input_string, expected_string)

    def test_cite(self):
        input_string = "Some citation \\cite{something}."
        expected_string = "Some citation~\\cite{something}."
        self.run_and_compare(input_string, expected_string)


class TestReplaceDoubleNonBreakingSpace(TestAbstract):
    command = ReplaceDoubleNonBreakingSpace

    def test_one_line(self):
        input_string = "Before target. Some~~text. After target."
        expected_string = "Before target. Some\\quad text. After target."
        self.run_and_compare(input_string, expected_string)


class TestReplaceNonBreakingSpace(TestAbstract):
    command = ReplaceNonBreakingSpace

    def test_simple(self):
        input_string = "Some ~thing."
        expected_string = "Some thing."
        self.run_and_compare(input_string, expected_string)


class TestReplaceOver(TestAbstract):
    command = ReplaceOver

    def test_numeric_denominator(self):
        input_string = "Expression ${\\Gamma \\over 2} = 8$."
        expected_string = "Expression $\\frac{\\Gamma}{2} = 8$."
        self.run_and_compare(input_string, expected_string)

    def test_greek_denominator(self):
        input_string = "Expression ${\\Gamma \\over \\Omega} = 8$."
        expected_string = "Expression $\\frac{\\Gamma}{\\Omega} = 8$."
        self.run_and_compare(input_string, expected_string)

    def test_ignore_overline(self):
        input_string = "This should not \\overline{change}"
        expected_string = input_string
        self.run_and_compare(input_string, expected_string)

    def test_over_frac_warn(self):
        input_string = "Some $2\\over 3^{4+x}$."
        expected_string = "Some $2\\over 3^{4+x}$."
        with pytest.warns(UserWarning, match="Could not convert"):
            self.run_and_compare(input_string, expected_string)


class TestAddLineBreakAfterDoubleBackslash(TestAbstract):
    command = AddLineBreakAfterDoubleBackslash

    def test_simple(self):
        input_string = "Some $2\\\\3 4\\\\\n6\\\\[2mm]7$."
        expected_string = dedent(
            """\
            Some $2\\\\
            3 4\\\\
            6\\\\
            [2mm]7$."""
        )
        self.run_and_compare(input_string, expected_string)


class TestAddBackslashForKeywords(TestAbstract):
    command = AddBackslashForKeywords

    def test_max_and_log(self):
        input_string = "maximum and logarithm $max_x log(x)$"
        expected_string = "maximum and logarithm $\\max_x \\log(x)$"
        self.run_and_compare(input_string, expected_string)

    def test_all_keywords(self):
        input_string = dedent(
            r"""\\
            Maximum value $max(this)$ is MAX.
            Minimum value $min(this)$ is MIN.
            Logarithm value $log(that)$ is LOG.
            Sine value $sin(angle)$ is SIN.
            """
        )

        expected_string = dedent(
            r"""\\
            Maximum value $\max(this)$ is MAX.
            Minimum value $\min(this)$ is MIN.
            Logarithm value $\log(that)$ is LOG.
            Sine value $\sin(angle)$ is SIN.
            """
        )

        self.run_and_compare(input_string, expected_string)

    @pytest.mark.skip(
        reason="""
        Contradicts the original behavior.
        Not clear how to easily separate math mode from normal text mode.
        """
    )
    def test_do_not_change_in_text(self):
        input_string = dedent(
            """\
            Maximum and logarithm max and log
            must remain unchanged in normal text.
            """
        )
        expected_string = input_string
        self.run_and_compare(input_string, expected_string)


class TestAddCurlyBracketsAroundRoundBracketsWithExp(TestAbstract):
    command = AddCurlyBracketsAroundRoundBracketsWithExp

    def test_basic(self):
        input_string = "$(a+b)^n \\left(a+b\\right)^{n+1}$"
        expected_string = "${(a+b)}^n {\\left(a+b\\right)}^{n+1}$"
        self.run_and_compare(input_string, expected_string)


class TestReplaceDefWithNewcommand(TestAbstract):
    command = ReplaceDefWithNewcommand

    def test_basic(self):
        input_string = "\\def\\e{\\text{r}}"
        expected_string = "\\newcommand{\\e}{\\text{r}}"
        self.run_and_compare(input_string, expected_string)


class TestAddLineBreakAroundBeginEnd(TestAbstract):
    command = AddLineBreakAroundBeginEnd

    def test_basic(self):
        input_string = dedent(
            """\
            A\\begin{equation}a+b\\end{equation} B
            \\begin{a}
            d+e
            \\end{a}
            B
            """
        )

        expected_string = dedent(
            """\
            A
            \\begin{equation}
            a+b
            \\end{equation}
            B
            \\begin{a}
            d+e
            \\end{a}
            B
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestReplaceCenterLine(TestAbstract):
    command = ReplaceCenterLine

    def test_basic(self):
        input_string = "Before \\centerline{foobar} after"
        expected_string = "Before {\\centering foobar} after"
        self.run_and_compare(input_string, expected_string)


class TestReplaceEqnarray(TestAbstract):
    command = ReplaceEqnarray

    def test_basic(self):
        input_string = dedent(
            """\
            A
            \\begin{eqnarray*}
            a+b
            \\end{eqnarray*}
            F"""
        )

        expected_string = dedent(
            """\
            A
            \\begin{align*}
            a+b
            \\end{align*}
            F"""
        )
        self.run_and_compare(input_string, expected_string)


class TestPutSpecOnSameLineAsEnvironment(TestAbstract):
    command = PutSpecOnSameLineAsEnvironment

    def test_options_next_line(self):
        input_string = dedent(
            """\
            \\begin{table}
            [h!]G
            continued
            """
        )
        expected_string = dedent(
            """\
            \\begin{table}[h!]
            G
            continued
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_options_separated_with_spaces_content_same_line(self):
        input_string = dedent(
            """\
            \\begin{table}  [h!]G
            continued
            """
        )
        expected_string = dedent(
            """\
            \\begin{table}[h!]
            G
            continued
            """
        )
        self.run_and_compare(input_string, expected_string)

    def test_options_separated_with_spaces_content_next_line(self):
        input_string = dedent(
            """\
            \\begin{table}  [h!]
            G
            continued
            """
        )
        expected_string = dedent(
            """\
            \\begin{table}[h!]
            G
            continued
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestPutLabelOnSameLineAsEnvironment(TestAbstract):
    command = PutLabelOnSameLineAsEnvironment

    def test_basic(self):
        # Questionable behavior, IMHO.
        # I would suggest the opposite: force newline before \label.
        input_string = "\\begin{table}[h!]\n\\label{foo}"
        expected_string = "\\begin{table}[h!]\\label{foo}"
        self.run_and_compare(input_string, expected_string)


class TestReplaceColonEqualWithColoneqq(TestAbstract):
    command = ReplaceColonEqualWithColoneqq

    def test_no_spaces(self):
        input_string = "A:=b+c"
        expected_string = "A\\coloneqq b+c"
        self.run_and_compare(input_string, expected_string)

    def test_normal_spaces(self):
        input_string = "A := b+c"
        expected_string = "A \\coloneqq b+c"
        self.run_and_compare(input_string, expected_string)

    def test_excessive_spaces(self):
        input_string = "A : = b+c"
        expected_string = "A \\coloneqq b+c"
        self.run_and_compare(input_string, expected_string)

    def test_reverse_eqncolon(self):
        input_string = "b+c =: A"
        expected_string = "b+c \\eqqcolon A"
        self.run_and_compare(input_string, expected_string)

    def test_reverse_eqncolon_excessive_spaces(self):
        input_string = "b+c = : A"
        expected_string = "b+c \\eqqcolon A"
        self.run_and_compare(input_string, expected_string)


class TestRemoveSpaceBeforeTabularColumnSpecification(TestAbstract):
    command = RemoveSpaceBeforeTabularColumnSpecification

    def test_tabular(self):
        input_string = dedent(
            """\
            \\begin{tabular}
              {ccc}
            content
            """
        )

        expected_string = dedent(
            """\
            \\begin{tabular}{ccc}
            content
            """
        )
        self.run_and_compare(input_string, expected_string)


class TestAddSpaceAroundEqualitySign(TestAbstract):
    command = AddSpaceAroundEqualitySign

    def test_basic(self):
        input_string = "x + y=z"
        expected_string = "x + y = z"
        self.run_and_compare(input_string, expected_string)

    def test_dollar_env(self):
        input_string = "$x + y=z$"
        expected_string = "$x + y = z$"
        self.run_and_compare(input_string, expected_string)

    def test_do_not_change_correct_spaces(self):
        input_string = "Line with correct spaces $x + y = z$ here."
        expected_string = input_string
        self.run_and_compare(input_string, expected_string)

    def test_ampersand(self):
        input_string = "a+b&=&c"
        expected_string = "a+b &=& c"
        self.run_and_compare(input_string, expected_string)
