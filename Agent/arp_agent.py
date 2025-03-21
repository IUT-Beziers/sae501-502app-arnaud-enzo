import requests
import time
from scapy.all import sniff, ARP, get_if_list
import ipaddress
import logging
from datetime import datetime
from collections import deque
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse

# Configuration
DEFAULT_API_URL = ""
DEFAULT_API_KEY = ""
PACKET_BUFFER_SIZE = 100

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Packet buffer
packet_buffer = deque(maxlen=PACKET_BUFFER_SIZE)

def is_private_ip(ip):
    return ipaddress.ip_address(ip).is_private

def create_session(api_key):
    """
    Create a new requests session with retries.
    """
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({'Authorization': f'Api-Key {api_key}'})
    return session

def packet_callback(packet, session, api_url):
    """
    Callback function for sniffing packets, captures ARP packets and sends them to the API.
    """
    try:
        if packet.haslayer(ARP):
            src_ip = packet[ARP].psrc
            dst_ip = packet[ARP].pdst
            if is_private_ip(src_ip) and is_private_ip(dst_ip):
                data = {
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'src_mac': packet[ARP].hwsrc,
                    'dst_mac': packet[ARP].hwdst,
                    'timestamp':  datetime.now().isoformat()
                }
                packet_buffer.append(data)
                logger.info(f"Captured packet: {data}")

                if len(packet_buffer) >= PACKET_BUFFER_SIZE:
                    # send table with the packets list to the loggers
                    packets_formated = []
                    for packet in packet_buffer:
                        packets_formated.append(f"src_ip: {packet['src_ip']}, dst_ip: {packet['dst_ip']}, src_mac: {packet['src_mac']}, dst_mac: {packet['dst_mac']}, timestamp: {packet['timestamp']}")
                    logger.info(f"Sending {len(packet_buffer)} packets to the API: {packets_formated}")
                    response = session.post(api_url, json=list(packet_buffer))
                    response.raise_for_status()
                    packet_buffer.clear()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending packet to API: {e}")

def select_interface():
    """
    Select a network interface for packet sniffing if not provided as an argument.
    """
    interfaces = get_if_list()
    print("Available interfaces:")
    for i, iface in enumerate(interfaces):
        print(f"{i + 1}. {iface}")
    choice = int(input("Select the interface number: ")) - 1
    return interfaces[choice]

def main(api_url, api_key, interface=None):
    """
    Main function to start the ARP monitoring agent."
    """
    if not interface:
        interface = select_interface()

    session = create_session(api_key)
    while True:
        sniff(prn=lambda packet: packet_callback(packet, session, api_url), iface=interface, store=0, count=100, timeout=10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ARP Monitoring Agent")
    parser.add_argument('--api-url', type=str, default=DEFAULT_API_URL, help="API endpoint URL")
    parser.add_argument('--api-key', type=str, default=DEFAULT_API_KEY, help="API key for authentication")
    parser.add_argument('--interface', type=str, help="Network interface to monitor")
    args = parser.parse_args()

    main(api_url=args.api_url, api_key=args.api_key, interface=args.interface)