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


def clean(string):

    out = string

    out = _remove_comments(out)
    out = _remove_trailing_whitespace(out)

    # Check for {\it ... }
    out = out.replace("{\\it ", "\\itshape{")

    # Replace multiple spaces by one
    out = re.sub(" +", " ", out)

    # TODO remove comments
    # TODO remove multiple newlines

    # Replace $$...$$ by \[...\]
    p = re.compile("\\$\\$")
    locations = [m.start() for m in p.finditer(out)]
    do_open = True
    offset = 0
    for loc in locations:
        insert = "\\[" if do_open else "\\]"
        off = 0
        if out[loc - 1 + offset] != "\n":
            insert = "\n" + insert
            off += 1
        if out[loc + 2 + offset] != "\n":
            insert += "\n"
            off += 1
        out = out[: loc + offset] + insert + out[loc + 2 + offset :]
        do_open = not do_open
        offset += off

    return out
