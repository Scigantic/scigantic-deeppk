import pytest

import scigantic_deeppk as deeppk

# Row counts per isoform+kind, reproduced exactly from Deep-PK's own stated
# totals at biosig.lab.uq.edu.au/deeppk/data (checked 2026-09-06). Update if
# the mirror is ever refreshed from a newer Deep-PK release.
_EXPECTED_COUNTS = {
    ("cyp1a2", "inhibitor"): 19891,
    ("cyp1a2", "substrate"): 366,
    ("cyp2c19", "inhibitor"): 19652,
    ("cyp2c19", "substrate"): 261,
    ("cyp2c9", "inhibitor"): 19283,
    ("cyp2c9", "substrate"): 1034,
    ("cyp2d6", "inhibitor"): 19700,
    ("cyp2d6", "substrate"): 917,
    ("cyp3a4", "inhibitor"): 23040,
    ("cyp3a4", "substrate"): 1551,
}


def test_full_mirror_shape_and_columns():
    df = deeppk.cyp_reference()
    assert len(df) == sum(_EXPECTED_COUNTS.values())
    assert list(df.columns) == ["isoform", "kind", "split", "smiles", "label"]
    assert set(df["label"].unique()) <= {0, 1}


def test_filter_by_isoform_and_kind_matches_site_totals():
    for (isoform, kind), expected in _EXPECTED_COUNTS.items():
        df = deeppk.cyp_reference(isoform=isoform, kind=kind)
        assert len(df) == expected
        assert (df["isoform"] == isoform).all()
        assert (df["kind"] == kind).all()


def test_split_column_uses_deeppks_own_split():
    df = deeppk.cyp_reference("cyp3a4", "inhibitor")
    assert set(df["split"]) == {"training", "val", "test"}


def test_invalid_isoform_raises():
    with pytest.raises(ValueError):
        deeppk.cyp_reference(isoform="not_a_real_isoform")


def test_invalid_kind_raises():
    with pytest.raises(ValueError):
        deeppk.cyp_reference(kind="not_a_real_kind")
