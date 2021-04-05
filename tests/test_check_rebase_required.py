#!/usr/bin/env python
import git
import io
import os
from pre_commit_hooks.check_rebase_required import main as check_rebase_required
import sys
import tempfile
import unittest
import unittest.mock


class TestCheckRebaseRequiredCase(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.repository = git.Repo.init(self.folder.name)
        self.args = ["--repository", self.repository.working_tree_dir]

        for x in range(1, 5):
            file = os.path.join(self.folder.name, str(x))
            open(file, "wb").close()
            self.repository.index.add([file])
            self.repository.index.commit("add file %s" % x)

    def tearDown(self):
        self.folder.cleanup()
        self.folder = None

    def test_main_branch_clean(self):
        self.assertEqual(check_rebase_required(self.args), 0)

    def test_active_branch_clean(self):
        feature_branch = self.repository.create_head("feature")
        self.repository.head.set_reference(feature_branch)

        self.assertEqual(check_rebase_required(self.args), 0)

    def test_active_branch_ahead(self):
        feature_branch = self.repository.create_head("feature")
        self.repository.head.set_reference(feature_branch)

        file = os.path.join(self.folder.name, "new")
        open(file, "wb").close()

        self.repository.index.add([file])
        self.repository.index.commit("add file new")

        self.assertEqual(check_rebase_required(self.args), 0)

    def test_active_branch_behind(self):
        main_branch = self.repository.head.reference
        feature_branch = self.repository.create_head("feature")
        feature_branch.commit = "HEAD~1"
        self.repository.head.set_reference(feature_branch)

        file = os.path.join(self.folder.name, "new")
        open(file, "wb").close()
        self.repository.index.add([file])
        self.repository.index.commit("add file new")

        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as mock_out:
            self.assertEqual(check_rebase_required(self.args), 1)
            self.assertEqual(
                mock_out.getvalue(),
                "Active branch 'feature' is behind 'main' by 1 commits and should be rebased.\n",
            )

    def test_active_branch_behind_allowed(self):
        self.args.append("--max-behind-commits=1")
        main_branch = self.repository.head.reference
        feature_branch = self.repository.create_head("feature")
        feature_branch.commit = "HEAD~1"
        self.repository.head.set_reference(feature_branch)

        file = os.path.join(self.folder.name, "new")
        open(file, "wb").close()
        self.repository.index.add([file])
        self.repository.index.commit("add file new")

        self.assertEqual(check_rebase_required(self.args), 0)


if __name__ == "__main__":
    unittest.main()
