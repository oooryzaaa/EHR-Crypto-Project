
"""
EHR Data Utilities
Developer: Erlinda

Uses fictional patient data for demonstrations.
"""


def validate_ehr(text: str) -> bool:
    """Check that EHR text is non-empty."""
    # TODO (Erlinda): Validate input.
    raise NotImplementedError("Implement validate_ehr")


def text_to_bytes(text: str) -> bytes:
    """Convert EHR text to UTF-8 bytes."""
    # TODO (Erlinda): Encode text.
    raise NotImplementedError("Implement text_to_bytes")


def bytes_to_text(data: bytes) -> str:
    """Convert UTF-8 bytes back to text."""
    # TODO (Erlinda): Decode bytes.
    raise NotImplementedError("Implement bytes_to_text")
