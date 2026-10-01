"""Plain Responses API completions; public search is a separate host operation."""
from __future__ import annotations
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from ..config import ProviderRole
from ..errors import ConfigurationError, ProviderError


def _default_transport(request, timeout):
    with urlopen(request, timeout=timeout) as response:
        return response.read(2_000_001)


class OpenAIResponsesChat:
    def __init__(self, config, *, transport=None):
        if config.kind != 'openai' or config.role is not ProviderRole.CHAT or not config.api_key:
            raise ConfigurationError('Responses chat requires an OpenAI chat configuration and API key')
        self.config = config
        self._transport = transport or _default_transport

    @property
    def label(self):
        return self.config.label

    def _request(self, messages, max_tokens, stream):
        rows = []
        for message in messages:
            content = message.content
            if message.image_data_url:
                content = [{'type': 'input_text', 'text': content},
                           {'type': 'input_image', 'image_url': message.image_data_url}]
            rows.append({'role': 'developer' if message.role == 'system' else message.role, 'content': content})
        payload = {'model': self.config.model, 'input': rows, 'max_output_tokens': max_tokens,
                   'store': False, 'stream': stream}
        return Request(self.config.base_url+'/responses', data=json.dumps(payload).encode(),
                       headers={'Authorization': 'Bearer '+self.config.api_key, 'Content-Type': 'application/json'}, method='POST')

    def complete(self, messages, *, response_schema=None, max_tokens=2048, temperature=0.0):
        try:
            raw = self._transport(self._request(messages, max_tokens, False), self.config.timeout_seconds)
            if len(raw) > 2_000_000:
                raise ProviderError('Completion response is too large')
            response = json.loads(raw)
            if response.get('error') or response.get('status') in {'failed', 'incomplete'}:
                raise ProviderError('Responses completion failed or was incomplete')
            answer = '\n\n'.join(p['text'] for item in response.get('output', []) for p in item.get('content', []) if p.get('type') == 'output_text')
            if not answer.strip():
                raise ProviderError('Responses API returned no answer text')
            return answer
        except HTTPError as exc:
            raise ProviderError(f'Responses API returned HTTP {exc.code}') from exc
        except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
            raise ProviderError(f'Responses completion failed: {type(exc).__name__}') from exc

    def stream_complete(self, messages, on_token, *, max_tokens=2048, temperature=0.0):
        if self._transport is not _default_transport:
            answer = self.complete(messages, max_tokens=max_tokens)
            on_token(answer)
            return answer
        answer, completed = '', False
        started = time.monotonic()
        try:
            with urlopen(self._request(messages, max_tokens, True), timeout=self.config.timeout_seconds) as response:
                for line in response:
                    if len(line) > 1_000_000 or time.monotonic()-started > self.config.timeout_seconds:
                        raise ProviderError('Responses stream exceeded its limit')
                    if not line.startswith(b'data:'):
                        continue
                    value = json.loads(line[5:].strip())
                    kind = value.get('type')
                    if kind in {'error', 'response.failed', 'response.incomplete'}:
                        raise ProviderError('Responses stream failed or was incomplete')
                    if kind == 'response.output_text.delta':
                        token = value['delta']
                        if not isinstance(token, str):
                            raise ProviderError('Responses stream returned invalid text')
                        answer += token
                        on_token(token)
                    if kind == 'response.completed':
                        completed = True
                        break
        except HTTPError as exc:
            raise ProviderError(f'Responses API returned HTTP {exc.code}') from exc
        except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
            raise ProviderError(f'Responses stream failed: {type(exc).__name__}') from exc
        if not completed:
            raise ProviderError('Responses stream ended before completion')
        if not answer.strip():
            raise ProviderError('Responses API returned no answer text')
        return answer
