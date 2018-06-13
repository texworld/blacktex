# -*- coding: utf-8 -*-
#
import re


def _remove_comments(string):
    # https://stackoverflow.com/a/2319116/353337
    # remove all occurance singleline comments (//COMMENT\n ) from string
    string = re.sub(re.compile("%.*?\n") , "\n", string)
    string = re.sub(re.compile("%.*?$") , "", string)
    return string


def _remove_trailing_whitespace(string):
    string = re.sub(" +\n", "\n", string)
    string = re.sub(" +$", "", string)
    return string


def _remove_multiple_spaces(string):
    return re.sub(" +", " ", string)


def _replace_dollar_dollar(string):
    '''Replace $$...$$ by \[...\].
    '''
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


def clean(string):
    out = string

    out = _remove_comments(out)
    out = _remove_trailing_whitespace(out)
    out = _remove_multiple_spaces(out)
    out = _replace_dollar_dollar(out)
    out = _replace_obsolete_text_mods(out)

    # TODO remove multiple newlines

    return out
