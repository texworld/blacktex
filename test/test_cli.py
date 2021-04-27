import tempfile
from pathlib import Path

import blacktex


def test_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        infile = tmpdir / "in.tex"
        outfile = tmpdir / "out.tex"
        with open(infile, "w") as f:
            f.write("a+b=c")

        blacktex.cli.main([str(infile), str(outfile)])

        with open(outfile) as f:
            line = f.read()
            assert line == "a+b = c"
