import pytest
from fastapi import HTTPException

from app.security import hasher, verify_password
from app.services import change_status


@pytest.mark.parametrize(
    "current,target",
    [
        ("DRAFT", "PUBLISHED"),
        ("PUBLISHED", "DRAFT"),
        ("DRAFT", "ARCHIVED"),
        ("PUBLISHED", "ARCHIVED"),
    ],
)
def test_allowed_transitions(current, target):
    assert change_status(current, target) == target


@pytest.mark.parametrize("target", ["DRAFT", "PUBLISHED", "ARCHIVED"])
def test_archive_is_read_only(target):
    with pytest.raises(HTTPException) as error:
        change_status("ARCHIVED", target)
    assert error.value.status_code == 409


def test_password_hash():
    encoded = hasher.hash("StrongPassword123!")
    assert encoded != "StrongPassword123!"
    assert verify_password("StrongPassword123!", encoded)
    assert not verify_password("wrong", encoded)
    assert not verify_password("anything", "invalid")
