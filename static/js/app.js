
/**
 * ERDOZA HEALTHCRYPT
 * Frontend Application
 * Developer: Oryza Qiara Ramadhani
 *
 * Uses Flask API and Python crypto modules.
 */

"use strict";

const $ = (id) => document.getElementById(id);

let currentStatus = null;


// ======================================
// API UTILITIES
// ======================================

async function apiRequest(url, method = "GET", data = null) {
    const options = {
        method,
        headers: {
            "Accept": "application/json"
        }
    };

    if (data !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    let response;

    try {
        response = await fetch(url, options);
    } catch {
        throw new Error(
            "Unable to connect to the Flask server."
        );
    }

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error(
            "The server returned an invalid response."
        );
    }

    if (!response.ok || !result.success) {
        throw new Error(
            result.message || "Request failed."
        );
    }

    return result;
}


function setText(id, value) {
    const element = $(id);

    if (element) {
        element.textContent = String(value);
    }
}


function showToast(message, type = "success") {
    const container = $("toastContainer");

    if (!container) return;

    const toast = document.createElement("div");

    toast.className = `app-toast ${type}`;
    toast.textContent = message;
    toast.setAttribute("role", "status");

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4500);
}


async function runAction(button, action) {
    if (button) button.disabled = true;

    try {
        await action();
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        if (button) button.disabled = false;
    }
}


// ======================================
// SESSION STATUS
// ======================================

async function loadStatus() {
    const result = await apiRequest("/api/status");

    currentStatus = result.data;
    renderStatus(currentStatus);

    return currentStatus;
}


function renderStatus(status) {
    // Dashboard metrics
    setText(
        "metricConnection",
        status.connected ? "Completed" : "Not Started"
    );

    setText(
        "metricEncryption",
        status.encrypted ? "Encrypted" : "Pending"
    );

    setText(
        "metricTransmission",
        status.transmitted ? "Transmitted" : "Pending"
    );

    setText("metricBlocks", status.block_count);

    // Dashboard workflow
    const workflow = [
        ["workflowPrepared", status.prepared],
        ["workflowConnected", status.connected],
        [
            "workflowEncrypted",
            status.encrypted && status.transmitted
        ],
        ["workflowDecrypted", status.decrypted]
    ];

    for (const [id, completed] of workflow) {
        const element = $(id);

        if (!element) continue;

        element.classList.toggle("completed", completed);

        const indicator = element.querySelector(
            ".workflow-indicator"
        );

        if (indicator) {
            indicator.textContent = completed ? "✓" : "○";
        }
    }

    // Cryptography indicators
    setText(
        "dhResult",
        status.connected ? "Shared Secrets Match" : "Not Started"
    );

    const dhResult = $("dhResult");

    if (dhResult) {
        dhResult.classList.toggle(
            "success",
            status.connected
        );
    }

    setText(
        "encryptedBlockCount",
        status.block_count
    );

    setText(
        "transmissionStatus",
        status.transmitted
            ? "Transmission Completed"
            : "Not Transmitted"
    );

    // Hospital indicators
    setText(
        "hospitalTransmission",
        status.transmitted ? "Received" : "Waiting"
    );

    setText(
        "hospitalBlockCount",
        status.block_count
    );

    setText(
        "hospitalDecryption",
        status.decrypted ? "Completed" : "Pending"
    );

    setText(
        "incomingPayloadStatus",
        status.transmitted
            ? "Encrypted EHR Available"
            : "No incoming encrypted record"
    );

    setText(
        "incomingPayloadDescription",
        status.transmitted
            ? `${status.block_count} encrypted blocks received in simulation.`
            : "Complete encryption and transmission before decrypting."
    );

    if ($("handshakeButton")) {
        $("handshakeButton").disabled = false;
    }

    if ($("encryptButton")) {
        $("encryptButton").disabled = !(
            status.prepared && status.connected
        );
    }

    if ($("transmitButton")) {
        $("transmitButton").disabled = !(
            status.encrypted && !status.transmitted
        );
    }

    if ($("decryptButton")) {
        $("decryptButton").disabled = !status.transmitted;
    }
}


// ======================================
// DOCUMENT PREVIEW
// ======================================

function renderDocument(id, text) {
    const container = $(id);

    if (!container) return;

    container.replaceChildren();

    const pre = document.createElement("pre");
    pre.className = "preview-text";

    // textContent prevents HTML injection
    pre.textContent = text;

    container.appendChild(pre);
}


// ======================================
// CLINIC PORTAL
// ======================================

function setupClinic() {
    const form = $("ehrForm");
    const sampleButton = $("fillDemoData");

    if (!form) return;

    sampleButton?.addEventListener("click", () => {
        $("patient_id").value = "EHR-2026-001";
        $("patient_name").value = "Pasien Simulasi A";
        $("age").value = "45";
        $("diagnosis").value = "Hipertensi (data fiktif)";
        $("treatment").value = "Terapi simulasi";

        showToast("Sample EHR data inserted.");
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!form.reportValidity()) return;

        const button = $("prepareButton");

        await runAction(button, async () => {
            const data = {
                patient_id: $("patient_id").value.trim(),
                patient_name: $("patient_name").value.trim(),
                age: $("age").value.trim(),
                diagnosis: $("diagnosis").value.trim(),
                treatment: $("treatment").value.trim()
            };

            const result = await apiRequest(
                "/api/ehr/prepare",
                "POST",
                data
            );

            renderDocument(
                "ehrPreview",
                result.preview
            );

            currentStatus = result.data;
            renderStatus(currentStatus);

            showToast(
                `EHR prepared successfully (${result.bytes} bytes).`
            );
        });
    });
}


