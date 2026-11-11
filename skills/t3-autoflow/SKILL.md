---
name: t3-autoflow
description: Run a planned, multi-model coding flow in T3 Code with adversarial reviews, project-discovered tests, and optional PR publication and merge. Use when the user asks for autoflow or its status, stop, or resume. Requires T3 delegation tools; does not apply to ordinary coding requests.
---

# T3 autoflow

Use GPT 6.1 Terra or equivalent to lead the workflow in the current T3 thread.
T3 owns child execution, cancellation, and completion wakeups. This is an agent-followed procedure, not a
sandboxed workflow engine. Read [the runtime contract](references/runtime.md)
before starting or resuming; read [the flow procedure](references/flow.md) to run.
Read [discovery](references/discovery.md) to choose models and find project tests.
Use [validation](references/validation.md) for handoff and check helpers.

## Scope and invariants

- Before any delegation, show the user a table of the selected models by role
  and ask them to confirm or change it. In the same request, ask whether the work
  should result in a PR and, if so, whether to merge it after all requirements
  pass. Wait for answers. See the confirmation step in the flow reference.
- Preserve the confirmed scope: local work only, PR publication, or PR and merge.
  Invoking this skill alone does not authorize publication or merge.
- One flow and one code writer per checkout. Delegates may share the flow checkout
  or use T3-managed worktree isolation. Multiple writers in one flow are allowed
  only as an optional wave of slices, each in its own T3-managed worktree, when
  the lead judges them independent under the flow procedure. Sequential execution
  is the default and fallback; never run parallel writers in a shared checkout.
  T3 owns worktree creation and lifecycle; follow the isolation and integration
  rules in the runtime contract.
- Discover available providers and models through T3 and select them by role.
  Honor prompt overrides; record the choices. No silent substitution or CLI relay.
- Architects plan modular slices. When two are available, the primary and
  secondary architects revise each other's plan until one accepts it unchanged.
  Coders own implementation, fixers return small fixes to the owning coder, and
  adversaries re-review until no fixes remain or the original coder stops for
  lack of progress. Coders can request architect arbitration. Use the role
  preferences in discovery and the briefs in the flow reference.
- Before publication or local handoff, the primary architect reviews the
  integrated code against every success criterion. Require a validated `review`
  pass on the exact candidate; changes invalidate it. See the final review in
  the flow reference.
- GPT Terra handles all test runs and GitHub interactions, including PR operations.
  Send test and PR failures to a coder. Include context in each brief; children
  inherit no history.
- For architect, coder, fixer, and adversary handoffs, request JSON only. Save
  the exact result outside the checkout and validate it with `python3 <skill-dir>/scripts/validate.py result <kind> <file>` before using
  its verdict. Do not derive control decisions from a prose summary or repair
  malformed results yourself. See the validator's `schemas` command for contracts.
  Workflow decisions and Terra operations use the evidence rules in runtime.md.
- Unit/e2e evidence comes from executing commands discovered in the project, never a coder's
  claim. Use `scripts/run-check.py` and inspect its JSON output and captured log.
- Architects and adversaries inspect only. Their read-only behavior is an instruction,
  not a T3 tool restriction. Unexpected changes invalidate the review.
- Do not waive open findings or hide failed checks, provider errors, or blockers.
- Children return questions or blocked results to the parent. After planning,
  return implementation blockers to the owning coder and write recovery guidance
  if work terminates.
  T3/provider permission prompts can still interrupt; never bypass them.

## Durable handoff

Store artifacts outside the checkout, for example under
`~/.local/state/t3-autoflow/<flow-id>/`. The parent writes flow state and saved
role results. Terra may write command evidence to paths assigned in its brief.
Persist the flow checkout path, each delegate's isolation and returned checkout/branch,
wave groupings with their common base revision and integration order, demoted
slices, integration revisions, parent thread ID/link, branch/base, confirmed PR
and merge answers, confirmed models, original coder ownership, findings and fix attempts, discovered
checks and their sources, accepted plan, final architect review and its candidate
revision, current phase/task, child task IDs and
thread links, last verified revision, PR URL, and whether merge was attempted. Append
significant events and evidence paths to `ledger.jsonl`. Write before yielding
and before external mutations; a ledger is a handoff record, not a process manager.

A valid JSON result is not proof that work succeeded. Inspect diffs, command
outputs, and current GitHub state before advancing. Scope verification to the
same revision and checkout content that will be published.

## Status, stop, and resume

- **Status:** read the flow artifacts and the parent thread via `t3_thread_read`.
  Report phase, last verified revision, active task links, per-slice wave stage,
  and blockers. Do not poll a running child using `task_status`.
- **Stop:** cancel every recorded outstanding task with `task_cancel`, including
  all wave writers; remove the parent's PR watch with `unwatch_pull_request`.
  Mark the flow stopped and leave branch, PR, worktrees, and evidence intact.
  Do not claim cancellation is complete merely because it was requested. Do not
  start another writer in an affected checkout until T3 confirms its writer ended.
- **Resume:** read the recorded parent thread before interpreting its state.
  Reconcile artifacts against branch, every recorded checkout and revision, T3
  activity, and PR state. Refuse any active writer, unknown changes in any
  recorded checkout, a different checkout, or an ambiguous merge.
  Recheck model availability and project test instructions; rerun stale checks.
  Reuse confirmed scope. If a confirmed model is unavailable, show the revised
  table and confirm it with the user before delegating. Reuse validated artifacts,
  but create fresh children for new work. Resume in the original parent where
  possible; cross-thread resume requires confirming that the old owner is inactive.
  A missing or ambiguous record requires operator reconciliation, not guessing.

There is no automatic crash restart or exactly-once execution guarantee. Never
relaunch a child or retry a merge merely because its result was lost.
