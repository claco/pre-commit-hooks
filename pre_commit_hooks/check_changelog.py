import argparse
import enum
import git
import jinja2
import re
from typing import Optional
from typing import Sequence

# See https://changelog.md/
# Added – For any new features that have been added since the last version was released
# Changed – To note any changes to the software’s existing functionality
# Deprecated– To note any features that were once stable but are no longer and have thus been removed
# Fixed– Any bugs or errors that have been fixed should be so noted
# Removed– This notes any features that have been deleted and removed from the software
# Security– This acts as an invitation to users who want to upgrade and avoid any software vulnerabilities
class ChangeType(enum.Enum):
    Added = 1
    Changed = 2
    Deprecated = 3
    Fixed = 4
    Removed = 5
    Security = 6


class ChangeTypePatterns:
    Added = r"(add|new|creat|onboard)"
    Changed = r"(bump|chang|disabl|updat|move|enabl|renam|revert|allow|upgrad|migrat|refact)"
    Deprecated = r"(deprecat|eol|end of life)"
    Fixed = r"(fix|resolv|correct)"
    Removed = r"(remov|delet)"
    Security = r"(security|vulnerabl|cve|auth|revok|access)"


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
                tag = name.split("~")[0]
            elif "^" in name:
                tag_commit = True
                tag = name.split("^")[0]
            else:
                tag_commit = False
                tag = name

            summary = label_change(args, commit.summary)

            if re.match(args.tag_filter, tag):
                changes[tag].append({"summary": summary})
            else:
                changes["Unreleased"].append({"summary": summary})
        else:
            summary = label_change(args, commit.summary)
            changes["Unreleased"].append({"summary": summary})

    return changes


def label_change(args, content):
    content = content.capitalize()
    content = re.sub("\s+", content, " ")

    if args.label_changes:
        if re.match("^.*:\s+", content):
            return content
        # elif re.match("^\[.*\]\s+", content):
        #     return "%s: %s" % ("Braces", content)
        else:
            for changeType in ChangeType:
                pattern = getattr(ChangeTypePatterns, changeType.name)
                if re.findall(pattern, content, re.IGNORECASE|re.DOTALL|re.MULTILINE):
                    return "%s: %s" % (changeType.name, content)

            return "%s: %s" % ("Changed", content)

    return content


def main(argv: Optional[Sequence[str]] = []) -> int:
    parser = argparse.ArgumentParser("Check and update changelog information in various formats.")
    parser.add_argument("--changelog-file", type=str, default="CHANGELOG.md")
    parser.add_argument("--changelog-format", type=str, default="text", choices=["text", "jinja"])
    parser.add_argument("--changelog-template", type=str, default="CHANGELOG.j2")
    parser.add_argument("--label-changes", nargs='?', const=True, default=False)
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
            file.write("# Changelog\n")
            for tag in tags:
                name = tag["name"]
                date = tag["date"]

                file.write("\n## [%s] - %s\n\n" % (name, date))
                for change in changes[name]:
                    file.write("- %s\n" % change["summary"])

    return 0


if __name__ == "__main__":
    exit(main())
