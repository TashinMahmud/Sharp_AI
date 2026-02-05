
from typing import Any

_SESSIONS: dict[tuple[str, str], dict[str, Any]] = {}


def _key(user_id: str, session_id: str) -> tuple[str, str]:
    return (user_id, session_id)


def get_session(user_id: str, session_id: str) -> dict[str, Any] | None:
    return _SESSIONS.get(_key(user_id, session_id))


def get_or_create_session(user_id: str, session_id: str) -> dict[str, Any]:
    key = _key(user_id, session_id)
    if key not in _SESSIONS:
        _SESSIONS[key] = {"messages": [], "summary": None}
    return _SESSIONS[key]


def set_session(user_id: str, session_id: str, data: dict[str, Any]) -> None:
    _SESSIONS[_key(user_id, session_id)] = data
