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

The flow reference uses unit and e2e as phase names. Run the applicable project
checks at those phases; do not claim nonexistent suites passed. Record actual
commands, outcomes, and any explicitly agreed verification limits.

## Select targets from T3

Use `orchestrator_capabilities` to discover enabled provider instances, available
models, and supported options. Search the catalog when relevant models are omitted.
Choose explicit targets from what is available; no hard-coded model IDs, provider
assumptions, or fixed role map is required from the user.

Select models according to the work:

- Architect: strong repository reasoning, planning, and architecture judgment.
- Checker: a strong independent reasoning model that challenges assumptions and
  acceptance criteria. Prefer a different provider from the architect.
- Coder: a fast capable coding model for mechanical tasks, a balanced coding
  model for ordinary changes, and a strong reasoning/coding model for difficult
  tasks. Select the tier needed for the actual task, not three mandatory targets.
- Adversaries A and B: strong code reviewers with distinct models, preferably
  different providers, who look for concrete failures and regressions.
- Correctness, security, efficiency, and UI gates: models capable in the relevant
  specialty. UI work benefits from visual/browser capability when available.
- Arbitrator: strong reasoning and judgment for weighing progress and evidence.
- Test runner: a fast economical model able to diagnose command output accurately.

Use supported reasoning options that fit the difficulty. Do not infer capability
solely from a model name or choose an unsupported option. When the catalog gives
little detail, use available model descriptions and known capabilities; if a
material choice is unclear, ask during planning rather than inventing metadata.
Reuse a suitable model for roles that do not require independence. Select the UI
role only when needed. Token prices need not be known to start the flow.

Honor explicit prompt constraints on providers, models, budget, and effort. A
request such as 'use Claude for planning' narrows discovery to that provider;
choose its suitable available model. An exact model request must be honored or
reported unavailable. Do not replace a user's unavailable choice without asking.

Before launching work, establish that independent roles can be filled: architect
and checker differ; the two adversaries differ from each other and all writers
of the task; gate models differ from its writers and adversaries. The same model
behind two provider instances does not establish independence. Prefer different
providers; record weaker diversity when only distinct models from one provider
are available. If catalog availability or prompt constraints make independence
impossible, surface that conflict during planning instead of silently weakening it.

Record selected provider/model/options and a short reason for each role when
used. Keep selections stable across retries and re-reviews. If a selected model
becomes unavailable, report it and follow the runtime's bounded failure path.
A different model is a new decision, not an invisible fallback. Retagging a coding
task upward also requires rechecking independence against every model that has
written or will review that task.

## Discover publication defaults

When publication is authorized, inspect the repository's Git remotes, upstream,
contributor instructions, and GitHub default branch to determine destination and
base. Respect prompt overrides and existing PR targets. Resolve ambiguous forks
or branches during planning. Local-only flows require no remote or GitHub login.
