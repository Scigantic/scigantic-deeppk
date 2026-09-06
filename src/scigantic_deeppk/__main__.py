"""Enables `python -m scigantic_deeppk`, same commands as the `scigantic-deeppk` console script."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
