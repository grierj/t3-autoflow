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

Terra runs applicable checks during implementation and the full set at final
verification; do not claim nonexistent suites passed. Record actual
commands, outcomes, and any explicitly agreed verification limits.

## Select targets from T3

Use the current T3 host's capability-discovery tools to find enabled provider
instances, available models, and supported options. Search the catalog when relevant models are omitted.
Choose explicit targets from what is available; no hard-coded model IDs, provider
assumptions, or fixed role map is required from the user.

Use these role preferences, resolving names to actual targets in the live catalog:

| Role | Preferred models | Responsibility |
| --- | --- | --- |
| Workflow lead | GPT 6.1 Terra or equivalent | Run the workflow and route work between roles |
| Architect | GPT Astra, Claude Opus, Muse Wonder Full | Plan, slice work, define implementation details and success criteria; arbitrate when a coder asks; review final code against the accepted plan |
| Coder | Claude Sonnet, GPT Sol | Own implementation and accept fixer changes |
| Adversary | Claude Sonnet, GPT Sol, Muse Spark, Grok 4.7 | Review for concrete defects and regressions |
| Fixer | Muse Spark, GPT Terra at maximum effort, Claude Sonnet | Make small, scoped fixes and return them to the owning coder |
| Tests and GitHub | GPT Terra | Run all tests and handle all GitHub interactions and PR operations |

These are model preferences, not provider IDs or a static catalog. Honor prompt
overrides. Resolve each name through T3 and use supported options. Terra fixers
require the catalog's maximum reasoning effort setting. Do not invent an option
or silently lower that effort. The workflow-equivalent allowance does not by
itself authorize replacing Terra for tests and GitHub.

Use two distinct architects when available. Both must agree on the plan, slices,
implementation details, and success criteria. With only one available architect,
record that limitation and proceed with its plan. Prefer adversaries who did not
implement the work; this is helpful, not required. Select reviewers from the
adversary pool as the work warrants, without requiring a fixed count or separate
specialist gates. Record any overlap with writers.

Keep each slice's original coder identity and task context across fix rounds,
including when slices run in a parallel wave and when a wave slice is demoted
to sequential repair. A fresh child can continue that ownership using the same
selected target and the full history of findings and attempts. Fixers do not
replace the owning coder.

Record provider, model, options, and role before launch. Keep selections stable
across retries and re-reviews. If a needed role has no available target, report
that limitation and ask for a choice rather than silently substituting. An exact
prompt choice must be honored or reported unavailable. After a provider error,
follow the runtime's bounded retry path.

## Discover publication defaults

When publication is authorized, have Terra inspect the repository's Git remotes, upstream,
contributor instructions, and GitHub default branch to determine destination and
base. Respect prompt overrides and existing PR targets. Resolve ambiguous forks
or branches during planning. Local-only flows require no remote or GitHub login.
