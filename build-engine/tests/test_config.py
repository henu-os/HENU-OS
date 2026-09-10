# Unit Test: Configuration Verification for HENU Build Engine (Debian 13 Trixie)
# Version: 3.0.0-alpha.1

import os
import sys
import unittest

script_dir = os.path.dirname(os.path.abspath(__file__))
engine_root = os.path.dirname(script_dir)
sys.path.insert(0, engine_root)

from src.modules.config_loader import ConfigLoader

class TestBuildConfig(unittest.TestCase):

    def setUp(self) -> None:
        self.workspace_root = os.path.dirname(engine_root)

    def test_load_and_merge_configs(self) -> None:
        """Verifies that the Debian split configuration files are correctly merged by ConfigLoader."""
        loader = ConfigLoader(self.workspace_root)
        try:
            config = loader.load_and_merge()
            self.assertIsNotNone(config)
            self.assertEqual(config["distribution"]["name"], "Debian")
            self.assertEqual(config["distribution"]["codename"], "trixie")
            
            # Check release config merge keys
            self.assertEqual(config["release"]["architecture"], "amd64")
            self.assertEqual(config["release"]["version"], "3.0.0-alpha.1")
            
            # Check package config merge keys
            self.assertTrue(isinstance(config["package_groups"]["developer_tools"], list))
        except Exception as e:
            self.fail(f"Configuration loader failed to merge YAML files: {e}")

if __name__ == "__main__":
    unittest.main()
