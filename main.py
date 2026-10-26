
"""
ERDOZA - SECURE EHR TRANSFER SYSTEM
Developer: Oryza
System Integration, Diffie-Hellman & CLI
Educational cryptography simulation.
Not intended for production healthcare systems.
"""

import time

from crypto.diffie_hellman import perform_handshake
from crypto.elgamal import generate_keys, encrypt, decrypt


# Educational parameters only.
# 467 is prime and 2 is a primitive root modulo 467.
P = 467
G = 2


class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def colorize(text, color):
    return f"{color}{text}{Colors.RESET}"


def divider():
    print("-" * 65)


def show_header():
    print()
    print("=" * 65)
    print(colorize(
        "              ERDOZA - SECURE EHR TRANSFER",
        Colors.CYAN
    ))
    print("          Clinic <-> Referral Hospital")
    print("=" * 65)
    print("  Diffie-Hellman Key Exchange + ElGamal Encryption")
    print("  Educational Cryptography Simulation")
    print("=" * 65)


def show_menu(connected, encrypted):
    print("\n" + colorize("MAIN MENU", Colors.BOLD))
    divider()

    connection_status = (
        colorize("DH COMPLETED", Colors.GREEN)
        if connected else colorize("NOT CONNECTED", Colors.RED)
    )

    data_status = (
        colorize("CIPHERTEXT AVAILABLE", Colors.GREEN)
        if encrypted else colorize("NO ENCRYPTED DATA", Colors.YELLOW)
    )

    print(f" Connection : {connection_status}")
    print(f" Data       : {data_status}")

    divider()
    print("[1] Establish DH Handshake")
    print("[2] Input & Encrypt EHR")
    print("[3] View Network Transmission")
    print("[4] Decrypt EHR at Hospital")
    print("[5] Reset Simulation")
    print("[0] Exit")
    divider()


def pause():
    input("\nPress Enter to continue...")


def simulate_loading(message):
    print(colorize(f"\n[SYSTEM] {message}", Colors.CYAN))
    time.sleep(0.6)


def perform_connection():
    print("\n" + "=" * 65)
    print(colorize(
        " DIFFIE-HELLMAN HANDSHAKE",
        Colors.BLUE
    ))
    print("=" * 65)

    simulate_loading("Initializing DH parameters...")

    print(f"Public prime (p)     : {P}")
    print(f"Public generator (g) : {G}")

    simulate_loading("Generating clinic and hospital key pairs...")

    result = perform_handshake(P, G)

    divider()

    print(colorize("[CLINIC]", Colors.BLUE))
    print(f"Public Key : {result['clinic_public']}")

    print()
    print(colorize("[HOSPITAL]", Colors.GREEN))
    print(f"Public Key : {result['hospital_public']}")

    divider()

    if result["success"]:
        print(colorize(
            "[SUCCESS] Both parties computed the same shared secret.",
            Colors.GREEN
        ))
        print(
            "Shared Secret :",
            result["clinic_secret"]
        )

        print(colorize(
            "[INFO] DH is unauthenticated in this educational demo.",
            Colors.YELLOW
        ))

    return result


def input_ehr():
    print("\n" + "=" * 65)
    print(colorize(
        " CLINIC - ELECTRONIC HEALTH RECORD",
        Colors.BLUE
    ))
    print("=" * 65)

    patient_id = input("Patient ID       : ").strip()
    patient_name = input("Patient Name     : ").strip()
    age = input("Age              : ").strip()
    diagnosis = input("Diagnosis        : ").strip()
    treatment = input("Treatment        : ").strip()

    fields = [
        patient_id,
        patient_name,
        age,
        diagnosis,
        treatment
    ]

    if not all(fields):
        raise ValueError("All EHR fields must be filled.")

    if not age.isdigit() or not 0 <= int(age) <= 130:
        raise ValueError("Age must be between 0 and 130.")

    ehr = (
        f"Patient ID: {patient_id}\n"
        f"Name: {patient_name}\n"
        f"Age: {age}\n"
        f"Diagnosis: {diagnosis}\n"
        f"Treatment: {treatment}"
    )

    return ehr


