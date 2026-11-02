import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/t3-autoflow/scripts'
sys.path.insert(0, str(SCRIPTS))
import validate as v
spec = importlib.util.spec_from_file_location('run_check', SCRIPTS / 'run-check.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class Validation(unittest.TestCase):
    def test_command_contract(self):
        v.command(dict(id='unit', argv=['python3', '-m', 'unittest'], timeoutMs=1000))
        for command in [dict(id='unit', argv='npm test', timeoutMs=1000),
                        dict(id='unit', argv=[], timeoutMs=1000),
                        dict(id='unit', argv=['npm', 'test'], timeoutMs=True),
                        dict(id='unit', argv=['npm', 'test']),
                        dict(id='unit', argv=['bad\0arg'], timeoutMs=1000)]:
            with self.subTest(command=command), self.assertRaises(ValueError):
                v.command(command)

    def test_review_consistency(self):
        good = {'verdict': 'pass', 'summary': 'Inspected diff', 'findings': []}
        v.result('review', good)
        for update in [{'verdict': 'findings'}, {'extra': True}, {'summary': ' '}, {'findings': ['bug']}]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                v.result('review', dict(good, **update))

    def test_plan_dependencies(self):
        task = dict(id='one', title='Implement', complexity='low', files=['x'],
                    acceptance=['Output matches expected'], dependencies=[], ui=False)
        plan = dict(goal='Example', tasks=[task], questions=[])
        v.result('plan', plan)
        for tasks in [[task, task], [dict(task, dependencies=['missing'])],
                      [dict(task, dependencies=['one'])]]:
            with self.assertRaises(ValueError):
                v.result('plan', dict(plan, tasks=tasks))

    def test_all_result_contracts(self):
        v.result('coder', dict(status='blocked', summary='Missing dependency', changedFiles=[],
                               deviations=[], judgementCalls=[]))
        v.result('arbitrator', dict(verdict='terminate', evidence='Repeated failure',
                                    action='Install dependency', dispositions=[]))
        with self.assertRaises(ValueError):
            v.result('checker', dict(verdict='agree', objections=['missing task'], questions=[]))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            path.write_text('{"verdict":"pass","verdict":"blocked"}')
            with self.assertRaises(ValueError):
                v.read(path)


class CheckExecution(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.com', 'commit', '--allow-empty', '-qm', 'fixture'], check=True)

    def check(self, code, timeout=2000, extra=()):
        return dict(id='unit', argv=[sys.executable, '-c', code, *extra], timeoutMs=timeout)

    def test_literal_argv_and_evidence(self):
        literal = '$(touch SHOULD_NOT_EXIST); `echo nope`'
        result = runner.run(self.check('import sys; print(sys.argv[1])', extra=[literal]),
                            self.repo, self.repo / 'output')
        self.assertTrue(result['passed'])
        self.assertEqual((self.repo / 'output').read_text().strip(), literal)
        self.assertFalse((self.repo / 'SHOULD_NOT_EXIST').exists())
        self.assertEqual(result['cwd'], str(self.repo))
        self.assertEqual(len(result['head']), 40)

    def test_failure_timeout_missing_command(self):
        checks = [self.check('print("failure"); raise SystemExit(7)'),
                  self.check('import time; time.sleep(5)', 20),
                  dict(id='unit', argv=[str(self.repo / 'missing')], timeoutMs=100)]
        for i, check in enumerate(checks):
            with self.subTest(i=i):
                result = runner.run(check, self.repo, self.repo / str(i))
                self.assertFalse(result['passed'])
        self.assertIn('failure', (self.repo / '0').read_text())

    def test_cli_and_no_overwrite(self):
        check = self.repo / 'check.json'
        check.write_text(json.dumps(self.check('print("ok")')))
        log, evidence = self.repo / 'log', self.repo / 'evidence.json'
        argv = [sys.executable, str(SCRIPTS / 'run-check.py'), str(check), str(self.repo), str(log), str(evidence)]
        first = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(json.loads(evidence.read_text())['passed'])
        before = evidence.read_bytes()
        second = subprocess.run(argv, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(evidence.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
