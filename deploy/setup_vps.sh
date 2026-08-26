#!/bin/bash
# Steel Brain VPS setup - Ubuntu 24. Run as root on fresh VPS. NSSM-discipline: hardened at deploy time.
set -e
apt update && apt install -y python3-venv python3-pip nginx certbot python3-certbot-nginx ufw git
useradd -r -m steelbrain || true
mkdir -p /opt/steel-brain && cd /opt/steel-brain
# --- copy repo here first (git clone or scp), then: ---
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
# validate KB before serving - refuses unverified entries
./venv/bin/python scripts/validate_kb.py
cp deploy/steel-brain.service /etc/systemd/system/
chown -R steelbrain:steelbrain /opt/steel-brain
systemctl daemon-reload && systemctl enable --now steel-brain
# firewall: ssh + http/https only
ufw allow OpenSSH && ufw allow 'Nginx Full' && ufw --force enable
echo "Now: point DNS at this VPS, then: certbot --nginx -d api.yourdomain.com"
echo "Nginx proxy: location / { proxy_pass http://127.0.0.1:8080; }"
echo "Issue first key: ./venv/bin/python scripts/issue_key.py issue 'first-user' 100"
