#!/usr/bin/env python
from datetime import datetime
import os
import unittest
import unittest.mock
from pre_commit_hooks import tests
from pre_commit_hooks.check_changelog import main as check_changelog


class TestCheckChangelog(tests.GitTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCheckChangelog, cls).setUpClass()

        cls.generateCommits(count=1)
        cls.generateRelease("v0.0.1")
        cls.generateCommits(count=2)
        cls.generateRelease("v0.0.2")
        cls.generateCommits(count=3)

    def setUp(self):
        self.changelog_file = os.path.join(self.folder.name, "CHANGELOG")
        self.check = check_changelog
        self.args = {"--changelog-file": self.changelog_file, "--repository": self.repository.working_dir}
        self.date = (datetime.now().date().strftime("%Y-%m-%d"))

    def test_check_changelog(self):
        self.assertCheckReturns(0)
        self.assertFileContains(
            self.changelog_file,
            [
                "# Changelog",
                "## [Unreleased] - %s" % self.date,
                "- Added 3.txt",
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.2] - %s" % self.date,
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.1] - %s" % self.date,
                "- Added 1.txt",
            ],
        )


    def test_check_changelog_label_changes(self):
        self.args["--label-changes"] = "True"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.changelog_file,
            [
                "# Changelog",
                "## [Unreleased] - %s" % self.date,
                "- Added: Added 3.txt",
                "- Added: Added 2.txt",
                "- Added: Added 1.txt",
                "## [v0.0.2] - %s" % self.date,
                "- Added: Added 2.txt",
                "- Added: Added 1.txt",
                "## [v0.0.1] - %s" % self.date,
                "- Added: Added 1.txt",
            ],
        )


    def test_check_changelog_jinja_template(self):
        self.args["--changelog-format"] = "jinja"
        self.args["--changelog-template"] = "tests/fixtures/templates/CHANGELOG.j2"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.changelog_file,
            [
                "# Changelog",
                "## [Unreleased] - %s" % self.date,
                "- Added 3.txt",
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.2] - %s" % self.date,
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.1] - %s" % self.date,
                "- Added 1.txt",
            ],
        )


if __name__ == "__main__":
    exit(unittest.main())
