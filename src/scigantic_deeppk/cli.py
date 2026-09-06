"""Command-line interface: `scigantic-deeppk predict` and `scigantic-deeppk cyp-reference`."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence, cast

from . import ISOFORMS, KINDS, PRED_TYPES
from . import cyp_reference as run_cyp_reference
from . import predict as run_predict


def _cmd_predict(args: argparse.Namespace) -> int:
    df = run_predict(args.smiles, pred_type=args.pred_type, timeout=args.timeout)
    print(df.to_csv(sep="\t", index=False), end="")
    return 0


def _cmd_cyp_reference(args: argparse.Namespace) -> int:
    df = run_cyp_reference(isoform=args.isoform, kind=args.kind)
    print(df.to_csv(sep="\t", index=False), end="")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="scigantic-deeppk")
    subparsers = parser.add_subparsers(dest="command", required=True)

    predict_parser = subparsers.add_parser(
        "predict", help="submit one or more SMILES to Deep-PK and print predictions"
    )
    predict_parser.add_argument("smiles", nargs="+")
    predict_parser.add_argument("--pred-type", choices=PRED_TYPES, default="admet")
    predict_parser.add_argument("--timeout", type=float, default=300.0)
    predict_parser.set_defaults(
        func=lambda a: _cmd_predict(
            argparse.Namespace(
                smiles=a.smiles[0] if len(a.smiles) == 1 else a.smiles,
                pred_type=a.pred_type,
                timeout=a.timeout,
            )
        )
    )

    ref_parser = subparsers.add_parser(
        "cyp-reference", help="print Deep-PK's own mirrored CYP450 inhibitor/substrate data"
    )
    ref_parser.add_argument("--isoform", choices=ISOFORMS, default=None)
    ref_parser.add_argument("--kind", choices=KINDS, default=None)
    ref_parser.set_defaults(func=_cmd_cyp_reference)

    args = parser.parse_args(argv)
    return cast(int, args.func(args))


if __name__ == "__main__":
    sys.exit(main())
