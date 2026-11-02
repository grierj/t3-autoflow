# T3 autoflow

A portable skill for autonomous coding in T3 Code. Give it a goal; the parent
coordinates planning, implementation, independent reviews, project checks, and
optional PR publication and merge. T3 owns child execution and CI wakeups.

The agent discovers testing instructions from the project and selects models
from T3's live provider/model catalog according to each role. Your prompt can
override those choices. There are no setup files or fixed model maps to maintain.

## Install

Copy `skills/t3-autoflow` into the parent provider's skill directory. For Codex,
run from this repository:

```sh
destination="${CODEX_HOME:-$HOME/.codex}/skills/t3-autoflow"
test ! -e "$destination" && mkdir -p "$(dirname "$destination")" && cp -R skills/t3-autoflow "$destination"
```

The command refuses to overwrite an existing install. For a Claude parent, use
`~/.claude/skills/t3-autoflow`. Reopen the T3 session if the skill is not listed.
Children receive self-contained briefs; they do not need the skill installed.
Python 3 and Git are required. Publication also needs GitHub access.

## Use

- `Use $t3-autoflow to implement <goal>, local work only.`
- `Use $t3-autoflow to implement <goal>, open a PR, and merge after checks pass.`
- `Use $t3-autoflow for <goal>. Use Claude for planning and Codex for coding; select the available models.`
- `Use $t3-autoflow status`, `stop`, or `resume` with a flow ID.

The skill reads repository instructions, manifests, CI, and test scripts to choose
checks. Planning questions go to you. After agreement, children report blockers
to the parent for arbitration and recovery. Publication and merge follow the
scope you authorized.

Delegates can share the flow checkout or use T3-managed worktrees. Ask for
worktree isolation when you want a separate checkout. T3 creates and manages
the worktrees; the parent integrates isolated changes into the flow branch
before running checks and reviews.

See the [skill](skills/t3-autoflow/SKILL.md),
[discovery rules](skills/t3-autoflow/references/discovery.md), and
[runtime contract](skills/t3-autoflow/references/runtime.md).

## Limits

This skill was extracted from pi-autoflow. It has no Pi runtime dependency.
JSON validation and command execution helpers support the parent, but T3 does
not enforce Pi-style output schemas, command gates, or read-only reviewer tools.
Permission prompts can still interrupt. Artifacts support manual reconciliation
and resume, not automatic crash restart or exactly-once execution.

The flow uses one writer per checkout, sequential implementation tasks, two independent adversaries,
specialist gates, and at most one merge-commit attempt. An ambiguous merge needs
reconciliation, never an automatic retry. Artifacts live outside the project under
`~/.local/state/t3-autoflow/<flow-id>/`.

Helper tests pass. A complete live plan-to-merge T3 flow remains unverified.

## Test

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

No third-party Python packages or Node dependencies are needed. Tests exercise
handoff contracts, discovered-command validation, literal argv execution, failing
commands, timeouts, missing executables, and preservation of prior evidence.
