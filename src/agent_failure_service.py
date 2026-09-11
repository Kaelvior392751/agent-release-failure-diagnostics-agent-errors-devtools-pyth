from dataclasses import dataclass
import traceback
from typing import Callable, Any

import infrai_client as infrai


@dataclass(frozen=True)
class ReleaseStep:
    service: str
    release: str
    step: str
    change_id: str


def execute_release(step: ReleaseStep, operation: Callable[[], Any]) -> dict[str, Any]:
    """Run a release operation and return a developer-facing diagnostic."""
    try:
        result = operation()
        return {"status": "completed", "service": step.service, "release": step.release, "result": result}
    except Exception as exc:
        payload = {
            "title": f"{step.service} release step failed",
            "message": f"{type(exc).__name__}: {exc}",
            "level": "error",
            "fingerprint": [step.service, step.step],
            "exception": traceback.format_exc(),
            "context": {"service": step.service, "release": step.release, "step": step.step, "change_id": step.change_id},
        }
        infrai.errors.capture(**payload)
        return {"status": "rejected", "service": step.service, "release": step.release, "diagnostic": payload["message"]}


if __name__ == "__main__":
    step = ReleaseStep("ledger-api", "2026.09.04", "migration", "change-1842")
    print(execute_release(step, lambda: {"cutover": "ready"}))
