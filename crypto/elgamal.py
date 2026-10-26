"""ElGamal encryption for fictional EHR data."""

import secrets

from utils.ehr_data import text_to_bytes, bytes_to_text, validate_ehr


def _is_probable_prime(number: int) -> bool:
    if number < 2:
        return False

    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if number == prime:
            return True
        if number % prime == 0:
            return False

    odd_part = number - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        odd_part //= 2
        powers_of_two += 1

    if number < 2**64:
        bases = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
    else:
        bases = tuple(
            secrets.randbelow(number - 3) + 2
            for _ in range(32)
        )

    for base in bases:
        base %= number
        if base in (0, 1):
            continue

        value = pow(base, odd_part, number)
        if value in (1, number - 1):
            continue

        for _ in range(powers_of_two - 1):
            value = pow(value, 2, number)
            if value == number - 1:
                break
        else:
            return False

    return True


def _validate_public_key(
    public_key: tuple[int, int, int],
) -> tuple[int, int, int]:
    if not isinstance(public_key, (tuple, list)) or len(public_key) != 3:
        raise ValueError("Public key must contain (p, g, y).")

    p, g, y = public_key
    if any(type(value) is not int for value in (p, g, y)):
        raise TypeError("Public key values must be integers.")
    if p <= 256 or not _is_probable_prime(p):
        raise ValueError("p must be a prime greater than 256.")
    if not 1 < g < p:
        raise ValueError("g must satisfy 1 < g < p.")
    if not 1 <= y < p:
        raise ValueError("Public key component y must satisfy 1 <= y < p.")

    return p, g, y


def generate_keys(p: int, g: int) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Return ElGamal public and private keys for prime modulus p and base g."""
    if type(p) is not int or type(g) is not int:
        raise TypeError("p and g must be integers.")
    if p <= 2 or not _is_probable_prime(p):
        raise ValueError("p must be a prime greater than 2.")
    if not 1 < g < p:
        raise ValueError("g must satisfy 1 < g < p.")

    private_key = secrets.randbelow(p - 2) + 1
    public_value = pow(g, private_key, p)
    return (p, g, public_value), (p, g, private_key)


def encrypt(
    plaintext: str,
    public_key: tuple[int, int, int],
) -> list[tuple[int, int]]:
    """Encrypt each UTF-8 byte into an ElGamal ciphertext pair."""
    p, g, public_value = _validate_public_key(public_key)
    if not isinstance(plaintext, str):
        raise TypeError("EHR plaintext must be a string.")
    if not validate_ehr(plaintext):
        raise ValueError("EHR plaintext must be a non-empty string.")

    ciphertext = []
    for byte in text_to_bytes(plaintext):
        ephemeral_key = secrets.randbelow(p - 2) + 1
        c1 = pow(g, ephemeral_key, p)
        message = byte + 1
        c2 = message * pow(public_value, ephemeral_key, p) % p
        ciphertext.append((c1, c2))

    return ciphertext


def decrypt(
    ciphertext: list[tuple[int, int]],
    private_key: tuple[int, int, int],
) -> str:
    """Decrypt ElGamal ciphertext pairs and decode the original UTF-8 text."""
    if not isinstance(private_key, (tuple, list)) or len(private_key) != 3:
        raise ValueError("Private key must contain (p, g, x).")

    p, g, private_value = private_key
    if any(type(value) is not int for value in (p, g, private_value)):
        raise TypeError("Private key values must be integers.")
    if p <= 256 or not _is_probable_prime(p):
        raise ValueError("p must be a prime greater than 256.")
    if not 1 < g < p:
        raise ValueError("g must satisfy 1 < g < p.")
    if not 1 <= private_value < p - 1:
        raise ValueError("Private key x must satisfy 1 <= x < p - 1.")
    if not isinstance(ciphertext, list):
        raise TypeError("Ciphertext must be a list of pairs.")

    plaintext_bytes = bytearray()
    for pair in ciphertext:
        if (
            not isinstance(pair, (tuple, list))
            or len(pair) != 2
            or any(type(value) is not int for value in pair)
        ):
            raise ValueError("Each ciphertext block must be an integer pair.")

        c1, c2 = pair
        if not 1 <= c1 < p or not 1 <= c2 < p:
            raise ValueError(
                "Ciphertext values must be in the range 1 to p - 1."
            )

        shared_secret = pow(c1, private_value, p)
        message = c2 * pow(shared_secret, -1, p) % p
        if not 1 <= message <= 256:
            raise ValueError("Ciphertext contains an invalid byte value.")
        plaintext_bytes.append(message - 1)

    return bytes_to_text(bytes(plaintext_bytes))