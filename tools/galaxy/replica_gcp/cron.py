"""Unix cron (5 fields: minute hour day-of-month month day-of-week), as Cloud Scheduler reads `schedule`.

Supports *, n, a-b, */s, a-b/s, n/s, lists and month/day names. Day-of-month and day-of-week combine with OR when
both are restricted (Vixie cron). Sunday is 0 or 7.
"""
import datetime

_FIELDS = (('minute', 0, 59), ('hour', 0, 23), ('dom', 1, 31), ('month', 1, 12), ('dow', 0, 7))
_NAMES = {
    'month': {m: i + 1 for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split())},
    'dow': {d: i for i, d in enumerate('sun mon tue wed thu fri sat'.split())},
}


def _value(tok, field, lo, hi):
    tok = tok.lower()
    v = _NAMES.get(field, {}).get(tok)
    if v is None:
        if not tok.isdigit():
            raise ValueError(f'bad {field} value {tok!r}')
        v = int(tok)
    if not lo <= v <= hi:
        raise ValueError(f'{field} value {v} outside {lo}-{hi}')
    return v


def _parse_field(text, field, lo, hi):
    out = set()
    for part in text.split(','):
        step = 1
        if '/' in part:
            part, s = part.split('/', 1)
            if not s.isdigit() or int(s) < 1:
                raise ValueError(f'bad step in {text!r}')
            step = int(s)
        if part == '*':
            a, b = lo, hi
        elif '-' in part:
            x, y = part.split('-', 1)
            a, b = _value(x, field, lo, hi), _value(y, field, lo, hi)
            if a > b:
                raise ValueError(f'bad range {part!r}')
        else:
            a = _value(part, field, lo, hi)
            b = hi if step > 1 else a
        out.update(range(a, b + 1, step))
    if field == 'dow' and 7 in out:
        out.add(0)
        out.discard(7)
    return out


def parse(spec):
    parts = spec.split() if isinstance(spec, str) else []
    if len(parts) != 5:
        raise ValueError(f'cron spec needs 5 fields: {spec!r}')
    sets = {}
    for text, (field, lo, hi) in zip(parts, _FIELDS):
        sets[field] = _parse_field(text, field, lo, hi)
    sets['dom_star'] = parts[2] == '*'
    sets['dow_star'] = parts[4] == '*'
    return sets


def matches(spec, when):
    """Whether the cron spec fires at the minute of datetime `when` (in the schedule's own time zone)."""
    s = parse(spec)
    if when.minute not in s['minute'] or when.hour not in s['hour'] or when.month not in s['month']:
        return False
    dom_ok = when.day in s['dom']
    dow_ok = (when.isoweekday() % 7) in s['dow']
    if s['dom_star'] or s['dow_star']:
        return dom_ok and dow_ok
    return dom_ok or dow_ok


def next_fire(spec, after, limit_minutes=366 * 24 * 60):
    t = after.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
    for _ in range(limit_minutes):
        if matches(spec, t):
            return t
        t += datetime.timedelta(minutes=1)
    return None