// ======================================
// CRYPTOGRAPHY MONITOR
// ======================================

async function refreshCryptoDetails() {
    if (!$("ciphertextOutput")) return;

    const result = await apiRequest(
        "/api/crypto/details"
    );

    const details = result.result;

    setText("dhPrime", details.p);
    setText("dhGenerator", details.g);

    if (details.dh) {
        setText(
            "clinicPublic",
            details.dh.clinic_public
        );

        setText(
            "hospitalPublic",
            details.dh.hospital_public
        );
    } else {
        setText("clinicPublic", "—");
        setText("hospitalPublic", "—");
    }

    const output = $("ciphertextOutput");

    if (!details.ciphertext) {
        output.textContent =
            "[ERDOZA] Waiting for encrypted data...\n" +
            "[INFO] Prepare EHR and run ElGamal encryption.";

        return;
    }

    const lines = [
        "[ERDOZA] ElGamal ciphertext available",
        `[INFO] Blocks: ${details.ciphertext.length}`,
        "[INFO] Displaying ciphertext pairs (c1, c2)",
        "----------------------------------------"
    ];

    details.ciphertext.forEach((pair, index) => {
        lines.push(
            `Block ${String(index + 1).padStart(3, "0")}: (${pair[0]}, ${pair[1]})`
        );
    });

    output.textContent = lines.join("\n");
}


function setupCryptography() {
    const handshakeButton = $("handshakeButton");
    const encryptButton = $("encryptButton");
    const transmitButton = $("transmitButton");

    if (!handshakeButton) return;

    handshakeButton.addEventListener("click", async () => {
        await runAction(handshakeButton, async () => {
            const result = await apiRequest(
                "/api/crypto/handshake",
                "POST"
            );

            currentStatus = result.data;
            renderStatus(currentStatus);

            await refreshCryptoDetails();

            showToast(result.message);
        });
    });

    encryptButton.addEventListener("click", async () => {
        await runAction(encryptButton, async () => {
            const result = await apiRequest(
                "/api/crypto/encrypt",
                "POST"
            );

            currentStatus = result.data;
            renderStatus(currentStatus);

            await refreshCryptoDetails();

            showToast(result.message);
        });
    });

    transmitButton.addEventListener("click", async () => {
        await runAction(transmitButton, async () => {
            const result = await apiRequest(
                "/api/ehr/transmit",
                "POST"
            );

            currentStatus = result.data;
            renderStatus(currentStatus);

            showToast(result.message);
        });
    });
}


// ======================================
// HOSPITAL PORTAL
// ======================================

function setupHospital() {
    const button = $("decryptButton");

    if (!button) return;

    button.addEventListener("click", async () => {
        await runAction(button, async () => {
            const result = await apiRequest(
                "/api/ehr/decrypt",
                "POST"
            );

            renderDocument(
                "decryptedPreview",
                result.recovered
            );

            const verification = $("verificationStatus");

            if (verification) {
                verification.textContent = result.verified
                    ? "Record Matches"
                    : "Record Mismatch";

                verification.classList.remove(
                    "success",
                    "error"
                );

                verification.classList.add(
                    result.verified ? "success" : "error"
                );
            }

            currentStatus = result.data;
            renderStatus(currentStatus);

            showToast(
                result.verified
                    ? "EHR decrypted and matched the original."
                    : "Decryption completed but records differ.",
                result.verified ? "success" : "error"
            );
        });
    });
}


// ======================================
// GLOBAL NAVIGATION AND RESET
// ======================================

function setupNavigation() {
    const toggle = $("menuToggle");
    const sidebar = $("sidebar");

    toggle?.addEventListener("click", () => {
        sidebar?.classList.toggle("open");
    });

    const resetButton = $("resetSimulation");

    resetButton?.addEventListener("click", async () => {
        const approved = confirm(
            "Reset the current EHR simulation?\n" +
            "All temporary data will be cleared."
        );

        if (!approved) return;

        await runAction(resetButton, async () => {
            const result = await apiRequest(
                "/api/reset",
                "POST"
            );

            currentStatus = result.data;
            renderStatus(currentStatus);

            // Clear the current page's local display
            if ($("ehrForm")) {
                $("ehrForm").reset();
            }

            if ($("ehrPreview")) {
                renderDocument(
                    "ehrPreview",
                    "No record prepared."
                );
            }

            if ($("decryptedPreview")) {
                renderDocument(
                    "decryptedPreview",
                    "No decrypted record."
                );
            }

            setText("verificationStatus", "Not Verified");

            if ($("ciphertextOutput")) {
                await refreshCryptoDetails();
            }

            showToast("Simulation reset successfully.");
        });
    });
}


// ======================================
// APPLICATION INITIALIZATION
// ======================================

document.addEventListener("DOMContentLoaded", async () => {
    setupNavigation();
    setupClinic();
    setupCryptography();
    setupHospital();

    try {
        await loadStatus();
        await refreshCryptoDetails();
    } catch (error) {
        showToast(error.message, "error");
    }

    console.log(
        "Erdoza HealthCrypt initialized."
    );
});
