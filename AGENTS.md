# Working on t3-autoflow

This repository contains a portable skill, not a workflow service. T3 owns child
execution, cancellation, and completion/CI wakeups. Do not add custom process
registries, polling loops, custom worktree management, or fallback execution backends.
T3-managed worktree isolation through delegation is supported.

Keep the skill self-contained under `skills/t3-autoflow/`. Discover project checks
from repository instructions and source artifacts. Discover models/providers
through T3 and select by role; honor prompt overrides. Do not introduce required
setup files, hard-coded model maps, or a Pi dependency.

`SKILL.md` is the entrypoint; references own discovery, runtime behavior, flow,
and validation details. Helpers validate results and capture command evidence.
They do not provide host enforcement or automatic replay. Keep those limits clear.

Run `python3 -B -m unittest discover -s tests -p 'test_*.py'` after helper changes.
Update relevant references and README when behavior changes. A live T3 fixture
flow is still needed before claiming end-to-end plan-to-merge verification.
