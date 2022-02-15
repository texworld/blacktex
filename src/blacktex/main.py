import re
from typing import Callable

from pylatexenc.latexwalker import (
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexWalker,
    nodelist_to_latex,
)
from pylatexenc.macrospec import ParsedMacroArgs


def _traverse_tree(nodelist: list, fun: Callable):
    nodelist = [fun(node) for node in nodelist if node is not None]

    for node in nodelist:
        if hasattr(node, "nodelist"):
            node.nodelist = _traverse_tree(node.nodelist, fun)

    return nodelist


def _remove_comments(string: str) -> str:
    """Remove comments unless the comment character is the last non-whitespace character
    in a line. (This is often used in macros etc.)
    """

    def _rm(node):
        if isinstance(node, LatexCommentNode):
            return None
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _rm)
    return nodelist_to_latex(nodelist)


def _remove_trailing_whitespace(string: str) -> str:
    return "\n".join([line.rstrip() for line in string.split("\n")])


def _remove_multiple_spaces(string: str) -> str:
    """Replaces multiple spaces by one, except after a newline."""
    return re.sub("([^\n ])  +", r"\1 ", string)


def _remove_multiple_newlines(string: str) -> str:
    string = re.sub("\n\n\n\n+", "\n\n\n", string)
    return string


def _remove_whitespace_around_brackets(string: str) -> str:
    string = re.sub("{[ \t]+", "{", string)
    string = re.sub("[ \t]+}", "}", string)
    string = re.sub("\\([ \t]+", "(", string)
    string = re.sub("[ \t]+\\)", ")", string)
    string = re.sub("[ \t]+\\\\right\\)", "\\\\right)", string)
    return string


def _replace_dollar_dollar(string: str) -> str:
    """Replace $$...$$ by \\[...\\]."""

    def _repl(node):
        if isinstance(node, LatexMathNode):
            if node.delimiters == ("$$", "$$"):
                node.delimiters = ("\\[", "\\]")
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _repl)
    return nodelist_to_latex(nodelist)


def _replace_dollar(string: str) -> str:
    """Replace $...$ by \\(...\\). See <https://tex.stackexchange.com/q/510/13262>."""

    def _repl(node):
        if isinstance(node, LatexMathNode):
            if node.delimiters == ("$", "$"):
                node.delimiters = ("\\(", "\\)")
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _repl)
    return nodelist_to_latex(nodelist)


def _macro(macroname, *nodelists):
    """Creates a pylatexenc node that corresponds to \\macroname{nodelist}"""
    return LatexMacroNode(
        macroname=macroname,
        nodeargd=ParsedMacroArgs(
            argspec="{" * len(nodelists),
            argnlist=[LatexGroupNode(nodelist=nodelist) for nodelist in nodelists],
        ),
    )


def _replace_obsolete_text_mods(string: str) -> str:
    r"""Replace {\it foo} by \textit{foo} etc"""
    # bracket, don't replace; see <https://github.com/nschloe/blacktex/issues/46>.
    replacements = [
        ("it", "textit"),
        ("bf", "textbf"),
        ("rm", "textrm"),
        ("sc", "textsc"),
        ("sf", "textsf"),
        ("sl", "textsl"),
        ("tt", "texttt"),
        # https://tex.stackexchange.com/a/25914/13262:
        # [\em] May be useful when defining macros. In continuous text
        # \emph{...} should be preferred to \em.
        ("em", "emph"),
    ]

    def _repl(node):
        if not isinstance(node, LatexGroupNode):
            return node
        # See if the first child in the group is a macro, e.g., {\it ...}
        child0 = node.nodelist[0]
        if not isinstance(child0, LatexMacroNode):
            return node

        for orig, repl in replacements:
            if child0.macroname == orig:
                node = _macro(repl, node.nodelist[1:])
                break

        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _repl)
    return nodelist_to_latex(nodelist)


def _add_space_after_single_subsuperscript(string: str) -> str:
    string = re.sub(r"([\^])([^{\\])([^_\^\s\$})])", r"\1\2 \3", string)
    return string


