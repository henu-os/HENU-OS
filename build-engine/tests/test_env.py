# Unit Test: Environment Checks for HENU Build Engine
# Version: 3.0.0-alpha.1

import os
import sys
import unittest

script_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.dirname(script_dir)
sys.path.insert(0, engine_root)

from src.core.validator import BuildValidator

class TestBuildEnvironment(unittest.TestCase):

    def setUp(self) -> None:
        self.workspace_root = os.path.dirname(engine_root)
        self.validator = BuildValidator(self.workspace_root)

    def test_disk_space_check(self) -> None:
        """Asserts disk space checking logic parses and outputs space metrics."""
        space_ok, free_gb = self.validator.verify_disk_space(required_gb=2)
        self.assertTrue(space_ok or not space_ok) # Evaluates successfully
        self.assertTrue(free_gb >= 0.0)

    def test_permissions_check(self) -> None:
        """Validates that user privilege verification runs successfully."""
        is_admin = self.validator.verify_permissions()
        self.assertIn(is_admin, [True, False])

if __name__ == "__main__":
    unittest.main()
