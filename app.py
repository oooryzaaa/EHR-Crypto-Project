import secrets
from flask import (
    Flask, render_template, request,
    jsonify, session
)

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)

# Educational parameters only
P = 467
G = 2

# Local development state.
# Not persistent and not intended for multiple workers.
DEMO_STATES = {}


def empty_state():
    return {
        "ehr": None,
        "dh": None,
        "public_key": None,
        "private_key": None,
        "ciphertext": None,
        "transmitted": False,
        "recovered": None,
    }


def get_state():
    sid = session.get("demo_id")

    if sid not in DEMO_STATES:
        sid = secrets.token_urlsafe(24)
        session["demo_id"] = sid
        DEMO_STATES[sid] = empty_state()

    return DEMO_STATES[sid]


def api_error(message, code=400, kind="error"):
    return jsonify({
        "success": False,
        "message": message,
        "kind": kind
    }), code


def summary(state):
    ciphertext = state["ciphertext"]

    return {
        "prepared": state["ehr"] is not None,
        "connected": state["dh"] is not None,
        "encrypted": ciphertext is not None,
        "transmitted": state["transmitted"],
        "decrypted": state["recovered"] is not None,
        "block_count": len(ciphertext) if ciphertext else 0,
        "algorithm": "ElGamal",
        "key_exchange": "Diffie-Hellman",
        "simulation": True
    }


# -------------------------
# Web Pages
# -------------------------

@app.get("/")
def dashboard():
    return render_template("dashboard.html")


@app.get("/clinic")
def clinic():
    return render_template("clinic.html")


@app.get("/cryptography")
def cryptography():
    return render_template("cryptography.html")


@app.get("/hospital")
def hospital():
    return render_template("hospital.html")


# -------------------------
# API: Status
# -------------------------

@app.get("/api/status")
def status():
    state = get_state()

    return jsonify({
        "success": True,
        "data": summary(state)
    })


# -------------------------
# API: Prepare EHR
# -------------------------

@app.post("/api/ehr/prepare")
def prepare_ehr():
    state = get_state()
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return api_error("Invalid JSON request.")

    required = [
        "patient_id",
        "patient_name",
        "age",
        "diagnosis",
        "treatment"
    ]

    values = {}

    for field in required:
        value = str(data.get(field, "")).strip()

        if not value:
            return api_error(
                f"Field '{field}' is required."
            )

        if len(value) > 200:
            return api_error(
                f"Field '{field}' is too long."
            )

        values[field] = value

    try:
        age = int(values["age"])
    except ValueError:
        return api_error("Age must be a number.")

    if not 0 <= age <= 130:
        return api_error("Age must be between 0 and 130.")

    ehr = (
        f"Patient ID: {values['patient_id']}\n"
        f"Name: {values['patient_name']}\n"
        f"Age: {age}\n"
        f"Diagnosis: {values['diagnosis']}\n"
        f"Treatment: {values['treatment']}"
    )

    state["ehr"] = ehr

    # New EHR invalidates old encryption.
    state["ciphertext"] = None
    state["transmitted"] = False
    state["recovered"] = None

    return jsonify({
        "success": True,
        "message": "Fictional EHR prepared.",
        "preview": ehr,
        "bytes": len(ehr.encode("utf-8")),
        "data": summary(state)
    })


# -------------------------
# API: Diffie-Hellman
# -------------------------

@app.post("/api/crypto/handshake")
def handshake():
    state = get_state()

    try:
        from crypto.diffie_hellman import perform_handshake

        result = perform_handshake(P, G)

        if not result.get("success"):
            return api_error("DH handshake failed.")

        state["dh"] = result

        # Reset old key/ciphertext when starting a new session.
        state["public_key"] = None
        state["private_key"] = None
        state["ciphertext"] = None
        state["transmitted"] = False
        state["recovered"] = None

        return jsonify({
            "success": True,
            "message": "DH shared secrets match.",
            "result": {
                "p": P,
                "g": G,
                "clinic_public": result["clinic_public"],
                "hospital_public": result["hospital_public"],
                "shared_secret_match": (
                    result["clinic_secret"]
                    == result["hospital_secret"]
                )
            },
            "data": summary(state)
        })

    except (ImportError, NotImplementedError) as exc:
        return api_error(
            f"DH or Math module is not ready: {exc}",
            409,
            "module_pending"
        )

    except (ValueError, RuntimeError) as exc:
        return api_error(str(exc), 400)


