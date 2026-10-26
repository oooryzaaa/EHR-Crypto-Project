import unittest
from unittest.mock import patch

from crypto.elgamal import decrypt, encrypt, generate_keys


class TestElGamal(unittest.TestCase):

    def setUp(self):
        self.p = 467
        self.g = 2
        self.public_key, self.private_key = generate_keys(self.p, self.g)

    def test_key_generation(self):
        p, g, public_value = self.public_key
        private_p, private_g, private_value = self.private_key

        self.assertEqual((p, g), (self.p, self.g))
        self.assertEqual((private_p, private_g), (self.p, self.g))
        self.assertEqual(public_value, pow(g, private_value, p))
        self.assertTrue(1 <= private_value < p - 1)

    def test_key_generation_is_independent_of_ehr_byte_size(self):
        public_key, private_key = generate_keys(23, 5)

        self.assertEqual(public_key[:2], (23, 5))
        self.assertEqual(private_key[:2], (23, 5))
        with self.assertRaises(ValueError):
            encrypt("EHR", public_key)

    def test_encrypt_decrypt_ascii_and_utf8(self):
        plaintext = "Patient: José 🩺\nDiagnosis: sehat"

        ciphertext = encrypt(plaintext, self.public_key)

        self.assertEqual(len(ciphertext), len(plaintext.encode("utf-8")))
        self.assertTrue(all(len(pair) == 2 for pair in ciphertext))
        self.assertEqual(decrypt(ciphertext, self.private_key), plaintext)

    def test_encryption_uses_fresh_ephemeral_key_per_byte(self):
        plaintext = "AA"
        with patch("crypto.elgamal.secrets.randbelow", side_effect=[4, 5]):
            ciphertext = encrypt(plaintext, self.public_key)

        self.assertNotEqual(ciphertext[0], ciphertext[1])

    def test_rejects_empty_or_invalid_plaintext(self):
        for plaintext in ("", " \t\n"):
            with self.subTest(plaintext=repr(plaintext)):
                with self.assertRaises(ValueError):
                    encrypt(plaintext, self.public_key)

        with self.assertRaises(TypeError):
            encrypt(None, self.public_key)

    def test_rejects_invalid_parameters_and_ciphertext(self):
        with self.assertRaises(ValueError):
            generate_keys(15, 2)
        with self.assertRaises(ValueError):
            generate_keys(self.p, 1)
        with self.assertRaises(ValueError):
            encrypt("valid EHR", (self.p, self.g, self.p))
        with self.assertRaises(ValueError):
            decrypt([(0, 1)], self.private_key)


if __name__ == "__main__":
    unittest.main()