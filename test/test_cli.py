import tempfile
from pathlib import Path

import blacktex


def test_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        infile = tmpdir / "in.tex"
        with open(infile, "w") as f:
            f.write("a+b=c")

        stdout = blacktex.cli.main([str(infile)])

        assert stdout == "a+b = c"
