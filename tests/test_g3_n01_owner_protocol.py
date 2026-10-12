"""Synthetic NONE membership only; no actual Owner, custody or consent."""
from dataclasses import replace
import unittest
from ash import g3_n01_owner_protocol as protocol
from ash import g3_n01_owner_state as state
from ash import g3_n01_owner_context as owner
from ash import g3_n02_presentation as page
from ash import g3_delegated_control_codec as codec
from tests import test_g3_n01_owner_state as fixture
appended=fixture.appended


class OwnerProtocolTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixture.OwnerStateTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.enrolled=self.fixture.enrolled;self.now=self.fixture.now+100
        history=self.fixture.ready()
        enrolled,objects=state.prepare_owner_enrollment(history,self.enrolled,now_ms=self.now-1)
        self.history=appended(history,enrolled,objects)
        self.projection=owner.OwnerProjection(owner.PROJECT,owner.OWNER,
            'session-test-12345678-1234-1234-1234-123456789012',self.now-50,self.now+900000,'a'*64)
        self.until=self.now+200000
    def challenge(self):return protocol.prepare_challenge(self.history,self.enrolled,self.projection,
        deadline_ms=self.until,nonce='b'*64,now_ms=self.now)
    def pending(self):
        candidate,objects,challenge,view=self.challenge()
        return appended(self.history,candidate,objects),page.render(challenge,view,csrf='c'*64,now_ms=self.now)
    def decision(self,shown,choice='CONFIRM'):
        return page.UntrustedDecision(choice,shown.challenge_id,shown.view_id,shown.proposal_id,shown.nonce,shown.presentation_sha256)
    def test_complete_current_context_challenge_view_is_one_none_transition(self):
        candidate,objects,challenge,view=self.challenge()
        result=appended(self.history,candidate,objects)
        self.assertEqual((candidate.group,result.authority),('T1','NONE'))
        rows=[codec.decode(row.value) for row in result.states[-1].checked.rows]
        self.assertEqual(sum(row['family']=='context' for row in rows),1)
        self.assertEqual(sum(row['family']=='challenge' for row in rows),1)
        self.assertFalse(any(row['family'] in ('grant','intent','claim') for row in rows))
        shown=page.render(challenge,view,csrf='c'*64,now_ms=self.now)
        self.assertIn(b'No grant, product execution',shown.html)
        with self.assertRaises(ValueError):protocol.prepare_challenge(result,self.enrolled,self.projection,
            deadline_ms=self.until,nonce='d'*64,now_ms=self.now+1)
    def test_both_decisions_atomically_consume_without_grant_and_replay_denies(self):
        history,shown=self.pending()
        for choice in ('CONFIRM','DENY'):
            decision=self.decision(shown,choice)
            candidate,objects=protocol.prepare_decision(history,self.enrolled,decision,self.projection,now_ms=self.now+1)
            terminal=appended(history,candidate,objects)
            rows=[codec.decode(row.value) for row in terminal.states[-1].checked.rows]
            self.assertEqual(next(row['state'] for row in rows if row['family']=='context'),'CONSUMED')
            self.assertEqual(next(row['state'] for row in rows if row['family']=='nonce'),'CONSUMED')
            self.assertEqual(next(row['choice'] for row in rows if row['family']=='decision'),choice)
            self.assertFalse(any(row['family']=='grant' for row in rows))
            with self.assertRaises(ValueError):protocol.prepare_decision(terminal,self.enrolled,decision,self.projection,now_ms=self.now+2)
    def test_exact_remote_revocation_evidence_closes_consumed_lineage_without_fake_grant(self):
        history,shown=self.pending()
        candidate,objects=protocol.prepare_decision(history,self.enrolled,self.decision(shown),self.projection,now_ms=self.now+1)
        terminal=appended(history,candidate,objects)
        candidate,objects=protocol.prepare_revoke_after_consumption(terminal,self.enrolled,
            remote_result='EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY',now_ms=self.now+2)
        closed=appended(terminal,candidate,objects)
        rows=[codec.decode(row.value) for row in closed.states[-1].checked.rows]
        self.assertEqual(next(row['quarantine'] for row in rows if row['family']=='root'),'CLOSED')
        self.assertEqual(next(row['state'] for row in rows if row['family']=='context'),'CONSUMED')
        self.assertTrue(any(codec.decode(raw).get('grant_revocation')=='NOT_PERFORMED_NO_GRANT' for raw in objects.values()))
        for result in ('PASS','UNKNOWN','EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY'):
            with self.assertRaises(ValueError):protocol.prepare_revoke_after_consumption(history,self.enrolled,remote_result=result,now_ms=self.now+2)
    def test_wrong_session_owner_incarnation_deadline_and_frozen_join_deny(self):
        for projection in (replace(self.projection,provider_user='different'),replace(self.projection,provider_project='different')):
            with self.assertRaises(ValueError):protocol.prepare_challenge(self.history,self.enrolled,projection,
                deadline_ms=self.until,nonce='b'*64,now_ms=self.now)
        for until in (self.now,self.now+300001,True):
            with self.assertRaises(ValueError):protocol.prepare_challenge(self.history,self.enrolled,self.projection,
                deadline_ms=until,nonce='b'*64,now_ms=self.now)
        history,shown=self.pending();decision=self.decision(shown)
        for field in ('challenge_id','view_id','proposal_id','nonce','presentation_sha256'):
            with self.assertRaises(ValueError):protocol.prepare_decision(history,self.enrolled,replace(decision,**{field:'d'*64}),self.projection,now_ms=self.now+1)
        with self.assertRaises(ValueError):protocol.prepare_decision(history,self.enrolled,decision,
            replace(self.projection,provider_session='different'),now_ms=self.now+1)
        with self.assertRaises(ValueError):protocol.prepare_decision(history,self.enrolled,decision,self.projection,now_ms=self.until)


if __name__=='__main__':unittest.main()
