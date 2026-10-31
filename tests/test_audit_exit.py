import unittest
from unittest.mock import patch
from scripts.run_audit import main

class AuditExitTest(unittest.TestCase):
    def test_evaluation_failure_is_not_success(self):
        with patch('scripts.run_audit.check_structure', return_value=True), patch('scripts.run_audit.run_subscript', side_effect=[0, 0, 0, 1]):
            self.assertEqual(main(), 1)
    def test_complete_audit_passes(self):
        with patch('scripts.run_audit.check_structure', return_value=True), patch('scripts.run_audit.run_subscript', return_value=0):
            self.assertEqual(main(), 0)
