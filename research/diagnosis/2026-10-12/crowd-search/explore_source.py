#!/usr/bin/env python3
"""Prepare isolated scratch exploration arms. Only Carrier.java/C.java differ from Mend2."""
import argparse
import shutil
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('repo', type=Path)
parser.add_argument('frozen_prototype_source', type=Path)
parser.add_argument('new_output', type=Path)
args = parser.parse_args()
args.new_output.mkdir()
shutil.copytree(args.repo / 'src/c_mend2', args.new_output / 'c_mend2')
for pkg, enabled in (('c_explore0', False), ('c_explore1', True)):
    shutil.copytree(args.repo / 'src/c_mend2', args.new_output / pkg)
    for path in (args.new_output / pkg).glob('*.java'):
        text = path.read_text().replace('package c_mend2;', 'package ' + pkg + ';')
        text = text.replace('import c_mend2.', 'import ' + pkg + '.').replace('import static c_mend2.', 'import static ' + pkg + '.')
        path.write_text(text)
    carrier = args.new_output / pkg / 'Carrier.java'
    text = (args.frozen_prototype_source / 'c_crowdprobe/Carrier.java').read_text().replace('package c_crowdprobe;', 'package ' + pkg + ';')
    text = text.replace('    static final int CROWD_EXPLORE_TURNS = 12;', '''    // Decisions never read these counters. cx packs starts[27:20], exploration turns[19:8], new sites[7:0].
    static MapLocation crowdOutcomeWell;
    public static int crowdSearchStarts, crowdSearchTurns, crowdSearchFound;''')
    text = text.replace('''        if (crowdRejected != null) {''', '''        if (C.CROWD_SEARCH && crowdOutcomeWell != null && role != 2) crowdOutcomeWell = null;
        if (crowdRejected != null) {''')
    text = text.replace('if (crowdRejected != null) {', 'if (C.CROWD_SEARCH && crowdRejected != null) {')
    text = text.replace('''            else if (well == null) {
                MapLocation other''', '''            else if (well == null) {
                if (Clock.getBytecodesLeft() < C.CROWD_SEARCH_GUARD) { state = 'W'; return; }
                MapLocation other''')
    text = text.replace('well = other; crowdRejected = null;', 'well = other; crowdRejected = null; crowdOutcomeWell = other;')
    text = text.replace("state = 'X'; searchTurns++; explore(); return;", "state = 'X'; searchTurns++; crowdSearchTurns++; explore(); return;")
    text = text.replace('''            if (G.rc.getWeight() == 0) { crowdRejected = well; crowdExploreUntil = G.round + CROWD_EXPLORE_TURNS; }''',
                        '''            if (C.CROWD_SEARCH && G.rc.getWeight() == 0 && Clock.getBytecodesLeft() >= C.CROWD_SEARCH_GUARD) {
                crowdRejected = well; crowdExploreUntil = G.round + C.CROWD_SEARCH_ROUNDS; crowdSearchStarts++;
            }''')
    text = text.replace("        prevState = state;", '''        prevState = state;
        if (C.CROWD_SEARCH) G.extra = ",cx=" + crowdTrace(crowdSearchStarts, crowdSearchTurns, crowdSearchFound);''')
    text = text.replace('''                else break;
            }
            if (rc.getWeight() >= C.CARRIER_RETURN_LOAD) returning = true;''', '''                else break;
                if (C.CROWD_SEARCH && crowdOutcomeWell != null && crowdOutcomeWell.equals(well)) {
                    crowdSearchFound++; crowdOutcomeWell = null;
                }
            }
            if (rc.getWeight() >= C.CARRIER_RETURN_LOAD) returning = true;''')
    text = text.replace('    static MapLocation crowdKnownMana()', '''    static int crowdTrace(int starts, int turns, int found) {
        return Math.min(starts, 255) << 20 | Math.min(turns, 4095) << 8 | Math.min(found, 255);
    }

    static MapLocation crowdKnownMana()''')
    carrier.write_text(text)
    constants = args.new_output / pkg / 'C.java'
    text = constants.read_text()
    needle = '    public static final int WELL_CROWD_PATIENCE = 6;'
    assert text.count(needle) == 1
    text = text.replace(needle, needle + '''
    /** c_explore1: bounded discovery only for empty Mana carriers with no known crowd alternative. */
    public static final boolean CROWD_SEARCH = ''' + str(enabled).lower() + ''';
    public static final int CROWD_SEARCH_ROUNDS = 12, CROWD_SEARCH_GUARD = 3000;''')
    constants.write_text(text)
    base = args.new_output / 'c_mend2'
    for path in (args.new_output / pkg).glob('*.java'):
        if path.name in ('Carrier.java', 'C.java'):
            continue
        normalized = path.read_text().replace('package ' + pkg + ';', 'package c_mend2;')
        normalized = normalized.replace('import ' + pkg + '.', 'import c_mend2.').replace('import static ' + pkg + '.', 'import static c_mend2.')
        assert normalized == (base / path.name).read_text(), 'unexpected unrelated source change'
