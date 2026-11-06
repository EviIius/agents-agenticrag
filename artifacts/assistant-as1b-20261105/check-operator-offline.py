"""Replay the trial operator with fake transports and temporary files only."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import sys
import tempfile
from unittest.mock import patch

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "server"))
from app.assistant import mac_reader as reader
from app.assistant.mac_probe import IDENTITY, ProbeFailure, reserve

operator = Path.home() / ".local/share/workbench/qa/assistant-as1b-20261105/run_read_trial.py"
compiled = compile(operator.read_text(), str(operator), "exec")
results = []
secret = "SYNTHETIC-PRIVATE-TEXT-NEVER-PRINT"
with tempfile.TemporaryDirectory(prefix="aether-reader-operator-offline-") as temporary:
    base = Path(temporary)
    def scenario(name, statuses, phases, expected_calls, expected_pass):
        home = base / name
        stage = home / ".local/share/workbench/qa/assistant-as1b-20261105"
        stage.mkdir(parents=True, mode=0o700)
        calls = []
        async def fake(build, digest, directory, request, *, approved_scope):
            assert approved_scope == "as1-b1"
            reserve(directory, request, limit=3)
            calls.append(request)
            status = statuses[len(calls)-1]
            if status == "exception":
                raise ProbeFailure(secret)
            reading = request.operation == "read_selected" and status == "ok"
            candidate = {"qualification":"unqualified", "window_title":secret,
                "group_identifier":secret,"boundary":[0],"items":[{
                    "path":[0,0],"value":secret,"description":secret,"identifier":secret,
                    "subrole":"","value_settable":False}],"settable_excluded":0} if reading else None
            return reader.ReadReply.model_validate_json(json.dumps({
                "protocol":1,"request_id":request.request_id,"operation":request.operation,
                "app":request.app,"helper_identity":IDENTITY,"helper_pid":12345,
                "status":status,"trusted":status=="ok","target_pid":23456 if reading else None,
                "bundle_id":"com.apple.MobileSMS" if reading else None,"candidate":candidate}))
        exits = []
        for phase in phases:
            output = io.StringIO()
            with patch.object(Path,"home",return_value=home), patch.object(reader,"run_read_probe",side_effect=fake), patch.object(sys,"argv",[str(operator),phase]), contextlib.redirect_stdout(output):
                try:
                    exec(compiled,{"__name__":"__main__"})
                except SystemExit as error:
                    exits.append(error.code==0)
                else:
                    exits.append(True)
            assert secret not in output.getvalue()
        assert len(calls)==expected_calls and exits==expected_pass
        results.append({"case":name,"pass":True,"synthetic_transport_calls":len(calls),
                        "private_output_leak":False,"native_calls":0})
    scenario("three-request-cap-and-private-output",["permission_required","ok","permission_required"],["permission","read","revoked","revoked"],3,[True,True,True,False])
    scenario("out-of-order",[],["read"],0,[False])
    scenario("permission-protocol-failure-stops",["unavailable"],["permission","read"],1,[False,False])
    scenario("read-refusal-stops",["ok","permission_required"],["permission","read","revoked"],2,[True,False,False])
    scenario("unexpected-revocation-success",["ok","ok","ok"],["permission","read","revoked","revoked"],3,[True,True,False,False])
    scenario("private-exception-stops",["exception"],["permission","permission","read"],1,[False,False,False])
report = {"operator_sha256":hashlib.sha256(operator.read_bytes()).hexdigest(),"passed":len(results),
          "checks":results,"native_calls":0,"model_calls":0}
(root/"artifacts/assistant-as1b-20261105/operator-offline.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
