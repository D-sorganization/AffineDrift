"""Historical research admission never promotes rejected numerical evidence."""

import hashlib
import json
from copy import deepcopy

import pytest

from src.affine_control.historical_research import admit_package, render_research_page

COMMIT = "a" * 40
SHA = "b" * 64


def record(player="tiger"):
    return {
        "player_id": player,
        "player_name": player.title(),
        "swing_id": player + "-swing",
        "fit_id": player + "-fit-v12",
        "producer_commit": COMMIT,
        "hashes": {name: SHA for name in ("source", "capture", "model", "fit", "input")},
        "source_clock": {
            "start": {"numerator": 1, "denominator": 3},
            "end": {"numerator": 2, "denominator": 3},
            "origin": "video_presentation_time",
            "frame_count": 2,
            "physical_time": "unknown",
        },
        "execution_status": "succeeded",
        "qualification": "monocular_research_hypothesis",
        "scientific_acceptance": "rejected",
        "optimizer_converged": False,
        "continuous_certified": False,
        "targets": [{"id": "sampled-grip", "passed": True}],
        "metrics": {
            name: 1.0
            for name in (
                "training_rms_px",
                "held_out_rms_px",
                "dense_rms_px",
                "grip_gap_mm",
                "grip_angle_deg",
                "penetration_mm",
            )
        },
        "metric_definition": "confidence-weighted Euclidean landmark RMS",
        "unknown_visibility_weight": 0.5,
        "rights": {"status": "unresolved", "distribution": "not_authorized"},
        "limitations": ["Physical time and camera remain unqualified"],
    }


def package():
    return {
        "schema": "upstreamdrift/historical-player-research/v1",
        "provider": {
            "repository": "D-sorganization/UpstreamDrift",
            "source_commit": COMMIT,
            "source_url": f"https://github.com/D-sorganization/UpstreamDrift/tree/{COMMIT}",
        },
        "distribution": {
            "scope": "local_research_only",
            "decision": "not_authorized_for_publication",
            "contains_original_media": False,
        },
        "records": [record(), record("hogan")],
    }


def admitted(value):
    payload = json.dumps(value).encode()
    return admit_package(payload, hashlib.sha256(payload).hexdigest(), len(payload), COMMIT)


def test_rejected_target_pass_remains_rejected_and_detached():
    value = package()
    result = admitted(value)
    value["records"][0]["player_name"] = "mutated"
    page = render_research_page(result)
    assert "Tiger" in page and "mutated" not in page
    assert "rejected" in page and "unknown" in page
    assert "Local Research" in page and "not_authorized" in page
    assert render_research_page(result) == page


@pytest.mark.parametrize(
    "field,value",
    [
        ("scientific_acceptance", "accepted"),
        ("qualification", "qualified"),
        ("continuous_certified", True),
        ("optimizer_converged", True),
    ],
)
def test_status_promotion_rejected(field, value):
    data = package()
    data["records"][0][field] = value
    with pytest.raises(ValueError):
        admitted(data)


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate_fit",
        "duplicate_target",
        "bad_clock",
        "negative_metric",
        "nan",
        "media",
        "local_path",
        "mutable_source",
        "unknown_field",
    ],
)
def test_invalid_evidence_fails_closed(mutation):
    data = package()
    item = data["records"][0]
    if mutation == "duplicate_fit":
        data["records"].append(deepcopy(item))
    elif mutation == "duplicate_target":
        item["targets"].append(deepcopy(item["targets"][0]))
    elif mutation == "bad_clock":
        item["source_clock"]["end"]["denominator"] = 0
    elif mutation == "negative_metric":
        item["metrics"]["dense_rms_px"] = -1
    elif mutation == "nan":
        item["metrics"]["dense_rms_px"] = float("nan")
    elif mutation == "media":
        data["distribution"]["contains_original_media"] = True
    elif mutation == "local_path":
        item["limitations"].append("C:/Users/private/video.mp4")
    elif mutation == "mutable_source":
        data["provider"][
            "source_url"
        ] = "https://github.com/D-sorganization/UpstreamDrift/tree/main"
    elif mutation == "unknown_field":
        item["raw_video"] = "original.mp4"
    with pytest.raises(ValueError):
        admitted(data)


