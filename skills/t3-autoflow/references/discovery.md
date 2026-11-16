# Discover tests and select models

Do this in the parent before implementation. The user supplies a goal, not setup
files. Prompt choices take precedence over the skill's defaults. Record the
result in flow artifacts so resuming work does not require rediscovery by guesswork.

## Find the project's test workflow

Read applicable `AGENTS.md` and other repository instructions first. Inspect the
README and contributor guide, package/build manifests, CI workflows, and test
scripts relevant to the changed component. Follow referenced scripts far enough
to understand their working directory, environment, prerequisites, and scope.
Use the project's documented commands rather than inventing `npm test` or another
conventional command based only on the language.

Record each applicable check's source file, command, cwd, required environment,
and purpose: unit, integration, e2e, lint, typecheck, or another project gate.
Keep required project gates even if they do not fit the unit/e2e labels. Prefer
the CI entrypoint when documentation is stale, but resolve material contradictions
during planning. In a monorepo, identify affected packages and required shared
checks. Include setup steps when the repository documents them.

Preserve exact command semantics. Direct commands can use the argv helper in
[validation.md](validation.md). If a documented command needs shell operators,
use the project's existing script or explicitly invoke the appropriate shell with
the documented command. Do not interpolate arbitrary model output into shell code.
Execute in the discovered directory with the required environment. Never expose
secrets in evidence logs; use the host's secret mechanism when needed.

If no unit or e2e suite exists, record that fact with inspected sources. Do not
invent a passing suite or require an empty setup file. The plan should include
appropriate regression tests for changed behavior, using existing conventions
where possible. If no meaningful automated verification can be established,
raise that limitation during planning and agree on concrete verification before
coding. Missing tooling, credentials, or a failing existing suite is a blocker
to resolve, not a reason to silently skip it. Revisit test discovery when the
implementation changes the build or test workflow.

The runner runs applicable checks during implementation and the full set at final
verification; do not claim nonexistent suites passed. Record actual
commands, outcomes, and any explicitly agreed verification limits.

## Find the project's review and merge criteria

Read the same repository instructions for review and merge requirements: review
concerns, who may review, re-review rules after new commits, where findings must
be recorded, merge conditions, and how to update a branch from its base. Record
each with its source. Follow them where possible, alongside the skill's own
reviews. Assign each to the step where it fits, usually the per-slice adversary
reviews or the final architect review on the PR, and record the assignment.

Ask the user during the preflight confirmation when following a criterion would
create a workflow problem, or when it is unclear where in the workflow it
belongs. Examples: a rule that conflicts with the skill's flow, needs a human or
a service the flow cannot reach, or names a review without saying when it runs.
Propose a concrete resolution with each question, such as which step covers the
review, how the rule maps onto the skill's roles, or what to record for a person
to check later. Do not silently drop or reinterpret a repository criterion.

## Select targets from T3

Use the current T3 host's capability-discovery tools to find enabled provider
instances, available models, and supported options. Search the catalog when relevant models are omitted.
Choose explicit targets from what is available; no hard-coded model IDs, provider
assumptions, or fixed role map is required from the user.

Select each role by the capability it needs. The example models show what
fits that capability today; they are not an allow-list. Any available model
with the capability can fill the role, and a role can have models not listed
here. Resolve example names to actual targets in the live catalog:

| Role | Capability to look for | Example models | Responsibility |
| --- | --- | --- | --- |
| Workflow lead | Reliable instruction following and routing across long contexts | GPT 6.1 Terra (default) | Run the workflow and route work between roles |
| Architect | The strongest available reasoning, planning, and repository comprehension | GPT Astra, Claude Opus, Muse Wonder Full | Plan, slice work, define implementation details and success criteria; arbitrate when a coder asks; review final code against the accepted plan |
| Coder | Strong multi-file code generation and tool use | Claude Sonnet, GPT Sol | Own implementation; fix adversary findings, architect review gaps, and check failures |
| Adversary | Careful code review that finds concrete defects, ideally from a different model than the coder | Claude Sonnet, GPT Sol, Muse Spark, Grok 4.7 | Review for concrete defects and regressions |
| Fixer | Fast, precise, mechanical edits | Muse Spark, GPT Terra at maximum effort, Claude Sonnet | Fix low-complexity CI failures on an open PR and trivial base-update conflicts; return anything larger to the owning coder |
| Test and PR runner | Exact command execution and faithful evidence reporting | GPT Terra | Run all tests, update the branch from its base, and handle all GitHub interactions and PR operations; report to the lead without editing code |

