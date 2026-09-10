# Unit Test: Structure Verification for HENU Workspace Layout
# Version: 3.0.0-alpha.1

import os
import sys
import unittest

script_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.dirname(script_dir)
sys.path.insert(0, engine_root)

from src.core.validator import BuildValidator

class TestWorkspaceStructure(unittest.TestCase):

    def setUp(self) -> None:
        self.workspace_root = os.path.dirname(engine_root)
        self.validator = BuildValidator(self.workspace_root)

    def test_verify_folders(self) -> None:
        """Verifies that all required folders are present in the workspace."""
        missing = self.validator.verify_folders_exist()
        self.assertEqual(len(missing), 0, f"Missing workspace folders: {missing}")

    def test_verify_configs(self) -> None:
        """Verifies that all 5 split configuration files are present."""
        missing = self.validator.verify_configs_exist()
        self.assertEqual(len(missing), 0, f"Missing configs: {missing}")

    def test_verify_constitution_exists(self) -> None:
        """Verifies the engineering rules file is present in docs/."""
        rules_path = os.path.join(self.workspace_root, "docs", "HENU_ENGINEERING_RULES.md")
        self.assertTrue(os.path.isfile(rules_path), f"HENU_ENGINEERING_RULES.md missing at: {rules_path}")

if __name__ == "__main__":
    unittest.main()
