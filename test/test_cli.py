import tempfile

import blacktex


def test_cli():
    infile = tempfile.NamedTemporaryFile().name
    with open(infile, "w") as f:
        f.write("a+b=c")

    outfile = tempfile.NamedTemporaryFile().name

    blacktex.cli.main([infile, outfile])

    with open(outfile) as f:
        line = f.read()
        assert line == "a+b = c"

    return
