import argparse
import sys

import blacktex


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    out = blacktex.clean(args.infile.read(), args.keep_comments, args.keep_dollar_math)

    if args.in_place:
        with open(args.infile.name, "w") as f:
            f.write(out)
    else:
        args.outfile.write(out)


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

    parser.add_argument(
        "-i", "--in-place", action="store_true", help="modify infile in place"
    )

    parser.add_argument(
        "-c", "--keep-comments", action="store_true", help="keep comments"
    )

    parser.add_argument(
        "-d",
        "--keep-dollar-math",
        action="store_true",
        help="keep inline math with $...$",
    )

    version_text = "blacktex {}, Python {}.{}.{}".format(
        blacktex.__version__,
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    parser.add_argument("--version", "-v", action="version", version=version_text)

    return parser
