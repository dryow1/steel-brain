# Steel Brain deploy runbook (ShipReady discipline)
## Deploy
1. VPS: Hetzner/DigitalOcean, Ubuntu 24, smallest tier (~US$5-8/mo)
2. scp/git the repo to /opt/steel-brain
3. bash deploy/setup_vps.sh   (validates KB - fails if any entry unverified, by design)
4. DNS + certbot for TLS
5. Verify: curl https://api.../health -> grades_servable must equal grades_loaded
## Checks
- /health reports version + servable count (check_pins pattern)
- systemd Restart=always (NSSM-equivalent)
- KB validation gate blocks deploys with unverified entries
## Backup
- shell.db (keys + usage): nightly cron -> sqlite3 .backup, keep 7 (hermes-ops pattern)
- kb/ is in git - the repo IS the KB backup
## Rollback
- git checkout previous tag, systemctl restart steel-brain