def encrypt_ehr(ehr, public_key):
    print("\n" + "=" * 65)
    print(colorize(
        " ELGAMAL ENCRYPTION",
        Colors.BLUE
    ))
    print("=" * 65)

    simulate_loading("Encoding EHR as UTF-8...")

    encoded = ehr.encode("utf-8")

    print(f"Original data size : {len(encoded)} bytes")

    simulate_loading("Encrypting with hospital public key...")

    ciphertext = encrypt(ehr, public_key)

    print(colorize(
        "[SUCCESS] EHR encrypted.",
        Colors.GREEN
    ))

    print(f"Ciphertext blocks : {len(ciphertext)}")

    return ciphertext


def show_transmission(ciphertext):
    print("\n" + "=" * 65)
    print(colorize(
        " PUBLIC NETWORK - TRANSMISSION VIEW",
        Colors.RED
    ))
    print("=" * 65)

    simulate_loading("Transmitting encrypted EHR...")

    print(colorize(
        "\n[NETWORK OBSERVER] Captured ciphertext:",
        Colors.RED
    ))

    divider()

    for index, pair in enumerate(ciphertext, start=1):
        print(f"Block {index:03d}: {pair}")

    divider()

    print(colorize(
        "[INFO] The network view displays encrypted data only.",
        Colors.YELLOW
    ))

    print(
        "[INFO] This does not demonstrate protection "
        "against message tampering."
    )


def decrypt_ehr(ciphertext, private_key):
    print("\n" + "=" * 65)
    print(colorize(
        " HOSPITAL - EHR DECRYPTION",
        Colors.GREEN
    ))
    print("=" * 65)

    simulate_loading("Decrypting with hospital private key...")

    recovered = decrypt(ciphertext, private_key)

    print(colorize(
        "\n[SUCCESS] EHR decrypted.",
        Colors.GREEN
    ))

    divider()

    print(recovered)

    divider()

    return recovered


def main():
    connected = False
    dh_result = None

    hospital_public_key = None
    hospital_private_key = None

    plaintext = None
    ciphertext = None

    show_header()

    while True:
        show_menu(connected, ciphertext is not None)

        choice = input("\nSelect menu: ").strip()

        try:
            if choice == "1":
                dh_result = perform_connection()

                simulate_loading(
                    "Generating hospital ElGamal keys..."
                )

                public_key, private_key = generate_keys(P, G)

                hospital_public_key = public_key
                hospital_private_key = private_key

                connected = True

                # A new session invalidates previous data.
                plaintext = None
                ciphertext = None

                print(colorize(
                    "\n[SUCCESS] Demo session initialized.",
                    Colors.GREEN
                ))

                pause()

            elif choice == "2":
                if not connected:
                    print(colorize(
                        "\n[ERROR] Complete DH handshake first.",
                        Colors.RED
                    ))
                    continue

                ehr = input_ehr()

                new_ciphertext = encrypt_ehr(
                    ehr,
                    hospital_public_key
                )

                plaintext = ehr
                ciphertext = new_ciphertext

                pause()

            elif choice == "3":
                if ciphertext is None:
                    print(colorize(
                        "\n[ERROR] No encrypted EHR available.",
                        Colors.RED
                    ))
                    continue

                show_transmission(ciphertext)
                pause()

            elif choice == "4":
                if ciphertext is None:
                    print(colorize(
                        "\n[ERROR] No encrypted EHR available.",
                        Colors.RED
                    ))
                    continue

                recovered = decrypt_ehr(
                    ciphertext,
                    hospital_private_key
                )

                if recovered == plaintext:
                    print(colorize(
                        "[VERIFIED] Decrypted EHR matches original.",
                        Colors.GREEN
                    ))
                else:
                    print(colorize(
                        "[WARNING] Decrypted EHR does not match.",
                        Colors.RED
                    ))

                pause()

            elif choice == "5":
                connected = False
                dh_result = None
                hospital_public_key = None
                hospital_private_key = None
                plaintext = None
                ciphertext = None

                print(colorize(
                    "\n[SYSTEM] Simulation reset.",
                    Colors.YELLOW
                ))

            elif choice == "0":
                print(colorize(
                    "\nThank you for using Erdoza EHR!",
                    Colors.CYAN
                ))
                break

            else:
                print(colorize(
                    "\n[ERROR] Invalid menu option.",
                    Colors.RED
                ))

        except NotImplementedError as error:
            print(colorize(
                f"\n[MODULE PENDING] {error}",
                Colors.YELLOW
            ))

        except (ValueError, UnicodeError) as error:
            print(colorize(
                f"\n[ERROR] {error}",
                Colors.RED
            ))

        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            break


if __name__ == "__main__":
    main()
