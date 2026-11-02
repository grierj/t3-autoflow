---
name: t3-autoflow
description: Run a planned, multi-model coding flow in T3 Code with independent reviews, project-discovered tests, and optional PR publication and merge. Use when the user asks for autoflow or its status, stop, or resume. Requires T3 delegation tools; does not apply to ordinary coding requests.
---

# T3 autoflow

Coordinate the flow in the current T3 parent thread. T3 owns child execution,
cancellation, and completion wakeups. This is an agent-followed procedure, not a
sandboxed workflow engine. Read [the runtime contract](references/runtime.md)
before starting or resuming; read [the flow procedure](references/flow.md) to run.
Read [discovery](references/discovery.md) to choose models and find project tests.
Use [validation](references/validation.md) for handoff and check helpers.

## Scope and invariants

- Preserve the user's requested scope. Record whether they authorized local work,
  PR publication, and merge. Invoking this skill alone does not authorize all three.
  Settle missing scope during planning, before autonomous execution.
- One flow and one code writer per checkout. Use shared-checkout delegates; never
  create worktrees. An existing T3-managed checkout is the working repository.
- Discover available providers and models through T3 and select them by role.
  Honor prompt overrides; record the choices. No silent substitution or CLI relay.
- Delegate planning, coding, review, and arbitration using the role briefs in the
  flow reference. Include all context in each brief; children inherit no history.
- Request JSON only. Save the exact result outside the checkout and validate it
  with `python3 <skill-dir>/scripts/validate.py result <kind> <file>` before using
  its verdict. Do not derive control decisions from a prose summary or repair
  malformed results yourself. See the validator's `schemas` command for contracts.
- Unit/e2e evidence comes from executing commands discovered in the project, never a coder's
  claim. Use `scripts/run-check.py` and inspect its JSON output and captured log.
- Reviewers and gates inspect only. Their read-only behavior is an instruction,
  not a T3 tool restriction. Unexpected changes invalidate the review.
- P0/P1 findings cannot be waived. Record explicit frontier-model disposition of
  every P2. Do not hide failed gates, provider errors, or unresolved findings.
- Children return questions or blocked results to the parent. After planning,
  route blockers to the arbitrator and write recovery guidance if work terminates.
  T3/provider permission prompts can still interrupt; never bypass them.

## Durable handoff

Store artifacts outside the checkout, for example under
`~/.local/state/t3-autoflow/<flow-id>/`. Only the parent writes these artifacts.
Persist the checkout path, parent thread ID/link, branch/base, authorized actions,
selected models, discovered checks and their sources, accepted plan, current phase/task, child task IDs and thread
links, last verified revision, PR URL, and whether merge was attempted. Append
significant events and evidence paths to `ledger.jsonl`. Write before yielding
and before external mutations; a ledger is a handoff record, not a process manager.

A valid JSON result is not proof that work succeeded. Inspect diffs, command
outputs, and current GitHub state before advancing. Scope verification to the
same revision and checkout content that will be published.

## Status, stop, and resume

- **Status:** read the flow artifacts and the parent thread via `t3_thread_read`.
  Report phase, last verified revision, active task links, and blockers. Do not
  poll a running child using `task_status`.
- **Stop:** cancel recorded outstanding tasks with `task_cancel`; remove the
  parent's PR watch with `unwatch_pull_request`. Mark the flow stopped and leave
  branch, PR, and evidence intact. Do not claim cancellation is complete merely
  because it was requested. Do not start another writer until T3 confirms it.
- **Resume:** read the recorded parent thread before interpreting its state.
  Reconcile artifacts against branch, checkout, T3 activity, and PR state. Refuse
  an active writer, unknown changes, a different checkout, or an ambiguous merge.
  Recheck model availability and project test instructions; rerun stale checks. Reuse validated artifacts,
  but create fresh children for new work. Resume in the original parent where
  possible; cross-thread resume requires confirming that the old owner is inactive.
  A missing or ambiguous record requires operator reconciliation, not guessing.

There is no automatic crash restart or exactly-once execution guarantee. Never
relaunch a child or retry a merge merely because its result was lost.
