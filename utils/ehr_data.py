
"""
EHR Data Utilities
Developer: Erlinda

Uses fictional patient data for demonstrations.
"""


def validate_ehr(text: str) -> bool:
    """Check that EHR text is non-empty."""
    return isinstance(text, str) and bool(text.strip())


def text_to_bytes(text: str) -> bytes:
    """Convert EHR text to UTF-8 bytes."""
    if not isinstance(text, str):
        raise TypeError("EHR text must be a string.")
    return text.encode("utf-8")


def bytes_to_text(data: bytes) -> str:
    """Convert UTF-8 bytes back to text."""
    if not isinstance(data, bytes):
        raise TypeError("EHR data must be bytes.")
    return data.decode("utf-8")
