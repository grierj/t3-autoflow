# Validation helpers

These helpers require Python 3 and no third-party packages.

## Results

Print the authoritative JSON Schema contracts for child briefs:

```sh
python3 <skill-dir>/scripts/validate.py schemas
python3 <skill-dir>/scripts/validate.py result review <response.json>
```

Kinds are `plan`, `checker`, `coder`, `review`, and `arbitrator`. Every field in a
contract is required; extra fields fail. Use empty arrays when appropriate.
Validation rejects duplicate IDs, contradictory review/checker verdicts, and
plan dependencies that are not already defined. Tasks must be topologically
ordered. The parent must still verify finding closure, severity-specific
arbitration permissions, and evidence against the actual diff. Syntactically valid
fabricated evidence does not pass a gate.

## Checks

The parent records a discovered command as an internal check artifact with
`id`, `argv`, and positive integer `timeoutMs`. This is execution evidence, not
user-maintained setup. Choose a timeout from project guidance or expected runtime
and record it; do not ask the user to create a file. For example, if the project
instructs `npm test`, record `{"id":"unit","argv":["npm","test"],"timeoutMs":120000}`.
Preserve the project's actual command, working directory, and environment. Freeze writers,
then run:

```sh
python3 <skill-dir>/scripts/run-check.py <check.json> <repo> <new-log> <new-evidence.json>
```

The helper returns nonzero on failure, timeout, or execution error. It never
reuses evidence filenames. A killed helper may leave an incomplete evidence file;
that is a failed verification, not a pass. The parent must inspect the recorded
exit code and output, and compare checkout content before/after. HEAD alone does
not identify uncommitted changes. Tests run in the foreground; timeout kills the
direct command only. Commands that leave background descendants need their own
cleanup contract; stop the flow on uncertain cleanup before starting a writer.
