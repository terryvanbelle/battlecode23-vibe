#!/usr/bin/env python3
"""Dead-code check for a bot package (owner prompt 127: Sym.observe existed but was never called, so the symmetry was
guessed in ~30% of games). Lists every method declared in src/<pkg>/*.java that is never referenced from the package's
other code (tests do not count), and constants (static final) never read.
    tools/deadcode.py [src/bot] [--allow name,name]     exit 1 if anything is unreferenced
Entry points (run, main) and engine callbacks are allowed. Overloads count as one name."""
import os, re, sys

ENTRY = {'run', 'main', 'toString', 'equals', 'hashCode'}

def scan(pkg_dir, allow=()):
    files = {f: open(os.path.join(pkg_dir, f)).read() for f in sorted(os.listdir(pkg_dir)) if f.endswith('.java')}
    strip = lambda s: re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"', ' ', s, flags=re.S)
    code = {f: strip(s) for f, s in files.items()}
    decl_m = re.compile(r'^\s*(?:public |protected |private )?(?:static )?(?:final )?(?:strictfp )?[\w<>\[\], ]+?\s+(\w+)\s*\([^;{]*\)\s*(?:throws [\w., ]+)?\s*\{', re.M)
    decl_c = re.compile(r'^\s*(?:public |protected |private )?static final [\w<>\[\]]+\s+(.+?);', re.M)
    methods, consts = {}, {}
    for f, s in code.items():
        for m in decl_m.finditer(s):
            name = m.group(1)
            if name in ('if', 'for', 'while', 'switch', 'catch', 'return', 'new') or name[0].isupper(): continue
            methods.setdefault(name, f)
        for m in decl_c.finditer(s):
            for part in m.group(1).split(','):
                n = part.split('=')[0].strip()
                if re.fullmatch(r'\w+', n): consts.setdefault(n, f)
    allcode = '\n'.join(code.values())
    dead = []
    for name, f in sorted(methods.items()):
        if name in ENTRY or name in allow: continue
        uses = len(re.findall(r'(?<![\w])' + name + r'\s*\(', allcode))
        decls = len(re.findall(r'[\w>\]]\s+' + name + r'\s*\([^;{]*\)\s*(?:throws [\w., ]+)?\s*\{', allcode))
        if uses - decls <= 0: dead.append(f'method {name} ({f})')
    for name, f in sorted(consts.items()):
        if name in allow: continue
        if len(re.findall(r'(?<![\w])' + name + r'(?![\w])', allcode)) <= 1: dead.append(f'constant {name} ({f})')
    return dead

if __name__ == '__main__':
    args = sys.argv[1:]; allow = ()
    if '--allow' in args:
        i = args.index('--allow'); allow = set(args[i + 1].split(',')); args = args[:i] + args[i + 2:]
    pkg = args[0] if args else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'bot')
    dead = scan(pkg, allow)
    for d in dead: print('UNREFERENCED', d)
    print(f'deadcode {pkg}: {len(dead)} unreferenced')
    sys.exit(1 if dead else 0)
