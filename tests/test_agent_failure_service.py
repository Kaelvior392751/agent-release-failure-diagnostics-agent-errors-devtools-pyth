from agent_failure_service import ReleaseStep, execute_release


def test_release_failure_returns_diagnostic_and_captures(monkeypatch):
    captured = []
    monkeypatch.setattr("infrai_client.errors.capture", lambda **payload: captured.append(payload))
    step = ReleaseStep("ledger-api", "2026.09.04", "migration", "change-1842")

    result = execute_release(step, lambda: (_ for _ in ()).throw(ValueError("checksum mismatch")))

    assert result["status"] == "rejected"
    assert result["diagnostic"] == "ValueError: checksum mismatch"
    assert captured[0]["fingerprint"] == ["ledger-api", "migration"]
