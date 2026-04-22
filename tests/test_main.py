import pytest

from secure_api.config import mask_secret


def test_mask_secret_hides_all_but_suffix() -> None:
    assert mask_secret("supersecretvalue", visible_suffix=4) == "************alue"


def test_mask_secret_short_values_are_fully_masked() -> None:
    assert mask_secret("abc", visible_suffix=4) == "***"


def test_mask_secret_empty_string_returns_empty() -> None:
    assert mask_secret("") == ""


def test_mask_secret_rejects_negative_suffix() -> None:
    with pytest.raises(ValueError):
        mask_secret("secret", visible_suffix=-1)
