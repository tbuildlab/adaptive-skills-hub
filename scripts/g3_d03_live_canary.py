"""One bounded real S3 diagnostic via native GitHub OIDC/STS. NO_AUTHORITY.

No AWS credential is printed, exported, cached or stored. Workflow reruns abort
before authentication; an ambiguous write is reconciled, never redispatched.
Protected R setup is a separate context and cannot be invoked from this runner.
"""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sys
import urllib.request
import re
from threading import Lock

from scripts import g3_d03_canary_vectors as v
from scripts import g3_d03_s3_fence as f
from scripts.g3_production_metadata import canonical_bytes

BUCKET = "nexus-d03-custody-862902859484-ap-southeast-1-v1"
OWNER = "862902859484"
A_ROLE = "arn:aws:iam::175880707430:role/G3QualD03DiagnosticCaller"
R_ROLE = "arn:aws:iam::862902859484:role/G3QualFenceAppendRead"
ROOT = Path(__file__).resolve().parents[1]
PHASE = "REQUEST_VALIDATION"


def emit(value):
    print(json.dumps(value, sort_keys=True), flush=True)


class BoundedS3:
    def __init__(self, sdk):
        self.sdk, self.attempts = sdk, 0
        self.drop_next_ack = False
        self.responses = []
        self.lock = Lock()

    def __getattr__(self, operation):
        def call(**kw):
            f.require(kw.get("Bucket") == BUCKET and kw.get("ExpectedBucketOwner") == OWNER)
            f.require("Key" not in kw or kw["Key"].startswith((v.NORMAL, v.FAULTS)))
            with self.lock:
                f.require(self.attempts < 1000)
                self.attempts += 1
                attempt = self.attempts
            try:
                r = getattr(self.sdk, operation)(**kw)
            except Exception as error:
                response = getattr(error, "response", {})
                status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                code = response.get("Error", {}).get("Code", "UNAVAILABLE")
                with self.lock: self.responses.append((operation, status, code))
                emit(dict(service="S3", operation=operation, attempt=attempt,
                    http_status=status, error_code=code))
                raise f.FenceError("D03_QUARANTINE") from None
            metadata = r.get("ResponseMetadata", {})
            with self.lock: self.responses.append((operation, metadata.get("HTTPStatusCode"), None))
            emit(dict(service="S3", operation=operation, attempt=attempt,
                http_status=metadata.get("HTTPStatusCode"), request_id=metadata.get("RequestId")))
            if operation == "put_object" and self.drop_next_ack:
                self.drop_next_ack = False
                raise f.FenceError("D03_INJECTED_ACK_LOSS_AFTER_REAL_COMMIT")
            return r
        return call


