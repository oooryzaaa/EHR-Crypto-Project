
"""
Erdoza EHR Project
Module: Diffie-Hellman Key Exchange
Developer: Oryza
Educational simulation of DH key exchange.
"""

import secrets

from crypto.math_utils import mod_exp


def generate_dh_keys(
    p: int,
    g: int
) -> tuple[int, int]:
    """
    Generate a Diffie-Hellman key pair.

    Args:
        p: Prime modulus.
        g: Generator of the selected group.

    Returns:
        (private_key, public_key)
    """
    if p <= 3:
        raise ValueError("Prime modulus must be greater than 3.")

    if not 1 < g < p:
        raise ValueError("Generator must satisfy 1 < g < p.")

    private_key = secrets.randbelow(p - 3) + 2

    public_key = mod_exp(g, private_key, p)

    return private_key, public_key


def compute_shared_secret(
    peer_public_key: int,
    private_key: int,
    p: int
) -> int:
    """
    Compute a shared secret using the peer's public key.
    """
    if not 2 <= peer_public_key <= p - 2:
        raise ValueError("Invalid peer public key.")

    if not 2 <= private_key <= p - 2:
        raise ValueError("Invalid private key.")

    return mod_exp(peer_public_key, private_key, p)


def perform_handshake(
    p: int,
    g: int
) -> dict:
    """
    Simulate a Diffie-Hellman handshake between
    a clinic and a referral hospital.
    """
    clinic_private, clinic_public = generate_dh_keys(p, g)

    hospital_private, hospital_public = generate_dh_keys(p, g)

    clinic_secret = compute_shared_secret(
        hospital_public,
        clinic_private,
        p
    )

    hospital_secret = compute_shared_secret(
        clinic_public,
        hospital_private,
        p
    )

    if clinic_secret != hospital_secret:
        raise RuntimeError("DH shared secret mismatch.")

    return {
        "clinic_public": clinic_public,
        "hospital_public": hospital_public,
        "clinic_secret": clinic_secret,
        "hospital_secret": hospital_secret,
        "success": True,
    }
