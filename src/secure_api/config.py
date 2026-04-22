def mask_secret(value: str, visible_suffix: int = 4) -> str:
    """Return a redacted view of a secret while keeping a short suffix."""
    if visible_suffix < 0:
        raise ValueError("visible_suffix must be non-negative")

    if not value:
        return ""

    if len(value) <= visible_suffix:
        return "*" * len(value)

    hidden_len = len(value) - visible_suffix
    return ("*" * hidden_len) + value[-visible_suffix:]
