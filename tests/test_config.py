from __future__ import annotations

import unittest

from _bootstrap import SRC  # noqa: F401
from agenticrag.config import ProviderRole, load_provider_config, load_store_config
from agenticrag.errors import ConfigurationError


class ProviderConfigTests(unittest.TestCase):
    def test_local_is_default_but_requires_explicit_model(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "LOCAL_CHAT_MODEL"):
            load_provider_config(ProviderRole.CHAT, {})

    def test_local_profile_rejects_non_loopback_url(self) -> None:
        env = {
            "AGENTICRAG_LOCAL_CHAT_MODEL": "qwen-test",
            "AGENTICRAG_LOCAL_CHAT_BASE_URL": "https://models.example.test/v1",
        }
        with self.assertRaisesRegex(ConfigurationError, "loopback"):
            load_provider_config(ProviderRole.CHAT, env)

    def test_openai_requires_explicit_key_and_model(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "OPENAI_CHAT_MODEL"):
            load_provider_config(ProviderRole.CHAT, {"AGENTICRAG_CHAT_PROVIDER": "openai"})
        with self.assertRaisesRegex(ConfigurationError, "OPENAI_API_KEY"):
            load_provider_config(
                ProviderRole.CHAT,
                {
                    "AGENTICRAG_CHAT_PROVIDER": "openai",
                    "AGENTICRAG_OPENAI_CHAT_MODEL": "comparison-model",
                },
            )

    def test_openai_rejects_cleartext_remote_credentials(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "HTTPS"):
            load_provider_config(
                ProviderRole.CHAT,
                {
                    "AGENTICRAG_CHAT_PROVIDER": "openai",
                    "AGENTICRAG_OPENAI_CHAT_MODEL": "comparison-model",
                    "AGENTICRAG_OPENAI_API_KEY": "secret",
                    "AGENTICRAG_OPENAI_BASE_URL": "http://models.example.test/v1",
                },
            )

    def test_roles_are_selected_independently_and_public_view_hides_key(self) -> None:
        env = {
            "AGENTICRAG_CHAT_PROVIDER": "openai",
            "AGENTICRAG_OPENAI_CHAT_MODEL": "comparison-model",
            "AGENTICRAG_OPENAI_API_KEY": "secret-value",
            "AGENTICRAG_LOCAL_EMBEDDING_MODEL": "local-embed",
        }
        chat = load_provider_config(ProviderRole.CHAT, env)
        embedding = load_provider_config(ProviderRole.EMBEDDING, env)
        self.assertEqual(chat.kind, "openai")
        self.assertEqual(embedding.kind, "local")
        self.assertNotIn("secret-value", repr(chat.public_dict()))
        self.assertTrue(chat.public_dict()["credential_configured"])

    def test_provider_failure_never_changes_selected_kind(self) -> None:
        env = {
            "AGENTICRAG_CHAT_PROVIDER": "local",
            "AGENTICRAG_LOCAL_CHAT_MODEL": "local-model",
            "AGENTICRAG_OPENAI_API_KEY": "should-not-be-used",
            "AGENTICRAG_OPENAI_CHAT_MODEL": "cloud-model",
        }
        config = load_provider_config(ProviderRole.CHAT, env)
        self.assertEqual(config.kind, "local")
        self.assertIsNone(config.api_key)

    def test_postgres_store_is_explicit_and_public_view_hides_dsn(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "POSTGRES_DSN"):
            load_store_config(environ={"AGENTICRAG_STORE": "postgres"})
        config = load_store_config(
            environ={
                "AGENTICRAG_STORE": "postgres",
                "AGENTICRAG_POSTGRES_DSN": "postgresql://user:secret@localhost/test",
                "AGENTICRAG_OBJECTS_PATH": ".data/test-objects",
            }
        )
        self.assertEqual(config.backend, "postgres")
        self.assertNotIn("secret", repr(config.public_dict()))
        self.assertTrue(config.public_dict()["postgres_dsn_configured"])


if __name__ == "__main__":
    unittest.main()
