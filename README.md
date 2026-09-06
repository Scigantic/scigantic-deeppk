<h1 align="center">scigantic-deeppk</h1>

<p align="center">
    <a href="https://github.com/Scigantic/scigantic-deeppk/actions/workflows/ci.yml">
        <img alt="CI" src="https://github.com/Scigantic/scigantic-deeppk/actions/workflows/ci.yml/badge.svg" /></a>
    <a href="https://pypi.org/project/scigantic-deeppk/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/scigantic-deeppk" /></a>
    <a href="https://pypi.org/project/scigantic-deeppk/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/scigantic-deeppk" /></a>
    <a href="https://github.com/Scigantic/scigantic-deeppk/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/github/license/Scigantic/scigantic-deeppk" /></a>
</p>

Client for [Deep-PK](https://biosig.lab.uq.edu.au/deeppk) (small-molecule pharmacokinetic and toxicity prediction across 73 endpoints), plus a mirrored copy of its CYP450 inhibitor/substrate reference data.

```python
import scigantic_deeppk as deeppk

df = deeppk.predict("CC(=O)OC1=CC=CC=C1C(=O)O", pred_type="metabolism")  # aspirin
```

## Installation

```console
$ pip install scigantic-deeppk
```

## Live predictions

Deep-PK ships no downloadable model or pip package, only a free async job API: POST submits SMILES, GET polls by `job_id` until the job finishes. `predict()` wraps that round trip and blocks until the result is ready:

```python
df = deeppk.predict("CC(=O)OC1=CC=CC=C1C(=O)O", pred_type="admet")

# Batch
df = deeppk.predict(["CCO", "CC(=O)OC1=CC=CC=C1C(=O)O"], pred_type="metabolism")
```

`pred_type` is one of `absorption`, `distribution`, `excretion`, `metabolism`, `toxicity`, `admet` (default, all 73 endpoints). A single molecule typically takes 30-90s; there is no synchronous endpoint, no documented rate limit, and no SLA, so this is fine for exploration but not for anything that needs to run offline or reproducibly.

The API's own docs page names the POST field `SMILES_string`; the field that actually works, found by testing against the live server, is lowercase `smiles` (`smiles_file` for a batch). `predict()` already gets this right, this is only worth knowing if you're calling the API directly.

## CYP450 reference data

Deep-PK's [data page](https://biosig.lab.uq.edu.au/deeppk/data) also publishes ~80 static training datasets, including CYP1A2/2C9/2C19/2D6/3A4 inhibitor and substrate sets. `cyp_reference()` reads a small (~1.5MB, 105,695-row) parquet mirror of just those ten, useful for e.g. checking compound overlap against another CYP dataset before trusting a transfer or leakage number:

```python
df = deeppk.cyp_reference("cyp3a4", "inhibitor")
df = deeppk.cyp_reference()  # every isoform and kind
```

Columns: `isoform` (one of `cyp1a2`/`cyp2c9`/`cyp2c19`/`cyp2d6`/`cyp3a4`), `kind` (`inhibitor`/`substrate`), `split` (Deep-PK's own `training`/`val`/`test` split), `smiles`, `label` (0/1). Row counts per isoform+kind reproduce Deep-PK's own stated totals exactly.

## Command line

```console
$ scigantic-deeppk predict "CC(=O)OC1=CC=CC=C1C(=O)O" --pred-type metabolism
$ scigantic-deeppk cyp-reference --isoform cyp3a4 --kind inhibitor
```

## License

MIT-0. See [LICENSE](LICENSE). This covers the code in this package only.

## Data license

Deep-PK's data page states the CYP450 datasets are "Open Knowledge" but publishes no formal license file or terms beyond that. `cyp_reference()`'s mirror reproduces that data as-is; check with the Ascher lab (biosig.lab.uq.edu.au/deeppk) before redistributing it further if that matters for your use.
