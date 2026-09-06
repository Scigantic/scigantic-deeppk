import pytest

import scigantic_deeppk as deeppk

_ASPIRIN = "CC(=O)OC1=CC=CC=C1C(=O)O"


def test_invalid_pred_type_raises():
    with pytest.raises(ValueError):
        deeppk.predict(_ASPIRIN, pred_type="not_a_real_pred_type")


def test_single_molecule_metabolism_prediction():
    df = deeppk.predict(_ASPIRIN, pred_type="metabolism", poll_interval=8, timeout=180)
    assert len(df) == 1
    assert df["SMILES"].iloc[0] == _ASPIRIN
    assert "[Metabolism/CYP 3A4 Inhibitor] Predictions" in df.columns


def test_batch_prediction_returns_one_row_per_molecule():
    smiles = [_ASPIRIN, "CC(C)Cc1ccc(cc1)C(C)C(=O)O"]  # aspirin, ibuprofen
    df = deeppk.predict(smiles, pred_type="metabolism", poll_interval=8, timeout=180)
    assert len(df) == 2
    assert list(df["SMILES"]) == smiles


def test_timeout_raises_before_job_ever_finishes():
    with pytest.raises(TimeoutError):
        deeppk.predict(_ASPIRIN, pred_type="admet", poll_interval=1, timeout=0.01)