# -------------------------
# API: ElGamal Encrypt
# -------------------------

@app.post("/api/crypto/encrypt")
def encrypt_ehr():
    state = get_state()

    if state["ehr"] is None:
        return api_error("Prepare EHR data first.")

    if state["dh"] is None:
        return api_error(
            "Complete the DH demonstration first."
        )

    try:
        from crypto.elgamal import generate_keys, encrypt

        # Key pair generated by hospital module.
        public_key, private_key = generate_keys(P, G)

        ciphertext = encrypt(
            state["ehr"],
            public_key
        )

        if not isinstance(ciphertext, list):
            return api_error(
                "ElGamal must return a list of ciphertext pairs."
            )

        for pair in ciphertext:
            if (
                not isinstance(pair, (list, tuple))
                or len(pair) != 2
                or not all(isinstance(x, int) for x in pair)
            ):
                return api_error(
                    "Invalid ciphertext pair format."
                )

        state["public_key"] = public_key
        state["private_key"] = private_key
        state["ciphertext"] = ciphertext
        state["transmitted"] = False
        state["recovered"] = None

        return jsonify({
            "success": True,
            "message": "EHR encrypted with ElGamal.",
            "block_count": len(ciphertext),
            "data": summary(state)
        })

    except (ImportError, NotImplementedError) as exc:
        return api_error(
            f"ElGamal module is not ready: {exc}",
            409,
            "module_pending"
        )

    except (ValueError, TypeError) as exc:
        return api_error(str(exc), 400)


# -------------------------
# API: Public Crypto Details
# -------------------------

@app.get("/api/crypto/details")
def crypto_details():
    state = get_state()

    dh = state["dh"]
    ciphertext = state["ciphertext"]

    result = {
        "p": P,
        "g": G,
        "dh": None,
        "elgamal_public_key": None,
        "ciphertext": None
    }

    if dh:
        result["dh"] = {
            "clinic_public": dh["clinic_public"],
            "hospital_public": dh["hospital_public"],
            "shared_secret_match": (
                dh["clinic_secret"]
                == dh["hospital_secret"]
            )
        }

    if state["public_key"] is not None:
        result["elgamal_public_key"] = (
            list(state["public_key"])
        )

    if ciphertext is not None:
        result["ciphertext"] = [
            list(pair) for pair in ciphertext
        ]

    return jsonify({
        "success": True,
        "result": result
    })


# -------------------------
# API: Simulated Transmission
# -------------------------

@app.post("/api/ehr/transmit")
def transmit():
    state = get_state()

    if state["ciphertext"] is None:
        return api_error("Encrypt EHR first.")

    state["transmitted"] = True

    return jsonify({
        "success": True,
        "message": (
            "Ciphertext marked as received "
            "in the local simulation."
        ),
        "data": summary(state)
    })


# -------------------------
# API: Hospital Decryption
# -------------------------

@app.post("/api/ehr/decrypt")
def decrypt_ehr():
    state = get_state()

    if not state["transmitted"]:
        return api_error("Transmit ciphertext first.")

    if state["private_key"] is None:
        return api_error("Private key unavailable.")

    try:
        from crypto.elgamal import decrypt

        recovered = decrypt(
            state["ciphertext"],
            state["private_key"]
        )

        if not isinstance(recovered, str):
            return api_error(
                "Decrypt must return a string."
            )

        state["recovered"] = recovered

        return jsonify({
            "success": True,
            "message": "Hospital decryption completed.",
            "recovered": recovered,
            "verified": recovered == state["ehr"],
            "data": summary(state)
        })

    except (ImportError, NotImplementedError) as exc:
        return api_error(
            f"Decryption module is not ready: {exc}",
            409,
            "module_pending"
        )

    except (ValueError, TypeError, UnicodeError) as exc:
        return api_error(str(exc), 400)


# -------------------------
# API: Reset
# -------------------------

@app.post("/api/reset")
def reset():
    state = get_state()
    state.clear()
    state.update(empty_state())

    return jsonify({
        "success": True,
        "message": "Simulation reset.",
        "data": summary(state)
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
