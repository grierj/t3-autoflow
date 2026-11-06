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

The primary architect inspects the repository and returns a `plan`. Divide the work
into modular coder assignments with file scope, dependencies, implementation
steps and interfaces, testable success criteria, complexity, and a UI flag.
Put implementation details in each task's `implementation` field and success
criteria in `acceptance`. Express genuine unknowns in `questions`. Make each
task's `files` specific enough that the lead can judge whether dependency-ready
tasks overlap, and put any interface one task defines for another in the agreed
implementation details, with a dependency where the consumer needs the result.

When a secondary architect is available, the architects exchange the plan
directly until one accepts the other's version:

1. The primary architect's validated plan goes to the secondary architect.
2. The secondary architect inspects the repository and reviews all four parts:
   plan, slices, implementation details, and success criteria, including shared
   files and unfrozen interfaces between dependency-independent tasks, since they
   bear on whether those tasks can run in parallel. It returns a `checker`
   result. On `agree`, the plan goes to the workflow lead to run.
3. On `revised`, the secondary architect has rewritten the plan itself, with
   `objections` explaining each change. The revised plan goes to the primary
   architect.
4. The primary architect reviews the revision the same way. On `agree`, the plan
   goes to the workflow lead to run.
5. On `revised`, the primary architect's rewritten plan goes back to the secondary
   architect, and the exchange returns to step 2.

The parent carries each plan between the architects verbatim. It does not edit,
summarize, merge, or add objections of its own. Save every plan version. Validate
each response with `validate.py result checker <response> <reviewed-plan>`, which
requires an `agree` to return the reviewed plan unchanged and a `revised` plan to
differ from it. The accepted plan is the version the agreeing architect received.
Each brief includes the plan under review, the full revision history with
objections, and any recorded user answers. A reviewing architect cannot agree
while its plan has open questions; it resolves them by revising.

With one architect, proceed with its plan and record the availability limit.
If a revision restores a plan version that an architect already rejected, the
architects are not converging: surface both positions and their objections to
the user rather than pretending they agreed.

Relay planning questions from any plan version to the user and record answers.
Send the answers with that plan to the next architect in the exchange. Once an
architect agrees and questions are resolved, freeze the plan and begin without
a redundant approval request. Publication and merge still require the user's
authorization.

## Implement and review

Process slices in dependency order, with one writer per checkout. Sequential
execution is the default. The lead may instead group dependency-ready slices
into a parallel wave when every slice in the wave meets all of these:

- Its dependencies are already integrated and committed, and it starts its own
  T3-managed worktree from the wave's common recorded flow revision.
- Its planned `files`, including test files, are specific and disjoint from
  every other slice in the wave. Scope too broad to establish disjointness,
  such as an overlapping directory or glob, is ineligible.
- It shares no hot files with the wave: lockfiles, manifests, schemas or
  migrations, generated output, route or registry tables, barrel exports, or
  shared fixtures and snapshots.
- Any interface between wave slices is already frozen in the agreed plan. A
  slice that must define an interface another wave slice consumes is a
  dependency; run it first.

Any doubt, or unavailable worktree isolation for a lead-chosen wave, means
record the reason and run those slices sequentially. If the user requested
isolation, its unavailability remains a blocker under the runtime contract.
A prompt may request a wave or forbid one; a request does not waive the
criteria above, and a prohibition means sequential execution.
There is no fixed wave size; include only slices that meet the criteria.
Record the wave, its common base revision, and each task ID before yielding.
Each wave brief lists the slice's declared `files` as its write scope and
instructs the coder to return `blocked` rather than edit outside that scope;
the parent still verifies the actual diff at integration. A slice blocked
solely by that write-scope limit exits the wave and proceeds sequentially
under a normal brief, unless the needed scope change is material enough to
require arbitration or an agreed plan revision first.

Then, per slice:

1. Assign a coder from the coder pool as the slice's owner. It implements the
   scope, including test code, and returns a `coder` result. It leaves changes
   for inspection without committing or pushing. In a wave, launch each coder
   in its own worktree without waiting for the others; completions wake the
   parent under the runtime contract. All test execution goes to Terra,
   including targeted reproductions and checks proposed by other roles.
