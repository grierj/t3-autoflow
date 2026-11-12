# Flow procedure

## Preflight

1. Read repository instructions. Confirm a clean Git checkout and no active flow
   or writer targeting it. Never stash or discard existing work.
2. Discover project checks and select roles through T3 using
   [discovery.md](discovery.md). Record check sources. Establish the workflow
   lead and test and PR runner using [runtime.md](runtime.md).
3. Confirm models and scope with the user, as described below, before any
   delegation.
4. For publication, the runner verifies GitHub access, remote, and base. Local-only
   flows need no GitHub access. Record the original branch and base SHA.
5. Create the external flow directory and record the parent thread, checkout,
   and confirmed settings. After plan agreement, create `autoflow/<flow-id>` as
   the flow branch. Use shared or T3-managed worktree isolation as described in
   the runtime contract.

## Confirm models and scope

The host parent asks the user before the first delegation; children never
contact humans. Show a Markdown table of the selected targets with one row per
role: workflow lead, each architect, the coder, adversary, and fixer pools, and
the test and PR runner. Use these columns:

| Role | Provider | Model | Options | Source |
| --- | --- | --- | --- | --- |

`Source` is either the prompt override or the skill preference that chose the
target. Give a pool one row per selected target. Below the table, note limits:
a single available architect, preferred models missing from the catalog and
what replaced them, the workflow lead choice, and expected writer/adversary overlap.

In the same request, ask:

1. Confirm these models, or name changes.
2. Should the work result in a pull request? If not, the flow is local only
   and ends on the architect-approved flow branch.
3. If a PR is opened, should the runner merge it after all requirements pass?
   Requirements are: discovered project checks pass, no adversary findings
   remain open, the final architect review passes on the exact head, GitHub
   checks and required reviews pass, and GitHub reports the PR mergeable.

Ask every question, even when the prompt already answers it. Offer the prompt's
answers as defaults. Use the host's structured question tool when available;
otherwise ask in chat and end the turn. Do not plan, delegate, or create the
flow branch until the user answers.

Resolve requested model changes through the live T3 catalog. Report unavailable
models or unsupported options rather than substituting. Show the revised table
and ask again until the user confirms it. Record the confirmed targets, the PR
and merge answers, and the confirmation in flow state and `ledger.jsonl`. A
confirmed PR does not authorize merge. Later scope changes need an explicit user
instruction; record each one in flow state and the ledger. The latest recorded
scope governs publication and merge.

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
2. The secondary architect inspects the repository and reviews the plan,
   slices, implementation details, and success criteria against the review
   checklist below. It returns a `checker` result. On `agree`, the plan goes to
   the workflow lead to run.
3. On `revised`, the secondary architect has rewritten the plan itself, with
   `objections` explaining each change. The revised plan goes to the primary
   architect.
4. The primary architect reviews the revision the same way. On `agree`, the plan
   goes to the workflow lead to run.
5. On `revised`, the primary architect's rewritten plan goes back to the secondary
   architect, and the exchange returns to step 2.

The primary architect drafts against this checklist, and each reviewing
architect checks it:

- **Goal coverage** (`goal`): together, the tasks deliver the whole goal and
  every user answer recorded so far.
- **Scope** (`scope`): nothing exceeds the requested scope or the authorized
  actions.
- **Testable criteria** (`criteria`): each `acceptance` entry is specific and
  observable enough to verify with a check or by inspecting code.
- **Verification** (`verification`): the plan uses the discovered project
  checks, includes regression tests for changed behavior, and states any
  verification limit explicitly.
- **Slice boundaries** (`slices`): each task is a coherent unit for one coder,
  with `files` specific enough to judge overlap.
- **Dependencies and interfaces** (`dependencies`): tasks are ordered correctly,
  and each interface one task defines for another is written into its
  implementation details with a dependency.
- **Shared files and parallel safety** (`parallel`): shared files and unfrozen
  interfaces between dependency-independent tasks are identified, since they
  decide whether those tasks can run in parallel.
- **Repository fit** (`repository`): the implementation follows the repository's
  instructions, existing patterns, and conventions.
- **Unknowns** (`unknowns`): open questions are stated in `questions` instead of
  resolved by guessing.
- **Other** (`other`): any other concrete defect. Its `issue` explains why no
  listed item covers it. These objections show where the checklist should grow,
  so do not force-fit one into the nearest item.

Revise only for a concrete defect. Each objection names its checklist `item`,
states the `issue`, and gives both:

