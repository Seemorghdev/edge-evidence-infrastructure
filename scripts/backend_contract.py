"""Pure, credential-free Terraform backend bucket contract normalization."""

from __future__ import annotations

from typing import Any


def nested(payload: dict[str, Any], *path: str) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def read_field(payload: dict[str, Any], *candidates: tuple[str, ...]) -> Any:
    for path in candidates:
        value = nested(payload, *path)
        if value is not None:
            return value
    return None


def normalized_bucket_name(value: Any) -> str:
    text = str(value or "")
    return text.removeprefix("gs://").rstrip("/")


def soft_delete_seconds(payload: dict[str, Any]) -> int | None:
    raw = read_field(
        payload,
        ("softDeletePolicy", "retentionDurationSeconds"),
        ("soft_delete_policy", "retention_duration_seconds"),
        ("soft_delete_policy", "retentionDurationSeconds"),
    )
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def bucket_contract(
    payload: dict[str, Any],
    *,
    expected_name: str,
    expected_location: str,
    expected_storage_class: str = "STANDARD",
    expected_soft_delete_seconds: int = 604800,
) -> tuple[bool, list[dict[str, Any]]]:
    observed = {
        "name": normalized_bucket_name(payload.get("name")),
        "location": str(payload.get("location") or "").lower(),
        "storage_class": str(
            read_field(
                payload,
                ("storageClass",),
                ("storage_class",),
                ("defaultStorageClass",),
                ("default_storage_class",),
            )
            or ""
        ).upper(),
        "uniform_bucket_level_access": bool(
            read_field(
                payload,
                ("iamConfiguration", "uniformBucketLevelAccess", "enabled"),
                ("iam_configuration", "uniform_bucket_level_access", "enabled"),
                ("uniform_bucket_level_access",),
            )
        ),
        "public_access_prevention": str(
            read_field(
                payload,
                ("iamConfiguration", "publicAccessPrevention"),
                ("iam_configuration", "public_access_prevention"),
                ("public_access_prevention",),
            )
            or ""
        ).lower(),
        "versioning": bool(
            read_field(payload, ("versioning", "enabled"), ("versioning_enabled",))
        ),
        "soft_delete_seconds": soft_delete_seconds(payload),
    }
    expected = {
        "name": normalized_bucket_name(expected_name),
        "location": expected_location.lower(),
        "storage_class": expected_storage_class.upper(),
        "uniform_bucket_level_access": True,
        "public_access_prevention": "enforced",
        "versioning": True,
        "soft_delete_seconds": expected_soft_delete_seconds,
    }
    drift = [
        {"field": key, "observed": observed[key], "expected": value}
        for key, value in expected.items()
        if observed[key] != value
    ]
    return not drift, drift
