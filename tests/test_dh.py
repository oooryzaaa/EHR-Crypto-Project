
import unittest

from crypto.diffie_hellman import (
    generate_dh_keys,
    compute_shared_secret,
    perform_handshake,
)


class TestDiffieHellman(unittest.TestCase):

    def setUp(self):
        self.p = 467
        self.g = 2

    def test_key_generation(self):
        private_key, public_key = generate_dh_keys(
            self.p, self.g
        )

        self.assertTrue(2 <= private_key <= self.p - 2)
        self.assertTrue(1 <= public_key < self.p)

    def test_shared_secret(self):
        alice_private = 5
        bob_private = 7

        alice_public = pow(self.g, alice_private, self.p)
        bob_public = pow(self.g, bob_private, self.p)

        alice_secret = compute_shared_secret(
            bob_public,
            alice_private,
            self.p
        )

        bob_secret = compute_shared_secret(
            alice_public,
            bob_private,
            self.p
        )

        self.assertEqual(alice_secret, bob_secret)

    def test_handshake(self):
        result = perform_handshake(self.p, self.g)

        self.assertTrue(result["success"])
        self.assertEqual(
            result["clinic_secret"],
            result["hospital_secret"]
        )

    def test_invalid_public_key(self):
        with self.assertRaises(ValueError):
            compute_shared_secret(0, 5, self.p)


if __name__ == "__main__":
    unittest.main()
