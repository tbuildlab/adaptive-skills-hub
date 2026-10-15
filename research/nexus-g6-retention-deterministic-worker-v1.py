"""One fixed retention transform; data only, no model/tools/commands/network.

This is an actual deterministic implementation, not an expected-answer fixture.
The production caller pins the input and this script before dispatch. Public
qualification supplies different, finite, explicitly PUBLIC fixture records.
"""
import json
import sys


def transform(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= 16384:
        raise ValueError('INPUT_BOUND')
    start = b'Source records: '
    end = b'\n/no_think'
    if raw.count(start) != 1 or raw.count(end) != 1:
        raise ValueError('INPUT_SHAPE')
    payload = raw.split(start, 1)[1].split(end, 1)[0]
    records = json.loads(payload)
    if type(records) is not list or len(records) != 3:
        raise ValueError('ROW_BOUND')
    seen = set()
    output = ['attempt,outcome,action,bytes']
    for record in records:
        if type(record) is not dict or set(record) != {'attempt', 'status', 'retired', 'retained_bytes'}:
            raise ValueError('ROW_SHAPE')
        name, status, amount = record['attempt'], record['status'], record['retained_bytes']
        if (type(name) is not str or not 0 < len(name) <= 16
                or not name.isascii() or not name.isalnum() or name in seen
                or record['retired'] is not True or type(amount) is not int or not 0 <= amount <= 65536
                or status not in ('QUARANTINE', 'NATIVE_BOUNDED_RESULT_OBSERVED')):
            raise ValueError('ROW_VALUE')
        seen.add(name)
        outcome = 'QUARANTINE' if status == 'QUARANTINE' else 'PUBLIC_ONLY_PASS'
        output.append(f'{name},{outcome},KEEP,{amount}')
    return ('\n'.join(output) + '\nEND_G6_AUDIT\n').encode('ascii')


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2:
            raise ValueError('ARGUMENT_SHAPE')
        with open(sys.argv[1], 'rb') as source:
            raw = source.read(16385)
        result = transform(raw)
        sys.stdout.buffer.write(result)
        sys.stdout.buffer.flush()
    except Exception:
        # Closed error only; no task, path, JSON contents or traceback leakage.
        sys.stderr.write('RETENTION_INPUT_REJECTED\n')
        raise SystemExit(2)
