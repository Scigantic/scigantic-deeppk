import pytest

from scigantic_deeppk.cli import main


def test_cyp_reference_command_prints_tsv(capsys):
    rc = main(["cyp-reference", "--isoform", "cyp3a4", "--kind", "substrate"])
    assert rc == 0
    out = capsys.readouterr().out
    lines = out.strip().split("\n")
    assert lines[0].split("\t") == ["isoform", "kind", "split", "smiles", "label"]
    assert len(lines) == 1552  # header + 1551 rows


def test_no_command_errors():
    with pytest.raises(SystemExit):
        main([])


def test_invalid_isoform_choice_errors():
    with pytest.raises(SystemExit):
        main(["cyp-reference", "--isoform", "not_a_real_isoform"])
