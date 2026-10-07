#!/usr/bin/env python3
"""Drop every markdown block (section, list item with its children, paragraph, code fence) that is tagged with the
forbidden year or names one of that year's teams/units. Conservative: any doubt -> drop."""
import re, sys

TAG = re.compile(r"2023|\bbc23\b|Gone Fishin|4 Musketeers|no thoughts|camel_case|don't @ me|Tempest|adamantium|"
                 r"elixir|amplifier|launcher|\banchor|\bislands?\b|destabili[sz]er|\bbooster", re.I)

def indent(l): return len(l) - len(l.lstrip(' '))
ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s")

def blocks(lines):
    """Yield (kind, level, start, end) blocks over line indices."""
    i, n = 0, len(lines)
    while i < n:
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.lstrip().startswith('```'):
            j = i + 1
            while j < n and not lines[j].lstrip().startswith('```'): j += 1
            yield ('code', indent(l), i, min(j + 1, n)); i = j + 1; continue
        m = re.match(r'^(#+)\s', l)
        if m: yield ('head', len(m.group(1)), i, i + 1); i += 1; continue
        m = ITEM.match(l)
        if m:
            base = indent(l); j = i + 1
            while j < n:
                lj = lines[j]
                if not lj.strip():
                    # blank: continue only if next non-blank is indented deeper than the item
                    k = j
                    while k < n and not lines[k].strip(): k += 1
                    if k < n and indent(lines[k]) > base and not re.match(r'^#+\s', lines[k]): j = k; continue
                    break
                if re.match(r'^#+\s', lj): break
                if ITEM.match(lj) and indent(lj) <= base: break
                if indent(lj) <= base and not ITEM.match(lj) and lj.lstrip().startswith('```'): break
                j += 1
            yield ('item', base, i, j); i = j; continue
        j = i + 1
        while j < n and lines[j].strip() and not re.match(r'^#+\s', lines[j]) and not ITEM.match(lines[j]) \
                and not lines[j].lstrip().startswith('```'): j += 1
        yield ('para', indent(l), i, j); i = j

def filt(text):
    lines = text.split('\n'); keep = [True] * len(lines); bl = list(blocks(lines))
    drop_level = None; prev_dropped_colon = False
    for kind, lvl, s, e in bl:
        body = '\n'.join(lines[s:e]); hit = bool(TAG.search(body))
        if kind == 'head':
            if drop_level is not None and lvl <= drop_level: drop_level = None
            if hit: drop_level = lvl
        dropped = drop_level is not None or hit or (kind == 'code' and prev_dropped_colon)
        if dropped:
            for k in range(s, e): keep[k] = False
        prev_dropped_colon = dropped and body.rstrip().endswith(':')
    out = [l for l, k in zip(lines, keep) if k]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out))

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    t = filt(open(src).read()); open(dst, 'w').write(t)
    print(f"{src}: {len(open(src).read().splitlines())} -> {len(t.splitlines())} lines; residual hits: {len(TAG.findall(t))}")