2. Inspect the diff and integrate isolated changes into the flow branch. The
   parent integrates one slice at a time, as results return, and records the
   integration order. Compare the actual changed files against the declared
   `files`, against integrated slices, and against the declared files of
   remaining wave slices. Overlap or an
   integration conflict demotes the later slice to sequential: hold its
   integration and return it to its owning coder to repair on the new
   integrated base. Record the demotion; it is not a flow failure. Terra
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
   Fix rounds stay sequential within a slice, including for wave slices; a
   slice entering its fix loop no longer counts as parallel with its own fixer.
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
If the architect recommends changed slices or implementation details, have the
primary architect produce a new validated `plan` and run it through the same
architect exchange when a secondary architect is available.
Reconcile completed work and task IDs before replacing the remaining queue.
Return the decision to the owning coder, then continue through Terra checks and
adversary review. Arbitration cannot turn failed verification into a pass.

If the original coder returns `stalled`, stop with the remaining findings and
attempts recorded. Do not have the workflow lead or a fixer override that decision
with another automatic retry. Runtime or permission blockers also stop the flow
when they cannot be resolved within the authorized scope.

## Final checks and architect review

When all slices are complete, Terra runs the full applicable project checks,
including integration and e2e suites. Failures return to the owning coder and
reopen the same fix and adversary review cycle. Rerun affected checks after fixes
and the full final check set before publication.

Inspect and commit only intended changes. For authorized publication, Terra
fetches the base. If it moved, update the branch and send conflicts or
implementation changes to a coder. Terra reruns checks and adversaries re-review
changed code before the final architect review. Freeze all writers in every
checkout and verify that all evidence matches the exact candidate. No wave
remains active from this point through publication.

Delegate a fresh, read-only review to the primary architect using its
recorded target. Supply the accepted plan and any agreed revisions, every task's
`acceptance` criteria, the candidate SHA and diff base, the full integrated diff,
resolved findings, and Terra's final check evidence. The architect inspects the
actual code and cross-slice behavior against the goal, implementation decisions,
and every success criterion. Passing tests or coder summaries alone do not prove
completion. Any additional test execution goes to Terra.

Request the existing `review` JSON contract. In `summary`, identify the reviewed
SHA and map each task ID and acceptance criterion to code locations and
verification evidence, including any agreed verification limits. Return
`findings` for unmet criteria or incorrect implementation, and `blocked` when
the evidence is insufficient to judge completion. Return `pass` only when every
criterion is satisfied. Save and validate the exact response, then verify its
coverage against the plan. Record the result path and reviewed revision in flow
state. A missing criterion or stale review cannot authorize publication.

Send findings to the owning coder through the existing fix, Terra check, and
adversary review cycle. Then repeat final checks and request a fresh architect
review with prior findings and fix evidence. Preserve the existing stalled and
blocked termination rules. Do not weaken success criteria to obtain a pass;
plan revisions require the architect exchange described above.

For local-only scope, finish with the architect-approved branch and report it.
For publication, require the architect's validated `pass` on the exact candidate
immediately before Terra pushes and opens the PR. Changes to the candidate or
accepted plan invalidate that pass, including base updates and later PR fixes.
Repeat the applicable checks, adversary reviews, and final architect review
before publishing the changed candidate. On resume, reuse a final review only
after verifying that its candidate, plan, and supporting evidence still match.

## Publication and merge

Terra handles all GitHub interactions and PR operations.
Use force-with-lease only for the flow's own previously published, rebased branch.

Terra pushes and opens a ready PR. Include the goal, implementation summary,
verification, the architect's success-criteria review, unresolved limitations,
and relevant model overlap or plan changes.
Keep the body current after fixes. Include a useful plan summary rather than a
link to an inaccessible local artifact. Link the PR immediately as described in
runtime.md.

When requested work awaits CI or reviews, the host parent registers a T3 watch
and yields. On a wake, Terra inspects checks, review comments, conflicts, and the
head SHA. PR breakage returns to a coder, then Terra checks, adversary re-review,
final architect review, and Terra push. Link again and wait through T3 as needed. No reported CI checks
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
