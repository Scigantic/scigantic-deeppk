# Changelog

All notable changes to this project are documented here. Versions correspond to PyPI releases.

## 0.1.0 - 2026-09-06

- Initial release: `predict()` submits SMILES to Deep-PK's live async job API (POST + poll by `job_id`) and returns predictions across its 73 ADMET/toxicity endpoints. `cyp_reference()` reads a mirrored copy of Deep-PK's own CYP1A2/2C9/2C19/2D6/3A4 inhibitor+substrate training data (105,695 rows).
