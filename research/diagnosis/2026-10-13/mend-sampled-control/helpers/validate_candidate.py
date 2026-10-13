#!/usr/bin/env python3
"""Read-only post-game gate. Costs remain unavailable until all evidence passes."""
import hashlib
import json
from pathlib import Path
import sys

RELEASE='5d4e42a51946cc1c2149426485bda8096ff1c088c77e3ed075c06ce5968ed72a'
IDS=[13460,11979,12422]


def sha(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular owned input required')
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1048576),b''):
            digest.update(data)
    return digest.hexdigest()


def rows(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('regular owned input required')
    with path.open() as stream:
        return [json.loads(line) for line in stream if line.strip()]


def assess(sampling,identity,robots,files,observed_off_sha,observed_on_sha,expected_off_sha):
    reasons=[]
    ids=sampling.get('requested_ids',[])
    if (not isinstance(ids,list) or not 3<=len(ids)<=5
            or any(type(value) is not int or value<=0 for value in ids) or len(ids)!=len(set(ids))):
        reasons.append('invalid_explicit_sample_ids')
        ids=[]
    if ids!=IDS:
        reasons.append('reviewed_explicit_sample_ids_mismatch')
    if (sampling.get('engine_sha256')!=RELEASE or sampling.get('engine_patch_used') is not False
            or sampling.get('host_sampling_override') is not True
            or sampling.get('bot_source_instrumented') is not False
            or sampling.get('own_package')!='c_mend3' or sampling.get('map')!='Cornucopia'
            or sampling.get('map_seed')!=272 or sampling.get('map_round_limit')!=2000):
        reasons.append('frozen_candidate_sampling_provenance_mismatch')
    if observed_off_sha!=expected_off_sha:
        reasons.append('candidate_off_replay_changed_after_off_completion')
    for mode,observed in (('off',observed_off_sha),('on',observed_on_sha)):
        if identity.get(mode+'_replay_sha256')!=observed:
            reasons.append(mode+'_replay_changed_after_identity')
    for field in ('fingerprint_identity','footer_result_identity','terminal_metadata_valid'):
        if identity.get(field) is not True:
            reasons.append(field+'_not_passed')
    if sampling.get('replay_sha256')!=observed_on_sha:
        reasons.append('sampled_replay_pin_mismatch')
    recorded=sampling.get('recorded_ids',[])
    if (sampling.get('selection_complete') is not True or not isinstance(recorded,list)
            or any(type(value) is not int for value in recorded)
            or len(recorded)!=len(ids) or set(recorded)!=set(ids)
            or sampling.get('selected_ids_with_wrong_type')!=[]):
        reasons.append('explicit_own_launcher_selection_incomplete')
    own_files={row.get('file'):row for row in files
               if row.get('game')==0 and row.get('map')=='Cornucopia' and row.get('side')=='A'}
    good=[]
    for identifier in ids:
        selected=[row for row in robots if row.get('game')==0 and row.get('side')=='A'
                  and row.get('package')=='c_mend3' and row.get('robot')==identifier]
        if len(selected)!=1:
            reasons.append('selected_launcher_'+str(identifier)+'_not_unique');continue
        robot=selected[0];profile=own_files.get(robot.get('file'))
        if (robot.get('type')!='LAUNCHER' or robot.get('map')!='Cornucopia'
                or robot.get('trace_valid') is not True
                or robot.get('exception_status')!='zero_through_last_turn'
                or robot.get('caller_context_status')!='zero_observed_ex_valid_native_nesting'
                or robot.get('native_costs_usable') is not True
                or robot.get('frequency_exact') is not True
                or robot.get('entry_budget_aligned') is not True
                or type(robot.get('recorded_bytecodes')) is not int
                or robot.get('native_counter')!=robot.get('recorded_bytecodes')
                or robot.get('team_capped') is not False
                or not isinstance(profile,dict) or profile.get('capped') is not False
                or profile.get('map_seed')!=272):
            reasons.append('selected_launcher_'+str(identifier)+'_cap_exception_or_alignment_unusable');continue
        good.append(identifier)
    return {'ready':not reasons,'status':'ready' if not reasons else 'not_ready',
            'explicit_sample_ids':ids,'complete_usable_launcher_ids':good,
            'identity_verified':all(identity.get(field) is True for field in
                                    ('fingerprint_identity','footer_result_identity','terminal_metadata_valid')),
            'native_costs_available':not reasons,'missing_requirements':reasons,
            'limits':'Full replay identity and selected-robot coverage gate only. Mend-specific method/tail scope must pass separately; sampling is selected diagnostic evidence, not workload population weights.'}


def main():
    if len(sys.argv)!=5:
        raise SystemExit('validate_candidate.py OWN_SAMPLED_OUTPUT PAIR_IDENTITY_DIRECTORY NATIVE_DIRECTORY FROZEN_OFF_SHA')
    output,pair,native=map(Path,sys.argv[1:4]);off_pin=sys.argv[4]
    if len(off_pin)!=64 or any(char not in '0123456789abcdef' for char in off_pin):
        raise SystemExit('candidate off completion SHA required')
    sampling=json.loads((output/'sampling.json').read_text())
    identity=json.loads((pair/'identity.json').read_text())
    result=assess(sampling,identity,rows(native/'robots.jsonl'),rows(native/'files.jsonl'),
                  sha(pair/'off.bc23'),sha(pair/'on.bc23'),off_pin)
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result['ready'] else 3)


if __name__=='__main__':
    main()
