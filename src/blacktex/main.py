import re
from typing import Callable

from pylatexenc.latexwalker import (
    LatexCharsNode,
    LatexCommentNode,
    LatexEnvironmentNode,
    LatexGroupNode,
    LatexMacroNode,
    LatexMathNode,
    LatexWalker,
    nodelist_to_latex,
)
from pylatexenc.macrospec import ParsedMacroArgs


def _traverse_tree(nodelist: list, funs: list[Callable], is_math_mode: bool = False):
    for fun in funs:
        nodelist_new = []
        for k, node in enumerate(nodelist):
            out = fun(node, is_math_mode, nodelist[:k], nodelist[k + 1 :])
            if out is not None:
                nodelist_new.append(out)
        nodelist = nodelist_new

    for node in nodelist:
        if hasattr(node, "nodelist"):
            node.nodelist = _traverse_tree(
                node.nodelist, funs, is_math_mode | isinstance(node, LatexMathNode)
            )

    return nodelist


def _macro(macroname, *nodelists):
    """Creates a pylatexenc node that corresponds to \\macroname{nodelist}"""
    return LatexMacroNode(
        macroname=macroname,
        nodeargd=ParsedMacroArgs(
            argspec="{" * len(nodelists),
            argnlist=[LatexGroupNode(nodelist=nodelist) for nodelist in nodelists],
        ),
    )


def _remove_comments(node, *_):
    """Remove comments."""
    # TODO unless the comment character is the last non-whitespace character in
    # a line. (This is often used in macros etc.)
    if isinstance(node, LatexCommentNode):
        return None
    return node


def _replace_dollar_dollar(node, *_):
    """Replace $$...$$ by \\[...\\]."""
    if isinstance(node, LatexMathNode) and node.delimiters == ("$$", "$$"):
        node.delimiters = ("\\[", "\\]")
    return node


def _replace_dollar(node, *_):
    """Replace $...$ by \\(...\\). See <https://tex.stackexchange.com/q/510/13262>."""
    if isinstance(node, LatexMathNode) and node.delimiters == ("$", "$"):
        node.delimiters = ("\\(", "\\)")
    return node


def _replace_obsolete_text_mods(node, _, prev_nodes, __):
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
    if not isinstance(node, LatexGroupNode):
        return node
    # See if the first child in the group is a macro, e.g., {\it ...}
    child0 = node.nodelist[0]
    if not isinstance(child0, LatexMacroNode):
        return node

    for orig, repl in replacements:
        if child0.macroname == orig:
            node = _macro(repl, node.nodelist[1:])
            # If the previous node is a macro, wrap the \textit in curly braces.
            if len(prev_nodes) > 0 and isinstance(prev_nodes[-1], LatexMacroNode):
                node = LatexGroupNode(nodelist=[node])
            break

    return node


def _replace_dots(node, *_):
    if isinstance(node, LatexMacroNode) and node.macroname == "cdots":
        node.macroname = "dots"
    if isinstance(node, LatexCharsNode) and "..." in node.chars:
        node.chars = node.chars.replace("...", r"\dots")
    return node


def _replace_over(node, *_):
    if not isinstance(node, LatexGroupNode):
        return node

    k0 = None
    for k, n2 in enumerate(node.nodelist):
        if isinstance(n2, LatexMacroNode) and n2.macroname == "over":
            k0 = k
            break

    if k0 is None:
        return node

    # We found an \over. Create a \frac from the rest of the nodes.
    return _macro("frac", node.nodelist[:k0], node.nodelist[k0 + 1 :])


def _replace_def_by_newcommand(node, *_):
    if isinstance(node, LatexMacroNode) and node.macroname == "def":
        node.macroname = "newcommand"
    return node


def _add_backslash_for_keywords(node, is_math_mode, *_):
    if not is_math_mode:
        return node
    if not isinstance(node, LatexCharsNode):
        return node
    for keyword in ["max", "min", "log", "sin", "cos", "exp"]:
        node.chars = node.chars.replace(keyword, f"\\{keyword}")
    return node


def _replace_eqnarray(node, *_):
    if not isinstance(node, LatexEnvironmentNode):
        return node
    # Also set envname, should be removed at some point
    # TODO https://github.com/phfaist/pylatexenc/issues/81
    if node.environmentname == "eqnarray":
        node.environmentname = "align"
        node.envname = "align"
    elif node.environmentname == "eqnarray*":
        node.environmentname = "align*"
        node.envname = "align*"
    return node


def _replace_colon_equal_by_coloneqq(node, *_):
    if not isinstance(node, LatexCharsNode):
        return node
    node.chars = re.sub(r":\s*=", r"\\coloneqq ", node.chars)
    node.chars = re.sub(r"=\s*:", r"\\eqqcolon ", node.chars)
    return node


