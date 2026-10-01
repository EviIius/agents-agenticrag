"""Loopback-hosted security boundary for trusted Tailscale Serve requests."""

from urllib.parse import urlsplit

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import Settings
from .errors import error_response

CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; "
    "base-uri 'none'; frame-ancestors 'none'"
)


class SecurityMiddleware:
    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app, self.settings = app, settings

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope["headers"]
        }
        raw_host = headers.get("host", "")
        try:
            parsed = urlsplit("http://" + raw_host)
            host = parsed.hostname or ""
            if parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
                host = ""
            _ = parsed.port
        except ValueError:
            host = ""
        origin = headers.get("origin")
        error = None
        if host.lower() not in self.settings.hosts:
            error = error_response("host_not_allowed", "This host is not allowed.", 403)
        elif (
            scope["method"] not in {"GET", "HEAD"}
            and origin
            and origin != f"{scope['scheme']}://{raw_host}"
        ):
            error = error_response(
                "origin_not_allowed", "This request did not come from this app.", 403
            )
        elif (
            self.settings.tailscale_owner
            and host not in {"localhost", "127.0.0.1", "::1"}
            and headers.get("tailscale-user-login") != self.settings.tailscale_owner
        ):
            error = error_response("owner_not_allowed", "This Tailscale user is not allowed.", 403)

        async def secure_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = list(message.get("headers", [])) + [
                    (b"content-security-policy", CSP.encode()),
                    (b"x-content-type-options", b"nosniff"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                ]
            await send(message)

        if error:
            await error(scope, receive, secure_send)
        else:
            await self.app(scope, receive, secure_send)
