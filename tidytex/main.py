# -*- coding: utf-8 -*-
#
import re


def _remove_comments(string):
    # https://stackoverflow.com/a/2319116/353337
    string = re.sub(re.compile("^ *%.*?\n"), "", string)
    string = re.sub(re.compile("\n *%.*?\n"), "\n", string)
    string = re.sub(re.compile("\n *%.*?$"), "\n", string)
    #
    string = re.sub(re.compile("%.*?\n"), "\n", string)
    string = re.sub(re.compile("%.*?$"), "", string)
    return string


def _remove_trailing_whitespace(string):
    string = re.sub(" +\n", "\n", string)
    string = re.sub(" +$", "", string)
    return string


def _remove_multiple_spaces(string):
    return re.sub(" +", " ", string)


def _remove_multiple_newlines(string):
    string = re.sub("\n\n\n", "\n\n", string)
    return string


def _remove_whitespace_after_curly(string):
    string = re.sub("{\s+", "{", string)
    return string


def _replace_dollar_dollar(string):
    """Replace $$...$$ by \[...\].
    """
    p = re.compile("\\$\\$")
    locations = [m.start() for m in p.finditer(string)]
    do_open = True
    offset = 0
    for loc in locations:
        insert = "\\[" if do_open else "\\]"
        off = 0
        if string[loc - 1 + offset] != "\n":
            insert = "\n" + insert
            off += 1
        if string[loc + 2 + offset] != "\n":
            insert += "\n"
            off += 1
        string = string[: loc + offset] + insert + string[loc + 2 + offset :]
        do_open = not do_open
        offset += off
    return string


def _replace_obsolete_text_mods(string):
    string = string.replace("{\\bf ", "\\textbf{")
    string = string.replace("{\\it ", "\\textit{")
    string = string.replace("{\\rm ", "\\textrm{")
    string = string.replace("{\\sc ", "\\textsc{")
    string = string.replace("{\\sf ", "\\textsf{")
    string = string.replace("{\\sl ", "\\textsl{")
    string = string.replace("{\\tt ", "\\texttt{")
    return string


def _add_space_after_single_exponent(string):
    string = re.sub("\\^([^{])([^ ])", "^\\1 \\2", string)
    return string


def _replace_dots(string):
    string = re.sub("\.\.\.", "\\dots", string)
    string = re.sub("\\\\ldots", "\\\\dots", string)
    string = re.sub("\\\\cdots", "\\\\dots", string)
    return string


def _replace_punctuation_outside_math(string):
    string = re.sub("\\.\\$", "$.", string)
    string = re.sub(",\\$", "$,", string)
    string = re.sub(";\\$", "$;", string)
    string = re.sub("!\\$", "$!", string)
    string = re.sub("\?\\$", "$?", string)
    return string


def _remove_whitespace_before_punctuation(string):
    string = re.sub("\s+\.", ".", string)
    string = re.sub("\s+,", ",", string)
    string = re.sub("\s+;", ";", string)
    string = re.sub("\s+!", "!", string)
    string = re.sub("\s+\?", "?", string)
    return string


def _add_nbsp_before_reference(string):
    string = re.sub("\s+\\\\ref{", "~\\\\ref{", string)
    string = re.sub("\s+\\\\eqref{", "~\\\\eqref{", string)
    string = re.sub("\s+\\\\cite", "~\\\\cite", string)
    return string


def _replace_double_nbsp(string):
    string = re.sub("~~", "\\quad ", string)
    return string


def _substitute_string_ranges(string, ranges, replacements):
    if ranges:
        lst = [string[: ranges[0][0]]]
        for k, replacement in enumerate(replacements[:-1]):
            lst += [replacement, string[ranges[k][1] + 1 : ranges[k + 1][0]]]
        lst += [replacements[-1], string[ranges[-1][1] + 1 :]]
        string = "".join(lst)
    return string


def _replace_over(string):
    p = re.compile("\\\\over")
    locations = [m.start() for m in p.finditer(string)]

    fracs = []
    ranges = []

    for loc in locations:
        # Starting from loc, search to the left for an open {
        num_open_brackets = 1
        k0 = loc
        while num_open_brackets > 0:
            if string[k0] == "{":
                num_open_brackets -= 1
            elif string[k0] == "}":
                num_open_brackets += 1
            k0 -= 1
        numerator = string[k0 + 2 : loc].strip()

        # Starting from loc+5, search to the right for an open }
        num_open_brackets = 1
        k1 = loc + 5
        while num_open_brackets > 0:
            if string[k1] == "}":
                num_open_brackets -= 1
            elif string[k1] == "{":
                num_open_brackets += 1
            k1 += 1
        denominator = string[loc + 5 : k1 - 1].strip()

        fracs.append((numerator, denominator))
        ranges.append((k0 + 1, k1 - 1))

    fracs = ["\\frac{{{}}}{{{}}}".format(num, den) for num, den in fracs]

    return _substitute_string_ranges(string, ranges, fracs)


def clean(string):
    out = string
    out = _remove_comments(out)
    out = _remove_trailing_whitespace(out)
    out = _remove_multiple_newlines(out)
    out = _remove_multiple_spaces(out)
    out = _replace_dollar_dollar(out)
    out = _replace_obsolete_text_mods(out)
    out = _remove_whitespace_after_curly(out)
    out = _add_space_after_single_exponent(out)
    out = _replace_dots(out)
    out = _replace_punctuation_outside_math(out)
    out = _remove_whitespace_before_punctuation(out)
    out = _add_nbsp_before_reference(out)
    out = _replace_double_nbsp(out)
    out = _replace_over(out)
    return out
