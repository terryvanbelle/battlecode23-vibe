import copy
import unittest
import validate_sampled as gate


class SampledEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.ids=[11,22,33]
        self.on='fixture-on-replay-checksum'
        self.sampling={'engine_sha256':gate.RELEASE,'engine_patch_used':False,
            'host_sampling_override':True,'bot_source_instrumented':False,
            'own_package':'c_mend2','map':'Cornucopia','map_seed':272,'map_round_limit':2000,
            'requested_ids':self.ids,'recorded_ids':self.ids,'selected_ids_with_wrong_type':[],
            'selection_complete':True,'replay_sha256':self.on}
        self.identity={'fingerprint_identity':True,'footer_result_identity':True,
            'terminal_metadata_valid':True,'off_replay_sha256':gate.OFF_SHA,'on_replay_sha256':self.on}
        self.files=[dict(game=0,map='Cornucopia',side='A',file=0,map_seed=272,capped=False),
                    dict(game=0,map='Cornucopia',side='B',file=1,map_seed=272,capped=True)]
        self.robots=[dict(game=0,map='Cornucopia',side='A',package='c_mend2',robot=i,file=0,
                         type='LAUNCHER',exception_status='zero_through_last_turn',
                         caller_context_status='zero_observed_ex_valid_native_nesting',
                         native_costs_usable=True,frequency_exact=True,entry_budget_aligned=True,
                         team_capped=False) for i in self.ids]

    def result(self,off=gate.OFF_SHA,on=None):
        return gate.assess(self.sampling,self.identity,self.robots,self.files,off,self.on if on is None else on)

    def test_complete_selected_own_scope_is_ready_and_other_cap_ignored(self):
        self.assertTrue(self.result()['ready'])
        self.assertEqual(self.result()['complete_usable_launcher_ids'],self.ids)
        self.sampling['recorded_ids']=list(reversed(self.ids))
        self.assertTrue(self.result()['ready'])

    def test_every_identity_dimension_and_preserved_replay_pin_required(self):
        for key in ('fingerprint_identity','footer_result_identity','terminal_metadata_valid'):
            with self.subTest(field=key):
                self.identity[key]=False;self.assertFalse(self.result()['ready']);self.identity[key]=True
        self.assertFalse(self.result(off='different control')['ready'])
        self.assertFalse(self.result(on='changed sampled replay')['ready'])

    def test_selected_caps_exception_tail_and_alignment_are_censored(self):
        for key,bad in (('exception_status','missing_counter'),('exception_status','observed_exception'),
                        ('caller_context_status','native_nesting_unverified'),('native_costs_usable',False),
                        ('frequency_exact',False),('entry_budget_aligned',False),('team_capped',True)):
            with self.subTest(field=key,value=bad):
                old=self.robots[1][key];self.robots[1][key]=bad
                self.assertFalse(self.result()['ready']);self.robots[1][key]=old
        self.files[0]['capped']=True;self.assertFalse(self.result()['ready'])

    def test_missing_wrong_type_and_duplicate_samples_fail(self):
        self.robots.pop();self.assertFalse(self.result()['ready'])
        self.robots.append(copy.deepcopy(self.robots[0]));self.assertFalse(self.result()['ready'])
        self.sampling['selection_complete']=False;self.assertFalse(self.result()['ready'])

    def test_instrumented_source_or_changed_map_or_role_are_refused(self):
        for key,bad in (('bot_source_instrumented',True),('engine_patch_used',True),
                        ('own_package','c_mend3'),('map_seed',273),('map_round_limit',300)):
            with self.subTest(field=key):
                old=self.sampling[key];self.sampling[key]=bad
                self.assertFalse(self.result()['ready']);self.sampling[key]=old


if __name__=='__main__':
    unittest.main()
