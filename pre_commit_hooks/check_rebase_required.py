import argparse
import git
import os
import re
from typing import Optional
from typing import Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser("Check if current branch requires rebase.")
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    parser.add_argument(
        "--branch",
        type=str,
        default="main",
        help="The base branch to compare to the local active branch.",
    )
    parser.add_argument(
        "--max-behind-commits",
        type=int,
        default=0,
        help="Max number of commits branch can be behind before rebase is required.",
    )
    parser.add_argument(
        "--remote",
        type=str,
        default="origin",
        help="The remote to compare to the local branch.",
    )
    parser.add_argument(
        "--repository",
        type=str,
        default=".",
        help="The folder containing the repository to check.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extra verbose information when rebase is required."
    )

    args = parser.parse_args(argv)

    retval = 0

    repository = git.Repo(args.repository)
    active_branch = repository.head.reference
    base_commit = repository.git.merge_base(args.branch, active_branch)
    behind = int(repository.git.rev_list("--left-only", "--count", "%s...%s" % (args.branch, active_branch)))
    commits = repository.git.rev_list("--left-only", "--pretty=oneline", "%s...%s" % (args.branch, active_branch))

    if (behind > args.max_behind_commits):
        retval = 1
        print("Active branch '%s' is behind '%s' by %s commits and should be rebased." % (active_branch, args.branch, behind))

        if (args.verbose):
            print()
            print("  Branched from: %s" % base_commit)
            print()
            print("  Commits:")
            print()
            print("    %s" % commits.replace("\n", "\n    "))

    return retval


if __name__ == "__main__":
    main()
