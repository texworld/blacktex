import argparse
import sys

import blacktex


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    out = blacktex.clean(args.infile.read())
    args.outfile.write(out)
    return


def _get_parser():
    parser = argparse.ArgumentParser(description="Clean up LaTeX files.")

    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input LaTeX file (default: stdin)",
    )

    parser.add_argument(
        "outfile",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output LaTeX file (default: stdout)",
    )

    version_text = "blacktex {}, Python {}.{}.{}".format(
        blacktex.__version__,
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    parser.add_argument("--version", "-v", action="version", version=version_text)

    return parser