def native_session():
    global PHASE
    import boto3
    from botocore.config import Config
    cfg = Config(retries={"total_max_attempts": 1}, connect_timeout=10, read_timeout=20)
    f.require(os.environ.get("GITHUB_REPOSITORY") == "TDY0225/adaptive-skills-hub")
    f.require(os.environ.get("GITHUB_REF") == "refs/heads/nexus-v2-production-qualification")
    f.require(os.environ.get("GITHUB_EVENT_NAME") == "push")
    f.require(os.environ.get("GITHUB_RUN_ATTEMPT") == "1")
    f.require(datetime.now(timezone.utc) < datetime(2026,11,10,5,36,46,tzinfo=timezone.utc))
    url = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"]
    f.require(url.startswith("https://"))
    url += ("&" if "?" in url else "?") + "audience=sts.amazonaws.com"
    req = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    PHASE = "GITHUB_NATIVE_OIDC_REQUEST"
    with urllib.request.urlopen(req, timeout=20) as response:
        token = json.load(response)["value"]
    # Unsigned STS operation uses only the native OIDC token in memory.
    from botocore import UNSIGNED
    unsigned = Config(signature_version=UNSIGNED, retries={"total_max_attempts":1},
        connect_timeout=10, read_timeout=20)
    PHASE = "A_WEB_IDENTITY_ASSUME_ROLE"
    a = boto3.client("sts", region_name="us-east-1", config=unsigned).assume_role_with_web_identity(
        RoleArn=A_ROLE, RoleSessionName="nexus-d03-oidc", WebIdentityToken=token, DurationSeconds=900)
    del token, req
    def client(service, credentials):
        return boto3.client(service, region_name="ap-southeast-1", config=cfg,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"])
    a_sts = client("sts", a["Credentials"])
    PHASE = "A_CALLER_IDENTITY_CHECK"
    identity = a_sts.get_caller_identity()
    f.require(identity["Account"] == "175880707430" and
        identity["Arn"] == "arn:aws:sts::175880707430:assumed-role/G3QualD03DiagnosticCaller/nexus-d03-oidc")
    PHASE = "R_SCOPED_ASSUME_ROLE"
    r = a_sts.assume_role(RoleArn=R_ROLE, RoleSessionName="nexus-d03-qualification", DurationSeconds=900)
    r_sts = client("sts", r["Credentials"])
    PHASE = "R_CALLER_IDENTITY_CHECK"
    identity = r_sts.get_caller_identity()
    f.require(identity["Account"] == OWNER and identity["Arn"] ==
        "arn:aws:sts::862902859484:assumed-role/G3QualFenceAppendRead/nexus-d03-qualification")
    emit(dict(native_oidc_a_to_r="VERIFIED", a_account="175880707430", r_account=OWNER))
    sdk = client("s3", r["Credentials"])
    iam = client("iam", r["Credentials"])
    # Preserve SDK clients, never serialize temporary STS responses/credentials.
    del a, r
    return sdk, r_sts, iam, a_sts


def must_quarantine(label, action, outcomes):
    try:
        action()
    except f.FenceError:
        outcomes[label] = "QUARANTINE"
        return
    raise f.FenceError("D03_UNEXPECTED_ACCEPTANCE")


def main():
    global PHASE
    request = json.loads((ROOT / "research/nexus-production-d03-run-request-v1.json").read_text())
    f.require(set(request) == {"schema_version", "stage", "request_id"})
    f.require(request["schema_version"] == "nexus.g3.d03.run-request.v1")
    f.require((request["stage"], request["request_id"]) in (
        ("append", "canary-v1-append-1"), ("recovery-read", "canary-v1-recovery-read-2")))
    sdk, r_sts, r_iam, _ = native_session()
    PHASE = "PROTECTED_REGISTRATION_AND_HISTORY"
    service = BoundedS3(sdk)
    expected = (ROOT / "research/nexus-production-d03-canary-registration-v1.json").read_bytes()
    expected = canonical_bytes(json.loads(expected))
    registration = json.loads(expected)
    f.require(registration["purpose"] == "TEST_ONLY" and registration["real_admission"] == "NO")
    gen = registration["genesis"]
    def scope(prefix):
        return f.Registration(BUCKET, OWNER, prefix, v.INSTANCE, 1, gen["id"], gen["body_sha256"],
            tuple(registration["admin_checkpoint_ids"]))
    until = datetime.now(timezone.utc) + timedelta(hours=1)
    read_registration = f.S3Fence(service, scope(v.FAULTS + "custody-registration-v1/"))
    inventory = read_registration.inventory("")
    f.require(len(inventory) == 1 and inventory[0][0].endswith("/registration.json"))
    observed = read_registration.retained(*inventory[0], until)
    f.require(observed == expected)
    emit(dict(protected_registration="EXACT_SINGLE_RETAINED_VERSION", version=inventory[0][1],
        sha256=f.sha(observed), purpose="TEST_ONLY"))
    fence = f.S3Fence(service, scope(v.NORMAL))
    outcomes = {}
    def service_refusal(label, action, status, code):
        before = len(service.responses)
        must_quarantine(label, action, outcomes)
        f.require(len(service.responses) == before+1)
        f.require(service.responses[-1][1:] == (status, code))
        outcomes[label] = f"REAL_SERVICE_{status}_{code}"
    vector = v.vectors()
    history = fence.read(valid_until=until)
    v.verify_consumer(history)
    if request["stage"] == "append":
        f.require(history.head == f.reference(vector[0][0]))
        # Each complete artifact is retained before the corresponding one-shot append.
        for seq in range(1,4):
            raw, objects = vector[seq]
            existing = dict(fence.inventory("objects/"))
            for digest, body in objects.items():
                key = v.NORMAL+"objects/"+digest
                if key in existing:
                    f.require(fence.retained(key,existing[key],until) == body)
                    continue
                service.put_object(Bucket=BUCKET, ExpectedBucketOwner=OWNER,
                    Key=key, Body=body, IfNoneMatch="*",
                    ContentType="application/json", ChecksumAlgorithm="SHA256")
            head = history.head
            if seq == 2:
                service.drop_next_ack = True
                must_quarantine("unknown_ack_after_real_commit", lambda:
                    fence.append(raw, head, valid_until=until), outcomes)
                must_quarantine("unknown_no_automatic_retry", lambda:
                    fence.append(raw, head, valid_until=until), outcomes)
                history = fence.reconcile(valid_until=until)
                f.require(history.head == f.reference(raw))
                outcomes["unknown_exact_version_reconciliation"] = "VERIFIED"
            elif seq == 3:
                # Two explicitly scheduled contenders, not a retry of an unknown write.
                from concurrent.futures import ThreadPoolExecutor
                f.require(fence.read(valid_until=until).head == head)
                before = len(service.responses)
                def contender():
                    try:
                        service.put_object(Bucket=BUCKET,ExpectedBucketOwner=OWNER,
                            Key=v.NORMAL+f"journal/{3:020d}",Body=raw,IfNoneMatch="*",
                            ContentType="application/json",ChecksumAlgorithm="SHA256")
                    except f.FenceError:
                        return
                with ThreadPoolExecutor(max_workers=2) as pool:
                    list(pool.map(lambda _:contender(), range(2)))
                f.require(sorted(x[1] for x in service.responses[before:]) == [200,412])
                fence.pending = raw
                history = fence.reconcile(valid_until=until)
                outcomes["concurrent_conditional_contenders"]="ONE_200_ONE_412_ONE_VERSION"
            else:
                history = fence.append(raw, head, valid_until=until)
        outcomes["valid_conditional_append_and_exact_readback"] = "VERIFIED"
        must_quarantine("stale_append", lambda:
            fence.append(vector[1][0], f.reference(vector[0][0]), valid_until=until), outcomes)
        # Additional duplicate/conflicting attempts target the already committed key.
        key = v.NORMAL + f"journal/{3:020d}"
        service_refusal("duplicate_conditional_write", lambda: service.put_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key,Body=vector[3][0],IfNoneMatch="*"),412,"PreconditionFailed")
        service_refusal("conflicting_conditional_write", lambda: service.put_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key,Body=vector[2][0],IfNoneMatch="*"),412,"PreconditionFailed")
        service_refusal("unconditional_overwrite", lambda: service.put_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key,Body=vector[2][0]),403,"AccessDenied")
        service_refusal("normal_delete_marker", lambda: service.delete_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key),403,"AccessDenied")
        current_version = dict(history.versions)[key]
        service_refusal("retained_version_delete", lambda: service.delete_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key,VersionId=current_version),403,"AccessDenied")
        service_refusal("retention_shortening", lambda: service.put_object_retention(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Key=key,VersionId=current_version,
            Retention={"Mode":"COMPLIANCE","RetainUntilDate":datetime.now(timezone.utc)+timedelta(days=1)}),403,"AccessDenied")
        service_refusal("fault_mutation", lambda: service.put_object(Bucket=BUCKET,
            ExpectedBucketOwner=OWNER,Key=v.FAULTS+"unauthorized-call.json",Body=b'{}',IfNoneMatch="*"),403,"AccessDenied")
        authorization = dict(schema_version="nexus.g3.d03.diagnostic-admin-authorization.v1",
            purpose="TEST_ONLY",generation=1,checkpoint=f.reference(vector[4][0]),
            previous_checkpoint=f.reference(vector[3][0]))
        service_refusal("independent_recovery_authorization_mutation",lambda:service.put_object(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,
            Key=v.FAULTS+f"admin-authorizations-v1/{4:020d}/authorization.json",
            Body=canonical_bytes(authorization),IfNoneMatch="*"),403,"AccessDenied")
        must_quarantine("known_recover_hash_without_independent_authorization",lambda:
            fence.independent_recovery_authorization(f.decoded(vector[4][0]),
                f.reference(vector[4][0]),until),outcomes)
        service_refusal("recovery_bucket_administration", lambda: service.get_bucket_policy(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER),403,"AccessDenied")
        try:
            r_sts.assume_role(RoleArn="arn:aws:iam::862902859484:role/G3QualRecoveryAdmin",
                RoleSessionName="nexus-d03-qualification",DurationSeconds=900)
        except Exception as error:
            f.require(getattr(error,"response",{}).get("Error",{}).get("Code") == "AccessDenied")
            outcomes["recovery_admin_assumption"]="DENY_REAL_STS"
        else: raise f.FenceError("D03_UNEXPECTED_ADMIN_ACCESS")
        for prefix in registration["fault_prefixes"]:
            must_quarantine("isolated_fault_"+prefix.rstrip('/').rsplit('/',1)[1], lambda prefix=prefix:
                f.S3Fence(service,scope(prefix)).read(valid_until=until), outcomes)
        must_quarantine("insufficient_retention_coverage", lambda:
            fence.read(valid_until=datetime.now(timezone.utc)+timedelta(days=8)),outcomes)
        must_quarantine("restored_stale_head", lambda:
            v.verify_consumer(history, restored_head=f.reference(vector[0][0])), outcomes)
        must_quarantine("generation_mismatch",lambda:v.verify_consumer(history,generation=2),outcomes)
        must_quarantine("incarnation_mismatch",lambda:v.verify_consumer(history,incarnation="stale"),outcomes)
        outcomes["automatic_redispatch"] = v.verify_consumer(history)["automatic_redispatch"]
    else:
        f.require(history.head == f.reference(vector[4][0]))
        # Prove custody control with unchanged policy bodies: even unexpected
        # acceptance would not widen access, and would fail qualification.
        policy = json.loads((ROOT / "research/nexus-production-d03-r-append-policy-v1.json").read_text())
        f.require(policy["r_account"] == OWNER and policy["bucket"] == BUCKET and
            policy["role_name"] == "G3QualFenceAppendRead" and
            policy["recovery_admin_role_name"] == "G3QualRecoveryAdmin")
        def iam_refusal(label, operation, **arguments):
            try:
                getattr(r_iam, operation)(**arguments)
            except Exception as error:
                response = getattr(error,"response",{})
                f.require(response.get("Error",{}).get("Code") == "AccessDenied" and
                    response.get("ResponseMetadata",{}).get("HTTPStatusCode") == 403)
                emit(dict(service="IAM",operation=operation,http_status=403,error_code="AccessDenied"))
                outcomes[label] = "REAL_IAM_403_AccessDenied"
            else:
                raise f.FenceError("D03_UNEXPECTED_ADMIN_ACCESS")
        for role, trust in ((policy["role_name"],policy["trust"]),
                (policy["recovery_admin_role_name"],policy["recovery_admin_trust"])):
            iam_refusal("trust_mutation_"+role,"update_assume_role_policy",
                RoleName=role,PolicyDocument=json.dumps(trust))
        iam_refusal("append_role_permission_mutation","put_role_policy",
            RoleName=policy["role_name"],PolicyName="D03ExactCustodyOnly",
            PolicyDocument=json.dumps(policy["permissions"]))
        service_refusal("bucket_policy_mutation",lambda:service.put_bucket_policy(
            Bucket=BUCKET,ExpectedBucketOwner=OWNER,Policy=json.dumps(policy["bucket_policy"])),
            403,"AccessDenied")
        result=v.verify_consumer(history, incarnation="canary-incarnation-2")
        f.require(result["epoch"]==2 and result["sequence"]==4)
        must_quarantine("restart_old_incarnation", lambda:
            v.verify_consumer(history,incarnation="canary-incarnation-1"),outcomes)
        must_quarantine("restart_old_generation",lambda:v.verify_consumer(history,generation=2),outcomes)
        rows=v.verify_snapshot(v.EncodedSnapshot(history.controls[-1],history.pages[-1]))
        f.require(any("canary-consumed-unknown" in row.key for row in rows))
        f.require(any("canary-incarnation-1" in row.key for row in rows))
        outcomes.update(restart_current_independent_history="VERIFIED",terminal_unknown_survives="VERIFIED",
            no_prior_bearer_restored="VERIFIED_NO_BEARER_EXISTS",automatic_redispatch="DENY")
    emit(dict(d03_stage=request["stage"],request_id=request["request_id"],
        github_run_id=os.environ.get("GITHUB_RUN_ID"), source_head=os.environ.get("GITHUB_SHA"),
        s3_attempts=service.attempts,outcomes=outcomes, authority="NONE",real_admission=False,
        evidence_classes=["REAL_AWS_SERVICE_RESPONSES","SYNTHETIC_CANARY_CONSUMER_ASSERTIONS"],
        n01_production_ledger_qualification="NOT_PERFORMED"))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        response = getattr(error,"response",{})
        code = response.get("Error",{}).get("Code","LOCAL_OR_TRANSPORT_FAILURE")
        if type(code) is not str or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}",code):
            code = "UNCLASSIFIED"
        status = response.get("ResponseMetadata",{}).get("HTTPStatusCode",getattr(error,"code",None))
        if type(status) is not int or not 100 <= status <= 599: status = None
        emit(dict(d03_stage_status="QUARANTINE",phase=PHASE,error_code=code,http_status=status,
            error_class=type(error).__name__ if type(error).__name__ in
            ("FenceError","ClientError","HTTPError","KeyError","ImportError") else "UNCLASSIFIED",
            real_admission=False))
        sys.exit(1)
