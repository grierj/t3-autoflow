# Flow procedure

## Preflight

1. Read repository instructions. Confirm a clean Git checkout and no active flow
   or writer targeting it. Never stash or discard existing work. If ownership
   cannot be established, stop before spending on children.
2. Discover tests from project instructions, manifests, CI, and test scripts.
   Select models from T3's live provider/model catalog by role, honoring prompt
   overrides. Follow [discovery.md](discovery.md); record command sources, selected
   targets, diversity warnings, and explicit authorization for publish/merge.
3. For publication, verify `gh auth status`, remote, base, and repository access.
   Local-only runs do not need GitHub. Record original branch and base SHA.
4. Create the external flow directory and record the parent thread and checkout.
   After plan agreement, create `autoflow/<flow-id>` in this checkout as the flow
   branch. Choose shared or T3-managed worktree isolation for delegates using
   [the runtime contract](runtime.md#checkout-isolation).

## Plan and human gate

Architect: inspect the repository; return a `plan`. Tasks must have testable
acceptance criteria, file scope, dependency IDs, low/medium/high complexity, and
an explicit UI flag. Prefer requested behavior over a mechanism unless the user
made that mechanism binding. Express genuine unknowns in `questions`.

Checker: independently challenge the plan for missing tasks, incorrect complexity,
untestable criteria, and hidden dependencies. Return a `checker` verdict with
concrete objections. Use a distinct model.

Questions go to the human during this phase. Record answers, revise the plan, and
check it again. Allow two architecture rounds, then surface unresolved objections.
On agreement with no open questions, freeze the plan and begin without a redundant
approval request. Existing authorization still controls publication and merge.

## Implement, verify, and review

Process tasks in dependency order. For each task:

1. Start a fresh coder selected for the task's complexity. It is the only code
   writer. Ask it to implement the assigned scope, leave changes for parent
   inspection, avoid committing/pushing, and return a `coder` result. It must not
   run suites; the parent runs the discovered unit command.
2. Inspect its diff and result. For an isolated coder, integrate its changes into
   the flow branch using the runtime contract before verification. Run unit tests
   in the flow checkout with the check helper. On failure,
   testRunner diagnoses the exact log and command without editing. Return its
   findings as a `review` result and route a fresh coder fix. Never accept a
   passing test claim in place of an actual successful command result.
3. Run adversaryA and adversaryB on the same frozen diff, independently and fresh.
   Each returns a `review`. Require evidence, severity, and a smallest proposed
   fix for each finding. Both models must differ from each other and every model that wrote this task. Read-only tasks can run concurrently, but no writer runs alongside them.
4. Fix P0/P1 findings. Send P2 findings to the arbitrator for explicit fix-now,
   defer-with-dependency, or documented-PR-deferral disposition. Never silently
   drop them. After a fix, rerun unit tests and both adversaries, supplying prior
   findings so reviewers check closure as well as new defects.
5. Run correctness, security, and efficiency gates, each returning `review`.
   Correctness checks acceptance and regressions; security requires concrete
   attack paths; efficiency reports material cost regressions, not style.
   Run the UI gate if the task's UI flag or actual changed files show UI work.
   It checks states, accessibility, and visible behavior, with a written account.
   Gate models must differ from the task's writers and adversaries. Accepted
   findings become scoped fix tasks and repeat the same verification cycle.

Record progress after each iteration: completed tasks, open findings by severity,
failing test names, normalized failure signature, and diffstat. Same failure for
three consecutive iterations, no measured change, blocked results, or two upward
retaggings send the evidence to the arbitrator. Coding has no arbitrary round cap.

Arbitrator: return `arbitrator` with evidence for progressing, try-fix, or terminate.
It may split/reorder tasks or raise complexity, never waive P0/P1. For try-fix,
request concrete plan tasks from the architect and validate them before queuing.
Give the architect the existing plan, findings, and failed attempts. A repeated
failure from that fix goes directly back to arbitration. If permission or runtime
limits prevent continuing, record the blocker; an arbitrator cannot override them.

Treat the arbitrator's free-text action as evidence for the architect, never as
executable queue changes. Every split, reorder, or complexity change must return
through a new validated architect plan. Reconcile task IDs and completed work
before replacing the remaining queue.

## Final checks and publication

When the queue empties, run all discovered, applicable e2e commands. Failures reopen the task
queue, including unit tests, reviews, and gates. Rerun the full e2e set after fixes.

Before publication, inspect and commit only the flow's intended changes. Verify
unit and e2e results still match that exact content, with no active children.
For local-only scope, finish here with a verified branch and report it.
For authorized publication, fetch the base. If it moved, rebase locally, resolve through the single-writer
process, and rerun unit/e2e. Re-review any changed implementation. Never publish
untested conflict resolutions. Use force-with-lease only for the flow's own branch
when a previously published head was rebased.

Push and open a ready PR, never a draft. The body includes goal, completed
tasks and models, changed files, deviations, judgement calls, fix-task origins,
verification, UI account, model diversity warnings, and usage if available. Keep
this record updated after fixes. Do not link an inaccessible local plan as if it
were a shared artifact; include its useful summary in the PR.

Link immediately as described in runtime.md. If CI/reviews are pending and the
requested work includes waiting or merging, register a T3 watch and yield. A failed
check becomes a fix task, then local tests/reviews, push/link, and CI again. No CI
checks reported counts as pass, recorded explicitly; query errors do not count as
no checks. Branch protection and required reviews still apply.

Merge only if authorized, all gates pass on the current head, and GitHub reports
readiness. Record `mergeAttempted: true` BEFORE attempting a merge-commit once.
Never squash, rebase-merge, bypass protection, or retry an ambiguous merge. Read
PR state to establish the outcome. Unwatch when finished or handing back.

## Termination

Cancel outstanding children, remove the watch, and preserve the branch and PR.
Write `RECOVERY.md` with state, last good commit, remaining tasks, exact blocker,
failed attempts, arbitrator reasoning, one most likely root cause, and one first
human action. Explain how to resume in the recorded parent thread and how the
user can abandon the work. Do not delete anything as part of termination. Include
recovery in the final reply; post a PR comment only if messaging was authorized.
