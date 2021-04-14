import argparse
import git
import jinja2
import re
from typing import Optional
from typing import Sequence


def fetch_changes(args):
    repository = git.Repo(args.repository)
    tags = [{"name": "Unreleased", "date": str(repository.head.commit.authored_datetime.date())}]
    changes = {"Unreleased": [], "tags": tags}

    # Assemble filtered tags in reverse order (newest to oldest)
    for tag in repository.tags:
        if re.match(args.tag_filter, tag.name):
            tags.insert(1, {"name": tag.name, "date": tag.commit.authored_datetime.date()})
            changes[tag.name] = []

    # Group commits by tag membership
    for commit in repository.iter_commits():
        (sha, name) = commit.name_rev.split(" ", 1)

        if name.startswith("tags/"):
            name = name.replace("tags/", "")
            if "~" in name:
                tag_commit = True
                (tag, name) = name.split("~")
            else:
                tag_commit = False
                tag = name

            if re.match(args.tag_filter, tag):
                changes[tag].append(commit.summary)
        else:
            changes["Unreleased"].append(commit.summary)

    return changes


def main(argv: Optional[Sequence[str]] = []) -> int:
    parser = argparse.ArgumentParser("Check and update changelog information in various formats.")
    parser.add_argument("--changelog-file", type=str, default="CHANGELOG")
    parser.add_argument("--changelog-format", type=str, default="text", choices=["text", "jinja"])
    parser.add_argument("--changelog-template", type=str, default="CHANGELOG.j2")
    parser.add_argument("--repository", type=str, default=".")
    parser.add_argument("--tag-filter", type=str, default="v?(\d+).(\d+).(\d+)")

    args = parser.parse_args(argv)
    changes = fetch_changes(args)
    tags = changes["tags"]

    if args.changelog_format == "jinja" and args.changelog_template:
        with open(args.changelog_template) as file:
            template = file.read()
        template = jinja2.Template(template)
        contents = template.render(changes=changes, tags=tags)

        with open(args.changelog_file, mode="+w", encoding="UTF-8") as file:
            file.write(contents)
    else:
        with open(args.changelog_file, mode="+w", encoding="UTF-8") as file:
            file.write("# Changelog")
            for tag in tags:
                name = tag["name"]
                date = tag["date"]

                file.write("\n## [%s] - %s\n\n" % (name, date))
                for change in changes[name]:
                    file.write("- %s\n" % change)

    return 0


if __name__ == "__main__":
    exit(main())
