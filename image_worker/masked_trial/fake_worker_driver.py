"""CPU-only PE3 worker double; fail if a real model/MLX import or network occurs."""

import importlib.abc
import importlib.metadata
import importlib.util
import json
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODE = sys.argv.pop(1)
sys.path.insert(0, str(HERE.parent / "product"))


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"mlx", "mflux", "torch", "transformers"}:
            raise RuntimeError("Real model import forbidden in CPU test")


sys.meta_path.insert(0, NoNative())
real_version = importlib.metadata.version
importlib.metadata.version = lambda name: (
    "0.22.0" if name == "mflux" else real_version(name)
)


def module(name, **values):
    value = types.ModuleType(name)
    value.__dict__.update(values)
    sys.modules[name] = value
    return value


class Layer:
    bits = 8 if MODE == "bad-bits" else 4


class Component:
    def __init__(self, vae=False):
        self.vae = vae

    def leaf_modules(self):
        return [] if self.vae else [("test", Layer())]


class Model:
    def __init__(self, **kwargs):
        self.vae = Component(True)
        self.transformer = self.text_encoder = Component()
        self.callbacks = types.SimpleNamespace(
            register=lambda callback: setattr(self, "progress", callback)
        )

    def generate_image(self, **kwargs):
        import socket

        from PIL import Image

        assert kwargs["mask_image"].mode == "L"
        assert set(kwargs["mask_image"].tobytes()) == {0, 255}
        assert kwargs["auto_mask"] is None and not kwargs["enhance_prompt"]
        assert not kwargs["verify"] and kwargs["verify_retries"] == 0
        assert kwargs["num_inference_steps"] == 40 and kwargs["guidance"] == 1.0
        record = {
            k: v for k, v in kwargs.items() if k not in {"mask_image", "image_paths"}
        }
        record["mask_sha256"] = (
            __import__("hashlib").sha256(kwargs["mask_image"].tobytes()).hexdigest()
        )
        Path(sys.argv[3]).parent.joinpath("fake-call.json").write_text(
            json.dumps(record)
        )
        if MODE == "network":
            socket.socket()
        if MODE == "helper":
            self._vision_reply()
        self.progress.call_before_loop()
        for t in range(40):
            self.progress.call_in_loop(t, None)
        self.progress.call_after_loop()
        return Image.new("RGB", (1024, 1024), "yellow")


cache = memory = None


def set_cache(value):
    global cache
    previous, cache = cache, value
    return previous


def set_memory(value):
    global memory
    previous, memory = memory, value
    return previous


mx = module(
    "mlx.core",
    metal=types.SimpleNamespace(is_available=lambda: True),
    set_cache_limit=set_cache,
    set_memory_limit=set_memory,
    synchronize=lambda: None,
    eval=lambda *args: None,
    get_peak_memory=lambda: 25 * 1024**3 if MODE == "peak" else 1,
    get_cache_memory=lambda: 0,
)
nn = module("mlx.nn", Module=Layer)
module("mlx", core=mx, nn=nn)
module("mlx.utils", tree_flatten=lambda values, **kwargs: values)
for name in (
    "mflux",
    "mflux.models",
    "mflux.models.qwen21",
    "mflux.models.qwen21.variants",
    "mflux.models.qwen21.variants.edit",
):
    module(name)
module("mflux.models.qwen21.variants.edit.qwen_image_21_edit", QwenImage21Edit=Model)
spec = importlib.util.spec_from_file_location("pe3_worker", HERE / "worker.py")
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)
try:
    worker.main()
except Exception:  # noqa: BLE001 — test mirrors the private worker failure boundary
    worker.emit("failed")
    sys.exit(1)
