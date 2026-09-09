from __future__ import annotations

from scripts.backend_contract import bucket_contract

EXPECTED_NAME = "example-state-bucket"
EXPECTED_LOCATION = "us-central1"


def test_bucket_contract_accepts_gcloud_storage_shape() -> None:
    payload = {
        "name": EXPECTED_NAME,
        "location": "US-CENTRAL1",
        "default_storage_class": "STANDARD",
        "uniform_bucket_level_access": True,
        "public_access_prevention": "enforced",
        "versioning_enabled": True,
        "soft_delete_policy": {"retentionDurationSeconds": "604800"},
    }

    ready, drift = bucket_contract(
        payload,
        expected_name=EXPECTED_NAME,
        expected_location=EXPECTED_LOCATION,
    )

    assert ready is True
    assert drift == []


def test_bucket_contract_keeps_api_style_shape_compatible() -> None:
    payload = {
        "name": f"gs://{EXPECTED_NAME}/",
        "location": EXPECTED_LOCATION,
        "storageClass": "STANDARD",
        "iamConfiguration": {
            "uniformBucketLevelAccess": {"enabled": True},
            "publicAccessPrevention": "enforced",
        },
        "versioning": {"enabled": True},
        "softDeletePolicy": {"retentionDurationSeconds": 604800},
    }

    ready, drift = bucket_contract(
        payload,
        expected_name=EXPECTED_NAME,
        expected_location=EXPECTED_LOCATION,
    )

    assert ready is True
    assert drift == []
