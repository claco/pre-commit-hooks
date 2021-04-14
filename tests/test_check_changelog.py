#!/usr/bin/env python
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

    def test_check_changelog(self):
        self.assertCheckReturns(0)
        self.assertFileContains(
            self.changelog_file,
            [
                "## [Unreleased] - 2021-04-14",
                "- Added 3.txt",
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.2] - 2021-04-14",
                "- Added 2.txt",
                "- Added 1.txt",
                "## [v0.0.1] - 2021-04-14",
                "- Added 1.txt",
            ],
        )


if __name__ == "__main__":
    exit(unittest.main())
