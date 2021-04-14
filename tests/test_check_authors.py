#!/usr/bin/env python
import os.path
import unittest
import unittest.mock
from pre_commit_hooks import tests
from pre_commit_hooks.check_authors import main as check_authors


class TestCheckAuthors(tests.GitTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCheckAuthors, cls).setUpClass()

        cls.generateCommits(author="Zeta Author <better.author@example.com>", count=2)
        cls.generateCommits(author="Anne Author <anne.author@example.com>", count=1)
        cls.generateCommits(author="Test Author <test.author@example.com>", count=5)

    def setUp(self):
        self.authors_file = os.path.join(self.folder.name, "AUTHORS")
        self.check = check_authors
        self.args = {"--authors-file": self.authors_file, "--repository": self.repository.working_dir}

    def test_check_authors(self):
        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Test Author <test.author@example.com>",
                "Zeta Author <better.author@example.com>",
                "Anne Author <anne.author@example.com>",
            ],
        )

    def test_check_authors_sort_default(self):
        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Test Author <test.author@example.com>",
                "Zeta Author <better.author@example.com>",
                "Anne Author <anne.author@example.com>",
            ],
        )

    def test_check_authors_sort_by_count(self):
        self.args["--sort"] = "count"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Test Author <test.author@example.com>",
                "Zeta Author <better.author@example.com>",
                "Anne Author <anne.author@example.com>",
            ],
        )

    def test_check_authors_sort_by_name(self):
        self.args["--sort"] = "name"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Anne Author <anne.author@example.com>",
                "Test Author <test.author@example.com>",
                "Zeta Author <better.author@example.com>",
            ],
        )

    def test_check_authors_sort_by_email(self):
        self.args["--sort"] = "email"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Anne Author <anne.author@example.com>",
                "Zeta Author <better.author@example.com>",
                "Test Author <test.author@example.com>",
            ],
        )

    def test_check_authors(self):
        self.args["--authors-format"] = "jinja"
        self.args["--authors-template"] = "tests/fixtures/templates/AUTHORS.j2"

        self.assertCheckReturns(0)
        self.assertFileContains(
            self.authors_file,
            [
                "Test Author <test.author@example.com> x5",
                "Zeta Author <better.author@example.com> x2",
                "Anne Author <anne.author@example.com> x1",
            ],
        )


if __name__ == "__main__":
    exit(unittest.main())
