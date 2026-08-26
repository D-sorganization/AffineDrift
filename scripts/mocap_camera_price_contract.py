"""Fail-closed contract for scoped markerless-mocap price observations."""

from __future__ import annotations

from datetime import date, timedelta
from typing import cast

from scripts.mocap_camera_registry_contract import CameraRegistryError

PRICE_ATTRIBUTES = frozenset({"camera_body_price", "complete_qualified_topology_cost"})
PRICE_KEYS = {
    "amount",
    "currency",
    "region",
    "sku",
    "configuration",
    "price_scope",
    "tax_status",
    "shipping_status",
    "availability",
}
PRICE_REVIEW_MAX_AGE = timedelta(days=31)
PRICE_SCOPES = frozenset({"camera_body_only", "complete_qualified_topology"})
PRICE_INCLUSION_STATES = frozenset({"excluded", "included", "not_established"})
PRICE_AVAILABILITY_STATES = frozenset(
    {
        "dispatch_estimate_published",
        "in_production",
        "online_shop_price_not_exposed",
        "quote_required",
    }
)


def _price_object(value: object, claim_id: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CameraRegistryError(f"claim {claim_id} price must be an object")
    price = cast(dict[str, object], value)
    if set(price) != PRICE_KEYS:
        raise CameraRegistryError(f"claim {claim_id} price fields differ")
    return price


def _required_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CameraRegistryError(f"{label} must be a non-empty string")
    return value


def _optional_text(value: object, label: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, label)


def _iso_date(value: object, label: str) -> date:
    text = _required_text(value, label)
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise CameraRegistryError(f"{label} must be an ISO date") from error


def _validate_metadata(price: dict[str, object], claim_id: str) -> str | None:
    currency = _optional_text(price["currency"], f"claim {claim_id} currency")
    region = _required_text(price["region"], f"claim {claim_id} region")
    _optional_text(price["sku"], f"claim {claim_id} SKU")
    _required_text(price["configuration"], f"claim {claim_id} configuration")
    scope = _required_text(price["price_scope"], f"claim {claim_id} price scope")
    tax_status = _required_text(price["tax_status"], f"claim {claim_id} tax status")
    shipping_status = _required_text(
        price["shipping_status"], f"claim {claim_id} shipping status"
    )
    availability = _required_text(price["availability"], f"claim {claim_id} availability")
    if region != "GLOBAL" and not (len(region) == 2 and region.isalpha() and region.isupper()):
        raise CameraRegistryError(f"claim {claim_id} region must be ISO alpha-2 or GLOBAL")
    if currency is not None and not (
        len(currency) == 3 and currency.isalpha() and currency.isupper()
    ):
        raise CameraRegistryError(f"claim {claim_id} currency must be ISO 4217 or null")
    if scope not in PRICE_SCOPES:
        raise CameraRegistryError(f"claim {claim_id} price scope is unsupported")
    if tax_status not in PRICE_INCLUSION_STATES:
        raise CameraRegistryError(f"claim {claim_id} tax status is unsupported")
    if shipping_status not in PRICE_INCLUSION_STATES:
        raise CameraRegistryError(f"claim {claim_id} shipping status is unsupported")
    if availability not in PRICE_AVAILABILITY_STATES:
        raise CameraRegistryError(f"claim {claim_id} availability is unsupported")
    return currency


def _validate_evidence_state(claim: dict[str, object], claim_id: str, attribute: str) -> None:
    evidence_class = _required_text(claim["evidence_class"], f"claim {claim_id} evidence class")
    status = _required_text(claim["status"], f"claim {claim_id} status")
    if attribute == "complete_qualified_topology_cost":
        if evidence_class != "unavailable" or status != "unavailable":
            raise CameraRegistryError(f"claim {claim_id} complete topology cost is unavailable")
    elif evidence_class != "vendor_spec" or status not in {"current", "provisional"}:
        raise CameraRegistryError(f"claim {claim_id} camera-body price must be a vendor observation")


def _validate_scope(
    price: dict[str, object], claim_id: str, attribute: str, sources: list[str]
) -> None:
    expected_scope = {
        "camera_body_price": "camera_body_only",
        "complete_qualified_topology_cost": "complete_qualified_topology",
    }[attribute]
    if price["price_scope"] != expected_scope:
        raise CameraRegistryError(f"claim {claim_id} price scope does not match its attribute")
    if attribute == "complete_qualified_topology_cost":
        if any(price[field] is not None for field in ("amount", "currency", "sku")):
            raise CameraRegistryError(f"claim {claim_id} complete topology cost must be unavailable")
        if price["availability"] != "quote_required" or sources:
            raise CameraRegistryError(f"claim {claim_id} complete topology cost requires a quote")
        return
    amount = price["amount"]
    currency = price["currency"]
    if amount is None:
        if currency is not None or price["availability"] != "online_shop_price_not_exposed":
            raise CameraRegistryError(f"claim {claim_id} unavailable body amount is inconsistent")
    elif type(amount) not in {int, float} or amount <= 0 or currency is None:
        raise CameraRegistryError(f"claim {claim_id} amount must be positive and typed with currency")
    if not sources:
        raise CameraRegistryError(f"claim {claim_id} camera-body price requires a vendor source")


def verify_price_claim(claim: dict[str, object], sources: list[str]) -> None:
    """Validate a typed body-price or complete-topology-cost claim.

    Args:
        claim: Registry claim whose attribute is in ``PRICE_ATTRIBUTES``.
        sources: Already validated source identifiers referenced by the claim.

    Raises:
        CameraRegistryError: If scope, metadata, freshness, or authority is invalid.
    """

    claim_id = _required_text(claim["id"], "price claim id")
    attribute = _required_text(claim["attribute"], f"claim {claim_id} attribute")
    if attribute not in PRICE_ATTRIBUTES:
        raise CameraRegistryError(f"claim {claim_id} is not a price claim")
    accessed_on = _iso_date(claim["accessed_on"], "price access date")
    review_due = _iso_date(claim["review_due"], "price review date")
    if review_due - accessed_on > PRICE_REVIEW_MAX_AGE:
        raise CameraRegistryError(f"claim {claim_id} volatile price review exceeds 31 days")
    price = _price_object(claim["value"], claim_id)
    _validate_metadata(price, claim_id)
    _validate_evidence_state(claim, claim_id, attribute)
    _validate_scope(price, claim_id, attribute, sources)