These are recommendations, not provider IDs or a static catalog. Honor prompt
overrides. Resolve each name through T3 and use supported options. A Terra
fixer should use the catalog's maximum reasoning effort unless the prompt sets
another; do not invent an option. When one model fills both the fixer and runner
roles, keep fixer tasks separate from runner tasks; see Route fixes in
[flow.md](flow.md). The workflow lead and the runner are separate roles and may
use different models.

Use two distinct architects when available: a primary and a secondary. They
revise each other's plan, slices, implementation details, and success criteria
until one accepts the other's version unchanged. With only one available
architect, record that limitation and proceed with its plan. Prefer adversaries who did not
implement the work; this is helpful, not required. Select reviewers from the
adversary pool as the work warrants, without requiring a fixed count or separate
specialist gates. Record any overlap with writers.

Keep each slice's original coder identity and task context across fix rounds,
including when slices run in a parallel wave and when a wave slice is demoted
to sequential repair. A fresh child can continue that ownership using the same
selected target and the full history of findings and attempts. Fixers do not
replace the owning coder.

Record provider, model, options, role, and the override, example, or
capability match that chose each target. Present them for user confirmation as described in
[flow.md](flow.md) before launch. Keep confirmed selections stable across
retries and re-reviews. Example models are recommendations, never
requirements. When none is available, or a better match exists, choose the
available model that best fits the role's capability, note why in the
confirmation, and let the user change it; ask for a choice
only when no suitable target exists. A model named in the prompt must be honored
or reported unavailable, never silently replaced. After a provider error,
follow the runtime's bounded retry path.

## Model selector

By default the host parent, the model the skill started under, selects the
role targets. The prompt can name another model to do the picking, the model
selector, for example "have Claude Opus choose the models". Naming a workflow
lead does not make it the selector; the lead routes work only after
confirmation.

The selector gets exactly one read-only task. It is the only delegation
allowed before the user confirms models and scope:

1. Resolve the named selector through the live catalog like any prompt-named
   model. If it is unavailable, report that and ask the user. Do not select in
   its place.
2. Create the external flow directory now, so the result can be saved there.
3. Delegate with the `general` role in the shared checkout. The brief carries
   the goal, the role table above with capabilities and examples, the
   architect and adversary guidance in this section, every prompt override
   verbatim, and the live catalog of providers, models, and supported options
   the parent discovered, since the child may lack catalog access. The
   selector inspects only. It does not edit, delegate further, or contact the
   user.
4. The selector returns a `selection` result: one target per selected role
   slot, with `providerInstanceId`, `model`, `options`, a `source` of
   `override`, `example`, or `capability`, and a `reason`. Architects are
   listed primary first. `notes` carry the limits the confirmation must state.
   Save the result and validate it with
   `python3 <skill-dir>/scripts/validate.py result selection <file>`.
5. The validator checks the shape only. The parent then confirms that every
   target and option exists in the live catalog and that every prompt override
   appears unchanged. If validation, either check, or the selection task
   itself fails, do not delegate again. Keep the saved result, show the user
   the selector's proposal or the error with each problem, and ask how to
   proceed. Never repair or quietly replace its picks. The runtime's one-retry
   rules for malformed results and provider errors do not apply to selection;
   only the user can authorize another selection task.
6. Present the validated targets in the confirmation table and name the
   selector. The user's changes apply as usual and need no new selection task.

The selector holds no flow role after confirmation unless it was also picked
for one. Record its target, task ID, and result path. On resume, the parent
revises an unavailable confirmed model itself. It reruns the selector only
when the user asks.

## Discover publication defaults

When the user confirms a PR, have the runner inspect the repository's Git remotes, upstream,
contributor instructions, and GitHub default branch to determine destination and
base. Respect prompt overrides and existing PR targets. Resolve ambiguous forks
or branches during planning. Local-only flows require no remote or GitHub login.
