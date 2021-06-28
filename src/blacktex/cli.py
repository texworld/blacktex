import argparse
import sys

import blacktex


def main(argv=None):
    parser = _get_parser()
    args = parser.parse_args(argv)

    if len(args.infiles) and not args.allow_multiple_files:
        print(
            "Too many files, the '-m' needs to be set to use multiple files.",
            file=sys.stderr,
        )
        return 1

    if args.allow_multiple_files and args.infile is sys.stdin:
        print(
            "Too few files, multiple file mode needs at least one file.",
            file=sys.stderr,
        )
        return 1

    elif args.allow_multiple_files:
        infile = [args.infile, args.outfile, *args.infiles]
    else:
        infile = args.infile

    return_values = blacktex.process_file(
        infile,
        args.outfile,
        args.in_place,
        args.keep_comments,
        args.keep_dollar_math,
        args.encoding,
    )

    return int(any(return_values))


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
        type=argparse.FileType("a+"),
        default=sys.stdout,
        help="output LaTeX file (default: stdout)",
    )

    parser.add_argument(
        "infiles",
        nargs="*",
        type=argparse.FileType("r"),
        default=[],
        help="list of files to process (needs '-m' flag)",
    )

    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        default=None,
        help="encoding to use for reading and writing files",
    )

    parser.add_argument(
        "-i", "--in-place", action="store_true", help="modify infile in place"
    )

    parser.add_argument(
        "-m",
        "--allow-multiple-files",
        action="store_true",
        help="allows passing multiple input files and activates in-place mode",
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
