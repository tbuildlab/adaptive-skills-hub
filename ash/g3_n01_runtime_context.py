"""Non-restorable N01 context custody over the fixed native SDK transport.

Always NONE. Protected source/deployment enrollment and N02 human ingress must
precede construction. No caller token, signature, SDK type or matching digest
alone establishes those gates. There is no credential loader or approval API.
"""
import hmac
import time

from stytch import Client

from ash.g3_control_semantics import require
from ash import g3_n01_owner_context as owner
from ash.g3_n01_stytch_transport import BoundedStytchSession


class CurrentSession:
    """Short-lived process memory only; never a receipt, grant or authority."""
    def __init__(self,client,transport,bearer,keys,*,review_from_ms,review_until_ms,operation_until_ms):
        self.__client=None;self.__transport=None;self.__bearer=None
        self.__projection=None;self.__deadline=None;self.__retired=True
        try:
            require(type(client) is Client and type(transport) is BoundedStytchSession)
            require(client.sync_client._session is transport and client.sync_client.project_id==owner.PROJECT)
            require(type(bearer) is str and 0<len(bearer)<=8192 and bearer.isascii())
            # Public pins are copied into this exact context, never refreshed.
            self.__keys=owner.public_keys(keys)
            self.__review_from=owner.integer(review_from_ms)
            self.__review_until=owner.integer(review_until_ms)
            self.__client=client;self.__transport=transport;self.__bearer=bearer
            projection,factor_deadline=self.__remote()
            now=int(time.time()*1000);monotonic=int(time.monotonic()*1000)
            self.__deadline=owner.ContextDeadline(authenticated_at_ms=projection.authenticated_at_ms,
                review_until_ms=self.__review_until,
                operation_until_ms=min(owner.integer(operation_until_ms),projection.remote_expires_at_ms,factor_deadline),
                # Account for authentication time already elapsed before construction.
                monotonic_start_ms=monotonic-(now-projection.authenticated_at_ms))
            self.__deadline.check(now_ms=now,monotonic_ms=monotonic)
            self.__projection=projection;self.__retired=False
        except Exception:
            self.retire()
            raise ValueError('N01_CURRENT_SESSION_RETIRED') from None

    @property
    def authority(self):return 'NONE'
    @property
    def retired(self):return self.__retired
    @property
    def deadline_ms(self):
        require(not self.__retired)
        return self.__deadline.until
    def __repr__(self):return 'CurrentSession(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_SESSION_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_SESSION_NOT_RESTORABLE')

    def __remote(self):
        transport=self.__transport
        require(transport is not None and not transport.retired)
        require(type(self.__client) is Client and self.__client.sync_client._session is transport
                and self.__client.sync_client.project_id==owner.PROJECT
                and self.__client.sessions.sync_client is self.__client.sync_client)
        before=transport.attempts
        try:
            # No duration, JWT-cache, renewal, discovery or fallback path.
            self.__client.sessions.authenticate(session_token=self.__bearer)
            require(transport.attempts==before+1)
            body=transport._native_body
            require(type(body) is dict and type(body.get('session_token')) is str
                    and body['session_token'].isascii()
                    and hmac.compare_digest(body['session_token'],self.__bearer))
            projection=owner.project_current_owner(body,self.__keys,review_from_ms=self.__review_from,
                review_until_ms=self.__review_until,now_ms=int(time.time()*1000))
            factors=body['session']['authentication_factors']
            times=[owner.timestamp(factor['last_authenticated_at'])[0] for factor in factors
                if (factor.get('type') in ('otp','email_otp') and factor.get('delivery_method')=='email')
                or (factor.get('type')=='totp' and factor.get('delivery_method')=='authenticator_app')]
            require(len(times)==2)
            return projection,min(times)+owner.MAX_CONTEXT_MS
        finally:
            # Even the SDK response buffer cannot retain bearer material between
            # operations. Only this context's private original bearer survives.
            transport._native_body=None

    def recheck(self):
        try:
            require(not self.__retired)
            self.__deadline.check(now_ms=int(time.time()*1000),monotonic_ms=int(time.monotonic()*1000))
            current,_=self.__remote()
            owner.same_current_session(self.__projection,current)
            self.__deadline.check(now_ms=int(time.time()*1000),monotonic_ms=int(time.monotonic()*1000))
            return current
        except Exception:
            self.retire()
            raise ValueError('N01_CURRENT_SESSION_RETIRED') from None

    def revoke(self):
        try:
            current=self.recheck()
            # Exact retained session only. No global user/account mutation.
            self.__client.sessions.revoke(session_id=current.provider_session)
            before=self.__transport.attempts
            try:self.__client.sessions.authenticate(session_token=self.__bearer)
            except Exception:pass  # Check exact native rejection, not generic SDK error.
            body=self.__transport._native_body
            require(self.__transport.attempts==before+1 and type(body) is dict
                    and body.get('status_code')==404 and body.get('error_type')=='session_not_found')
            return 'EXACT_REMOTE_SESSION_REVOKED_NON_AUTHORITY'
        except Exception:
            raise ValueError('N01_CURRENT_SESSION_RETIRED') from None
        finally:self.retire()

    def retire(self):
        self.__retired=True
        if self.__deadline is not None:self.__deadline.retire()
        if self.__transport is not None:self.__transport.close()
        self.__client=None;self.__transport=None;self.__bearer=None;self.__projection=None
