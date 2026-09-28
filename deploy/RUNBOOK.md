# Steel Brain deploy runbook (ShipReady discipline)
## Deploy
1. VPS: Hetzner/DigitalOcean, Ubuntu 24, smallest tier (~US$5-8/mo)
2. scp/git the repo to /root/steel-brain
3. bash deploy/setup_vps.sh   (validates KB - fails if any entry unverified, by design)
4. DNS + certbot for TLS
5. Verify: curl https://api.../health -> grades_servable must equal grades_loaded
## Update to v0.2.0 (remote MCP)
    cd /root/steel-brain && git pull
    ./venv/bin/pip install -r requirements.txt
    systemctl restart steel-brain
    curl -s -X POST https://api.steelbrain.dev/mcp -H 'Content-Type: application/json' \
      -H 'Accept: application/json, text/event-stream' \
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'     # expect 3 tools
## Checks
- /health reports version + servable count (check_pins pattern)
- systemd Restart=always (NSSM-equivalent)
- KB validation gate blocks deploys with unverified entries
## Backup
- shell.db (keys + usage): nightly cron -> sqlite3 .backup, keep 7 (hermes-ops pattern)
- kb/ is in git - the repo IS the KB backup
## Rollback
- git checkout previous tag, systemctl restart steel-brain

## TODO (future hardening)
- Currently runs as root on the droplet. Move to a dedicated non-root `steelbrain` user + `/opt/steel-brain` (least-privilege hardening) once the service is stable.