- **`source`:** where the defect is shown, outside the reviewer's opinion: a
  repository file and line, a discovered check or its source, the user's request
  or a recorded answer, a repository instruction, or conflicting plan elements
  named by task ID and field, such as a consumer of an interface no task defines.
- **`failure`:** what would concretely go wrong if the plan ran as written.

Architects do not run checks during planning; any test they want goes to the runner.
An observation that is only a preference, such as naming, phrasing, or a
different but equally valid split, is not grounds for revision. Record it in
`dropped` with the reason it was not acted on. Agreement can carry `dropped`
entries but no objections. Append each response's objections and `dropped`
entries to the ledger, so the flow shows whether the rule is catching defects
or suppressing them. The receiving architect judges whether each objection's
source and failure hold when it reviews the revision.

The parent carries each plan between the architects verbatim. It does not edit,
summarize, merge, or add objections of its own. Save every plan version. Validate
each response with `validate.py result checker <response> <reviewed-plan>`, which
requires an `agree` to return the reviewed plan unchanged and a `revised` plan to
differ from it. The accepted plan is the version the agreeing architect received.
Each brief includes the plan under review, the full revision history with
objections and `dropped` entries, recorded user answers, the discovered project checks and their
sources, and the authorized scope and actions. A reviewing architect cannot agree
while its plan has open questions; it resolves them by revising.

With one architect, proceed with its plan and record the availability limit.
If a revision restores a plan version that an architect already rejected, the
architects are not converging: surface both positions and their objections to
the user rather than pretending they agreed.

Relay planning questions from any plan version to the user and record answers.
Send the answers with that plan to the next architect in the exchange. Once an
architect agrees and questions are resolved, freeze the plan and begin without
a redundant approval request. Publication and merge follow the latest recorded
scope.

## Route fixes

Route every fix by where the problem was found, not by how small the change
looks. Before the PR opens, the fixer has no role.

| Problem | Goes to |
| --- | --- |
| Adversary review findings, at any size or severity | Owning coder |
| Final architect review findings | Owning coder |
| Runner check failures before the PR opens, slice or final | Owning coder |
| Base-update conflicts and PR review comments | Owning coder |
| CI failure on an open PR that is low complexity | Fixer |
| Any other CI failure on an open PR | Owning coder |

The test and PR runner is not a fixer. A runner task runs checks and GitHub
operations and returns evidence; do not ask it to edit code, even for a one-line
change. If the same model is also selected as the fixer, the fix is a separate
fixer task with the `implementation` role, not part of a runner task.

A CI failure is low complexity only when all of these hold:

- The CI log identifies the cause and its location.
- The fix is mechanical and local: formatting, lint, a type error, a missing
  import, or a generated file or snapshot that the intended change explains.
- It changes no behavior, interface, plan decision, or acceptance criterion,
  and does not weaken a test to make it pass.
- It stays within the files of one slice.

When in doubt, send it to the owning coder. Flaky, infrastructure, credential,
or base-branch failures are not code fixes; investigate them through the runner or
record a blocker. Give the fixer the PR URL, head SHA, failing check, exact CI
log, and file scope. If the fix proves larger, the fixer returns `blocked` and
the failure goes to the owning coder. A completed fixer change skips coder
acceptance and adversary re-review. The runner reruns affected checks, the
primary architect does a fresh final review with the fixer's diff and the CI
log, and the runner pushes. Architect findings go to the owning coder, not back
to the fixer.

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
   parent under the runtime contract. All test execution goes to the runner,
   including targeted reproductions and checks proposed by other roles.
2. Inspect the diff and integrate isolated changes into the flow branch. The
   parent integrates one slice at a time, as results return, and records the
   integration order. Compare the actual changed files against the declared
   `files`, against integrated slices, and against the declared files of
   remaining wave slices. Overlap or an
   integration conflict demotes the later slice to sequential: hold its
   integration and return it to its owning coder to repair on the new
   integrated base. Record the demotion; it is not a flow failure. The runner
   runs the applicable discovered checks using the check helper. Send failures
   and exact logs to the owning coder for diagnosis and repair.
3. Adversaries inspect the same frozen candidate and return `review` results.
   Ask for concrete evidence, severity, and the smallest proposed fix. Cover
   correctness, security, efficiency, and UI behavior where relevant within these
   reviews. Prefer reviewers who did not write the code, without making that a
   condition of proceeding. Read-only reviews may run concurrently.
4. Send every adversary finding to the owning coder with the review evidence,
   including findings with a small proposed fix. The coder repairs them and
   returns a `coder` result. Fixers take no part in this loop; see Route fixes.
   Fix rounds stay sequential within a slice, including for wave slices.
