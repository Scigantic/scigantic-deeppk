"""Thin client for Deep-PK (biosig.lab.uq.edu.au/deeppk) plus a mirrored
CYP450 reference dataset.

Deep-PK ships no downloadable model or pip package, only a free async job
API (verified live: POST submits `smiles` or `smiles_file`, GET polls by
`job_id` until the job stops reporting `{"status": "running"}`) -- so
`predict()` always makes a network call, there is no local/offline mode.

`cyp_reference()` reads a small (~1.5MB, 105,695-row) parquet mirror of
Deep-PK's own CYP1A2/2C9/2C19/2D6/3A4 inhibitor+substrate training data,
hosted at MIRROR_URL -- useful for checking compound overlap against
another CYP dataset before trusting a transfer/leakage number.
"""

from __future__ import annotations

import json
import time
from typing import Optional, Sequence, Union

import pandas as pd
import requests

__version__ = "0.1.0"

API_URL = "https://biosig.lab.uq.edu.au/deeppk/api/predict"
MIRROR_URL = "https://groq-seq-align.s3.amazonaws.com/deeppk/cyp_reference.parquet"

PRED_TYPES = ("absorption", "distribution", "excretion", "metabolism", "toxicity", "admet")
ISOFORMS = ("cyp1a2", "cyp2c9", "cyp2c19", "cyp2d6", "cyp3a4")
KINDS = ("inhibitor", "substrate")

__all__ = [
    "predict",
    "cyp_reference",
    "DeepPKError",
    "PRED_TYPES",
    "ISOFORMS",
    "KINDS",
    "API_URL",
    "MIRROR_URL",
]


class DeepPKError(RuntimeError):
    """Deep-PK's API rejected a submission or a job failed."""


def predict(
    smiles: Union[str, Sequence[str]],
    pred_type: str = "admet",
    poll_interval: float = 5.0,
    timeout: float = 300.0,
) -> pd.DataFrame:
    """Submit one SMILES string or a list of them to Deep-PK, one row per molecule.

    Blocks until the job completes or `timeout` seconds pass -- Deep-PK has
    no synchronous endpoint, so there is no way to avoid the wait. A single
    molecule typically takes 30-90s; batches are not much slower per molecule.
    """
    if pred_type not in PRED_TYPES:
        raise ValueError(f"pred_type must be one of {PRED_TYPES}, got {pred_type!r}")

    if isinstance(smiles, str):
        resp = requests.post(API_URL, data={"smiles": smiles, "pred_type": pred_type}, timeout=30)
    else:
        csv_body = "smiles\n" + "\n".join(smiles) + "\n"
        resp = requests.post(
            API_URL,
            data={"pred_type": pred_type},
            files={"smiles_file": ("smiles.csv", csv_body, "text/csv")},
            timeout=30,
        )
    resp.raise_for_status()
    submission = resp.json()
    if "job_id" not in submission:
        raise DeepPKError(f"Deep-PK rejected the submission: {submission}")
    job_id = submission["job_id"]

    deadline = time.monotonic() + timeout
    while True:
        resp = requests.get(API_URL, data={"job_id": job_id}, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, str):
            result = json.loads(result)
        if isinstance(result, dict) and result.get("status") == "running":
            if time.monotonic() > deadline:
                raise TimeoutError(f"Deep-PK job {job_id} still running after {timeout}s")
            time.sleep(poll_interval)
            continue
        if not isinstance(result, dict) or "message" in result:
            raise DeepPKError(f"Deep-PK job {job_id} failed: {result}")
        break

    rows = [result[str(i)] for i in range(len(result))]
    return pd.DataFrame(rows)


def cyp_reference(isoform: Optional[str] = None, kind: Optional[str] = None) -> pd.DataFrame:
    """Load Deep-PK's own CYP450 inhibitor/substrate training data.

    `isoform` one of ISOFORMS, `kind` one of KINDS; leave either as None
    for every isoform/kind. Columns: isoform, kind, split (Deep-PK's own
    training/val/test), smiles, label (0/1).
    """
    if isoform is not None and isoform not in ISOFORMS:
        raise ValueError(f"isoform must be one of {ISOFORMS}, got {isoform!r}")
    if kind is not None and kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}, got {kind!r}")

    df = pd.read_parquet(MIRROR_URL)
    if isoform is not None:
        df = df[df["isoform"] == isoform]
    if kind is not None:
        df = df[df["kind"] == kind]
    return df.reset_index(drop=True)
