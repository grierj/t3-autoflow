#!/usr/bin/env python3
"""Run one discovered project command without a shell; emit evidence, not a model verdict."""
import json
from pathlib import Path
import subprocess
import sys
from validate import command, read


def run(check, cwd, log_path):
    command(check)
    cwd = str(Path(cwd).resolve(strict=True))
    head = subprocess.run(['git', '-C', cwd, 'rev-parse', 'HEAD'], check=True,
                          capture_output=True, text=True).stdout.strip()
    evidence = dict(id=check['id'], argv=check['argv'], cwd=cwd, head=head,
                    output=str(Path(log_path).resolve()), exitCode=None, timedOut=False)
    # Exclusive creation prevents a rerun from destroying prior evidence.
    with open(log_path, 'xb') as output:
        try:
            completed = subprocess.run(check['argv'], cwd=cwd, stdout=output,
                                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                       timeout=check['timeoutMs'] / 1000, shell=False)
            evidence['exitCode'] = completed.returncode
        except subprocess.TimeoutExpired:
            evidence['timedOut'] = True
        except OSError as error:
            evidence['error'] = str(error)
    evidence['passed'] = evidence['exitCode'] == 0 and not evidence['timedOut']
    return evidence


if __name__ == '__main__':
    try:
        if len(sys.argv) != 5:
            raise ValueError('usage: run-check.py CHECK_JSON REPO NEW_LOG EVIDENCE_JSON')
        # Reserve the evidence path before executing a possibly side-effecting check.
        with open(sys.argv[4], 'x') as evidence_file:
            evidence = run(read(sys.argv[1]), sys.argv[2], sys.argv[3])
            json.dump(evidence, evidence_file, indent=2)
        print(json.dumps(evidence))
        sys.exit(0 if evidence['passed'] else 1)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
