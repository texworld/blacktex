import io
from pathlib import Path
from typing import List

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch

import blacktex


@pytest.fixture()
def infiles(tmp_path: Path):
    tmp_files = [tmp_path / f"infile_{i}.tex" for i in range(1, 4)]
    [tmp_file.write_text(f"{tmp_file.name}\na+b=c") for tmp_file in tmp_files]
    yield tmp_files


def test_cli_stdin(monkeypatch: MonkeyPatch, capsys: CaptureFixture):
    monkeypatch.setattr("sys.stdin", io.StringIO("stdin\na+b = c"))
    return_value = blacktex.cli.main([])

    sdtout, _ = capsys.readouterr()

    assert return_value == 0
    assert sdtout == "stdin\na+b = c"


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


def test_cli_outfile(infiles: List[Path], tmp_path: Path):
    infile = infiles[0]
    out_file = tmp_path / "out.tex"

    assert not out_file.exists()

    return_value = blacktex.cli.main([str(infile), str(out_file)])

    assert return_value == 1
    assert out_file.exists()
    assert out_file.read_text() == "infile_1.tex\na+b = c"


def test_cli_existing_outfile(infiles: List[Path], tmp_path: Path):
    infile = infiles[0]
    out_file = tmp_path / "out.tex"
    out_file.write_text("foo bar")

    assert out_file.exists()

    return_value = blacktex.cli.main([str(infile), str(out_file)])

    assert return_value == 1
    assert out_file.exists()
    assert out_file.read_text() == "infile_1.tex\na+b = c"


def test_cli_multiple_files_no_flag(infiles: List[Path], capsys: CaptureFixture):
    return_value = blacktex.cli.main([str(infile) for infile in infiles])

    _, stderr = capsys.readouterr()

    assert return_value == 1
    assert stderr == "Too many files, the '-m' needs to be set to use multiple files.\n"
    for infile in infiles:
        assert infile.read_text() == f"{infile.name}\na+b=c"


def test_cli_multiple_files_flag_stdin(infiles: List[Path], capsys: CaptureFixture):

    return_value = blacktex.cli.main(["-m"])

    _, stderr = capsys.readouterr()

    assert return_value == 1
    assert stderr == "Too few files, multiple file mode needs at least one file.\n"


def test_cli_multiple_files(infiles: List[Path]):
    return_value = blacktex.cli.main(["-m", *[str(infile) for infile in infiles]])

    assert return_value == 1
    for infile in infiles:
        assert infile.read_text() == f"{infile.name}\na+b = c"
