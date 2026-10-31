import tempfile
import unittest
from pathlib import Path

import tests._pathfix  # noqa: F401
from provenance.hash_utils import sha256_bytes, sha256_file, verify_file_hash
from security.secrets_detector import contains_secret, scan_for_secrets


class TestSecretsDetector(unittest.TestCase):
    def test_detects_aws_key(self):
        self.assertTrue(contains_secret("AKIA" + "A" * 16))

    def test_detects_bearer_token(self):
        self.assertTrue(contains_secret("Authorization: Bearer abcdefghijklmnopqrstuvwx"))

    def test_detects_private_key_block(self):
        self.assertTrue(contains_secret("-----BEGIN RSA PRIVATE KEY-----"))

    def test_plain_legal_question_has_no_secrets(self):
        self.assertEqual(scan_for_secrets("Cual es el plazo de tramitacion del permiso"), [])


class TestHashUtils(unittest.TestCase):
    def test_sha256_bytes_matches_known_value(self):
        # sha256("") es un valor conocido y estable.
        self.assertEqual(
            sha256_bytes(b""),
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )

    def test_verify_file_hash_detects_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "archivo.txt"
            path.write_text("contenido original", encoding="utf-8")
            hash_real = sha256_file(path)
            self.assertTrue(verify_file_hash(path, hash_real))
            self.assertFalse(verify_file_hash(path, "0" * 64))

    def test_verify_file_hash_rejects_unverified_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "archivo.txt"
            path.write_text("contenido", encoding="utf-8")
            self.assertFalse(verify_file_hash(path, "NO_VERIFICADO"))


if __name__ == "__main__":
    unittest.main()
