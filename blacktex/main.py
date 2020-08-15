from abc import ABC, abstractmethod
import re
import warnings


class TexString:
    def __init__(self, string):
        self.string = string


class Command(ABC):
    def __init__(self, receiver):
        self.receiver = receiver

    @abstractmethod
    def execute(self):
        pass

    def find_locations(self, pattern):
        p = re.compile(pattern)
        return [m.start() for m in p.finditer(self.receiver.string)]

    def do_replace(self, mapping):
        for match_pattern, replacement_pattern in mapping.items():
            self.receiver.string = re.sub(
                match_pattern, replacement_pattern, self.receiver.string,
            )

    @staticmethod
    def substitute_string_ranges(string, ranges, replacements):
        if ranges:
            lst = [string[: ranges[0][0]]]
            for k, replacement in enumerate(replacements[:-1]):
                lst += [replacement, string[ranges[k][1] : ranges[k + 1][0]]]
            lst += [replacements[-1], string[ranges[-1][1] :]]
            string = "".join(lst)
        return string


class RemoveComments(Command):
    def execute(self):
        self._drop_commented_lines()
        # https://stackoverflow.com/a/2319116/353337
        mapping = {
            "%.*?\n": "\n",
            "%.*?$": "",
        }
        self.do_replace(mapping)

    def _drop_commented_lines(self):
        self.receiver.string = "".join(
            [
                line
                for line in self.receiver.string.splitlines(True)
                if not self._is_commented_line(line)
            ]
        )

    @staticmethod
    def _is_commented_line(line):
        return line.lstrip().startswith("%")


class RemoveTrailingWhitespace(Command):
    def execute(self):
        mapping = {
            r"[ \t]+(\n|\Z)": r"\1",
        }
        self.do_replace(mapping)


class RemoveMultipleSpaces(Command):
    def execute(self):
        """Replace multiple spaces by one, except after a newline."""
        mapping = {"([^\n ])  +": r"\1 "}
        self.do_replace(mapping)


class RemoveMultipleNewlines(Command):
    def execute(self):
        mapping = {"\n\n\n\n": "\n\n\n"}
        self.do_replace(mapping)


class RemoveWhitespaceAroundBrackets(Command):
    def execute(self):
        mapping = {
            r"{\s+": "{",
            r"\s+}": "}",
            r"\(\s+": "(",
            r"\s+\)": ")",
            r"\s+\\right\)": r"\\right)",
        }
        self.do_replace(mapping)


class ReplaceDoubleDollarInline(Command):
    def execute(self):
        """Replace $$...$$ with \\[...\\]."""
        if self.locations:
            self._make_replacements()

    @property
    def locations(self):
        locations = self.find_locations(r"\$\$")
        if len(locations) % 2 != 0:
            excerpt = self.receiver.string[locations[0] : 20]
            msg = f"Unmatching number of double dollar signs\n{excerpt}"
            raise ValueError(msg)
        return locations

    def _make_replacements(self):
        assert len(self.locations) % 2 == 0
        while self.locations:
            start_idx, end_idx = self._find_range()

            replacement_str = self._find_replacement()
            preceding = self.receiver.string[:start_idx].rstrip()
            following = self.receiver.string[end_idx:].lstrip()
            self.receiver.string = "".join([preceding, replacement_str, following])

    def _find_range(self):
        return (self.locations[0], self.locations[1] + 2)

    def _find_replacement(self):
        start_idx = self.locations[0] + 2
        end_idx = self.locations[1]
        inner_content = self.receiver.string[start_idx:end_idx].strip()
        return "\n".join(["", r"\[", inner_content, r"\]", ""])


class ReplaceObsoleteTextMods(Command):
    def execute(self):
        mapping = {
            r"{\\bf\s+(.*)\}": r"\\textbf{\1}",
            r"{\\it\s+(.*)\}": r"\\textit{\1}",
            r"{\\rm\s+(.*)\}": r"\\textrm{\1}",
            r"{\\sc\s+(.*)\}": r"\\textsc{\1}",
            r"{\\sf\s+(.*)\}": r"\\textsf{\1}",
            r"{\\sl\s+(.*)\}": r"\\textsl{\1}",
            r"{\\tt\s+(.*)\}": r"\\texttt{\1}",
            # https://tex.stackexchange.com/a/25914/13262:
            # [\em] May be useful when defining macros.
            # In continuous text \emph{...} should be
            # preferred to \em.
            r"{\\em\s+(.*)\}": r"\\emph{\1}",
        }
        self.do_replace(mapping)


class AddSpaceAfterSingleSubsuperscript(Command):
    def execute(self):
        mapping = {
            "([_\\^])([^{\\\\])([^_\\^\\s\\$})])": r"\1\2 \3",
        }
        self.do_replace(mapping)


class ReplaceDots(Command):
    def execute(self):
        mapping = {
            "\\.\\.\\.": "\\\\dots",
            ",\\\\cdots,": ",\\\\dots,",
        }
        self.do_replace(mapping)