5. After the coder's repair, the runner reruns affected checks. Adversaries
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
Return the decision to the owning coder, then continue through runner checks and
adversary review. Arbitration cannot turn failed verification into a pass.

If the original coder returns `stalled`, stop with the remaining findings and
attempts recorded. Do not have the workflow lead or a fixer override that decision
with another automatic retry. Runtime or permission blockers also stop the flow
when they cannot be resolved within the authorized scope.

## Final checks and architect review

When all slices are complete, the runner runs the full applicable project checks,
including integration and e2e suites. Failures return to the owning coder and
reopen the same fix and adversary review cycle. Rerun affected checks after fixes
and the full final check set before publication.

Inspect and commit only intended changes. For authorized publication, the runner
fetches the base. If it moved, update the branch and send conflicts or
implementation changes to the owning coder. The runner reruns checks and adversaries re-review
changed code before the final architect review. Freeze all writers in every
checkout and verify that all evidence matches the exact candidate. No wave
remains active from this point through publication.

Delegate a fresh, read-only review to the primary architect using its
recorded target. Supply the accepted plan and any agreed revisions, every task's
`acceptance` criteria, the candidate SHA and diff base, the full integrated diff,
resolved findings, and the runner's final check evidence. The architect inspects the
actual code and cross-slice behavior against the goal, implementation decisions,
and every success criterion. Passing tests or coder summaries alone do not prove
completion. Any additional test execution goes to the runner.

Request the existing `review` JSON contract. In `summary`, identify the reviewed
SHA and map each task ID and acceptance criterion to code locations and
verification evidence, including any agreed verification limits. Return
`findings` for unmet criteria or incorrect implementation, and `blocked` when
the evidence is insufficient to judge completion. Return `pass` only when every
criterion is satisfied. Save and validate the exact response, then verify its
coverage against the plan. Record the result path and reviewed revision in flow
state. A missing criterion or stale review cannot authorize publication.

Send findings to the owning coder through the existing fix, runner check, and
adversary review cycle. Then repeat final checks and request a fresh architect
review with prior findings and fix evidence. Preserve the existing stalled and
blocked termination rules. Do not weaken success criteria to obtain a pass;
plan revisions require the architect exchange described above.

For local-only scope, finish with the architect-approved branch and report it.
For publication, require the architect's validated `pass` on the exact candidate
immediately before the runner pushes and opens the PR. Changes to the candidate or
accepted plan invalidate that pass, including base updates and later PR fixes.
Repeat the applicable checks, adversary reviews, and final architect review
before publishing the changed candidate. A fixer change skips the adversary
reviews; see Route fixes. On resume, reuse a final review only
after verifying that its candidate, plan, and supporting evidence still match.

## Publication and merge

The runner handles all GitHub interactions and PR operations.
Use force-with-lease only for the flow's own previously published, rebased branch.

The runner pushes and opens a ready PR. Include the goal, implementation summary,
verification, the architect's success-criteria review, unresolved limitations,
and relevant model overlap or plan changes.
Keep the body current after fixes. Include a useful plan summary rather than a
link to an inaccessible local artifact. Link the PR immediately as described in
runtime.md.

When requested work awaits CI or reviews, the host parent registers a T3 watch
and yields. On a wake, the runner inspects checks, review comments, conflicts, and the
head SHA. Route PR breakage as in Route fixes: low-complexity CI failures go to
a fixer and everything else to the owning coder. A coder change gets runner
checks, adversary re-review, final architect review, and a runner push. A fixer
change gets the same without the adversary re-review. Link again and wait through T3 as needed. No reported CI checks
means no CI suite was reported, not that a suite ran successfully. Query failures
are blockers. Branch protection and required reviews still apply.

The runner merges only when the latest recorded scope authorizes merge, through the
preflight confirmation or a later explicit user instruction, every merge
requirement listed in preflight holds on the current head, and GitHub reports
readiness.
Record `mergeAttempted: true` before one merge-commit attempt. Never bypass
protection or retry an ambiguous merge. Inspect PR state to establish the outcome.
Without merge authorization, finish with the open, linked PR and report it.
The host parent unwatches when finished or handing back.

## Termination

Cancel outstanding children, remove the watch, and preserve the branch and PR.
Write `RECOVERY.md` with the state, last verified revision, remaining tasks,
blocker or coder's stalled decision, failed attempts, and any architect reasoning.
Give a concrete next action and explain how to resume in the recorded parent
thread. Do not delete work. Include recovery in the final reply. The runner posts a
PR comment only when messaging was authorized.
