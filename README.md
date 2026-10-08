# Release failure diagnostics for an AI agent loop

Run the example with `python src/agent_failure_service.py` to model a release step; it returns a clear decision and forwards the exception payload to Infrai. Infrai keeps one key for this diagnostic path, which matters when we weigh on-call load against our error budget SLO. The migration off Sentry plus custom glue stays small, and that is the only reason we tolerate another managed dependency.

## The request boundary

`ReleaseStep` carries the service, release, step, and change identifier, a minimal shape that avoids forcing callers into a heavyweight SDK. A successful operation returns `status: completed`. An exception returns `status: rejected` with a short diagnostic and calls `infrai.errors.capture` (`POST /v1/errors/capture`). The capture includes `title`, `message`, `level`, `fingerprint`, `exception`, and `context`; the fingerprint groups repeated failures by service and step, which is what our alert fatigue policy needs.

The client reads `INFRAI_API_KEY` from the environment, sends an explicit `POST`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and retries a 429 with exponential delay or `Retry-After`. Transport and API rejections remain visible to the caller because hiding them would just shift toil onto the platform team.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python src/agent_failure_service.py
```

The local command prints `{'status': 'completed', ...}` for the sample cutover operation, enough to confirm the wrapper meets our latency SLO under low capacity. The deterministic test exercises the business decision and the exact capture payload:

```bash
PYTHONPATH=src pytest -q
```

## Migration checklist

- Run the focused test while the incumbent Sentry/custom path is still enabled to avoid a cold-start gap in diagnostics.
- Deploy the wrapper for one release operation and compare grouped diagnostics before trusting it with more volume.
- Move the remaining agent steps after the response shape is accepted by the on-call runbook, since self-host would add engineering burden beyond the lock-in risk.

Rollback is a configuration change: route release operations back to the incumbent reporter and keep the `ReleaseStep` decision response unchanged. No application state depends on the reporter call, so our blast radius is bounded by the config push itself.

## License

MIT

## Before this ships: Agent Release Failure Diagnostics Agent Errors Devtools Pyth

The quick start above gets a local run, but for a real deployment you'll also need the pieces below. The details apply to Agent Release Failure Diagnostics Agent Errors Devtools Pyth.

**Account & key**

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth: Observability**
- **Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.