def test_exact_payload_size_hash_and_producer_are_admission_preconditions():
    payload = json.dumps(package()).encode()
    for digest, size, commit in [
        ("c" * 64, len(payload), COMMIT),
        (hashlib.sha256(payload).hexdigest(), len(payload) + 1, COMMIT),
        (hashlib.sha256(payload).hexdigest(), len(payload), "d" * 40),
    ]:
        with pytest.raises(ValueError):
            admit_package(payload, digest, size, commit)


def test_generic_third_player_and_order_independent_generation():
    data = package()
    data["records"].append(record("third-player"))
    expected = render_research_page(admitted(data))
    data["records"].reverse()
    actual = render_research_page(admitted(data))

    # Exact-byte provenance changes with input order; generic presentation order does not.
    def without_hash(page):
        return [line for line in page.splitlines() if not line.startswith("Package SHA-256:")]

    assert without_hash(actual) == without_hash(expected)
    assert "Third-Player" in expected


def acquisition(tmp_path):
    from src.affine_control.historical_research import (
        HistoricalResearchConsumer,
        ResearchImportPins,
    )
    from src.affine_control.historical_research.admission import SCHEMA_ID, SCHEMA_PATH
    from src.affine_control.programming_companion import (
        ConsumerPolicy,
        DirectoryTransport,
        ImportRequest,
    )

    payload = json.dumps(package()).encode()
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "research.json").write_bytes(payload)
    schema = SCHEMA_PATH.read_bytes()
    (bundle / "schema.json").write_bytes(schema)
    policy = ConsumerPolicy(
        "raw.githubusercontent.com",
        "D-sorganization",
        "UpstreamDrift",
        "https://github.com/D-sorganization/UpstreamDrift",
        "research.json",
        "schema.json",
        SCHEMA_ID,
    )
    prefix = f"https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/{COMMIT}/"
    request = ImportRequest(
        COMMIT,
        prefix + "research.json",
        hashlib.sha256(payload).hexdigest(),
        prefix + "schema.json",
        hashlib.sha256(schema).hexdigest(),
    )
    consumer = HistoricalResearchConsumer(
        policy, DirectoryTransport(bundle, prefix), tmp_path / "store"
    )
    return consumer, ResearchImportPins(request, len(payload), len(schema)), bundle


def test_shared_transport_and_atomic_store_install_are_local_research_only(tmp_path):
    consumer, pins, _ = acquisition(tmp_path)
    inspected = consumer.inspect(pins)
    assert len(inspected.records) == 2
    assert not (tmp_path / "store").exists()
    lock = consumer.install(pins)
    assert lock.publication_state == "draft"
    assert consumer.install(pins) == lock
    assert consumer.recall().manifest_sha256 == inspected.manifest_sha256
    saved = tmp_path / "store/historical-player-research-v1/snapshots" / lock.snapshot_id
    (saved / "manifest.json").write_bytes(b"changed")
    with pytest.raises(ValueError):
        consumer.recall()


def test_renderer_does_not_enable_markdown_or_html_from_labels():
    data = package()
    data["records"][0]["player_name"] = "![Secret](https://example.test/pixel) <script>x</script>"
    page = render_research_page(admitted(data))
    assert "![Secret]" not in page
    assert "<script>" not in page


def test_serialized_record_is_detached_from_validated_evidence():
    result = admitted(package())
    detached = result.records[0].to_record()
    detached["scientific_acceptance"] = "accepted"
    assert result.records[0].to_record()["scientific_acceptance"] == "rejected"


def test_duplicate_json_keys_and_oversized_payload_rejected():
    from src.affine_control.historical_research.models import MAX_BYTES

    for payload in [b'{"schema":"one","schema":"two"}', b"x" * (MAX_BYTES + 1)]:
        with pytest.raises(ValueError):
            admit_package(payload, hashlib.sha256(payload).hexdigest(), len(payload), COMMIT)


def test_local_scope_cannot_be_promoted_to_public():
    data = package()
    data["distribution"]["scope"] = "public"
    with pytest.raises(ValueError):
        admitted(data)


