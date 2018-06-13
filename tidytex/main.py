# -*- coding: utf-8 -*-
#


def clean(string):

    out = string

    # Check for {\it ... }
    out = out.replace("{\\it ", "\\itshape{")
    return out