def _add_space_after_single_subsuperscript(node, *_):
    if not isinstance(node, LatexCharsNode):
        return node
    node.chars = re.sub(r"([\^])([^{\\])([^_\^\s\$})])", r"\1\2 \3", node.chars)
    return node


def _remove_whitespace_before_punctuation(node, *_):
    if not isinstance(node, LatexCharsNode):
        return node
    node.chars = re.sub(r"\s+([\.,;!\?\":])", r"\1", node.chars)
    return node


def _replace_double_nbsp(string: str) -> str:
    return re.sub("~~", r"\\quad ", string)


def _replace_centerline(string: str) -> str:
    return re.sub(r"\\centerline{", r"{\\centering ", string)


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


def _remove_space_before_tabular_column_specification(string: str) -> str:
    return re.sub(r"(\\begin{tabular})\s*({.*?})", r"\1\2", string)


def _remove_trailing_whitespace(string: str) -> str:
    return "\n".join([line.rstrip() for line in string.split("\n")])


def _remove_multiple_spaces(string: str) -> str:
    """Replaces multiple spaces by one, except after a newline."""
    return re.sub("([^\n ])  +", r"\1 ", string)


def _remove_multiple_newlines(string: str) -> str:
    string = re.sub("\n\n\n\n+", "\n\n\n", string)
    return string


def _remove_whitespace_around_brackets(string: str) -> str:
    string = re.sub(r"{[ \t]+", "{", string)
    string = re.sub(r"[ \t]+}", "}", string)
    string = re.sub(r"\([ \t]+", "(", string)
    string = re.sub(r"[ \t]+\)", ")", string)
    string = re.sub(r"[ \t]+\\right\)", r"\\right)", string)
    return string


def _add_nbsp_before_reference(string: str) -> str:
    string = re.sub(r"\s+\\ref{", r"~\\ref{", string)
    string = re.sub(r"\s+\\eqref{", r"~\\eqref{", string)
    string = re.sub(r"\s+\\cite", r"~\\cite", string)
    return string


def _replace_nbsp_space(string: str) -> str:
    string = re.sub("~ ", " ", string)
    string = re.sub(" ~", " ", string)
    return string


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


def _put_spec_on_same_line_as_environment(string: str) -> str:
    string = re.sub(r"(\\begin{.*?})\s*(\[.*?\])\n", r"\1\2", string)
    string = re.sub(r"(\\begin{.*?})\s*(\[.*?\])([^\n])", r"\1\2\n\3", string)
    return string


def _put_label_on_same_line_as_environment(string: str) -> str:
    out = re.sub(r"(\\begin{.*?})(\[.*?])?\s+(\\label{.*?})(\n)?", r"\1\2\3\4", string)
    out = re.sub(r"(\\section{.*?})\s+(\\label{.*?})(\n)?", r"\1\2\3", out)
    out = re.sub(r"(\\subsection{.*?})\s+(\\label{.*?})(\n)?", r"\1\2\3", out)
    return out


def _add_linebreak_after_double_backslash(string: str) -> str:
    return re.sub(r"\\\\([^\n])", r"\\\\\n\1", string)


def _replace_punctuation_at_math_end(string: str) -> str:
    """$a+b.$  ->  $a+b$."""
    return re.sub(r"([\.,;!\?])\\\)", r"\)\1", string)


def clean(string: str, keep_comments: bool = False, keep_dollar: bool = False) -> str:
    out = string
    out = _remove_trailing_whitespace(out)

    # now apply all functions that operate on the pylatexenc tree
    funs = []
    if not keep_comments:
        funs.append(_remove_comments)
    funs.append(_replace_dollar_dollar)
    if not keep_dollar:
        funs.append(_replace_dollar)
    funs += [
        _replace_obsolete_text_mods,
        _replace_dots,
        _replace_over,
        _replace_def_by_newcommand,
        _add_backslash_for_keywords,
        _replace_eqnarray,
        _replace_colon_equal_by_coloneqq,
        _add_space_after_single_subsuperscript,
        _remove_whitespace_before_punctuation,
    ]
    #
    w = LatexWalker(out)
    nodelist, _, _ = w.get_latex_nodes(pos=0)
    nodelist = _traverse_tree(nodelist, funs)
    out = nodelist_to_latex(nodelist)

    out = _replace_punctuation_at_math_end(out)
    out = _add_nbsp_before_reference(out)
    out = _replace_double_nbsp(out)
    out = _replace_nbsp_space(out)
    out = _si_percentage(out)
    out = _add_linebreak_after_double_backslash(out)
    out = _add_linebreak_around_begin_end(out)
    out = _replace_centerline(out)
    out = _put_spec_on_same_line_as_environment(out)
    out = _put_label_on_same_line_as_environment(out)
    out = _remove_space_before_tabular_column_specification(out)
    out = _add_spaces_around_equality_sign(out)
    out = _remove_multiple_newlines(out)
    out = _remove_multiple_spaces(out)
    out = _remove_whitespace_around_brackets(out)
    return out
