"""Regression checks for actual runtime-PID memory capture and cancelled streams."""
import asyncio
import importlib.util
import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
import httpx

OUT=Path(__file__).parent
os.environ['ATELIER_TRIAL_DATA']=str(Path.home()/'.local/share/workbench/qa/workflow-studio/offline-repair-controls')
spec=importlib.util.spec_from_file_location('trial_capture',OUT/'native_host.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# The listening process is selected by socket ownership, not executable name.
with patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'111\n','')):
    with patch.object(module.subprocess,'check_output',return_value='111 1 9000 /Applications/Ollama\n112 111 42000 /runtime/runner\n113 999 70000 /another/ollama\n'):
        rows=module.runtime_processes()
        assert [r['pid'] for r in rows]==[111,112] and sum(r['rss_kib'] for r in rows)==51000
actual=module.memory()
assert actual['runtime_processes'] and all(r['rss_kib']>0 for r in actual['runtime_processes'])

class Stream(httpx.AsyncByteStream):
    closed=False
    async def __aiter__(self):
        yield b'{"message":{"content":"synt'
        yield b'hetic"},"done":false}\n{"message":{"content":""},"done":true}\n'
    async def aclose(self):self.closed=True
class CancelledClose(Stream):
    async def aclose(self):raise asyncio.CancelledError()

async def check():
    with tempfile.TemporaryDirectory(prefix='atelier-capture-offline-') as folder:
        module.OUT=Path(folder)
        module.captures[:]=[{}]
        inner=Stream();stream=module.ObservedStream(inner,1)
        async for _ in stream:pass
        await stream.aclose()
        record=module.captures[0]
        assert record['first_content_at']<=record['done_at']<=record['closed_at']
        assert inner.closed and record['completed_stream'] and record['close_error'] is None
        assert (module.OUT/'call-01-response.ndjson').read_bytes().endswith(b'"done":true}\n')
        module.captures[:]=[{}]
        stream=module.ObservedStream(CancelledClose(),1)
        try:await stream.aclose()
        except asyncio.CancelledError:pass
        else:raise AssertionError('Cancellation must propagate')
        record=json.loads((module.OUT/'requests.json').read_text())[0]
        assert record['close_error']=='CancelledError' and not record['completed_stream'] and 'closed_at' in record
asyncio.run(check())
(OUT/'offline-controls.json').write_text(json.dumps({'passed':True,'native_calls':0,'checks':['Listener PID and descendant RSS; unrelated names excluded','Actual existing listener RSS available','Fragmented NDJSON timing and successful closure','Cancelled closure retained honestly with error, not a success'], 'actual_runtime_memory':actual},indent=2)+'\n')
print('Offline capture controls pass; zero native calls.')
