# Cortapis Hardened Deployment Guide

## Deployment Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone https://github.com/Chamacoi/Repo-Cortapi-s.git
cd Repo-Cortapi-s
git checkout cortapis-security-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install hardened dependencies
pip install -r requirements_hardened.txt
```

### 2. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Output will be something like:
# b'your_fernet_key_here...'
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env  # or use your editor
```

**Important settings:**
```bash
FLASK_ENV=production
CORTAPIS_ENCRYPTION_KEY=your_generated_key_here
CORTAPIS_API_KEY_REQUIRED=True
CORTAPIS_API_KEYS=your_api_key_1,your_api_key_2
CORTAPIS_ENFORCE_HTTPS=True
```

### 4. Generate SSL Certificates (HTTPS)

```bash
# Self-signed (development)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Production: Use Let's Encrypt
# certbot certonly --standalone -d yourdomain.com
```

### 5. Start Server

#### Development
```bash
cd cortapis_security
python web_interface_hardened.py
```

#### Production with Gunicorn
```bash
gunicorn \
  --certfile=cert.pem \
  --keyfile=key.pem \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --access-logfile cortapis_access.log \
  --error-logfile cortapis_error.log \
  web_interface_hardened:app
```

#### Production with Nginx + Gunicorn

**1. Create systemd service:**

```bash
sudo nano /etc/systemd/system/cortapis.service
```

```ini
[Unit]
Description=Cortapis Security System
After=network.target

[Service]
Type=notify
User=cortapis
WorkingDirectory=/opt/cortapis
Environment="PATH=/opt/cortapis/venv/bin"
Environment="FLASK_ENV=production"
Environment="CORTAPIS_ENCRYPTION_KEY=your_key"
Environment="CORTAPIS_API_KEYS=your_keys"
ExecStart=/opt/cortapis/venv/bin/gunicorn \
  --certfile=cert.pem \
  --keyfile=key.pem \
  --bind 127.0.0.1:5000 \
  --workers 4 \
  cortapis_security.web_interface_hardened:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**2. Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl start cortapis
sudo systemctl enable cortapis
```

**3. Configure Nginx reverse proxy:**

```bash
sudo nano /etc/nginx/sites-available/cortapis
```

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self'" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**4. Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/cortapis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Testing API

### Generate API Key
```bash
python -c "import os; print(os.urandom(32).hex())"
```

### Test Encryption Endpoint
```bash
curl -X POST https://yourdomain.com/api/encrypt \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"text": "Contact admin@example.com for access"}'
```

### Test Decryption
```bash
curl -X POST https://yourdomain.com/api/decrypt \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"session_id": "your_session_id_here"}'
```

## Monitoring

### View Logs
```bash
# Application logs
tail -f cortapis.log

# Access logs
tail -f cortapis_access.log

# Error logs
tail -f cortapis_error.log
```

### Health Check
```bash
curl https://yourdomain.com/
```

## Security Checklist

- [x] HTTPS enabled with valid certificates
- [x] API authentication enforced
- [x] Rate limiting enabled
- [x] CORS configured
- [x] Security headers set
- [x] Debug mode disabled
- [x] Logging enabled
- [ ] Database configured for session persistence
- [ ] Regular backups configured
- [ ] WAF (Web Application Firewall) enabled
- [ ] DDoS protection enabled
- [ ] Firewall rules configured
- [ ] Regular security audits scheduled

## Performance Tuning

### Gunicorn Workers
```bash
# Formula: (2 x CPU cores) + 1
gunicorn --workers 5 ...  # For 2-core system
gunicorn --workers 9 ...  # For 4-core system
```

### Keep-Alive
```bash
gunicorn --keepalive 5 ...
```

## Backup Strategy

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf cortapis_backup_$DATE.tar.gz \
  /opt/cortapis/cortapis.log \
  /opt/cortapis/.env
aws s3 cp cortapis_backup_$DATE.tar.gz s3://your-backup-bucket/
```

---

**For more information, see SECURITY_AUDIT.md**