def _replace_dots(string: str) -> str:
    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    for node in nodelist:
        if isinstance(node, LatexMacroNode) and node.macroname == "cdots":
            node.macroname = "dots"
    string = nodelist_to_latex(nodelist)

    string = re.sub(r"\.\.\.", r"\\dots", string)
    return string


def _replace_punctuation_at_math_end(string: str) -> str:
    return re.sub(r"([\.,;!\?])\\\)", r"\)\1", string)


def _remove_whitespace_before_punctuation(string: str) -> str:
    string = re.sub(r"\s+\.", ".", string)
    string = re.sub(r"\s+,", ",", string)
    string = re.sub(r"\s+;", ";", string)
    string = re.sub(r"\s+!", "!", string)
    string = re.sub(r"\s+\?", "?", string)
    return string


def _add_nbsp_before_reference(string: str) -> str:
    string = re.sub(r"\s+\\ref{", r"~\\ref{", string)
    string = re.sub(r"\s+\\eqref{", r"~\\eqref{", string)
    string = re.sub(r"\s+\\cite", r"~\\cite", string)
    return string


def _replace_double_nbsp(string: str) -> str:
    return re.sub("~~", r"\\quad ", string)


def _replace_nbsp_space(string: str) -> str:
    string = re.sub("~ ", " ", string)
    string = re.sub(" ~", " ", string)
    return string


def _substitute_string_ranges(string: str, ranges, replacements) -> str:
    if ranges:
        lst = [string[: ranges[0][0]]]
        for k, replacement in enumerate(replacements[:-1]):
            lst += [replacement, string[ranges[k][1] : ranges[k + 1][0]]]
        lst += [replacements[-1], string[ranges[-1][1] :]]
        string = "".join(lst)
    return string


def _replace_over(string: str) -> str:
    def _replace(node):
        if isinstance(node, LatexGroupNode):
            k0 = None
            for k, n2 in enumerate(node.nodelist):
                if isinstance(n2, LatexMacroNode) and n2.macroname == "over":
                    k0 = k
                    break

            if k0 is not None:
                # We found an \over. Create a \frac from the rest of the nodes.
                return _macro("frac", node.nodelist[:k0], node.nodelist[k0 + 1 :])
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)

    nodelist = _traverse_tree(nodelist, _replace)

    return nodelist_to_latex(nodelist)


def _add_linebreak_after_double_backslash(string: str) -> str:
    return re.sub(r"\\\\([^\n])", r"\\\\\n\1", string)


def _add_backslash_for_keywords(string: str) -> str:
    insert = []
    for keyword in ["max", "min", "log", "sin", "cos", "exp"]:
        p = re.compile(rf"[^A-Za-z]{keyword}[^A-Za-z]")
        locations = [m.start() for m in p.finditer(string)]
        for loc in locations:
            if string[loc] != "\\":
                insert.append(loc)

    return _substitute_string_ranges(
        string, [(i + 1, i + 1) for i in insert], len(insert) * ["\\"]
    )


def _replace_def_by_newcommand(string: str) -> str:
    def _repl(node):
        if isinstance(node, LatexMacroNode):
            if node.macroname == "def":
                node.macroname = "newcommand"
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _repl)
    return nodelist_to_latex(nodelist)


def _add_linebreak_around_begin_end(string: str) -> str:
    string = re.sub(r"([^\n ]) *(\\begin{.*?})", r"\1\n\2", string)
    string = re.sub(r"(\\begin{.*?}) *([^\n ])", r"\1\n\2", string)

    string = re.sub(r"([^\n ]) *(\\end{.*?})", r"\1\n\2", string)
    string = re.sub(r"(\\end{.*?}) *([^\n ])", r"\1\n\2", string)

    string = re.sub(r"([^\n ]) *(\\\[)", r"\1\n\2", string)
    string = re.sub(r"(\\\[) *([^\n ])", r"\1\n\2", string)

    string = re.sub(r"([^\n ]) *(\\\])", r"\1\n\2", string)
    string = re.sub(r"(\\\]) *([^\n ])", r"\1\n\2", string)
    return string


