from pathlib import Path
from typing import List

import pytest
from _pytest.capture import CaptureFixture

import blacktex


@pytest.fixture()
def infiles(tmp_path: Path):
    tmp_files = [tmp_path / f"infile_{i}.tex" for i in range(1, 4)]
    [tmp_file.write_text(f"{tmp_file.name}\na+b=c") for tmp_file in tmp_files]
    yield tmp_files


def test_cli_stdout(infiles: List[Path], capsys: CaptureFixture):
    infile = infiles[0]

    return_value = blacktex.cli.main([str(infile)])

    sdtout, _ = capsys.readouterr()

    assert return_value == 0
    assert sdtout == "infile_1.tex\na+b = c"
    assert infile.read_text() == "infile_1.tex\na+b=c"


def test_cli_encoding(tmp_path: Path):
    infile = tmp_path / "infile_encoding.tex"
    result = "äöüéкий的"
    infile.write_text(result, encoding="utf8")

    return_value = blacktex.cli.main(["-i", "-e=utf8", str(infile)])

    assert return_value == 0
    assert infile.read_text(encoding="utf8") == result


def test_cli_inplace(infiles: List[Path]):
    infile = infiles[0]

    return_value = blacktex.cli.main(["-i", str(infile)])

    assert return_value == 1
    assert infile.read_text() == "infile_1.tex\na+b = c"


def test_cli_multiple_files(infiles: List[Path]):
    return_value = blacktex.cli.main(["-i", *[str(infile) for infile in infiles]])

    assert return_value == 1
    for infile in infiles:
        assert infile.read_text() == f"{infile.name}\na+b = c"
