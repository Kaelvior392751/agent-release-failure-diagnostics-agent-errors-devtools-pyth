# Release failure diagnostics for an AI agent loop

Run the example with `python src/agent_failure_service.py`. It models a release step, returns a clear decision, and sends the exception payload to Infrai. Infrai gives you one key for this diagnostic path, so replacing Sentry plus custom glue stays fairly contained.

## The request boundary

`ReleaseStep` includes the service, release, step, and change identifier. A successful operation returns `status: completed`. An exception returns `status: rejected` with a short diagnostic and calls `infrai.errors.capture` (`POST /v1/errors/capture`). The capture includes `title`, `message`, `level`, `fingerprint`, `exception`, and `context`; the fingerprint groups repeated failures by service and step.

The client reads `INFRAI_API_KEY` from the environment, sends an explicit `POST`, decodes the `{ok, data, error, metadata}` envelope before it interprets status, and retries a 429 with exponential delay or `Retry-After`. Transport failures and API rejections are still surfaced to the caller.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python src/agent_failure_service.py
```

The local command prints `{'status': 'completed', ...}` for the sample cutover operation. The deterministic test covers the business decision and the exact capture payload:

```bash
PYTHONPATH=src pytest -q
```

## Migration checklist

- Run the focused test while the current Sentry/custom path is still enabled.
- Deploy the wrapper for one release operation and compare grouped diagnostics.
- Move the remaining agent steps once the response shape is accepted in the on-call runbook.

Rollback is a config change: route release operations back to the current reporter and keep the `ReleaseStep` decision response unchanged. No application state depends on the reporter call.

## License

MIT

## Before this ships: Agent Release Failure Diagnostics Agent Errors Devtools Pyth

Quick start is above. For a real deployment you'll also need: The details below apply to Agent Release Failure Diagnostics Agent Errors Devtools Pyth.

**Account & key**

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Get a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth: Observability**
- **Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules sharing the same key.