class ReplacePunctuationOutsideMath(Command):
    def execute(self):
        mapping = {
            "\\.\\$": "$.",
            ",\\$": "$,",
            ";\\$": "$;",
            "!\\$": "$!",
            "\\?\\$": "$?",
        }
        self.do_replace(mapping)


class RemoveWhitespaceBeforePunctuation(Command):
    def execute(self):
        mapping = {
            "\\s+\\.": ".",
            "\\s+,": ",",
            "\\s+;": ";",
            "\\s+!": "!",
            "\\s+\\?": "?",
        }
        self.do_replace(mapping)


class AddNonBreakingSpaceBeforeReference(Command):
    def execute(self):
        mapping = {
            "\\s+\\\\ref{": "~\\\\ref{",
            "\\s+\\\\eqref{": "~\\\\eqref{",
            "\\s+\\\\cite": "~\\\\cite",
        }
        self.do_replace(mapping)


class ReplaceDoubleNonBreakingSpace(Command):
    def execute(self):
        mapping = {"~~": "\\\\quad "}
        self.do_replace(mapping)


class ReplaceNonBreakingSpace(Command):
    def execute(self):
        mapping = {
            "~ ": " ",
            " ~": " ",
        }
        self.do_replace(mapping)


class ReplaceOver(Command):
    def execute(self):
        locations = self.find_locations("\\\\over[^a-z]")
        ranges, replacements = self._find_ranges_and_replacements(locations)
        self.receiver.string = self.substitute_string_ranges(
            self.receiver.string, ranges, replacements,
        )

    def _find_ranges_and_replacements(self, locations):
        frac_values = []
        ranges = []

        for loc in locations:
            range_and_frac_pair = self._find_range_and_frac_pair(
                loc, self.receiver.string,
            )
            if range_and_frac_pair:
                range_, frac_pair = range_and_frac_pair
                ranges.append(range_)
                frac_values.append(frac_pair)
            else:
                continue

        replacements = [f"\\frac{{{num}}}{{{den}}}" for num, den in frac_values]

        return ranges, replacements

    def _find_range_and_frac_pair(self, location, string):
        skip = False

        # Starting from loc, search to the left for an open {
        num_open_brackets = 1
        k0 = location - 1
        while num_open_brackets > 0:
            try:
                char0 = string[k0]
            except IndexError:
                skip = True
                break

            if char0 == "{":
                num_open_brackets -= 1
            elif char0 == "}":
                num_open_brackets += 1
            k0 -= 1

        if skip:
            warning = (
                "Could not convert \\over to \\frac at \n```\n"
                + string[max(0, location - 20) : location + 24]
                + "\n```\n"
            )
            warnings.warn(warning)
            return

        numerator = string[k0 + 2 : location].strip()

        # Starting from location+5, search to the right for an open }
        num_open_brackets = 1
        k1 = location + 5
        while num_open_brackets > 0:
            if string[k1] == "}":
                num_open_brackets -= 1
            elif string[k1] == "{":
                num_open_brackets += 1
            k1 += 1
        denominator = string[location + 5 : k1 - 1].strip()

        frac_pair = (numerator, denominator)
        range_ = (k0 + 1, k1)
        return range_, frac_pair


class AddLineBreakAfterDoubleBackslash(Command):
    def execute(self):
        mapping = {r"\\\\([^\n])": r"\\\\\n\1"}
        self.do_replace(mapping)


class AddBackslashForKeywords(Command):
    def execute(self):
        ranges, replacements = self._find_ranges_and_replacements()
        self.receiver.string = self.substitute_string_ranges(
            self.receiver.string, ranges, replacements,
        )

    def _find_ranges_and_replacements(self):
        where_to_insert = []
        for keyword in ["max", "min", "log", "sin", "cos", "exp"]:
            pattern = fr"[^A-Za-z]{keyword}[^A-Za-z]"
            for loc in self.find_locations(pattern):
                if self.receiver.string[loc] != "\\":
                    where_to_insert.append(loc)

        ranges = [(i + 1, i + 1) for i in where_to_insert]

        replacements = len(where_to_insert) * ["\\"]
        return ranges, replacements


class AddCurlyBracketsAroundRoundBracketsWithExp(Command):
    def execute(self):
        locations = self.find_locations(r"\)\^")
        ranges, replacements = self._find_ranges_and_replacements(locations)
        self.receiver.string = self.substitute_string_ranges(
            self.receiver.string, ranges, replacements,
        )

    def _find_ranges_and_replacements(self, locations):
        insert = []
        replacements = []
        for loc in locations:
            # Starting from loc, search to the left for an open (
            num_open_brackets = 1
            k = loc - 1
            while num_open_brackets > 0:
                if self.receiver.string[k] == "(":
                    num_open_brackets -= 1
                elif self.receiver.string[k] == ")":
                    num_open_brackets += 1
                k -= 1
            k += 1

            if k - 5 >= 0 and self.receiver.string[k - 5 : k] == "\\left":
                insert.append(k - 5)
            else:
                insert.append(k)
            replacements.append("{")

            insert.append(loc + 1)
            replacements.append("}")

        ranges = [(i, i) for i in insert]
        return ranges, replacements


