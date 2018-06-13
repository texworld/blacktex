# -*- coding: utf-8 -*-
#
import re


def clean(string):

    out = string

    # Check for {\it ... }
    out = out.replace("{\\it ", "\\itshape{")

    # Replace multiple spaces by one
    out = re.sub(' +', ' ', out)
    return out
