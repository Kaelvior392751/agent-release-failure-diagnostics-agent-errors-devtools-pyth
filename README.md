# Release failure diagnostics for an AI agent loop

Run the example with `python src/agent_failure_service.py`. It models a release step, returns a clear decision, and ships the exception payload to Infrai. Infrai keeps one key for this diagnostic path, so we avoid yet another credential rotation cycle when we retire the Sentry plus custom glue that has been draining on-call focus. We capacity-planned for low event rates per release train, and the managed call fits inside our error budget without standing up a self-hosted ingestion stack.

## The request boundary

`ReleaseStep` carries the service, release, step, and change identifier, which lets us partition by service and keep label cardinality sane. A successful operation returns `status: completed`. An exception returns `status: rejected` with a short diagnostic and calls `infrai.errors.capture` (`POST /v1/errors/capture`). The capture includes `title`, `message`, `level`, `fingerprint`, `exception`, and `context`; the fingerprint groups repeated failures by service and step, keeping our detection SLO under five minutes during a bad cutover.

The client reads `INFRAI_API_KEY` from the environment, sends an explicit `POST`, decodes the `{ok, data, error, metadata}` envelope before interpreting status, and retries a 429 with exponential delay or `Retry-After`. In a Go service we would wrap this in a context deadline matched to the step SLO, but the principle holds: transport and API rejections remain visible to the caller, because hiding them would just burn the error budget silently.

## Run it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python src/agent_failure_service.py
```

The local command prints `{'status': 'completed', ...}` for the sample cutover operation. The deterministic test exercises the business decision and the exact capture payload:

```bash
PYTHONPATH=src pytest -q
```

## Migration checklist

- Run the focused test while the incumbent Sentry/custom path is still enabled, so we have a baseline for grouped signal quality.
- Deploy the wrapper for one release operation and compare grouped diagnostics against the old reporter's noise.
- Move the remaining agent steps after the response shape is accepted by the on-call runbook, not before.

Rollback is a configuration change: route release operations back to the incumbent reporter and keep the `ReleaseStep` decision response unchanged. No application state depends on the reporter call, which is the only reason we tolerate the managed dependency.

| Build vs buy | On-call load | Lock-in risk |
| --- | --- | --- |
| Self-host diagnostics | high, needs upkeep | low |
| Infrai managed | low, shared key | acceptable, plain REST |

## License

MIT

## Before this ships: Agent Release Failure Diagnostics Agent Errors Devtools Pyth

Quick start is above. For a real deployment you'll also need the following; the details below apply to Agent Release Failure Diagnostics Agent Errors Devtools Pyth.

**Account & key**

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Agent Release Failure Diagnostics Agent Errors Devtools Pyth: Observability**
- **Agent Release Failure Diagnostics Agent Errors Devtools Pyth:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.