class ReplaceDefWithNewcommand(Command):
    def execute(self):
        ranges, replacements = self._find_ranges_and_replacements()
        self.receiver.string = self.substitute_string_ranges(
            self.receiver.string, ranges, replacements,
        )

    def _find_ranges_and_replacements(self):
        p = re.compile(r"\\def\\[A-Za-z]+")

        ranges = []
        replacements = []
        for m in p.finditer(self.receiver.string):
            ranges.append((m.start(), m.end()))
            replacements.append(
                "\\newcommand{{{}}}".format(
                    self.receiver.string[m.start() + 4 : m.end()]
                )
            )
        return ranges, replacements


class AddLineBreakAroundBeginEnd(Command):
    def execute(self):
        mapping = {
            r"([^\n ]) *(\\begin{.*?})": r"\1\n\2",
            r"(\\begin{.*?}) *([^\n ])": r"\1\n\2",
            r"([^\n ]) *(\\end{.*?})": r"\1\n\2",
            r"(\\end{.*?}) *([^\n ])": r"\1\n\2",
            r"([^\n ]) *(\\\[)": r"\1\n\2",
            r"(\\\[) *([^\n ])": r"\1\n\2",
            r"([^\n ]) *(\\\])": r"\1\n\2",
            r"(\\\]) *([^\n ])": r"\1\n\2",
        }
        self.do_replace(mapping)


class ReplaceCenterLine(Command):
    def execute(self):
        mapping = {r"\\centerline{": r"{\\centering "}
        self.do_replace(mapping)


class ReplaceEqnarray(Command):
    def execute(self):
        mapping = {"eqnarray": "align"}
        self.do_replace(mapping)


class PutSpecOnSameLineAsEnvironment(Command):
    def execute(self):
        mapping = {
            r"(\\begin{.*?})\s*(\[.*?\])\n": r"\1\2",
            r"(\\begin{.*?})\s*(\[.*?\])([^\n])": r"\1\2\n\3",
        }
        self.do_replace(mapping)


class PutLabelOnSameLineAsEnvironment(Command):
    def execute(self):
        mapping = {
            r"(\\begin{.*?})(\[.*?])?\s+(\\label{.*?})(\n)?": r"\1\2\3\4",
            r"(\\section{.*?})\s+(\\label{.*?})(\n)?": r"\1\2\3",
            r"(\\subsection{.*?})\s+(\\label{.*?})(\n)?": r"\1\2\3",
        }
        self.do_replace(mapping)


class ReplaceColonEqualWithColoneqq(Command):
    def execute(self):
        mapping = {
            r":\s*=\s*": r"\\coloneqq ",
            r"=\s*:\s*": r"\\eqqcolon ",
        }
        self.do_replace(mapping)


class RemoveSpaceBeforeTabularColumnSpecification(Command):
    def execute(self):
        mapping = {r"(\\begin{tabular})\s*({.*?})": r"\1\2"}
        self.do_replace(mapping)


class AddSpaceAroundEqualitySign(Command):
    def execute(self):
        mapping = {
            r"([^\s&])=": r"\1 =",
            r"([^\s])&=": r"\1 &=",
            r"=([^\s&])": r"= \1",
            r"=&([^\s])": r"=& \1",
        }
        self.do_replace(mapping)


def clean(string):
    receiver = TexString(string)
    commands = [
        RemoveComments(receiver),
        RemoveTrailingWhitespace(receiver),
        RemoveMultipleSpaces(receiver),
        RemoveMultipleNewlines(receiver),
        RemoveWhitespaceAroundBrackets(receiver),
        ReplaceDoubleDollarInline(receiver),
        ReplaceObsoleteTextMods(receiver),
        AddSpaceAfterSingleSubsuperscript(receiver),
        ReplaceDots(receiver),
        ReplacePunctuationOutsideMath(receiver),
        RemoveWhitespaceBeforePunctuation(receiver),
        AddNonBreakingSpaceBeforeReference(receiver),
        ReplaceDoubleNonBreakingSpace(receiver),
        ReplaceNonBreakingSpace(receiver),
        ReplaceOver(receiver),
        AddLineBreakAfterDoubleBackslash(receiver),
        AddBackslashForKeywords(receiver),
        AddCurlyBracketsAroundRoundBracketsWithExp(receiver),
        ReplaceDefWithNewcommand(receiver),
        AddLineBreakAroundBeginEnd(receiver),
        ReplaceCenterLine(receiver),
        ReplaceEqnarray(receiver),
        PutSpecOnSameLineAsEnvironment(receiver),
        PutLabelOnSameLineAsEnvironment(receiver),
        ReplaceColonEqualWithColoneqq(receiver),
        RemoveSpaceBeforeTabularColumnSpecification(receiver),
        AddSpaceAroundEqualitySign(receiver),
    ]
    [c.execute() for c in commands]
    return receiver.string
