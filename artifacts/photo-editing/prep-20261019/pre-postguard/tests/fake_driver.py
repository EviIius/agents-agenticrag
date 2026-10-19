"""CPU-only subprocess double. Never import MLX/MFLUX or load weights."""

import importlib.abc
import importlib.util
import json
import os
import signal
import sys
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
mode = os.environ.get("PE0_FAKE_MODE", "normal")
fake_mode = Path(sys.argv[1]).parent / "fake-mode"
if fake_mode.exists():
    mode = fake_mode.read_text()
(Path(sys.argv[1]).parent / "fake-pid").write_text(str(os.getpid()))


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"mlx", "mflux", "torch", "transformers"}:
            raise RuntimeError("Real native import forbidden in offline tests")


sys.meta_path.insert(0, NoNative())


def audit(event, args):
    if event in {"socket.connect", "socket.connect_ex"}:
        raise RuntimeError("Network forbidden in offline worker test")


sys.addaudithook(audit)


def module(name, **values):
    obj = types.ModuleType(name)
    obj.__dict__.update(values)
    sys.modules[name] = obj
    return obj


class Layer:
    bits = 4 if mode == "bad-bits" else 8


class Component:
    def leaf_modules(self):
        return [("fake", Layer())]


class Model:
    def __init__(self, **kwargs):
        self.callbacks = types.SimpleNamespace(
            register=lambda value: setattr(self, "progress", value)
        )
        self.vae = self.transformer = self.text_encoder = Component()

    def parameters(self):
        return []

    def generate_image(self, **kwargs):
        from PIL import Image

        output = Path(sys.argv[3])
        (output.parent / "fake-call.json").write_text(
            json.dumps({"class": type(self).__name__, "kwargs": kwargs})
        )
        self.progress.call_before_loop()
        if mode == "stall":
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
        for t in range(4):
            self.progress.call_in_loop(t, None)
            time.sleep(60 if mode == "stall" and t == 0 else 0.02)
        self.progress.call_after_loop()
        if mode == "mutate-reference":
            Path(kwargs["image_paths"][0]).write_bytes(b"changed")
        if mode == "mutate-original":
            (output.parent / "inputs/original").write_bytes(b"changed")
        size = (512, 512) if mode == "bad-output" else (1024, 1024)
        return Image.new("RGB", size, "cornflowerblue")


class Generate(Model):
    pass


class Edit(Model):
    pass


cache = 0


def set_cache(value):
    global cache
    previous, cache = cache, value
    return previous


mx = module(
    "mlx.core",
    metal=types.SimpleNamespace(is_available=lambda: True),
    set_cache_limit=set_cache,
    eval=lambda *a: None,
    synchronize=lambda: None,
    get_peak_memory=lambda: 25 * 1024**3 if mode == "peak" else 100,
    get_cache_memory=lambda: 0,
)
nn = module("mlx.nn", Module=Layer)
module("mlx", core=mx, nn=nn)
module("mlx.utils", tree_flatten=lambda values, **kw: values)
module("mflux")
module("mflux.models")
module("mflux.models.common")
module(
    "mflux.models.common.config",
    ModelConfig=types.SimpleNamespace(
        flux2_klein_4b=lambda: types.SimpleNamespace(model_name="black-forest-labs/FLUX.2-klein-4B")
    ),
)
module("mflux.models.flux2")
module("mflux.models.flux2.variants", Flux2Klein=Generate, Flux2KleinEdit=Edit)
spec = importlib.util.spec_from_file_location("pe0_worker", HERE / "worker.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
try:
    worker.main()
except Exception:
    worker.emit("failed")
    sys.exit(1)
