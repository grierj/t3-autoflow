# T3 runtime contract

Use the live tool schemas in the current session; names below omit MCP prefixes.
If a required tool is unavailable, try discovery once, then stop with the missing
capability. Do not replace T3 delegation with subprocesses, Pi, or new top-level
threads. This pack requires Python 3, Git, and authenticated `gh` for publication.

## Workflow lead and host parent

GPT 6.1 Terra or an available equivalent makes workflow decisions. If the current
parent is that selected model, it runs the flow directly. Otherwise, delegate
coordination decisions to the selected workflow model with the current artifacts
and available role targets. The host parent carries out its routing decisions
through T3 and saves results. Do not silently let the parent take over the lead's
role because it uses a different model. A coordination result is JSON containing
the next phase, role, task brief, and supporting evidence paths. The parent checks
that the routing follows this procedure before dispatching. The handoff validator
does not validate coordination or operations results.

All test execution and GitHub interactions go through GPT Terra. If the parent
is not the selected Terra target, use bounded Terra operations tasks for checks,
GitHub reads, publication, and merge. Supply exact commands, candidate revision,
authorized actions, and evidence paths. Terra operations may write check evidence
and perform explicitly authorized GitHub actions. They must not implement fixes.
Use the check helper's JSON evidence for test results and verify actual PR state
for publication results. Reserve JSON handoff schemas for the role results they
cover; operations return evidence paths, command outcomes, PR URL, and head SHA.

The host parent owns T3 task lifecycle, durable artifacts, PR linking, and watches.
These host bookkeeping calls stay with the parent even when another model leads.
Children never watch PRs. A Terra child links immediately after its PR mutation;
the parent also links the returned PR before proceeding. Delegate PR operations
one mutation at a time so results can be recorded and reconciled before continuing.

## Delegate and consume a result

Discover T3's available targets before the first delegation using the current
host's capability-discovery tools and [discovery.md](discovery.md). Search omitted models when needed. Honor the
user's explicit providers, models, and options. Otherwise choose from the live
catalog according to the role and task difficulty. Record choices before launch.
A disabled requested provider or unsupported requested option is a blocker, not
permission to substitute. Consult capabilities again after an error or a user-named
provider change, following the current host instructions.

For each task, use `delegate_task` with the chosen `isolation`, the appropriate
`role`, and explicit `target: {providerInstanceId, model, options}`. Use a stable
`clientRequestId` for the intended submission and record the returned task ID.
Do not assume that request IDs provide crash-safe deduplication. Omit runtimeMode
unless the user explicitly selected one; inherit permissions.

### Checkout isolation

Use `isolation: "shared"` for work in the flow checkout, or `isolation: "worktree"`
when the user requests isolation or the task benefits from a separate checkout.
Let T3 create and manage the worktree through the delegation tool. Never run
shell worktree setup or put checkout creation instructions in a child's brief.
If the requested isolation is unavailable, report the blocker instead of silently
switching to shared execution.

Record the checkout and branch returned by T3. An isolated child works in its
assigned checkout, not the parent's path. Verify its starting revision matches
the intended task base before editing. Worktrees do not inherit uncommitted
changes. Before delegating dependent work, commit the accepted flow changes and
use the live tool schema to select that revision. If T3 cannot provide the
required starting content, stop and reconcile before proceeding.

After an isolated coder or fixer finishes, inspect its actual checkout and diff.
The parent commits only intended changes and integrates them into the flow
branch, for example by cherry-picking. Route conflicts to the owning coder.
Record source and integrated revisions. A fixer change still returns to its
owning coder for acceptance before Terra checks and adversary review in the flow
checkout.
An isolated child's result alone does not establish that integration succeeded.

Reviews of uncommitted flow changes use shared isolation. An isolated reviewer
must inspect the exact committed candidate revision, including the same diff
base. Confirm that revision before accepting its verdict. Keep the existing
dependency order and writer freeze during checks and reviews; worktree support
does not introduce parallel implementation. Preserve worktrees with outstanding
changes for recovery and leave lifecycle management to T3.

T3's tool role is separate from the autoflow model role. Map architect to
`design`, coders and fixers to `implementation`, Terra checks to `test`, the second
architect and adversaries to `review`, and architect arbitration or workflow
coordination to `general`. Select a supported role for Terra GitHub operations.

The brief must contain the repository path, branch, read/write scope, goal,
acceptance criteria, relevant plan and evidence, output contract, and instructions
not to delegate further or contact humans. Read-only roles must not write result
files; return JSON and let the parent save it. Only Terra operations children
may publish or merge, within their explicit brief.

`mode: "wait"` can obtain a result in the current turn. For async or a timed-out
wait, obey `next`: persist state, end the turn, and let completion wake the parent.
Do not poll, sleep, create watchers, or use `t3_thread_send` to re-run reviews.
On completion, use the delivered result or read the completed task with
`task_status`; use `t3_thread_read` if the complete child response is needed.
A completed turn with live descendants is not a completed task.

Save exact role JSON responses without changing their values. Validate them
before routing. For coordination and operations, inspect the required evidence
and authorized scope instead of using an unrelated role schema. A malformed response gets one fresh request for a conforming result on
the same selected model, then becomes a blocker. A provider error similarly
gets at most one same-target retry. If arbitration itself is unavailable, terminate
with the infrastructure error recorded. Do not recurse through fallback models.

New review/re-check means a new `delegate_task` with the prior findings and diff.
Cancel superseded tasks using `task_cancel`. A child question is not permission
to answer for the user: relay planning questions; after planning, cancel the
blocked child and return its evidence to the owning coder. The coder may request
architect arbitration. Permission prompts remain under the host's control.

## Check and publish

Terra runs exact discovered project checks with `scripts/run-check.py`. The helper
executes one command in the foreground and records exit status, argv, cwd, HEAD,
and output path. It has no process registry, retry loop, or wakeup mechanism.
Freeze writers and verify tracked/untracked checkout changes before and after
checks and reviews. Any unexpected change invalidates their results.

Terra uses Git/`gh` or available GitHub tools for all GitHub interactions.
Immediately after creating or pushing to a PR, call `link_pull_request` with the full URL as the next tool
call. Every PR in a stack must be linked, though autoflow normally uses one PR.
The parent owns watches. Have Terra read existing comments and route needed
changes to a coder before calling `watch_pull_request`; then end the turn. On a CI wake, Terra inspects actual checks,
reviews, conflicts, and head SHA. Do not treat a wake as a merge decision.
Never use `gh --watch`, sleep loops, or scheduled polling. If a later invocation
requires waiting again, follow the current tool instructions for watch registration.
Remove watches with `unwatch_pull_request` when stopping, finishing, or handing
control back, but retain the watch while deliberately yielding for CI.

## What the skill cannot enforce

T3's delegation contract inspected for this port has no `outputSchema`, command
acceptance gate, read-only tool list, or disabled intercom bridge. The validator
rejects malformed results at the parent boundary; it cannot constrain generation
or force the parent to invoke it. Review instructions do not sandbox children.
The ledger supports manual reconciliation, not Pi's workflow replay/reuse.
Usage and cost data may be unavailable; report unavailable rather than estimate.
Strict enforcement needs host support, not stronger prompt wording.