@pytest.mark.parametrize("manifest_delta,schema_delta", [(1, 0), (0, 1)])
def test_acquisition_requires_independent_manifest_and_schema_byte_pins(
    tmp_path, manifest_delta, schema_delta
):
    from src.affine_control.historical_research import ResearchImportPins

    consumer, original, _ = acquisition(tmp_path)
    pins = ResearchImportPins(
        original.request,
        original.manifest_bytes + manifest_delta,
        original.schema_bytes + schema_delta,
    )
    with pytest.raises(ValueError, match="byte"):
        consumer.install(pins)
    assert not (tmp_path / "store").exists()


def test_swing_identity_cannot_change_player_ownership():
    data = package()
    data["records"][1]["swing_id"] = data["records"][0]["swing_id"]
    with pytest.raises(ValueError, match="swing"):
        admitted(data)


def test_recall_rejects_foreign_repository_lock_even_when_bytes_match(tmp_path):
    from dataclasses import replace

    consumer, pins, _ = acquisition(tmp_path)
    lock = consumer.install(pins)
    foreign = replace(lock, repository="different/provider")
    path = tmp_path / "store/historical-player-research-v1/active-lock.json"
    path.write_bytes(foreign.to_bytes())
    with pytest.raises(ValueError, match="provider"):
        consumer.recall()


def test_recall_revalidates_immutable_transport_urls(tmp_path):
    from dataclasses import replace

    consumer, pins, _ = acquisition(tmp_path)
    lock = consumer.install(pins)
    changed = replace(lock, manifest_url=lock.manifest_url.replace(COMMIT, "main"))
    path = tmp_path / "store/historical-player-research-v1/active-lock.json"
    path.write_bytes(changed.to_bytes())
    with pytest.raises(ValueError):
        consumer.recall()


def test_schema_pin_cannot_substitute_a_different_admission_contract(tmp_path):
    from dataclasses import replace

    from src.affine_control.historical_research import ResearchImportPins

    consumer, pins, bundle = acquisition(tmp_path)
    altered = json.loads((bundle / "schema.json").read_bytes())
    altered["properties"]["schema"]["const"] = "different/v1"
    payload = json.dumps(altered).encode()
    (bundle / "schema.json").write_bytes(payload)
    changed = replace(pins.request, schema_sha256=hashlib.sha256(payload).hexdigest())
    with pytest.raises(ValueError, match="schema"):
        consumer.install(ResearchImportPins(changed, pins.manifest_bytes, len(payload)))
    assert not (tmp_path / "store").exists()


@pytest.mark.parametrize("mode", ["redirect", "hash", "empty", "oversize"])
def test_acquisition_rejects_transport_inconsistency_before_storage(tmp_path, mode):
    from src.affine_control.historical_research import HistoricalResearchConsumer
    from src.affine_control.historical_research.admission import SCHEMA_ID
    from src.affine_control.historical_research.models import MAX_BYTES
    from src.affine_control.programming_companion import ConsumerPolicy
    from src.affine_control.programming_companion.models import FetchResult

    _, pins, bundle = acquisition(tmp_path)
    payload = (bundle / "research.json").read_bytes()

    class BrokenTransport:
        def fetch(self, url, max_bytes):
            content = {
                "hash": payload + b" ",
                "empty": b"",
                "oversize": b"x" * (MAX_BYTES + 1),
            }.get(mode, payload)
            return FetchResult(url, url, (url,) if mode == "redirect" else (), content)

    policy = ConsumerPolicy(
        "raw.githubusercontent.com",
        "D-sorganization",
        "UpstreamDrift",
        "https://github.com/D-sorganization/UpstreamDrift",
        "research.json",
        "schema.json",
        SCHEMA_ID,
    )
    consumer = HistoricalResearchConsumer(policy, BrokenTransport(), tmp_path / "rejected")
    with pytest.raises(ValueError):
        consumer.install(pins)
    assert not (tmp_path / "rejected").exists()


def test_conflicting_research_pin_cannot_replace_saved_evidence(tmp_path):
    from dataclasses import replace

    from src.affine_control.historical_research import ResearchImportPins
    from src.affine_control.programming_companion.errors import ExistingPinConflict

    consumer, pins, _ = acquisition(tmp_path)
    initial = consumer.install(pins)
    candidate = replace(pins.request, manifest_sha256="c" * 64)
    with pytest.raises(ExistingPinConflict):
        consumer.install(ResearchImportPins(candidate, pins.manifest_bytes, pins.schema_bytes))
    assert consumer.recall().manifest_sha256 == initial.manifest_sha256
