# Local search service

Prepared from SPEC Appendix F. Docker Desktop or OrbStack is required; neither is installed on this Mac yet.
The service binds only 127.0.0.1:8888. It does not change the app port, launchd label or Tailscale routing.

After the host runtime is approved and installed, copy settings.yml.template to settings.yml, replace
REPLACE_WITH_RANDOM_SECRET with a random secret, set file mode 600, and run docker compose up -d.
Then run the Workbench Search settings Test. Pin compose.yaml to the tested image digest only after success.

settings.yml is gitignored. Never expose port 8888 to the LAN or Tailscale.
This prepared configuration has not been started or validated against a real container.
