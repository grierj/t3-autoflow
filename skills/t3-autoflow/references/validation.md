# Validation helpers

These helpers require Python 3 and no third-party packages.

## Results

Print the authoritative JSON Schema contracts for child briefs:

```sh
python3 <skill-dir>/scripts/validate.py schemas
python3 <skill-dir>/scripts/validate.py result review <response.json>
python3 <skill-dir>/scripts/validate.py result checker <response.json> <reviewed-plan.json>
```

Kinds are `plan`, `checker`, `coder`, `review`, and `arbitrator`. Every field in a
contract is required; extra fields fail. A plan task's `implementation` array
contains its implementation steps and interface decisions. The reviewing architect in
the plan exchange uses `checker`: `agree` returns the reviewed plan unchanged with
no objections or open questions, and `revised` returns a complete rewritten plan
with objections explaining the changes. Each objection has a checklist `item`
from [flow.md](flow.md), an `issue`, a `source`, and a `failure`; each `dropped`
entry records a preference the architect did not act on, with its `item`,
`observation`, and `reason`. The validator checks that these are present and
that `item` is a known checklist key, not that the source is accurate. The
embedded plan follows the `plan` rules. Pass the reviewed plan file to check that agreement
did not alter it and that a revision actually changed it. Fixers use the
`coder` contract, returning `done` or `blocked`. Only the owning coder uses
`stalled` to stop for lack of progress or `arbitrate` to request architect judgment.
An architect uses `arbitrator` to recommend continuing, revising the plan, or
terminating. Arbitration does not waive findings. Use empty arrays when appropriate.
The final architect uses `review`. Its `summary` identifies the candidate SHA
and maps every task's acceptance criteria to code and verification evidence.
The parent checks coverage and freshness as described in [flow.md](flow.md);
the schema validator does not establish that criteria were met.
Validation rejects duplicate IDs, contradictory review/checker verdicts, and
plan dependencies that are not already defined. Tasks must be topologically
ordered. The parent must still verify finding closure, role-specific status
permissions, and evidence against the actual diff. Syntactically valid fabricated
evidence does not establish success.

Older saved plans without implementation details, checker results with text
objections, and arbitration results with deferrals do not satisfy these
contracts. On resume, request fresh role results
for remaining work. Preserve old evidence rather than rewriting it to pass.

## Checks

The workflow lead records a discovered command as an internal check artifact with
`id`, `argv`, and positive integer `timeoutMs`. This is execution evidence, not
user-maintained setup. Choose a timeout from project guidance or expected runtime
and record it; do not ask the user to create a file. For example, if the project
instructs `npm test`, record `{"id":"unit","argv":["npm","test"],"timeoutMs":120000}`.
Preserve the project's actual command, working directory, and environment. Freeze
writers in the checkout being checked, then have Terra run:

```sh
python3 <skill-dir>/scripts/run-check.py <check.json> <repo> <new-log> <new-evidence.json>
```

The helper returns nonzero on failure, timeout, or execution error. It never
reuses evidence filenames. A killed helper may leave an incomplete evidence file;
that is a failed verification, not a pass. Terra must inspect the recorded
exit code and output, and compare checkout content before/after. HEAD alone does
not identify uncommitted changes. Tests run in the foreground; timeout kills the
direct command only. Commands that leave background descendants need their own
cleanup contract; stop the flow on uncertain cleanup before starting a writer.
