"""Retained synthetic reproduction of the actual runtime capability shape."""
import httpx
import respx
from tests.test_image_embedding_release import engine as engine, daily, embedding, metadata, progress

@respx.mock
async def test_actual_embedding_capabilities_can_handoff(engine):
    loaded = [daily(), embedding()]
    metadata(loaded)
    respx.post("http://127.0.0.1:11434/api/show").respond(200, json={"capabilities":["tools","thinking","embedding"]})
    def release(request):
        loaded[:] = [daily()]
        return httpx.Response(200, json={"done":True,"done_reason":"unload"})
    respx.post("http://127.0.0.1:11434/api/chat").mock(side_effect=release)
    async with engine.capacity.lease():
        await engine.prepare_memory(progress)
    assert loaded == [daily()]
