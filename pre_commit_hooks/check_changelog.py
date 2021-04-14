import argparse
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = []) -> int:
    parser = argparse.ArgumentParser("Check and update changelog information in various formats.")
    parser.add_argument("filenames", nargs="*", help="Filenames to check")

    args = parser.parse_args(argv)

    return 0


if __name__ == "__main__":
    exit(main())
