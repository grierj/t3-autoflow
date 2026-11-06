#!/usr/bin/env python3
"""Dependency-free validation of model handoffs and discovered test commands."""
import json
import sys



def obj(properties):
    return dict(type='object', properties=properties, required=list(properties), additionalProperties=False)


def array(items, minimum=0):
    return dict(type='array', items=items, minItems=minimum)


def enum(*values):
    return dict(type='string', enum=list(values))


TEXT = dict(type='string', minLength=1)
TEXTS = array(TEXT)
COMPLEXITY = enum('low', 'medium', 'high')
TASK = obj(dict(id=TEXT, title=TEXT, complexity=COMPLEXITY, files=array(TEXT, 1),
                implementation=array(TEXT, 1), acceptance=array(TEXT, 1),
                dependencies=TEXTS, ui=dict(type='boolean')))
FINDING = obj(dict(id=TEXT, severity=enum('P0', 'P1', 'P2'), summary=TEXT,
                   evidence=TEXT, fix=TEXT, complexity=COMPLEXITY))
PLAN = obj(dict(goal=TEXT, tasks=array(TASK, 1), questions=TEXTS))
SCHEMAS = {
    'plan': PLAN,
    'checker': obj(dict(verdict=enum('agree', 'revised'), objections=TEXTS, plan=PLAN)),
    'coder': obj(dict(status=enum('done', 'blocked', 'stalled', 'arbitrate'), summary=TEXT, changedFiles=TEXTS,
                      deviations=TEXTS, judgementCalls=TEXTS)),
    'review': obj(dict(verdict=enum('pass', 'findings', 'blocked'), summary=TEXT, findings=array(FINDING))),
    'arbitrator': obj(dict(verdict=enum('progressing', 'try-fix', 'terminate'), evidence=TEXT,
                           action=TEXT))
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(schema, value, path='$'):
    """Validate only the JSON Schema vocabulary used by SCHEMAS."""
    kind = schema['type']
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool}
    require(type(value) is types[kind], f'{path}: expected {kind}')
    if 'enum' in schema:
        require(value in schema['enum'], f'{path}: expected one of {schema["enum"]}')
    if kind == 'string':
        require(len(value.strip()) >= schema.get('minLength', 0), f'{path}: empty string')
    elif kind == 'array':
        require(len(value) >= schema.get('minItems', 0), f'{path}: too few items')
        for i, item in enumerate(value):
            validate(schema['items'], item, f'{path}[{i}]')
    elif kind == 'object':
        require(set(value) == set(schema['required']), f'{path}: missing or unknown fields')
        for key, item in value.items():
            validate(schema['properties'][key], item, f'{path}.{key}')


def plan_order(plan):
    seen = set()
    for task in plan['tasks']:
        require(task['id'] not in seen, 'duplicate task ID')
        require(set(task['dependencies']) <= seen, 'dependencies must precede task')
        seen.add(task['id'])


def result(kind, value, reviewed=None):
    validate(SCHEMAS[kind], value)
    if kind == 'plan':
        plan_order(value)
    elif kind == 'checker':
        plan_order(value['plan'])
        agree = value['verdict'] == 'agree'
        require(not agree or not (value['objections'] or value['plan']['questions']),
                'agreement has unresolved items')
        require(agree or bool(value['objections']), 'revision needs objections')
        if reviewed is not None:
            result('plan', reviewed)
            require(agree == (value['plan'] == reviewed),
                    'agreement must return the reviewed plan unchanged; a revision must change it')
    elif kind == 'review':
        require((value['verdict'] == 'findings') == bool(value['findings']), 'verdict contradicts findings')
        ids = [f['id'] for f in value['findings']]
        require(len(ids) == len(set(ids)), 'duplicate finding ID')
    return value


def keys(value, allowed, required=()):
    require(type(value) is dict, 'expected object')
    require(set(value) <= set(allowed), f'unknown fields: {set(value) - set(allowed)}')
    require(set(required) <= set(value), f'missing fields: {set(required) - set(value)}')


def command(value):
    keys(value, ['id', 'argv', 'timeoutMs'], ['id', 'argv', 'timeoutMs'])
    validate(TEXT, value['id'])
    validate(array(TEXT, 1), value['argv'])
    require(all('\0' not in arg for arg in value['argv']), 'argv contains NUL')
    require(type(value['timeoutMs']) is int and value['timeoutMs'] > 0, 'timeoutMs must be positive integer')


def read(path):
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, f'duplicate JSON field: {key}')
            value[key] = item
        return value
    with open(path) as handle:
        return json.load(handle, object_pairs_hook=unique_pairs)


def main(args):
    if args == ['schemas']:
        return SCHEMAS
    if len(args) == 3 and args[0] == 'result' and args[1] in SCHEMAS:
        return result(args[1], read(args[2]))
    if len(args) == 4 and args[:2] == ['result', 'checker']:
        return result('checker', read(args[2]), read(args[3]))
    raise ValueError('usage: validate.py schemas | result KIND FILE | result checker FILE REVIEWED_PLAN')


if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:]), indent=2))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
