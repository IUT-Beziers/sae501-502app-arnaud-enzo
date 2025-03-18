#!/bin/bash

while [[ $# -gt 0 ]]; do
    case "$1" in
        --api-url)
            API_URL="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        --interface)
            INTERFACE="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Install dependencies
echo "Installing dependencies..."
if [ -x "$(command -v apt-get)" ]; then
    apt-get update
    apt-get install -y python3 python3-pip
elif [ -x "$(command -v yum)" ]; then
    yum install -y python3 python3-pip
elif [ -x "$(command -v dnf)" ]; then
    dnf install -y python3 python3-pip
else
    echo "Unsupported package manager"
    exit 1
fi
pip install scapy requests ipaddress

# Download the agent script
echo "Downloading agent script..."
curl -o arp_agent.py https://raw.githubusercontent.com/your-repo/arp-agent/main/arp_agent.py
mv arp_agent.py /root/arp_agent.py
chmod +x /root/arp_agent.py

# Create service file
echo "Creating service file..."
cat > /etc/systemd/system/arp-agent.service <<EOF
[Unit]
Description=ARP Agent
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/arp_agent.py --api-url "$API_URL" --api-key "$API_KEY" --interface "$INTERFACE"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the agent
echo "Starting ARP agent..."
systemctl daemon-reload
systemctl enable arp-agent
systemctl start arp-agent