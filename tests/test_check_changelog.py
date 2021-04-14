#!/usr/bin/env python
import os
import unittest
import unittest.mock
from pre_commit_hooks import tests
from pre_commit_hooks.check_changelog import main as check_changelog


class TestCheckChangelog(tests.GitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_check_changelog(self):
        self.assertEqual(0, check_changelog())


if __name__ == "__main__":
    unittest.main()
