# Flow procedure

## Preflight

1. Read repository instructions. Confirm a clean Git checkout and no active flow
   or writer targeting it. Never stash or discard existing work.
2. Discover project checks and select roles through T3 using
   [discovery.md](discovery.md). Record targets, check sources, and authorization
   for local work, publication, and merge. Establish the workflow lead and Terra
   operations role using [runtime.md](runtime.md).
3. For publication, Terra verifies GitHub access, remote, and base. Local-only
   flows need no GitHub access. Record the original branch and base SHA.
4. Create the external flow directory and record the parent thread and checkout.
   After plan agreement, create `autoflow/<flow-id>` as the flow branch. Use shared
   or T3-managed worktree isolation as described in the runtime contract.

## Plan with architects

The first architect inspects the repository and returns a `plan`. Divide the work
into modular coder assignments with file scope, dependencies, implementation
steps and interfaces, testable success criteria, complexity, and a UI flag.
Put implementation details in each task's `implementation` field and success
criteria in `acceptance`. Express genuine unknowns in `questions`.

When a second architect is available, have it inspect the repository and challenge
all four parts: plan, slices, implementation details, and success criteria.
It returns a `checker` verdict. Revise through the first architect and have the
second architect check the revised plan until both agree. With one architect,
proceed without a checker and record the availability limit. If the architects
cannot resolve a disagreement, surface it rather than pretending they agreed.

Relay planning questions to the user and record answers. Once the architects
agree and questions are resolved, freeze the plan and begin without a redundant
approval request. Publication and merge still require the user's authorization.

## Implement and review

Process slices in dependency order, with one writer per checkout:

1. Assign a coder from the coder pool as the slice's owner. It implements the
   scope, including test code, and returns a `coder` result. It leaves changes
   for inspection without committing or pushing. All test execution goes to
   Terra, including targeted reproductions and checks proposed by other roles.
2. Inspect the diff and integrate isolated changes into the flow branch. Terra
   runs the applicable discovered checks using the check helper. Send failures
   and exact logs to the owning coder for diagnosis and repair.
3. Adversaries inspect the same frozen candidate and return `review` results.
   Ask for concrete evidence, severity, and the smallest proposed fix. Cover
   correctness, security, efficiency, and UI behavior where relevant within these
   reviews. Prefer reviewers who did not write the code, without making that a
   condition of proceeding. Read-only reviews may run concurrently.
4. Route small, scoped fixes to a fixer. Larger changes stay with the owning
   coder. A fixer returns a `coder` result and its changes to the owning coder,
   who inspects, accepts or revises them, and remains responsible for the slice.
   A fixer cannot declare the slice complete or decide that the loop has stalled.
5. After the coder accepts the changes, Terra reruns affected checks. Adversaries
   re-review the resulting candidate with prior findings and fix evidence. Use
   fresh review tasks. Repeat until no fixes remain or the original coder reports
   that no progress is being made.

Keep findings and failed checks open until evidence shows closure. Record each
attempt and give the owning coder the accumulated history. Do not waive an open
finding to call the slice complete. A blocked review is not a clean review.
There is no fixed iteration cap, automatic complexity escalation, or mandatory
arbitration after a failure count.

The owning coder can return `arbitrate` to request an architect's judgment. The
architect returns an `arbitrator` result based on the plan, evidence, and attempts.
If the architect recommends changed slices or implementation details, obtain a
new validated `plan` and the second architect's agreement when available.
Reconcile completed work and task IDs before replacing the remaining queue.
Return the decision to the owning coder, then continue through Terra checks and
adversary review. Arbitration cannot turn failed verification into a pass.

If the original coder returns `stalled`, stop with the remaining findings and
attempts recorded. Do not have the workflow lead or a fixer override that decision
with another automatic retry. Runtime or permission blockers also stop the flow
when they cannot be resolved within the authorized scope.

## Final checks and publication

When all slices are complete, Terra runs the full applicable project checks,
including integration and e2e suites. Failures return to the owning coder and
reopen the same fix and adversary review cycle. Rerun affected checks after fixes
and the full final check set before publication.

Terra handles all GitHub interactions and PR operations. Before publication,
inspect and commit only intended changes. Verify evidence matches the exact
candidate with no active writers. For local-only scope, finish with the verified
branch and report it. For authorized publication, fetch the base. If it moved,
update the branch and send conflicts or implementation changes to a coder.
Terra reruns checks and adversaries re-review changed code before publication.
Use force-with-lease only for the flow's own previously published, rebased branch.

Terra pushes and opens a ready PR. Include the goal, implementation summary,
verification, unresolved limitations, and relevant model overlap or plan changes.
Keep the body current after fixes. Include a useful plan summary rather than a
link to an inaccessible local artifact. Link the PR immediately as described in
runtime.md.

When requested work awaits CI or reviews, the host parent registers a T3 watch
and yields. On a wake, Terra inspects checks, review comments, conflicts, and the
head SHA. PR breakage returns to a coder, then Terra checks, adversary re-review,
and Terra push. Link again and wait through T3 as needed. No reported CI checks
means no CI suite was reported, not that a suite ran successfully. Query failures
are blockers. Branch protection and required reviews still apply.

Terra merges only when authorized, checks and reviews pass on the current head,
and GitHub reports readiness. Record `mergeAttempted: true` before one merge-commit
attempt. Never bypass protection or retry an ambiguous merge. Inspect PR state
to establish the outcome. The host parent unwatches when finished or handing back.

## Termination

Cancel outstanding children, remove the watch, and preserve the branch and PR.
Write `RECOVERY.md` with the state, last verified revision, remaining tasks,
blocker or coder's stalled decision, failed attempts, and any architect reasoning.
Give a concrete next action and explain how to resume in the recorded parent
thread. Do not delete work. Include recovery in the final reply. Terra posts a
PR comment only when messaging was authorized.
