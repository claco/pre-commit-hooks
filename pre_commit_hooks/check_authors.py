import argparse
import git
import jinja2
import json
import os.path
import pkgutil
import re
from typing import Optional
from typing import Sequence


def fetch_authors(args):
    authors = []

    repository = git.Repo(args.repository)
    lines = repository.git.shortlog("--summary", "--email", "--numbered", "--all", "--no-merges").split("\n")

    for line in lines:
        line = line.strip()
        (count, name, email) = re.split("\s+(.*)\s+", line)
        count = int(count)
        email = re.sub("[<>]+", "", email)

        authors.append({"count": count, "name": name, "email": email, "type": "author"})

    if args.sort in ["count"]:
        reverse = True
    else:
        reverse = False

    authors = sorted(authors, key=lambda k: k[args.sort], reverse=reverse)

    return authors


def main(argv: Optional[Sequence[str]] = []) -> int:
    parser = argparse.ArgumentParser("Check and update authors information in various formats.")
    parser.add_argument("--authors-file", type=str, default="AUTHORS")
    parser.add_argument("--authors-format", type=str, default="text", choices=["text", "jinja"])
    parser.add_argument("--authors-template", type=str, default="AUTHORS.j2")
    parser.add_argument("--repository", type=str, default=".")
    parser.add_argument("--sort", type=str, default="count", choices=["count", "name", "email"])

    args = parser.parse_args(argv)
    authors = fetch_authors(args)

    if args.authors_format == "jinja" and args.authors_template:
        with open(args.authors_template) as file:
            template = file.read()
        template = jinja2.Template(template)
        contents = template.render(authors=authors)

        with open(args.authors_file, mode="+w", encoding="UTF-8") as file:
            file.write(contents)
    else:
        with open(args.authors_file, mode="+w", encoding="UTF-8") as file:
            for author in authors:
                file.write("%s <%s>\n" % (author["name"], author["email"]))

    return 0


if __name__ == "__main__":
    exit(main())
