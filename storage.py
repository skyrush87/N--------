import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


TABLE_NAME = "agent_taikun_state"


class StorageError(RuntimeError):
    """A safe-to-display error from cloud state storage."""


@dataclass
class DepartmentState:
    history: list[dict[str, str]]
    plan: str
    approved: bool


def _setting(name: str) -> str:
    try:
        value = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        value = None
    return str(value or os.getenv(name, "")).strip()


def _supabase_config() -> tuple[str, str]:
    url = _setting("SUPABASE_URL").rstrip("/")
    service_key = _setting("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not service_key:
        raise StorageError(
            "Supabase 설정이 없습니다. SUPABASE_URL과 "
            "SUPABASE_SERVICE_ROLE_KEY를 설정해 주세요."
        )
    if not url.startswith("https://"):
        raise StorageError("SUPABASE_URL은 HTTPS 주소여야 합니다.")
    return url, service_key


def _headers(service_key: str) -> dict[str, str]:
    return {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }


def _validate_history(history: list[dict[str, str]]) -> None:
    if not isinstance(history, list) or any(
        not isinstance(message, dict)
        or not isinstance(message.get("role"), str)
        or not isinstance(message.get("content"), str)
        for message in history
    ):
        raise StorageError("저장된 대화 기록 형식이 올바르지 않습니다.")


def load_department_state(user_id: str, department: str) -> DepartmentState:
    url, service_key = _supabase_config()
    try:
        response = requests.get(
            f"{url}/rest/v1/{TABLE_NAME}",
            headers=_headers(service_key),
            params={
                "select": "history,plan,approved",
                "user_id": f"eq.{user_id}",
                "department": f"eq.{department}",
                "limit": "1",
            },
            timeout=15,
        )
        response.raise_for_status()
        rows = response.json()
    except requests.RequestException as exc:
        raise StorageError("클라우드 기록을 불러오지 못했습니다. Supabase 설정을 확인해 주세요.") from exc

    if not isinstance(rows, list):
        raise StorageError("클라우드 기록 응답 형식이 올바르지 않습니다.")
    if not rows:
        return DepartmentState(history=[], plan="", approved=False)

    row = rows[0]
    if not isinstance(row, dict):
        raise StorageError("클라우드 기록 응답 형식이 올바르지 않습니다.")
    history = row.get("history")
    plan = row.get("plan")
    approved = row.get("approved")
    _validate_history(history)
    if not isinstance(plan, str) or not isinstance(approved, bool):
        raise StorageError("저장된 부서 상태 형식이 올바르지 않습니다.")
    return DepartmentState(history=history, plan=plan, approved=approved)


def save_department_state(
    user_id: str,
    department: str,
    history: list[dict[str, str]],
    plan: str,
    approved: bool,
) -> None:
    _validate_history(history)
    url, service_key = _supabase_config()
    try:
        response = requests.post(
            f"{url}/rest/v1/{TABLE_NAME}",
            headers={
                **_headers(service_key),
                "Prefer": "resolution=merge-duplicates,return=minimal",
            },
            params={"on_conflict": "user_id,department"},
            json={
                "user_id": user_id,
                "department": department,
                "history": history,
                "plan": plan,
                "approved": approved,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            timeout=15,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise StorageError("클라우드 기록을 저장하지 못했습니다. Supabase 설정을 확인해 주세요.") from exc
