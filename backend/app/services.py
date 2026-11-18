from fastapi import HTTPException


def ensure_editable(status: str):
    if status == "ARCHIVED":
        raise HTTPException(409, "Архивный проект доступен только для чтения")


def change_status(current: str, target: str) -> str:
    ensure_editable(current)
    return target
