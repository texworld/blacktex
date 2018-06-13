# -*- coding: utf-8 -*-
#
import re


def clean(string):

    out = string

    # Check for {\it ... }
    out = out.replace("{\\it ", "\\itshape{")

    # Replace multiple spaces by one
    out = re.sub(" +", " ", out)

    # TODO remove trailing whitespace
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
