import argparse
import git
import itertools
import os.path
import re
import tempfile
import unittest


class TestCase(unittest.TestCase):
    pass


class GitTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.branch = "main"
        cls.folder = tempfile.TemporaryDirectory()
        cls.repository = git.Repo.init(cls.folder.name, initial_branch=cls.branch)
        cls.args = {}

    @classmethod
    def tearDownClass(cls):
        cls.repository.close()
        cls.folder.cleanup()

    @classmethod
    def generateCommits(cls, **kwargs):
        commits = []

        parser = argparse.ArgumentParser()
        parser.add_argument("--author", type=str, default="Test Author <test.author@example.com>")
        parser.add_argument("--branch", type=str, default=cls.branch)
        parser.add_argument("--committer", type=str, default="Test Committer <test.committer@example.com>")
        parser.add_argument("--count", type=int, default=1)

        argv = list(filter(None, [("--%s=%s" % x) for x in kwargs.items()]))
        args = parser.parse_args(argv)

        if args.branch != cls.repository.head.reference.name:
            cls.repository.create_head(args.branch)

        for x in range(1, args.count + 1):
            (name, email) = list(filter(None, re.split("^(.*)\s+<(.*)>", args.author)))
            author = git.Actor(name, email)

            (name, email) = list(filter(None, re.split("^(.*)\s+<(.*)>", args.committer)))
            committer = git.Actor(name, email)

            filename = os.path.join(cls.folder.name, "%d.txt" % x)

            with open(filename, "+w") as file:
                file.write("File %d contents" % x)
                cls.repository.index.add([filename])
                commits.append(cls.repository.index.commit("Added %d.txt" % x, author=author, committer=committer))

        return commits

    @classmethod
    def generateRelease(cls, tag):
        return cls.repository.create_tag(tag)

    def assertCheckReturns(self, code):
        # TODO(claco): Hack Tuples Flatten
        args = list(itertools.chain.from_iterable(self.args.items()))

        self.assertEqual(code, self.check(args))

    def assertFileContains(self, file, content):
        with open(file, mode="r", encoding="UTF-8") as file:
            contents = file.read()

        if type(content) == list:
            contents = contents.split("\n")
            contents = list(filter(None, contents))
            content = list(filter(None, content))

            self.assertListEqual(contents, content)
        else:
            self.assertRegex(contents, content)