def _replace_centerline(string: str) -> str:
    return re.sub(r"\\centerline{", r"{\\centering ", string)


def _replace_eqnarray(string: str) -> str:
    def _repl(node):
        if isinstance(node, LatexEnvironmentNode):
            # Also set envname, should be removed at some point
            # TODO https://github.com/phfaist/pylatexenc/issues/81
            if node.environmentname == "eqnarray":
                node.environmentname = "align"
                node.envname = "align"
            elif node.environmentname == "eqnarray*":
                node.envname = "align*"
        return node

    w = LatexWalker(string)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, _repl)
    return nodelist_to_latex(nodelist)


def _put_spec_on_same_line_as_environment(string: str) -> str:
    string = re.sub(r"(\\begin{.*?})\s*(\[.*?\])\n", r"\1\2", string)
    string = re.sub(r"(\\begin{.*?})\s*(\[.*?\])([^\n])", r"\1\2\n\3", string)
    return string


def _put_label_on_same_line_as_environment(string: str) -> str:
    out = re.sub(r"(\\begin{.*?})(\[.*?])?\s+(\\label{.*?})(\n)?", r"\1\2\3\4", string)
    out = re.sub(r"(\\section{.*?})\s+(\\label{.*?})(\n)?", r"\1\2\3", out)
    out = re.sub(r"(\\subsection{.*?})\s+(\\label{.*?})(\n)?", r"\1\2\3", out)
    return out


def _replace_colon_equal_by_coloneqq(string: str) -> str:
    out = re.sub(r":\s*=", r"\\coloneqq ", string)
    out = re.sub(r"=\s*:", r"\\eqqcolon ", out)
    return out


def _remove_space_before_tabular_column_specification(string: str) -> str:
    return re.sub(r"(\\begin{tabular})\s*({.*?})", r"\1\2", string)


def _add_spaces_around_equality_sign(string: str) -> str:
    string = re.sub(r"([^\s&])=", r"\1 =", string)
    string = re.sub(r"([^\s])&=", r"\1 &=", string)

    string = re.sub(r"=([^\s&])", r"= \1", string)
    string = re.sub(r"=&([^\s])", r"=& \1", string)
    return string


def _si_percentage(string: str) -> str:
    # match float like https://stackoverflow.com/a/12643073/353337
    string = re.sub(r"([+-]?([0-9]*[.])?[0-9]+)[ \t]*\\%", r"\\SI{\1}{\%}", string)
    return string


def clean(string: str, keep_comments: bool = False, keep_dollar: bool = False) -> str:
    out = string
    out = _remove_trailing_whitespace(out)
    if not keep_comments:
        out = _remove_comments(out)
    out = _replace_dollar_dollar(out)
    if not keep_dollar:
        out = _replace_dollar(out)
    out = _replace_punctuation_at_math_end(out)
    out = _replace_obsolete_text_mods(out)
    out = _add_space_after_single_subsuperscript(out)
    out = _replace_dots(out)
    out = _remove_whitespace_before_punctuation(out)
    out = _add_nbsp_before_reference(out)
    out = _replace_double_nbsp(out)
    out = _replace_nbsp_space(out)
    out = _replace_over(out)
    out = _si_percentage(out)
    out = _add_linebreak_after_double_backslash(out)
    out = _add_backslash_for_keywords(out)
    out = _replace_def_by_newcommand(out)
    out = _add_linebreak_around_begin_end(out)
    out = _replace_centerline(out)
    out = _replace_eqnarray(out)
    out = _put_spec_on_same_line_as_environment(out)
    out = _put_label_on_same_line_as_environment(out)
    out = _replace_colon_equal_by_coloneqq(out)
    out = _remove_space_before_tabular_column_specification(out)
    out = _add_spaces_around_equality_sign(out)
    out = _remove_multiple_newlines(out)
    out = _remove_multiple_spaces(out)
    out = _remove_whitespace_around_brackets(out)
    return out
