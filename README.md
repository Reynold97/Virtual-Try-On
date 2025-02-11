# Virtual Try-On Demo Application

This application provides a web interface for virtual try-on of garments using the IDM-VTON model on Replicate.

## Prerequisites

- Python 3.10 or higher
- pip
- systemd (for service deployment)
- Git
- Node.js and npm
- debianutils

### Install System Dependencies

```bash
# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js and npm
sudo apt-get install -y nodejs

# Install debianutils (for the 'which' command)
sudo apt-get update
sudo apt-get install -y debianutils

# Verify installations
node --version
npm --version
which node  # Should show the path to Node.js
```

## Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/Reynold97/Virtual-Try-On.git
cd /root/Virtual-Try-On
```

2. **Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

3. **Install required packages**
```bash
pip install gradio
pip install replicate
pip install pillow
pip install requests
pip install python-dotenv
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```bash
nano .env
```

Add your Replicate API token:
```
REPLICATE_API_TOKEN=your_token_here
```

## Running as a Systemd Service

1. **Create a systemd service file**
```bash
sudo nano /etc/systemd/system/virtual-tryon.service
```

Add the following content:
```ini
[Unit]
Description=Virtual Try-On Demo Application
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/Virtual-Try-On
Environment="PATH=/root/Virtual-Try-On/venv/bin"
EnvironmentFile=/root/Virtual-Try-On/.env
ExecStart=/root/Virtual-Try-On/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Update the app.py launch parameters**
Modify the launch parameters in app.py to work with the service:
```python
demo.launch(
    server_name="0.0.0.0",  # Allow external connections
    server_port=7860,
    show_error=True
)
```

3. **Set proper permissions**
```bash
# Set ownership
sudo chown -R root:root /root/Virtual-Try-On

# Set proper permissions for the .env file
chmod 600 /root/Virtual-Try-On/.env
```

4. **Start and enable the service**
```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Start the service
sudo systemctl start virtual-tryon

# Enable the service to start on boot
sudo systemctl enable virtual-tryon

# Check the status
sudo systemctl status virtual-tryon
```

5. **View logs**
```bash
# View service logs
sudo journalctl -u virtual-tryon -f
```

## Firewall Configuration

If you're using UFW (Uncomplicated Firewall):
```bash
sudo ufw allow 7860
```

For other firewalls, ensure port 7860 is open for incoming connections.

## NGINX Reverse Proxy (Optional)

If you want to serve the application through NGINX:

1. **Install NGINX**
```bash
sudo apt update
sudo apt install nginx
```

2. **Create NGINX configuration**
```bash
sudo nano /etc/nginx/sites-available/virtual-tryon
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable the site**
```bash
sudo ln -s /etc/nginx/sites-available/virtual-tryon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Configuration (Optional)

To secure your application with Let's Encrypt:

1. **Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain SSL certificate**
```bash
sudo certbot --nginx -d your_domain.com
```

## Troubleshooting

1. **Check service status**
```bash
sudo systemctl status virtual-tryon
```

2. **View application logs**
```bash
sudo journalctl -u virtual-tryon -f
```

3. **Check NGINX logs**
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Security Considerations

1. **File Permissions**
   - Keep the .env file secure with restricted permissions
   - Note: Running as root is not recommended for production environments. Consider creating a dedicated service user for better security.

2. **Firewall**
   - Only open necessary ports
   - Consider using rate limiting in NGINX

3. **Updates**
   - Regularly update system packages
   - Keep Python packages up to date

## Maintenance

1. **Updating the application**
```bash
# Stop the service
sudo systemctl stop virtual-tryon

# Pull latest changes
git pull

# Activate virtual environment and update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start the service
sudo systemctl start virtual-tryon
```

2. **Backup considerations**
   - Regularly backup your .env file
   - Consider backing up any custom configurations

## Contributing

[Add your contribution guidelines here]

## License

[Add your license information here]